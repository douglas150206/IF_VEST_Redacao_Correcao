#!/usr/bin/env python3
"""Detecta cópia literal dos textos motivadores numa redação do ENEM.

Técnica: n-gramas de palavras ("shingles"). Monta-se o conjunto de todas as
sequências de N palavras dos textos motivadores; percorre-se a redação e marca-se
toda sequência de N palavras que já exista nesse conjunto. Palavras marcadas e
contíguas viram trechos legíveis.

Antes de comparar, cada palavra é normalizada: minúsculas, acentos removidos via
decomposição Unicode, e tudo que não for letra ou dígito descartado. Assim
"Educação," e "educacao" são equivalentes, e a detecção não cai por mudança de
pontuação ou acentuação.

O que este script NÃO faz, e exige leitura humana:

- Detecta apenas cópia **literal**. Substituir quatro palavras num trecho de
  trinta derruba o recall a zero, porque nenhuma janela de sete palavras
  permanece intacta. Texto parafraseado passa limpo.
- Não distingue cópia de **citação legítima**. Trecho entre aspas com
  atribuição é repertório, não cópia.

Só biblioteca padrão. Sem dependências.

Uso:
    python detectar_copia.py --redacao r.txt --apoio motivadores.txt
    python detectar_copia.py --texto "..." --apoio-texto "..."
    python detectar_copia.py --redacao r.txt --apoio m.txt --json
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import unicodedata
from dataclasses import dataclass, asdict
from pathlib import Path

TAMANHO_SHINGLE = 7

# Uma linha da folha de redação do ENEM comporta cerca de dez palavras. O
# detector conta palavras e a regra oficial conta linhas, então a conversão é
# necessária — e aproximada, por isso fica nomeada aqui.
PALAVRAS_POR_LINHA = 10

# Regra oficial: "Texto composto por cópia da Prova de Redação e/ou do Caderno
# de Questões, sem que haja mais de 7 linhas sem cópia."
LINHAS_PROPRIAS_MINIMAS = 7

# Guarda contra falso positivo em redação curta. A regra das 7 linhas pressupõe
# a folha de 30 linhas: ali, sobrar 7 próprias significa que o resto é cópia.
# Num texto de 11 linhas significa o contrário. Honra o título da regra na
# grade ("texto COMPOSTO POR cópia") mas não está literalmente escrito nela.
PERCENTUAL_COPIA_DOMINANTE = 50

# Percentual a partir do qual se considera "muitos trechos de cópia" para o
# teto da Competência II. A grade não quantifica; é decisão de projeto.
PERCENTUAL_MUITA_COPIA = 25

_SOMENTE_ALFANUM = re.compile(r"[^a-z0-9]")


def normalizar(palavra: str) -> str:
    return _SOMENTE_ALFANUM.sub("", unicodedata.normalize("NFD", palavra.lower()))


@dataclass(frozen=True)
class Trecho:
    texto: str
    palavras: int


def detectar(redacao: str, apoio: str, n: int = TAMANHO_SHINGLE) -> dict:
    orig_red = [p for p in redacao.split() if normalizar(p)]
    norm_red = [normalizar(p) for p in orig_red]
    norm_apoio = [normalizar(p) for p in apoio.split() if normalizar(p)]

    total = len(norm_red)
    if len(norm_apoio) < n or total < n:
        return {
            "percentual_copiado": 0,
            "palavras_copiadas": 0,
            "total_palavras": total,
            "trechos": [],
        }

    shingles = {
        " ".join(norm_apoio[i : i + n]) for i in range(len(norm_apoio) - n + 1)
    }

    copiado = [False] * total
    for i in range(total - n + 1):
        if " ".join(norm_red[i : i + n]) in shingles:
            for j in range(i, i + n):
                copiado[j] = True

    trechos: list[Trecho] = []
    inicio = -1
    for i in range(total + 1):
        marcada = i < total and copiado[i]
        if marcada and inicio == -1:
            inicio = i
        elif not marcada and inicio != -1:
            trechos.append(Trecho(" ".join(orig_red[inicio:i]), i - inicio))
            inicio = -1

    palavras_copiadas = sum(copiado)
    # Math.round do JS arredonda .5 para cima; round() do Python usa
    # arredondamento bancário. floor(x + 0.5) mantém paridade com o sistema.
    percentual = math.floor((palavras_copiadas / total) * 100 + 0.5)
    trechos.sort(key=lambda t: t.palavras, reverse=True)

    return {
        "percentual_copiado": percentual,
        "palavras_copiadas": palavras_copiadas,
        "total_palavras": total,
        "trechos": [asdict(t) for t in trechos],
    }


def aplicar_regras(resultado: dict) -> dict:
    """Traduz a detecção nas duas consequências previstas pela grade."""
    total = resultado["total_palavras"]
    copiadas = resultado["palavras_copiadas"]
    pct = resultado["percentual_copiado"]

    proprias = max(0, total - copiadas)
    linhas_proprias = proprias // PALAVRAS_POR_LINHA

    anula = (
        total > 0
        and pct >= PERCENTUAL_COPIA_DOMINANTE
        and linhas_proprias <= LINHAS_PROPRIAS_MINIMAS
    )

    return {
        "palavras_proprias": proprias,
        "linhas_proprias": linhas_proprias,
        "anula_por_copia": anula,
        "motivo_anulacao": (
            f"{pct}% do texto é cópia literal e restam apenas {linhas_proprias} "
            f"linha(s) de produção própria, quando a regra exige mais de "
            f"{LINHAS_PROPRIAS_MINIMAS}."
            if anula
            else None
        ),
        "teto_competencia_2": (
            80 if (not anula and pct >= PERCENTUAL_MUITA_COPIA) else None
        ),
    }


def ler(caminho: str | None, texto: str | None, rotulo: str) -> str:
    if texto is not None:
        return texto
    if caminho is None:
        sys.exit(f"erro: informe --{rotulo} (arquivo) ou --{rotulo}-texto (conteúdo)")
    p = Path(caminho)
    if not p.is_file():
        sys.exit(f"erro: arquivo não encontrado: {p}")
    return p.read_text(encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--redacao", help="arquivo com a redação do aluno")
    ap.add_argument("--texto", help="a redação direto na linha de comando")
    ap.add_argument("--apoio", help="arquivo com os textos motivadores")
    ap.add_argument("--apoio-texto", dest="apoio_texto",
                    help="os textos motivadores direto na linha de comando")
    ap.add_argument("--shingle", type=int, default=TAMANHO_SHINGLE,
                    help=f"tamanho do n-grama (padrão: {TAMANHO_SHINGLE})")
    ap.add_argument("--json", action="store_true", help="saída em JSON")
    args = ap.parse_args()

    redacao = ler(args.redacao, args.texto, "redacao")
    apoio = ler(args.apoio, args.apoio_texto, "apoio")

    resultado = detectar(redacao, apoio, args.shingle)
    regras = aplicar_regras(resultado)

    if args.json:
        print(json.dumps({**resultado, **regras}, ensure_ascii=False, indent=2))
        return 0

    print(f"Cópia detectada: {resultado['percentual_copiado']}% "
          f"({resultado['palavras_copiadas']} de {resultado['total_palavras']} palavras)")
    print(f"Produção própria: {regras['palavras_proprias']} palavras "
          f"≈ {regras['linhas_proprias']} linhas")
    print()

    if regras["anula_por_copia"]:
        print("REGRA DE ANULAÇÃO POR CÓPIA — SE APLICA")
        print(f"  {regras['motivo_anulacao']}")
        print("  As cinco competências recebem 0.")
    elif regras["teto_competencia_2"]:
        print("TETO DA COMPETÊNCIA II — SE APLICA")
        print(f"  Há muitos trechos de cópia: a Competência II não passa de "
              f"{regras['teto_competencia_2']} pontos (nível 2).")
    else:
        print("Nenhuma regra automática de cópia se aplica.")

    if resultado["trechos"]:
        print(f"\nTrechos copiados ({len(resultado['trechos'])}), maiores primeiro:")
        for i, t in enumerate(resultado["trechos"][:10], start=1):
            texto = t["texto"] if len(t["texto"]) <= 100 else t["texto"][:97] + "..."
            print(f"  {i}. [{t['palavras']} palavras] {texto}")
        if len(resultado["trechos"]) > 10:
            print(f"  ... e mais {len(resultado['trechos']) - 10}")

    print("\nLembre-se: isto detecta apenas cópia literal. Paráfrase passa limpo,")
    print("e citação legítima com atribuição não é cópia — confira antes de penalizar.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
