"""Experimento 1 — confiabilidade teste-reteste da correção automática.

Pergunta: dada a MESMA redação, quanto a nota varia entre execuções idênticas?

Isso não mede acurácia (não há gabarito oficial neste corpus) — mede
consistência, que é pré-requisito para qualquer uso avaliativo. Um corretor que
dá 200 e 920 para o mesmo texto é inútil mesmo que a média esteja certa.

Reaproveita o prompt e a montagem de entrada do módulo de produção
(`corretor.corretor`), então mede o sistema real, não uma reimplementação. A
chamada à API é feita aqui para poder registrar tokens e latência, que o módulo
não expõe.

Uso:

    # quanto vai custar, sem chamar nada
    python experimento_confiabilidade.py --estimar

    # roda de fato
    python experimento_confiabilidade.py --repeticoes 3
    python experimento_confiabilidade.py --repeticoes 5 --modelos claude-opus-5
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import anthropic

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "porte_fastapi"))

# Importar a config carrega o .env do projeto, então ANTHROPIC_API_KEY fica
# disponível sem precisar exportar segredo no shell.
from corretor.config import config  # noqa: E402,F401
from corretor.corretor import PROMPT_SISTEMA, montar_prompt  # noqa: E402
from corretor.esquemas import CorrecaoIA  # noqa: E402
from corretor.plagio import detectar_copia  # noqa: E402

MODELOS_PADRAO = ["claude-opus-5", "claude-sonnet-4-5"]
MAX_TOKENS = 8000
ESFORCO = "medium"


def carregar_corpus() -> dict:
    return json.loads((AQUI / "corpus" / "redacoes.json").read_text(encoding="utf-8"))


def corrigir_uma_vez(
    cliente: anthropic.Anthropic, modelo: str, redacao: str, tema: dict
) -> dict:
    """Uma correção. Devolve notas, tokens e latência."""
    plagio = detectar_copia(redacao, tema["textos_apoio"])
    prompt = montar_prompt(redacao, tema["titulo"], tema["textos_apoio"], plagio)

    inicio = time.monotonic()
    # `claude-sonnet-4-5` é modelo antigo: não aceita `effort`. Só o envia para
    # os modelos que suportam, para a comparação não morrer num 400.
    extras = {} if modelo.endswith("-4-5") else {"output_config": {"effort": ESFORCO}}
    resposta = cliente.messages.parse(
        model=modelo,
        max_tokens=MAX_TOKENS,
        system=PROMPT_SISTEMA,
        messages=[{"role": "user", "content": prompt}],
        output_format=CorrecaoIA,
        **extras,
    )
    duracao = time.monotonic() - inicio

    if resposta.stop_reason == "refusal" or resposta.parsed_output is None:
        raise RuntimeError(f"correção não concluída: stop_reason={resposta.stop_reason}")

    c: CorrecaoIA = resposta.parsed_output
    return {
        "nota_total": c.nota_total,
        "competencias": [x.nota for x in sorted(c.competencias, key=lambda y: y.numero)],
        "niveis": [x.nivel for x in sorted(c.competencias, key=lambda y: y.numero)],
        "plagio_percentual": plagio.percentual_copiado,
        "tokens_entrada": resposta.usage.input_tokens,
        "tokens_saida": resposta.usage.output_tokens,
        "segundos": round(duracao, 1),
    }


def resumir(notas: list[int]) -> dict:
    return {
        "n": len(notas),
        "media": round(statistics.mean(notas), 1),
        "desvio_padrao": round(statistics.stdev(notas), 1) if len(notas) > 1 else 0.0,
        "minimo": min(notas),
        "maximo": max(notas),
        "amplitude": max(notas) - min(notas),
        "identicas": len(set(notas)) == 1,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repeticoes", type=int, default=3)
    p.add_argument("--modelos", nargs="+", default=MODELOS_PADRAO)
    p.add_argument("--redacoes", nargs="+", default=None, help="ids, ex.: R1 R4")
    p.add_argument("--estimar", action="store_true", help="só mostra o tamanho da corrida")
    args = p.parse_args()

    corpus = carregar_corpus()
    redacoes = corpus["redacoes"]
    if args.redacoes:
        redacoes = [r for r in redacoes if r["id"] in args.redacoes]

    total = len(redacoes) * len(args.modelos) * args.repeticoes
    print(f"redações: {len(redacoes)}  modelos: {len(args.modelos)}  "
          f"repetições: {args.repeticoes}")
    print(f"total de chamadas à API: {total}")
    if args.estimar:
        print("\n(--estimar: nada foi chamado)")
        return 0

    cliente = anthropic.Anthropic()  # lê ANTHROPIC_API_KEY do ambiente
    tema = corpus["tema"]
    bruto: list[dict] = []
    feito = 0

    for redacao in redacoes:
        for modelo in args.modelos:
            for rep in range(1, args.repeticoes + 1):
                feito += 1
                print(f"  [{feito}/{total}] {redacao['id']} · {modelo} · rep {rep}",
                      end="", flush=True)
                try:
                    r = corrigir_uma_vez(cliente, modelo, redacao["texto"], tema)
                except Exception as erro:  # noqa: BLE001 — registra e segue
                    print(f"  ERRO: {erro}")
                    bruto.append({"redacao": redacao["id"], "modelo": modelo,
                                  "repeticao": rep, "erro": str(erro)})
                    continue
                print(f"  nota {r['nota_total']}  ({r['segundos']}s)")
                bruto.append({"redacao": redacao["id"], "faixa": redacao["faixa_esperada"],
                              "modelo": modelo, "repeticao": rep, **r})

    # ── Resumo ───────────────────────────────────────────────────────────────
    resumo = []
    for redacao in redacoes:
        for modelo in args.modelos:
            notas = [b["nota_total"] for b in bruto
                     if b["redacao"] == redacao["id"] and b["modelo"] == modelo
                     and "nota_total" in b]
            if notas:
                resumo.append({"redacao": redacao["id"],
                               "faixa": redacao["faixa_esperada"],
                               "modelo": modelo, **resumir(notas)})

    print("\n" + "=" * 84)
    print(f"{'redação':<9}{'faixa':<8}{'modelo':<22}{'média':>8}{'dp':>8}"
          f"{'mín':>7}{'máx':>7}{'ampl.':>8}")
    print("-" * 84)
    for r in resumo:
        print(f"{r['redacao']:<9}{r['faixa']:<8}{r['modelo']:<22}"
              f"{r['media']:>8}{r['desvio_padrao']:>8}{r['minimo']:>7}"
              f"{r['maximo']:>7}{r['amplitude']:>8}")

    for modelo in args.modelos:
        linhas = [r for r in resumo if r["modelo"] == modelo]
        if linhas:
            amp = statistics.mean(r["amplitude"] for r in linhas)
            dp = statistics.mean(r["desvio_padrao"] for r in linhas)
            print(f"\n{modelo}: amplitude média {amp:.1f} pontos, "
                  f"desvio padrão médio {dp:.1f}")

    tokens = sum(b.get("tokens_saida", 0) for b in bruto)
    print(f"\ntokens de saída somados: {tokens}")

    saida = AQUI / "resultados"
    saida.mkdir(exist_ok=True)
    carimbo = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    arquivo = saida / f"confiabilidade_{carimbo}.json"
    arquivo.write_text(
        json.dumps(
            {
                "gerado_em": carimbo,
                "parametros": {"repeticoes": args.repeticoes, "modelos": args.modelos,
                               "max_tokens": MAX_TOKENS, "esforco": ESFORCO},
                "resumo": resumo,
                "bruto": bruto,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"dados salvos em {arquivo.relative_to(AQUI.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
