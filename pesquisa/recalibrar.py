"""Corrige a compressão de escala do corretor com uma curva de recalibração.

Diagnóstico que motiva isto
---------------------------
A medição contra nota humana (experimento 2) mostrou que o viés médio é
desprezível (+16 pontos) mas o erro absoluto é de 115, e que o erro muda de
sinal conforme a faixa:

    fraca  +150   |   baixa  -15   |   média  -73   |   alta  -80

Ou seja: o sistema empurra redação fraca para cima e puxa redação boa para
baixo. Ele comprime uma escala de 0 a 1000 num intervalo mais estreito.

Isso é defeito de instrumento, não de julgamento, e tem conserto conhecido:
medir a relação entre o que o instrumento lê e o valor verdadeiro, e inverter.
Uma balança que lê comprimido não se conserta pedindo para ela "prestar mais
atenção" — foi isso que o prompt calibrado tentou, e piorou.

Dois modelos de correção
------------------------
- **Linear**: humano ≈ a + b × sistema. Com b > 1 a escala se expande. Robusto
  com pouca amostra, mas assume que a compressão é uniforme.
- **Isotônica**: ajusta uma função monótona qualquer. Captura compressão
  desigual entre faixas, ao custo de precisar de mais dados.

Honestidade metodológica
------------------------
Ajustar e avaliar nos mesmos 25 pares daria um número bonito e falso. Por isso
a avaliação é por **validação cruzada leave-one-out**: para cada redação, a
curva é ajustada nas outras 24 e aplicada àquela. O erro reportado é o que se
espera em redação nunca vista.

A amostra é estratificada com peso nas faixas baixas, então a curva ajustada
aqui não representa a população. Antes de usar em produção, reajustar sobre
amostra representativa — de preferência as redações do cursinho corrigidas
pelas corretoras do INEP.

Uso:
    python recalibrar.py
    python recalibrar.py --arquivo resultados/concordancia_atual_....json
"""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

AQUI = Path(__file__).resolve().parent
NOTA_MAX = 1000
PASSO = 40  # as notas do ENEM são múltiplos de 40


def ajuste_linear(xs: list[float], ys: list[float]) -> tuple[float, float]:
    """Mínimos quadrados: devolve (a, b) de y ≈ a + b·x."""
    n = len(xs)
    mx, my = statistics.mean(xs), statistics.mean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    b = sxy / sxx if sxx else 1.0
    return my - b * mx, b


def ajuste_isotonico(xs: list[float], ys: list[float]) -> list[tuple[float, float]]:
    """Regressão isotônica (pool adjacent violators). Devolve pontos (x, y)."""
    pares = sorted(zip(xs, ys))
    # Blocos de (soma, peso, x_maximo)
    blocos: list[list[float]] = []
    for x, y in pares:
        blocos.append([y, 1.0, x])
        while len(blocos) > 1 and blocos[-2][0] / blocos[-2][1] > blocos[-1][0] / blocos[-1][1]:
            s2, w2, _ = blocos.pop()
            s1, w1, x1 = blocos.pop()
            blocos.append([s1 + s2, w1 + w2, max(x1, _)])
    pontos = []
    i = 0
    for soma, peso, _ in blocos:
        media = soma / peso
        for _ in range(int(peso)):
            pontos.append((pares[i][0], media))
            i += 1
    return pontos


def aplicar_isotonico(pontos: list[tuple[float, float]], x: float) -> float:
    """Interpola linearmente entre os pontos da curva isotônica."""
    if not pontos:
        return x
    if x <= pontos[0][0]:
        return pontos[0][1]
    if x >= pontos[-1][0]:
        return pontos[-1][1]
    for (x0, y0), (x1, y1) in zip(pontos, pontos[1:]):
        if x0 <= x <= x1:
            if x1 == x0:
                return y0
            t = (x - x0) / (x1 - x0)
            return y0 + t * (y1 - y0)
    return pontos[-1][1]


def arredondar(valor: float) -> int:
    """Nota do ENEM é múltiplo de 40, entre 0 e 1000."""
    v = max(0.0, min(float(NOTA_MAX), valor))
    return int(round(v / PASSO) * PASSO)


