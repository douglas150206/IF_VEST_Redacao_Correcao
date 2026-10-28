"""Experimento 2 — concordância com nota humana (Essay-BR).

O experimento 1 mediu **consistência**: o sistema repete a mesma nota? Este
mede **acurácia**: a nota está certa?

A diferença importa porque todo o trabalho de calibração feito até aqui foi
cego. Sem gabarito, dá para ver a nota mudar, mas não para saber se mudou na
direção certa. O corpus próprio do projeto não tem nota oficial; o Essay-BR tem.

Duas métricas, e a distinção entre elas decide a leitura do resultado:

- **Viés** (erro médio com sinal): média de (sistema − humano), preservando o
  sinal. Mede se o sistema é sistematicamente generoso ou severo. Deve tender a
  zero. Viés não se compensa entre alunos — desloca a nota de todo mundo.
- **Erro absoluto médio**: média de |sistema − humano|. Mede a acurácia. É este
  que se compara com os 40 pontos que a Profa. Daniela indicou como diferença
  aceitável entre dois corretores.

Um corretor com viés zero e erro absoluto de 40 é aceitável: erra para os dois
lados e se compensa. Um com viés de +60 não é, ainda que o erro absoluto seja o
mesmo — ele está consistentemente errado na mesma direção.

Corpus: Essay-BR (MARINHO; ANCHIETA; MOURA, 2021), licença MIT, em
`corpus/essay-br/`. As notas são dos anotadores daquele projeto, não da banca
do cursinho — servem para calibrar, mas a validação final tem que ser contra as
amostras corrigidas pelas corretoras do INEP.

Uso:
    python experimento_concordancia.py --amostrar          # mostra a amostra, não gasta API
    python experimento_concordancia.py --n 25
    python experimento_concordancia.py --n 25 --prompt calibrado
"""

from __future__ import annotations

import argparse
import ast
import csv
import json
import random
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
from corretor.ancoras import PROMPT_ANCORADO  # noqa: E402
from corretor.grade_inep import PROMPT_SISTEMA as PROMPT_CALIBRADO  # noqa: E402
from corretor.plagio import detectar_copia  # noqa: E402

PROMPTS = {
    "atual": PROMPT_SISTEMA,
    "calibrado": PROMPT_CALIBRADO,
    "ancorado": PROMPT_ANCORADO,
}
CORPUS = AQUI / "corpus" / "essay-br"
MODELO_PADRAO = "claude-opus-5"
MAX_TOKENS = 8000
ESFORCO = "medium"
SEMENTE = 20261023  # amostra reproduzível entre rodadas

# Faixas de nota e quantas redações tirar de cada uma numa amostra de 25.
# A distribuição é deliberadamente diferente da natural do corpus: as faixas
# baixas estão super-representadas porque é lá que o erro relatado é maior
# (nota oficial 320 recebendo 520 a 600). Isso significa que a média geral da
# amostra NÃO representa a população — por isso o relatório sempre quebra o
# resultado por faixa, que é a leitura que interessa.
FAIXAS = [
    ("fraca", 0, 400, 8),
    ("baixa", 400, 600, 8),
    ("media", 600, 800, 6),
    ("alta", 800, 1001, 3),
]


def _lista(campo: str) -> list:
    """Campos do Essay-BR vêm como lista Python serializada em string."""
    try:
        valor = ast.literal_eval(campo)
        return valor if isinstance(valor, list) else [campo]
    except (ValueError, SyntaxError):
        return [campo]


def carregar() -> tuple[list[dict], dict[str, str]]:
    with (CORPUS / "testing.csv").open(encoding="utf-8") as f:
        redacoes = list(csv.DictReader(f))
    with (CORPUS / "prompts.csv").open(encoding="utf-8") as f:
        temas = {l["id"]: "\n\n".join(_lista(l["description"])) for l in csv.DictReader(f)}
    return redacoes, temas


def amostrar(redacoes: list[dict], n: int) -> list[dict]:
    """Amostra estratificada por faixa de nota, com peso nas faixas baixas."""
    rng = random.Random(SEMENTE)
    escala = n / sum(q for *_, q in FAIXAS)
    escolhidas: list[dict] = []
    for nome, lo, hi, quota in FAIXAS:
        pool = [r for r in redacoes if lo <= int(r["score"]) < hi]
        alvo = max(1, round(quota * escala))
        rng.shuffle(pool)
        for r in pool[:alvo]:
            escolhidas.append({**r, "faixa": nome})
    return escolhidas


