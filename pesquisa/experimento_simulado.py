"""Concordância do sistema com as corretoras do simulado do cursinho.

Por que este experimento e não o do Essay-BR
---------------------------------------------
O Essay-BR deu a primeira régua, mas é de outro contexto: outras redações,
outro tema, outros anotadores. Este usa as redações do próprio cursinho,
corrigidas pelas corretoras treinadas pelo INEP que avaliam os alunos de
verdade. É o alvo real.

E tem uma vantagem que o Essay-BR não tem: **duas avaliadoras independentes
por redação**. Isso dá o teto da tarefa. Elas concordam em QWK 0,867; nenhum
sistema automático pode fazer melhor do que isso contra "a nota certa", porque
onde elas discordam não existe nota certa única.

Três comparações, e as três importam:
  - sistema contra a nota final (média das duas avaliadoras);
  - sistema contra a avaliadora A;
  - sistema contra a avaliadora B.

A nota final é média, então cai fora da escala de 40 em 40 (aparecem 100, 60).
Comparar com cada avaliadora separadamente evita esse artefato e mostra se o
sistema está mais perto de uma delas.

Limitação declarada: os textos motivadores do simulado não vieram, então o
detector de cópia não roda e o prompt não recebe os textos de apoio. Para esta
medição não é impeditivo — nenhuma das oito redações é cópia —, mas significa
que a entrada não é idêntica à de produção.

Uso:
    python experimento_simulado.py --listar          # não gasta API
    python experimento_simulado.py
    python experimento_simulado.py --prompt ancorado
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import anthropic
import openpyxl

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "porte_fastapi"))

from corretor.config import config  # noqa: E402,F401
from corretor.ancoras import PROMPT_ANCORADO  # noqa: E402
from corretor.corretor import PROMPT_SISTEMA, montar_prompt  # noqa: E402
from corretor.esquemas import CorrecaoIA  # noqa: E402
from corretor.grade_inep import PROMPT_SISTEMA as PROMPT_CALIBRADO  # noqa: E402
from corretor.plagio import detectar_copia  # noqa: E402

PROMPTS = {
    "atual": PROMPT_SISTEMA,
    "calibrado": PROMPT_CALIBRADO,
    "ancorado": PROMPT_ANCORADO,
}

CORPUS = AQUI / "corpus" / "simulado"
MODELO_PADRAO = "claude-opus-5"
MAX_TOKENS = 8000
ESFORCO = "medium"
NIVEIS = [0, 40, 80, 120, 160, 200]

# Tema inferido do conteúdo das redações — todas tratam de insegurança
# alimentar. O enunciado oficial do simulado não veio junto; se vier, trocar.
TEMA = "Os desafios para o enfrentamento da insegurança alimentar no Brasil"

_CABECALHO = re.compile(
    r"REDAÇÃO\s+(\d+)\s+—\s+PRONTUÁRIO:\s*([A-Z]{2}\s*\d+)", re.IGNORECASE
)


def carregar_transcricoes() -> dict[str, str]:
    texto = (CORPUS / "transcricao_lote1.txt").read_text(encoding="utf-8")
    marcas = list(_CABECALHO.finditer(texto))
    saida = {}
    for i, m in enumerate(marcas):
        fim = marcas[i + 1].start() if i + 1 < len(marcas) else len(texto)
        corpo = texto[m.end():fim].replace("=" * 70, "").strip()
        saida[m.group(2).replace(" ", "").upper()] = corpo
    return saida


def carregar_notas() -> dict[str, dict]:
    wb = openpyxl.load_workbook(CORPUS / "Catalogo redações.xlsx", data_only=True)
    ws = wb["Notas_Humanas"]
    cab, inicio = None, 0
    for n, linha in enumerate(ws.iter_rows(values_only=True), start=1):
        if linha and linha[0] == "Turma":
            cab = [str(c).strip() if c is not None else "" for c in linha]
            inicio = n
            break
    if cab is None:
        raise RuntimeError("cabeçalho da aba Notas_Humanas não encontrado")
    col = {nome: i for i, nome in enumerate(cab)}

    saida = {}
    for linha in ws.iter_rows(min_row=inicio + 1, values_only=True):
        if not linha or linha[col["Prontuário"]] is None:
            continue
        p = str(linha[col["Prontuário"]]).replace(" ", "").upper()
        try:
            saida[p] = {
                "final": [int(linha[col[f"C{c} Final"]]) for c in range(1, 6)],
                "A": [int(linha[col[f"C{c} A"]]) for c in range(1, 6)],
                "B": [int(linha[col[f"C{c} B"]]) for c in range(1, 6)],
                "total": int(linha[col["Nota final humana"]]),
            }
        except (TypeError, ValueError, KeyError):
            continue
    return saida


def corrigir(cliente, modelo: str, redacao: str, sistema: str) -> dict:
    plagio = detectar_copia(redacao, "")
    prompt = montar_prompt(redacao, TEMA, None, plagio)
    inicio = time.monotonic()
    resposta = cliente.messages.parse(
        model=modelo,
        max_tokens=MAX_TOKENS,
        system=[{"type": "text", "text": sistema,
                 "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": prompt}],
        output_format=CorrecaoIA,
        output_config={"effort": ESFORCO},
    )
    if resposta.stop_reason == "refusal" or resposta.parsed_output is None:
        raise RuntimeError(f"stop_reason={resposta.stop_reason}")
    c: CorrecaoIA = resposta.parsed_output
    return {
        "nota_total": c.nota_total,
        "competencias": [x.nota for x in sorted(c.competencias, key=lambda y: y.numero)],
        "segundos": round(time.monotonic() - inicio, 1),
    }


def qwk(a: list[int], b: list[int], categorias: list[int]) -> float | None:
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


def comparar(resultados: list[dict], referencia: str) -> dict:
    difs = [r["sistema_total"] - sum(r[referencia]) for r in resultados]
    por_comp = {}
    qwks = []
    for c in range(5):
        s = [r["sistema_comp"][c] for r in resultados]
        h = [r[referencia][c] for r in resultados]
        k = qwk(s, h, NIVEIS)
        if k is not None:
            qwks.append(k)
        por_comp[f"C{c + 1}"] = {
            "vies": round(statistics.mean(x - y for x, y in zip(s, h)), 1),
            "erro_absoluto": round(statistics.mean(abs(x - y) for x, y in zip(s, h)), 1),
            "qwk": round(k, 3) if k is not None else None,
        }
    return {
        "vies": round(statistics.mean(difs), 1),
        "erro_absoluto": round(statistics.mean(abs(d) for d in difs), 1),
        "qwk_medio": round(statistics.mean(qwks), 3) if qwks else None,
        "por_competencia": por_comp,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prompt", choices=sorted(PROMPTS), default="atual")
    ap.add_argument("--modelo", default=MODELO_PADRAO)
    ap.add_argument("--listar", action="store_true", help="não chama a API")
    args = ap.parse_args()

    transcricoes = carregar_transcricoes()
    notas = carregar_notas()
    casadas = sorted(set(transcricoes) & set(notas))

    print(f"redações com transcrição e nota: {len(casadas)}")
    for p in casadas:
        print(f"  {p}  humano {notas[p]['total']:>4}  "
              f"{len(transcricoes[p].split()):>4} palavras")
    if args.listar:
        print("\n(--listar: nada foi chamado)")
        return 0

    print(f"\nprompt: {args.prompt}   modelo: {args.modelo}")
    print(f"chamadas à API: {len(casadas)}\n")

    cliente = anthropic.Anthropic()
    resultados = []
    for i, p in enumerate(casadas, start=1):
        n = notas[p]
        print(f"  [{i}/{len(casadas)}] {p}  humano {n['total']:>4}", end="", flush=True)
        try:
            s = corrigir(cliente, args.modelo, transcricoes[p], PROMPTS[args.prompt])
        except Exception as erro:  # noqa: BLE001
            print(f"  ERRO: {erro}")
            continue
        print(f"  sistema {s['nota_total']:>4}  ({s['nota_total'] - n['total']:+})")
        resultados.append({
            "prontuario": p,
            "sistema_total": s["nota_total"],
            "sistema_comp": s["competencias"],
            "final": n["final"],
            "A": n["A"],
            "B": n["B"],
            "humano_total": n["total"],
        })

    if not resultados:
        print("\nnenhuma correção concluída")
        return 1

    print("\n" + "=" * 68)
    print(f"SISTEMA CONTRA AS CORRETORAS DO SIMULADO  (n = {len(resultados)})")
    print("=" * 68)

    relatorio = {}
    for ref, rotulo in (("final", "nota final (média de A e B)"),
                        ("A", "avaliadora A"), ("B", "avaliadora B")):
        m = comparar(resultados, ref)
        relatorio[ref] = m
        print(f"\ncontra {rotulo}:")
        print(f"  viés {m['vies']:+.1f}   erro absoluto {m['erro_absoluto']:.1f}"
              f"   QWK {m['qwk_medio']}")

    print("\nreferências:")
    print("  concordância entre as duas corretoras: QWK 0,867")
    print("  sistema contra Essay-BR (outro corpus): QWK 0,500")
    print("  estado da arte publicado:               0,60 a 0,73")

    m = relatorio["final"]
    print(f"\n{'comp.':<7}{'viés':>9}{'erro abs':>11}{'QWK':>9}")
    print("-" * 36)
    for nome, v in m["por_competencia"].items():
        print(f"{nome:<7}{v['vies']:>+9.1f}{v['erro_absoluto']:>11.1f}"
              f"{(v['qwk'] if v['qwk'] is not None else 0):>9.3f}")

    saida = AQUI / "resultados"
    saida.mkdir(exist_ok=True)
    carimbo = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    arquivo = saida / f"simulado_{args.prompt}_{carimbo}.json"
    arquivo.write_text(json.dumps({
        "gerado_em": carimbo,
        "corpus": "simulado do cursinho, lote 1",
        "tema_inferido": TEMA,
        "parametros": {"prompt": args.prompt, "modelo": args.modelo,
                       "max_tokens": MAX_TOKENS, "esforco": ESFORCO},
        "relatorio": relatorio,
        "resultados": resultados,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\ndados salvos em {arquivo.relative_to(AQUI.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
