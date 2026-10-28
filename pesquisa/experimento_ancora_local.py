"""Ancoragem com as redações do próprio cursinho, validada leave-one-out.

O que esta tentativa faz de diferente
--------------------------------------
As três anteriores falharam, e a medição no simulado explica por quê: o
problema não é a régua estar deslocada como um todo. É que **o modelo não usa
a parte de baixo da escala**. Nas oito redações do lote 1 ele nunca desceu de
560; as corretoras desceram a 320.

- A grade do INEP pedia rigor genérico. Rigor genérico comprime tudo para o
  meio, e foi o que aconteceu.
- A ancoragem anterior usava redações do Essay-BR — outro contexto, outras
  anotadoras, outra régua. A âncora de nota baixa de lá não ensina a régua
  daqui.

Esta usa as redações do próprio simulado, corrigidas pelas corretoras que o
cursinho de fato usa. Entre as oito há três de nota baixa (320, 380, 420), que
é exatamente o que falta ao modelo ver.

Contaminação
------------
Ancorar com a redação que se vai avaliar mede memorização, não calibração.
Por isso cada redação é avaliada com um prompt montado a partir das **outras
sete** — oito prompts distintos, cada um cego ao seu próprio caso.

Com n = 8 nenhuma métrica agregada sustenta conclusão forte. A pergunta aqui é
mais simples e mais robusta que QWK: **o sistema passa a descer abaixo de
560?** Isso é visível caso a caso.

Uso:
    python experimento_ancora_local.py --listar
    python experimento_ancora_local.py
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

from corretor.config import config  # noqa: E402,F401
from corretor.corretor import PROMPT_SISTEMA, montar_prompt  # noqa: E402
from corretor.esquemas import CorrecaoIA  # noqa: E402
from corretor.plagio import detectar_copia  # noqa: E402

sys.path.insert(0, str(AQUI))
from experimento_simulado import (  # noqa: E402
    MAX_TOKENS, ESFORCO, NIVEIS, TEMA, carregar_notas, carregar_transcricoes,
    comparar, qwk,
)

MODELO_PADRAO = "claude-opus-5"

# Quantas âncoras usar por prompt, e com que perfil. A prioridade é cobrir a
# parte de baixo, que é onde o sistema falha; uma âncora alta serve de
# contraponto para o modelo não achar que tudo é ruim.
PERFIL_ANCORAS = [("baixa", 0, 500, 2), ("alta", 700, 1001, 1)]

NOMES = {
    1: "domínio da norma culta",
    2: "compreensão da proposta",
    3: "seleção e organização de argumentos",
    4: "mecanismos de coesão",
    5: "proposta de intervenção",
}


def montar_bloco(ancoras: list[dict]) -> str:
    """Monta o texto das âncoras para entrar no system prompt."""
    blocos = []
    for i, a in enumerate(ancoras, start=1):
        notas = "\n".join(
            f"  Competência {n} ({NOMES[n]}): {v}"
            for n, v in enumerate(a["final"], start=1)
        )
        blocos.append(
            f"### Referência {i} — nota final {a['total']}\n\n"
            f"{a['texto']}\n\n"
            f"Notas atribuídas pelas corretoras:\n{notas}\n"
            f"  Total: {a['total']}"
        )

    return """

## REDAÇÕES DE REFERÊNCIA DESTE CURSINHO

As redações abaixo foram corrigidas pelas mesmas corretoras que avaliam os
alunos daqui, sobre o mesmo tema. Use-as como régua.

Repare especialmente nas notas baixas. A escala vai de 0 a 200 por competência
e **a parte de baixo é usada de verdade**: notas 40 e 80 são comuns em redações
com problemas reais de argumentação ou de proposta. Não existe piso implícito
em 120. Uma redação fraca recebe nota de redação fraca.

Antes de fechar cada competência, compare a redação enviada com estas
referências e pergunte de qual delas ela está mais perto naquela competência.
Quando a sua impressão discordar do que as referências indicam, confie nelas.

""" + "\n\n---\n\n".join(blocos) + """

## FIM DAS REFERÊNCIAS