def corrigir(
    cliente: anthropic.Anthropic, modelo: str, redacao: str, titulo: str,
    apoio: str, sistema: str,
) -> dict:
    plagio = detectar_copia(redacao, apoio)
    prompt = montar_prompt(redacao, titulo, apoio, plagio)
    inicio = time.monotonic()
    resposta = cliente.messages.parse(
        model=modelo,
        max_tokens=MAX_TOKENS,
        # O system é idêntico em todas as correções da rodada. Marcá-lo como
        # cacheável faz a segunda chamada em diante pagar leitura de cache em
        # vez do prompt inteiro — o que importa sobretudo no prompt ancorado,
        # que carrega ~2.900 tokens fixos de redações de referência.
        system=[{
            "type": "text",
            "text": sistema,
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{"role": "user", "content": prompt}],
        output_format=CorrecaoIA,
        output_config={"effort": ESFORCO},
    )
    if resposta.stop_reason == "refusal" or resposta.parsed_output is None:
        raise RuntimeError(f"stop_reason={resposta.stop_reason}")
    c: CorrecaoIA = resposta.parsed_output
    uso = resposta.usage
    return {
        "nota_total": c.nota_total,
        "competencias": [x.nota for x in sorted(c.competencias, key=lambda y: y.numero)],
        "plagio_percentual": plagio.percentual_copiado,
        "tokens_saida": uso.output_tokens,
        "cache_lido": getattr(uso, "cache_read_input_tokens", 0) or 0,
        "segundos": round(time.monotonic() - inicio, 1),
    }


def relatar(pares: list[dict]) -> dict:
    """Viés e erro absoluto, no total, por competência e por faixa."""
    def metricas(difs: list[int]) -> dict:
        return {
            "n": len(difs),
            "vies": round(statistics.mean(difs), 1),
            "erro_absoluto": round(statistics.mean(abs(d) for d in difs), 1),
            "dp": round(statistics.stdev(difs), 1) if len(difs) > 1 else 0.0,
        }

    difs_total = [p["sistema_total"] - p["humano_total"] for p in pares]
    geral = metricas(difs_total)
    geral["fora_de_100"] = sum(1 for d in difs_total if abs(d) > 100)
    geral["fora_de_100_pct"] = round(geral["fora_de_100"] / len(difs_total) * 100, 1)

    por_competencia = {}
    for i in range(5):
        difs = [p["sistema_comp"][i] - p["humano_comp"][i] for p in pares]
        por_competencia[f"C{i + 1}"] = metricas(difs)

    por_faixa = {}
    for nome, *_ in FAIXAS:
        difs = [p["sistema_total"] - p["humano_total"] for p in pares if p["faixa"] == nome]
        if difs:
            por_faixa[nome] = metricas(difs)

    return {"geral": geral, "por_competencia": por_competencia, "por_faixa": por_faixa}


def imprimir(rel: dict, pares: list[dict]) -> None:
    g = rel["geral"]
    print("\n" + "=" * 72)
    print(f"CONCORDÂNCIA COM NOTA HUMANA  (n = {g['n']})")
    print("=" * 72)
    print(f"\nViés (sistema − humano):   {g['vies']:+.1f} pontos")
    print(f"Erro absoluto médio:        {g['erro_absoluto']:.1f} pontos")
    print(f"Fora da margem de 100:      {g['fora_de_100']} de {g['n']} "
          f"({g['fora_de_100_pct']}%)")
    print("\nLeitura: viés é o que precisa tender a zero. Erro absoluto é o que se")
    print("compara com os 40 pontos aceitos entre dois corretores humanos.")

    print(f"\n{'faixa':<8}{'n':>4}{'viés':>10}{'erro abs':>11}")
    print("-" * 36)
    for nome, m in rel["por_faixa"].items():
        print(f"{nome:<8}{m['n']:>4}{m['vies']:>+10.1f}{m['erro_absoluto']:>11.1f}")

    print(f"\n{'comp.':<8}{'viés':>10}{'erro abs':>11}")
    print("-" * 32)
    for nome, m in rel["por_competencia"].items():
        print(f"{nome:<8}{m['vies']:>+10.1f}{m['erro_absoluto']:>11.1f}")

    piores = sorted(pares, key=lambda p: abs(p["sistema_total"] - p["humano_total"]),
                    reverse=True)[:5]
    print("\nMaiores discrepâncias:")
    print(f"  {'humano':>8}{'sistema':>9}{'dif':>7}  tema")
    for p in piores:
        d = p["sistema_total"] - p["humano_total"]
        print(f"  {p['humano_total']:>8}{p['sistema_total']:>9}{d:>+7}  {p['titulo'][:40]}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n", type=int, default=25, help="tamanho da amostra")
    ap.add_argument("--prompt", choices=sorted(PROMPTS), default="atual")
    ap.add_argument("--modelo", default=MODELO_PADRAO)
    ap.add_argument("--amostrar", action="store_true",
                    help="mostra a amostra e sai, sem chamar a API")
    args = ap.parse_args()

    redacoes, temas = carregar()
    amostra = amostrar(redacoes, args.n)

    print(f"corpus: Essay-BR, split de teste ({len(redacoes)} redações)")
    print(f"amostra estratificada: {len(amostra)} redações, semente {SEMENTE}")
    for nome, *_ in FAIXAS:
        qtd = sum(1 for r in amostra if r["faixa"] == nome)
        notas = [int(r["score"]) for r in amostra if r["faixa"] == nome]
        if notas:
            print(f"  {nome:<7} {qtd:>3} redações   notas {min(notas)}–{max(notas)}")

    if args.amostrar:
        print("\n(--amostrar: nada foi chamado)")
        return 0

    print(f"prompt: {args.prompt}   modelo: {args.modelo}")
    print(f"chamadas à API: {len(amostra)}\n")

    cliente = anthropic.Anthropic()
    pares: list[dict] = []
    for i, r in enumerate(amostra, start=1):
        texto = " ".join(_lista(r["essay"]))
        apoio = temas.get(r["prompt"], "")
        humano_comp = [int(x) for x in _lista(r["competence"])]
        print(f"  [{i}/{len(amostra)}] humano {r['score']:>4} · {r['faixa']:<6}",
              end="", flush=True)
        try:
            s = corrigir(cliente, args.modelo, texto, r["title"], apoio,
                         PROMPTS[args.prompt])
        except Exception as erro:  # noqa: BLE001 — registra e segue
            print(f"  ERRO: {erro}")
            continue
        d = s["nota_total"] - int(r["score"])
        print(f"  sistema {s['nota_total']:>4}  ({d:+})")
        pares.append({
            "titulo": r["title"],
            "faixa": r["faixa"],
            "humano_total": int(r["score"]),
            "humano_comp": humano_comp,
            "sistema_total": s["nota_total"],
            "sistema_comp": s["competencias"],
            "plagio_percentual": s["plagio_percentual"],
            "tokens_saida": s["tokens_saida"],
            "cache_lido": s["cache_lido"],
        })

    lidos = sum(p["cache_lido"] for p in pares)
    if lidos:
        print(f"\ncache de prompt: {lidos} tokens lidos do cache "
              f"({lidos // max(1, len(pares))} por correção)")
    else:
        print("\naviso: nenhum token veio do cache — o prefixo está sendo invalidado")

    if not pares:
        print("\nnenhuma correção concluída — nada a relatar")
        return 1

    rel = relatar(pares)
    imprimir(rel, pares)

    saida = AQUI / "resultados"
    saida.mkdir(exist_ok=True)
    carimbo = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    arquivo = saida / f"concordancia_{args.prompt}_{carimbo}.json"
    arquivo.write_text(
        json.dumps({
            "gerado_em": carimbo,
            "corpus": "Essay-BR (testing split)",
            "parametros": {"n": args.n, "prompt": args.prompt, "modelo": args.modelo,
                           "max_tokens": MAX_TOKENS, "esforco": ESFORCO,
                           "semente": SEMENTE},
            "relatorio": rel,
            "pares": pares,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\ndados salvos em {arquivo.relative_to(AQUI.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
