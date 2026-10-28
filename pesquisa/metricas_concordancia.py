"""Correlação e kappa ponderado entre a nota do sistema e a nota humana.

Por que estas métricas e não as anteriores
------------------------------------------
Viés e erro absoluto respondem "o quanto erra". Não respondem "o sistema
ordena as redações do mesmo jeito que o humano?". E essa é a pergunta que
decide se o problema tem conserto por calibração.

Se o sistema ordena bem mas com escala errada, uma curva de correção resolve.
Se ele ordena mal, nenhuma transformação monótona salva — porque nenhuma curva
reordena pontos. Foi por isso que a recalibração falhou, e é isto que mede.

O *quadratic weighted kappa* é a métrica padrão da área de correção automática.
Ela corrige pelo acaso e penaliza o erro proporcionalmente ao quadrado da
distância entre os níveis, então discordar por um nível pesa bem menos do que
discordar por quatro. Serve para comparar com a literatura: Barbosa, Silveira e
Mauá (2025) relatam QWK de 0,60 a 0,73 por competência no Essay-BR, que é o
estado da arte em português.

Interpretação convencional do kappa: abaixo de 0,20 é desprezível; 0,21 a 0,40
razoável; 0,41 a 0,60 moderado; 0,61 a 0,80 substancial.

Uso:
    python metricas_concordancia.py
    python metricas_concordancia.py --arquivo resultados/concordancia_calibrado_....json
"""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

AQUI = Path(__file__).resolve().parent
NIVEIS = [0, 40, 80, 120, 160, 200]


def pearson(xs: list[float], ys: list[float]) -> float | None:
    n = len(xs)
    if n < 2:
        return None
    mx, my = statistics.mean(xs), statistics.mean(ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx == 0 or syy == 0:
        return None
    return sxy / (sxx * syy) ** 0.5


def qwk(a: list[int], b: list[int], categorias: list[int]) -> float | None:
    """Quadratic weighted kappa sobre categorias ordinais."""
    k = len(categorias)
    indice = {v: i for i, v in enumerate(categorias)}
    pares = [(indice.get(x), indice.get(y)) for x, y in zip(a, b)]
    pares = [(i, j) for i, j in pares if i is not None and j is not None]
    if not pares:
        return None
    n = len(pares)

    observada = [[0.0] * k for _ in range(k)]
    for i, j in pares:
        observada[i][j] += 1

    marg_a = [sum(1 for i, _ in pares if i == t) for t in range(k)]
    marg_b = [sum(1 for _, j in pares if j == t) for t in range(k)]
    esperada = [[marg_a[i] * marg_b[j] / n for j in range(k)] for i in range(k)]

    peso = [[((i - j) ** 2) / ((k - 1) ** 2) for j in range(k)] for i in range(k)]
    num = sum(peso[i][j] * observada[i][j] for i in range(k) for j in range(k))
    den = sum(peso[i][j] * esperada[i][j] for i in range(k) for j in range(k))
    if den == 0:
        return None
    return 1 - num / den


def classificar(valor: float | None) -> str:
    if valor is None:
        return "—"
    v = abs(valor)
    if valor < 0:
        return "pior que o acaso"
    if v <= 0.20:
        return "desprezível"
    if v <= 0.40:
        return "razoável"
    if v <= 0.60:
        return "moderado"
    if v <= 0.80:
        return "substancial"
    return "quase perfeito"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--arquivo", type=Path, default=None)
    args = ap.parse_args()

    caminho = args.arquivo
    if caminho is None:
        candidatos = sorted((AQUI / "resultados").glob("concordancia_*.json"))
        if not candidatos:
            print("nenhum resultado de concordância encontrado")
            return 1
        caminho = candidatos[-1]
    if not caminho.is_absolute():
        caminho = AQUI / caminho

    dados = json.loads(caminho.read_text(encoding="utf-8"))
    pares = dados["pares"]
    print(f"fonte: {caminho.name}   n = {len(pares)}\n")

    h_total = [p["humano_total"] for p in pares]
    s_total = [p["sistema_total"] for p in pares]

    r = pearson(s_total, h_total)
    print("NOTA TOTAL")
    print(f"  correlação de Pearson: {r:+.3f}" if r is not None else "  correlação: —")
    if r is not None:
        print(f"  variância explicada:   {r * r:.1%}")
        print(f"  desvio padrão humano:  {statistics.stdev(h_total):.0f}")
        print(f"  desvio padrão sistema: {statistics.stdev(s_total):.0f}")

    print("\nPOR COMPETÊNCIA")
    print(f"  {'':<5}{'QWK':>8}{'r':>9}  interpretação")
    print("  " + "-" * 46)
    qwks = []
    for i in range(5):
        hc = [p["humano_comp"][i] for p in pares]
        sc = [p["sistema_comp"][i] for p in pares]
        k = qwk(sc, hc, NIVEIS)
        rc = pearson(sc, hc)
        if k is not None:
            qwks.append(k)
        txt_k = f"{k:+.3f}" if k is not None else "—"
        txt_r = f"{rc:+.3f}" if rc is not None else "—"
        print(f"  C{i + 1:<4}{txt_k:>8}{txt_r:>9}  {classificar(k)}")

    if qwks:
        media = statistics.mean(qwks)
        print(f"\n  QWK médio: {media:+.3f}  ({classificar(media)})")
        print("\n  Referência: Barbosa, Silveira e Mauá (2025) relatam 0,60 a 0,73")
        print("  por competência neste mesmo corpus — estado da arte em português.")
        if media < 0.40:
            print("\n  Abaixo de 0,40 significa que o sistema ordena as redações de")
            print("  forma pouco parecida com a do avaliador humano. Nenhuma curva de")
            print("  correção conserta isso: curva monótona reescala, não reordena.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
