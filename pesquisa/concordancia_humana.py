"""Concordância entre as duas avaliadoras humanas do simulado.

Por que esta é a medição mais importante do projeto
----------------------------------------------------
Até aqui o sistema foi comparado com "a nota humana", como se ela fosse um
ponto fixo. Não é. A planilha do simulado traz duas avaliadoras independentes,
Bruna e Aline, corrigindo as mesmas redações, e a nota final é a média das
duas.

Isso permite medir o **teto**: o quanto dois corretores treinados concordam
entre si. Nenhum sistema automático pode concordar com "a nota verdadeira"
mais do que os humanos concordam entre eles — porque, onde eles discordam, não
existe nota verdadeira única.

Se a concordância humana for alta, há espaço real para melhorar o sistema. Se
for parecida com a do sistema, o problema muda de natureza: deixa de ser
"consertar a IA" e passa a ser "a tarefa tem incerteza irredutível, e a
interface precisa comunicar isso".

Também verifica a tolerância informada pela Profa. Daniela — até 40 pontos
entre corretores por competência, até 100 na nota final — contra o que as
avaliadoras de fato fizeram.

Uso:
    python concordancia_humana.py
    python concordancia_humana.py --planilha "caminho/Catalogo redações.xlsx"
"""

from __future__ import annotations

import argparse
import statistics
from pathlib import Path

import openpyxl

AQUI = Path(__file__).resolve().parent
PADRAO = AQUI / "corpus" / "simulado" / "Catalogo redações.xlsx"
NIVEIS = [0, 40, 80, 120, 160, 200]


