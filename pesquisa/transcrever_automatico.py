"""Transcreve as redações digitalizadas por modelo de visão, sem revisão humana.

Por que isto existe
-------------------
O experimento 5 mediu a ancoragem sobre transcrições feitas à mão, com
cuidado e com marcação de dúvida. Em produção o texto não chega assim: chega
do reconhecimento automático do manuscrito, com os erros que ele comete.

Se o ruído de reconhecimento consumir o ganho da ancoragem, a mudança não
vale em produção por melhor que seja no papel. Este script produz a versão
automática das mesmas redações, para que o experimento possa ser repetido
sobre a entrada real.

Nenhuma revisão é feita de propósito: o objetivo é medir o sistema como ele
funciona, não como gostaríamos que funcionasse.

Uso:
    python transcrever_automatico.py --listar
    python transcrever_automatico.py
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path

import anthropic
import pymupdf

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "porte_fastapi"))
sys.path.insert(0, str(AQUI))

from corretor.config import config  # noqa: E402,F401
from experimento_simulado import carregar_notas  # noqa: E402

CORPUS = AQUI / "corpus" / "simulado"
DESTINO = CORPUS / "transcricao_automatica.txt"
LOTES = Path.home() / "Downloads"
MODELO = "claude-opus-5"

# Área da folha onde fica a redação, em pontos de PDF. Deixa de fora o
# cabeçalho com prontuário e, principalmente, o nome do aluno, que aparece
# manuscrito no topo de algumas folhas.
AREA = pymupdf.Rect(70, 185, 525, 645)

INSTRUCAO = """\
Esta é uma redação manuscrita de um estudante, digitalizada.

Transcreva o texto exatamente como está escrito, incluindo erros de
ortografia, acentuação, concordância e pontuação. Esses erros são o objeto da
avaliação e não podem ser corrigidos.

Regras:
- Não corrija nada. Se o aluno escreveu "pessar", transcreva "pessar".
- Junte as linhas em parágrafos contínuos, respeitando os recuos do original.
- Onde não conseguir ler uma palavra, escreva [?] no lugar dela.
- Não inclua o cabeçalho do formulário, números de linha, nem nome ou
  prontuário, caso apareçam.
- Devolva apenas a transcrição, sem comentário."""


def pagina_de(lote_pagina: str) -> tuple[int, int] | None:
    m = re.search(r"Lote\s*(\d+)\s*/\s*p\.?\s*(\d+)", str(lote_pagina or ""))
    return (int(m.group(1)), int(m.group(2))) if m else None


def recortar(lote: int, pagina: int) -> bytes:
    caminho = LOTES / f"Lote{lote}_Redação_simulado.pdf"
    if not caminho.is_file():
        raise FileNotFoundError(caminho)
    doc = pymupdf.open(caminho)
    pix = doc[pagina - 1].get_pixmap(dpi=200, clip=AREA)
    return pix.tobytes("png")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--listar", action="store_true")
    ap.add_argument("--modelo", default=MODELO)
    args = ap.parse_args()

    import base64
    import openpyxl

    wb = openpyxl.load_workbook(CORPUS / "Catalogo redações.xlsx", data_only=True)
    ws = wb["Notas_Humanas"]
    cab, ini = None, 0
    for n, l in enumerate(ws.iter_rows(values_only=True), start=1):
        if l and l[0] == "Turma":
            cab = [str(c).strip() if c is not None else "" for c in l]
            ini = n
            break
    col = {k: i for i, k in enumerate(cab)}

    alvos = []
    for l in ws.iter_rows(min_row=ini + 1, values_only=True):
        if not l or l[col["Prontuário"]] is None:
            continue
        loc = pagina_de(l[col["Lote/Página no PDF"]])
        if loc and loc[0] in (1, 3):
            alvos.append((str(l[col["Prontuário"]]).replace(" ", "").upper(), *loc))

    notas = carregar_notas()
    alvos = sorted(set(alvos), key=lambda x: notas.get(x[0], {}).get("total", 0))

    print(f"redações com digitalização disponível: {len(alvos)}")
    for p, lote, pag in alvos:
        print(f"  {p}  lote {lote} p.{pag}  humano {notas.get(p, {}).get('total')}")
    if args.listar:
        print("\n(--listar: nada foi chamado)")
        return 0

    print(f"\nchamadas à API: {len(alvos)}\n")
    cliente = anthropic.Anthropic()
    blocos = []

    for i, (p, lote, pag) in enumerate(alvos, start=1):
        print(f"  [{i}/{len(alvos)}] {p}", end="", flush=True)
        inicio = time.monotonic()
        try:
            imagem = base64.standard_b64encode(recortar(lote, pag)).decode()
            r = cliente.messages.create(
                model=args.modelo,
                max_tokens=4000,
                messages=[{"role": "user", "content": [
                    {"type": "image", "source": {"type": "base64",
                                                 "media_type": "image/png",
                                                 "data": imagem}},
                    {"type": "text", "text": INSTRUCAO},
                ]}],
                output_config={"effort": "medium"},
            )
            texto = "".join(b.text for b in r.content if b.type == "text").strip()
        except Exception as erro:  # noqa: BLE001
            print(f"  ERRO: {erro}")
            continue
        print(f"  {len(texto.split()):>4} palavras  "
              f"{round(time.monotonic() - inicio)}s")
        blocos.append(f"{'=' * 70}\nREDAÇÃO — PRONTUÁRIO: {p}\n{'=' * 70}\n\n{texto}\n")

    cabecalho = (
        "TRANSCRIÇÃO AUTOMÁTICA — gerada por modelo de visão, sem revisão\n\n"
        "Produzida por pesquisa/transcrever_automatico.py para medir o sistema\n"
        "sobre a entrada que ele recebe em produção, onde o texto vem do\n"
        "reconhecimento do manuscrito e não de transcrição cuidadosa.\n\n"
        "Os erros de reconhecimento foram deliberadamente mantidos.\n\n"
        "ATENÇÃO: arquivo com texto de alunos. Não versionar.\n\n\n"
    )
    DESTINO.write_text(cabecalho + "\n\n".join(blocos), encoding="utf-8")
    print(f"\nsalvo em {DESTINO.relative_to(AQUI.parent)}")
    print(f"{len(blocos)} de {len(alvos)} redações transcritas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