Volte agora à redação enviada para correção. As acima são régua, não o texto a
avaliar.
"""


def escolher_ancoras(candidatas: list[dict]) -> list[dict]:
    escolhidas = []
    for _, lo, hi, quota in PERFIL_ANCORAS:
        faixa = sorted(
            (c for c in candidatas if lo <= c["total"] < hi),
            key=lambda c: c["total"],
        )
        escolhidas.extend(faixa[:quota])
    return sorted(escolhidas, key=lambda c: c["total"])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--modelo", default=MODELO_PADRAO)
    ap.add_argument("--listar", action="store_true")
    args = ap.parse_args()

    transcricoes = carregar_transcricoes()
    notas = carregar_notas()
    casadas = sorted(set(transcricoes) & set(notas))

    corpus = [
        {"prontuario": p, "texto": transcricoes[p], **notas[p]}
        for p in casadas
    ]

    print(f"redações disponíveis: {len(corpus)}")
    for c in corpus:
        print(f"  {c['prontuario']}  {c['total']:>4}  {c['final']}")

    print("\nâncoras que cada rodada usaria (deixando a testada de fora):")
    for alvo in corpus[:3]:
        outras = [c for c in corpus if c["prontuario"] != alvo["prontuario"]]
        esc = escolher_ancoras(outras)
        print(f"  testando {alvo['prontuario']} ({alvo['total']}) → "
              f"âncoras {[a['total'] for a in esc]}")

    if args.listar:
        print("\n(--listar: nada foi chamado)")
        return 0

    print(f"\nchamadas à API: {len(corpus)}\n")
    cliente = anthropic.Anthropic()
    resultados = []

    for i, alvo in enumerate(corpus, start=1):
        outras = [c for c in corpus if c["prontuario"] != alvo["prontuario"]]
        ancoras = escolher_ancoras(outras)
        sistema = PROMPT_SISTEMA + montar_bloco(ancoras)

        plagio = detectar_copia(alvo["texto"], "")
        prompt = montar_prompt(alvo["texto"], TEMA, None, plagio)

        print(f"  [{i}/{len(corpus)}] {alvo['prontuario']}  humano "
              f"{alvo['total']:>4}  âncoras {[a['total'] for a in ancoras]}",
              end="", flush=True)
        inicio = time.monotonic()
        try:
            resposta = cliente.messages.parse(
                model=args.modelo,
                max_tokens=MAX_TOKENS,
                system=[{"type": "text", "text": sistema}],
                messages=[{"role": "user", "content": prompt}],
                output_format=CorrecaoIA,
                output_config={"effort": ESFORCO},
            )
            c: CorrecaoIA = resposta.parsed_output
            if c is None:
                raise RuntimeError(f"stop_reason={resposta.stop_reason}")
        except Exception as erro:  # noqa: BLE001
            print(f"  ERRO: {erro}")
            continue

        comps = [x.nota for x in sorted(c.competencias, key=lambda y: y.numero)]
        d = c.nota_total - alvo["total"]
        print(f"  → {c.nota_total:>4}  ({d:+})  {round(time.monotonic() - inicio)}s")
        resultados.append({
            "prontuario": alvo["prontuario"],
            "sistema_total": c.nota_total,
            "sistema_comp": comps,
            "final": alvo["final"],
            "A": alvo["A"],
            "B": alvo["B"],
            "humano_total": alvo["total"],
            "ancoras": [a["total"] for a in ancoras],
        })

    if not resultados:
        print("\nnenhuma correção concluída")
        return 1

    print("\n" + "=" * 68)
    print(f"ANCORAGEM LOCAL, LEAVE-ONE-OUT  (n = {len(resultados)})")
    print("=" * 68)

    relatorio = {ref: comparar(resultados, ref) for ref in ("final", "A", "B")}
    for ref, rotulo in (("final", "nota final"), ("A", "avaliadora A"),
                        ("B", "avaliadora B")):
        m = relatorio[ref]
        print(f"\ncontra {rotulo}: viés {m['vies']:+.1f}   "
              f"erro absoluto {m['erro_absoluto']:.1f}   QWK {m['qwk_medio']}")

    print("\nA PERGUNTA QUE IMPORTA: o sistema desce abaixo de 560?")
    fracas = [r for r in resultados if r["humano_total"] < 500]
    for r in fracas:
        print(f"  {r['prontuario']}  humano {r['humano_total']:>4}  "
              f"sistema {r['sistema_total']:>4}  ({r['sistema_total'] - r['humano_total']:+})")
    if fracas:
        print(f"\n  menor nota dada pelo sistema: "
              f"{min(r['sistema_total'] for r in resultados)}")
        print("  (prompt atual: 560 · prompt ancorado no Essay-BR: 560)")

    print(f"\n{'comp.':<7}{'viés':>9}{'erro abs':>11}{'QWK':>9}")
    print("-" * 36)
    for nome, v in relatorio["final"]["por_competencia"].items():
        print(f"{nome:<7}{v['vies']:>+9.1f}{v['erro_absoluto']:>11.1f}"
              f"{(v['qwk'] if v['qwk'] is not None else 0):>9.3f}")

    saida = AQUI / "resultados"
    saida.mkdir(exist_ok=True)
    carimbo = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    arquivo = saida / f"simulado_ancora_local_{carimbo}.json"
    arquivo.write_text(json.dumps({
        "gerado_em": carimbo,
        "metodo": "ancoragem com redações do próprio simulado, leave-one-out",
        "parametros": {"modelo": args.modelo, "max_tokens": MAX_TOKENS,
                       "esforco": ESFORCO, "perfil_ancoras": PERFIL_ANCORAS},
        "relatorio": relatorio,
        "resultados": resultados,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\ndados salvos em {arquivo.relative_to(AQUI.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
