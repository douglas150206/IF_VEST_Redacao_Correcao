"""Extrai do resultado bruto os números que vão para o artigo.

Uso: python analisar.py [arquivo.json]   (padrão: o mais recente)
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent


def carregar(caminho: Path | None) -> dict:
    if caminho is None:
        arquivos = sorted((AQUI / "resultados").glob("confiabilidade_*.json"))
        if not arquivos:
            raise SystemExit("nenhum resultado encontrado")
        caminho = arquivos[-1]
    print(f"fonte: {caminho.name}\n")
    return json.loads(caminho.read_text(encoding="utf-8"))


def main() -> None:
    dados = carregar(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
    bruto = [b for b in dados["bruto"] if "nota_total" in b]
    corpus = json.loads((AQUI / "corpus" / "redacoes.json").read_text(encoding="utf-8"))
    copia = {r["id"]: r.get("copia_medida", 0) for r in corpus["redacoes"]}
    modelos = dados["parametros"]["modelos"]
    ids = sorted({b["redacao"] for b in bruto})

    def notas(rid: str, modelo: str) -> list[int]:
        return [b["nota_total"] for b in bruto
                if b["redacao"] == rid and b["modelo"] == modelo]

    print("NOTAS BRUTAS POR REDAÇÃO (todas as repetições)")
    print("-" * 92)
    for rid in ids:
        for modelo in modelos:
            n = notas(rid, modelo)
            if n:
                print(f"{rid} ({copia[rid]:>2}% cópia)  {modelo:<20} {n}")
    print()

    print("DISPERSÃO — coeficiente de variação (dp / média)")
    print("-" * 92)
    print(f"{'redação':<10}{'cópia':>7}{'modelo':<22}{'média':>8}{'dp':>7}"
          f"{'CV':>8}{'idênticas':>11}")
    for rid in ids:
        for modelo in modelos:
            n = notas(rid, modelo)
            if len(n) < 2:
                continue
            media = statistics.mean(n)
            dp = statistics.stdev(n)
            cv = (dp / media * 100) if media else 0.0
            iguais = f"{max(n.count(x) for x in set(n))}/{len(n)}"
            print(f"{rid:<10}{copia[rid]:>6}%{modelo:<22}{media:>8.0f}{dp:>7.1f}"
                  f"{cv:>7.1f}%{iguais:>11}")
    print()

    print("REGRA DE CÓPIA — com que frequência a nota foi zerada")
    print("-" * 92)
    print(f"{'cópia medida':<14}{'redação':<10}{'modelo':<22}{'zerou':>10}"
          f"{'nota média':>12}")
    for rid in sorted(ids, key=lambda r: copia[r]):
        for modelo in modelos:
            n = notas(rid, modelo)
            if not n:
                continue
            zeros = sum(1 for x in n if x == 0)
            print(f"{copia[rid]:>11}%  {rid:<10}{modelo:<22}"
                  f"{f'{zeros}/{len(n)}':>10}{statistics.mean(n):>12.0f}")
    print()

    print("VIÉS ENTRE MODELOS (média opus − média sonnet, por redação)")
    print("-" * 92)
    if len(modelos) == 2:
        difs = []
        for rid in ids:
            a, b = notas(rid, modelos[0]), notas(rid, modelos[1])
            if a and b:
                d = statistics.mean(a) - statistics.mean(b)
                difs.append(d)
                print(f"{rid:<10}{copia[rid]:>4}% cópia   {d:+.0f} pontos")
        if difs:
            print(f"\nmédia das diferenças: {statistics.mean(difs):+.0f} pontos "
                  f"({modelos[0]} mais alto em {sum(1 for d in difs if d > 0)} "
                  f"de {len(difs)} redações)")
    print()

    print("AGREGADO POR MODELO")
    print("-" * 92)
    for modelo in modelos:
        amps, cvs = [], []
        for rid in ids:
            n = notas(rid, modelo)
            if len(n) > 1:
                amps.append(max(n) - min(n))
                m = statistics.mean(n)
                if m:
                    cvs.append(statistics.stdev(n) / m * 100)
        if amps:
            print(f"{modelo:<22} amplitude média {statistics.mean(amps):>5.1f}  "
                  f"CV médio {statistics.mean(cvs):>5.1f}%")

    tokens = sum(b.get("tokens_saida", 0) for b in bruto)
    seg = sum(b.get("segundos", 0) for b in bruto)
    print(f"\n{len(bruto)} correções · {tokens} tokens de saída · "
          f"{seg/60:.0f} min de processamento")


if __name__ == "__main__":
    main()