def metricas(sistema: list[int], humano: list[int]) -> dict:
    difs = [s - h for s, h in zip(sistema, humano)]
    return {
        "vies": round(statistics.mean(difs), 1),
        "erro_absoluto": round(statistics.mean(abs(d) for d in difs), 1),
        "fora_de_100": sum(1 for d in difs if abs(d) > 100),
        "n": len(difs),
    }


def validacao_cruzada(sistema: list[int], humano: list[int], metodo: str) -> list[int]:
    """Leave-one-out: cada previsão vem de uma curva que não viu aquele ponto."""
    previstos = []
    for i in range(len(sistema)):
        xs = [x for j, x in enumerate(sistema) if j != i]
        ys = [y for j, y in enumerate(humano) if j != i]
        if metodo == "linear":
            a, b = ajuste_linear(xs, ys)
            previstos.append(arredondar(a + b * sistema[i]))
        else:
            curva = ajuste_isotonico(xs, ys)
            previstos.append(arredondar(aplicar_isotonico(curva, sistema[i])))
    return previstos


def linha(nome: str, m: dict, base: dict | None = None) -> str:
    delta = ""
    if base:
        d = m["erro_absoluto"] - base["erro_absoluto"]
        delta = f"  ({d:+.1f})"
    return (f"{nome:<28}{m['vies']:>+8.1f}{m['erro_absoluto']:>12.1f}"
            f"{m['fora_de_100']:>8}{delta}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--arquivo", type=Path, default=None,
                    help="JSON do experimento de concordância (padrão: o mais recente)")
    args = ap.parse_args()

    caminho = args.arquivo
    if caminho is None:
        candidatos = sorted((AQUI / "resultados").glob("concordancia_atual_*.json"))
        if not candidatos:
            print("nenhum resultado de concordância encontrado")
            return 1
        caminho = candidatos[-1]
    if not caminho.is_absolute():
        caminho = AQUI / caminho

    dados = json.loads(caminho.read_text(encoding="utf-8"))
    pares = dados["pares"]
    sistema = [p["sistema_total"] for p in pares]
    humano = [p["humano_total"] for p in pares]

    print(f"fonte: {caminho.name}   n = {len(pares)}\n")
    print(f"{'':<28}{'viés':>8}{'erro abs':>12}{'fora 100':>8}")
    print("-" * 64)

    base = metricas(sistema, humano)
    print(linha("sem correção", base))

    resultados = {"sem_correcao": base}
    for metodo in ("linear", "isotonica"):
        previstos = validacao_cruzada(sistema, humano, metodo)
        m = metricas(previstos, humano)
        resultados[metodo] = m
        print(linha(f"{metodo} (validação cruzada)", m, base))

    # A curva final, ajustada em todos os pontos — é esta que iria para produção.
    a, b = ajuste_linear(sistema, humano)
    print(f"\nCurva linear ajustada em todos os {len(pares)} pares:")
    print(f"  humano ≈ {a:.1f} + {b:.3f} × sistema")
    if b > 1:
        print(f"  b = {b:.3f} > 1 confirma a compressão: a escala do sistema é")
        print(f"  {1 / b:.0%} da escala humana e precisa ser expandida.")

    print("\nExemplos da correção linear:")
    print(f"  {'sistema':>9}{'corrigido':>11}")
    for s in (200, 400, 600, 800):
        print(f"  {s:>9}{arredondar(a + b * s):>11}")

    melhor = min(("linear", "isotonica"),
                 key=lambda k: resultados[k]["erro_absoluto"])
    ganho = base["erro_absoluto"] - resultados[melhor]["erro_absoluto"]
    print(f"\nMelhor método: {melhor}  "
          f"({'reduz' if ganho > 0 else 'piora'} o erro em {abs(ganho):.1f} pontos)")

    saida = AQUI / "resultados" / "recalibracao.json"
    saida.write_text(json.dumps({
        "fonte": caminho.name,
        "n": len(pares),
        "metricas": resultados,
        "curva_linear": {"a": round(a, 2), "b": round(b, 4)},
        "aviso": ("Ajustada em amostra estratificada com peso nas faixas baixas; "
                  "não representa a população. Reajustar sobre amostra "
                  "representativa antes de usar em produção."),
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"salvo em {saida.relative_to(AQUI.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