def qwk(a: list[int], b: list[int], categorias: list[int]) -> float | None:
    """Quadratic weighted kappa sobre categorias ordinais."""
    k = len(categorias)
    idx = {v: i for i, v in enumerate(categorias)}
    pares = [(idx.get(x), idx.get(y)) for x, y in zip(a, b)]
    pares = [(i, j) for i, j in pares if i is not None and j is not None]
    if len(pares) < 2:
        return None
    n = len(pares)
    obs = [[0.0] * k for _ in range(k)]
    for i, j in pares:
        obs[i][j] += 1
    ma = [sum(1 for i, _ in pares if i == t) for t in range(k)]
    mb = [sum(1 for _, j in pares if j == t) for t in range(k)]
    esp = [[ma[i] * mb[j] / n for j in range(k)] for i in range(k)]
    w = [[((i - j) ** 2) / ((k - 1) ** 2) for j in range(k)] for i in range(k)]
    num = sum(w[i][j] * obs[i][j] for i in range(k) for j in range(k))
    den = sum(w[i][j] * esp[i][j] for i in range(k) for j in range(k))
    return 1 - num / den if den else None


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2:
        return None
    mx, my = statistics.mean(xs), statistics.mean(ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    return sxy / (sxx * syy) ** 0.5 if sxx and syy else None


def carregar(caminho: Path) -> list[dict]:
    wb = openpyxl.load_workbook(caminho, data_only=True)
    ws = wb["Notas_Humanas"]

    # O cabeçalho real não está na primeira linha: as duas primeiras são
    # título e subtítulo da planilha.
    cabecalho = None
    inicio = 0
    for n, linha in enumerate(ws.iter_rows(values_only=True), start=1):
        if linha and linha[0] == "Turma":
            cabecalho = [str(c).strip() if c is not None else "" for c in linha]
            inicio = n
            break
    if cabecalho is None:
        raise RuntimeError("não achei o cabeçalho da aba Notas_Humanas")

    col = {nome: i for i, nome in enumerate(cabecalho)}
    registros = []
    for linha in ws.iter_rows(min_row=inicio + 1, values_only=True):
        if not linha or linha[col["Prontuário"]] is None:
            continue
        reg = {"prontuario": str(linha[col["Prontuário"]]).strip(),
               "turma": linha[col["Turma"]]}
        valido = True
        for c in range(1, 6):
            for lado in ("A", "B"):
                chave = f"C{c} {lado}"
                v = linha[col[chave]] if chave in col else None
                if v is None:
                    valido = False
                    break
                reg[chave] = int(v)
            if not valido:
                break
        if valido:
            registros.append(reg)
    return registros


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--planilha", type=Path, default=PADRAO)
    args = ap.parse_args()

    if not args.planilha.is_file():
        print(f"planilha não encontrada: {args.planilha}")
        return 1

    regs = carregar(args.planilha)
    print(f"redações com as duas avaliadoras: {len(regs)}\n")

    fora_da_escala = [
        (r["prontuario"], f"C{c} {lado}", r[f"C{c} {lado}"])
        for r in regs for c in range(1, 6) for lado in ("A", "B")
        if r[f"C{c} {lado}"] not in NIVEIS
    ]
    if fora_da_escala:
        print(f"aviso: {len(fora_da_escala)} nota(s) fora da escala de 40 em 40 —")
        for p, campo, v in fora_da_escala[:8]:
            print(f"  {p} {campo} = {v}")
        print()

    print("CONCORDÂNCIA ENTRE AS DUAS AVALIADORAS")
    print(f"  {'':<6}{'QWK':>8}{'r':>9}{'dif média':>12}{'|dif| média':>13}{'= iguais':>10}")
    print("  " + "-" * 58)
    qwks = []
    for c in range(1, 6):
        a = [r[f"C{c} A"] for r in regs]
        b = [r[f"C{c} B"] for r in regs]
        difs = [x - y for x, y in zip(a, b)]
        k = qwk(a, b, NIVEIS)
        if k is not None:
            qwks.append(k)
        iguais = sum(1 for d in difs if d == 0) / len(difs) * 100
        print(f"  C{c:<5}{(f'{k:+.3f}' if k else '—'):>8}"
              f"{(f'{pearson(a, b):+.3f}' if pearson(a, b) else '—'):>9}"
              f"{statistics.mean(difs):>+12.1f}"
              f"{statistics.mean(abs(d) for d in difs):>13.1f}{iguais:>9.0f}%")

    ta = [sum(r[f"C{c} A"] for c in range(1, 6)) for r in regs]
    tb = [sum(r[f"C{c} B"] for c in range(1, 6)) for r in regs]
    difs_t = [x - y for x, y in zip(ta, tb)]

    print(f"\n  QWK médio entre humanos: {statistics.mean(qwks):+.3f}")
    print("\nNOTA TOTAL")
    print(f"  correlação:                {pearson(ta, tb):+.3f}")
    print(f"  diferença média (A − B):   {statistics.mean(difs_t):+.1f}")
    print(f"  diferença absoluta média:  {statistics.mean(abs(d) for d in difs_t):.1f}")
    print(f"  maior diferença:           {max(abs(d) for d in difs_t)}")

    print("\nTOLERÂNCIAS INFORMADAS PELA PROFA. DANIELA")
    por_comp = [abs(r[f"C{c} A"] - r[f"C{c} B"])
                for r in regs for c in range(1, 6)]
    acima_40 = sum(1 for d in por_comp if d > 40)
    acima_100 = sum(1 for d in difs_t if abs(d) > 100)
    print(f"  competências com diferença > 40 pontos: "
          f"{acima_40} de {len(por_comp)} ({acima_40 / len(por_comp) * 100:.0f}%)")
    print(f"  redações com diferença > 100 na nota final: "
          f"{acima_100} de {len(difs_t)} ({acima_100 / len(difs_t) * 100:.0f}%)")

    print("\nCOMPARAÇÃO COM O SISTEMA (Essay-BR, n=25)")
    print(f"  QWK humano × humano: {statistics.mean(qwks):+.3f}")
    print("  QWK sistema × humano: +0.500")
    print("  Estado da arte publicado (Barbosa et al., 2025): 0,60 a 0,73")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
