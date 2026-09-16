# -*- coding: utf-8 -*-
"""Gera o artigo dentro do template oficial da RECIMA21, preservando
cabeçalho, rodapé, estilos e configuração de página do arquivo original."""

import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from conteudo import (ABSTRACT, AUTORES, CEGO, CORPO, KEYWORDS, PALABRAS_CLAVE,
                      PALAVRAS_CHAVE, REFERENCIAS, RESUMEN, RESUMO, TABELAS,
                      TITULOS)

# A revista exige avaliação cega na primeira submissão; --final inclui os autores.
FINAL = "--final" in sys.argv

TPL = AQUI / "template_recima21.docx"
UNZ = AQUI / "_build"
SAIDA = AQUI / ("ARTIGO_RECIMA21_versao-final.docx" if FINAL
                else "ARTIGO_RECIMA21.docx")

LARGURA = 8504          # largura útil da página, em twips (A4 com margens de 3 cm)
ARIAL = '<w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>'


def esc(t):
    return html.escape(t, quote=False)


def runs(texto, sz=20, bold=False):
    """Converte texto com marcação _itálico_ em uma sequência de <w:r>."""
    saida = []
    for i, parte in enumerate(texto.split("_")):
        if not parte:
            continue
        rpr = ARIAL + (f'<w:b/>' if bold else '') + (f'<w:i/>' if i % 2 else '')
        rpr += f'<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/>'
        saida.append(f'<w:r><w:rPr>{rpr}</w:rPr>'
                     f'<w:t xml:space="preserve">{esc(parte)}</w:t></w:r>')
    return "".join(saida)


def par(texto="", *, jc="both", line=360, before=0, after=0, first=0, left=0,
        bold=False, sz=20, keep=False):
    ppr = "<w:pPr>"
    if keep:
        ppr += "<w:keepNext/>"
    ppr += f'<w:spacing w:before="{before}" w:after="{after}" ' \
           f'w:line="{line}" w:lineRule="auto"/>'
    if first or left:
        ppr += f'<w:ind w:left="{left}" w:firstLine="{first}"/>'
    ppr += f'<w:jc w:val="{jc}"/><w:rPr>{ARIAL}'
    if bold:
        ppr += "<w:b/>"
    ppr += f'<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/></w:rPr></w:pPr>'
    return f"<w:p>{ppr}{runs(texto, sz=sz, bold=bold) if texto else ''}</w:p>"


def celula(texto, largura, *, bold=False, jc="center", fundo=None, span=1):
    sombra = f'<w:shd w:val="clear" w:color="auto" w:fill="{fundo}"/>' if fundo else ""
    grid = f'<w:gridSpan w:val="{span}"/>' if span > 1 else ""
    ppr = ('<w:pPr><w:spacing w:before="40" w:after="40" w:line="240" '
           f'w:lineRule="auto"/><w:jc w:val="{jc}"/>'
           f'<w:rPr>{ARIAL}{"<w:b/>" if bold else ""}'
           '<w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr></w:pPr>')
    return (f'<w:tc><w:tcPr><w:tcW w:w="{largura}" w:type="dxa"/>{grid}{sombra}'
            f'<w:vAlign w:val="center"/></w:tcPr>'
            f'<w:p>{ppr}{runs(texto, sz=18, bold=bold) if texto else ""}</w:p></w:tc>')


def tabela(chave):
    spec = TABELAS[chave]
    larguras, linhas = spec["widths"], spec["rows"]
    bordas = ("<w:tblBorders>" + "".join(
        f'<w:{b} w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
        for b in ("top", "left", "bottom", "right", "insideH", "insideV")
    ) + "</w:tblBorders>")
    xml = ('<w:tbl><w:tblPr><w:tblStyle w:val="Tabelanormal"/>'
           f'<w:tblW w:w="{sum(larguras)}" w:type="dxa"/>'
           '<w:jc w:val="center"/>' + bordas +
           '<w:tblLayout w:type="fixed"/><w:tblLook w:val="04A0" w:firstRow="1" '
           'w:lastRow="0" w:firstColumn="1" w:lastColumn="0" w:noHBand="0" '
           'w:noVBand="1"/></w:tblPr><w:tblGrid>' +
           "".join(f'<w:gridCol w:w="{w}"/>' for w in larguras) + "</w:tblGrid>")
    for i, linha in enumerate(linhas):
        cabecalho = i == 0
        xml += ('<w:tr><w:trPr><w:cantSplit/>'
                + ('<w:tblHeader/>' if cabecalho else '')
                + '<w:jc w:val="center"/></w:trPr>')
        j = 0
        while j < len(linha):
            valor = linha[j]
            span, largura = 1, larguras[j]
            while j + span < len(linha) and linha[j + span] is None:
                largura += larguras[j + span]
                span += 1
            texto = valor or ""
            alinha = "center" if (cabecalho or len(texto) <= 30) else "both"
            xml += celula(texto, largura, bold=cabecalho, jc=alinha,
                          fundo="D9D9D9" if cabecalho else None, span=span)
            j += span
        xml += "</w:tr>"
    return xml + "</w:tbl>"


# Reextrai o template intacto a cada execução.
if UNZ.exists():
    shutil.rmtree(UNZ)
subprocess.run(["unzip", "-oq", str(TPL), "-d", str(UNZ)], check=True)

# ─── Montagem do corpo ──────────────────────────────────────────────────────
corpo = []

for t in TITULOS:
    corpo.append(par(t.upper(), jc="center", line=240, after=240, bold=True))

corpo.append(par())
if FINAL:
    for autor in AUTORES:
        corpo.append(par(autor, jc="center", line=240, after=120))
    corpo.append(par())
else:
    corpo.append(par(CEGO, jc="center", line=240, after=240))
corpo.append(par())

for rotulo, texto, chave, palavras in (
    ("RESUMO", RESUMO, "PALAVRAS-CHAVE", PALAVRAS_CHAVE),
    ("ABSTRACT", ABSTRACT, "KEYWORDS", KEYWORDS),
    ("RESUMEN", RESUMEN, "PALABRAS CLAVE", PALABRAS_CLAVE),
):
    corpo.append(par(rotulo, jc="left", line=240, before=120, after=60, bold=True))
    corpo.append(par(texto, line=240, after=120))
    corpo.append(par(f"{chave}: {palavras}", line=240, after=240))

corpo.append(par())

for tipo, valor in CORPO:
    if tipo == "h1":
        corpo.append(par(valor, jc="left", before=240, after=120, bold=True))
    elif tipo == "h2":
        corpo.append(par(valor, jc="left", before=240, after=120, bold=True))
    elif tipo == "p":
        corpo.append(par(valor, first=709))
    elif tipo == "cit":
        corpo.append(par(valor, left=2268, line=240, before=120, after=120, sz=18))
    elif tipo == "cap":
        corpo.append(par(valor, jc="left", line=240, before=240, after=60,
                         bold=True, keep=True))
    elif tipo == "tbl":
        corpo.append(tabela(valor))
    elif tipo == "fonte":
        corpo.append(par(valor, jc="left", line=240, before=60, after=240, sz=18))

corpo.append(par("REFERÊNCIAS", jc="left", before=240, after=120, bold=True))
for r in sorted(REFERENCIAS, key=lambda s: s.lower()):
    corpo.append(par(r, jc="left", line=240, after=240))

# ─── Escrita do document.xml ────────────────────────────────────────────────
original = (UNZ / "word" / "document.xml").read_text(encoding="utf-8")
abertura = original[:original.index("<w:body>") + len("<w:body>")]
sectpr = re.search(r"<w:sectPr.*?</w:sectPr>", original, re.S).group(0)

(UNZ / "word" / "document.xml").write_text(
    abertura + "".join(corpo) + sectpr + "</w:body></w:document>", encoding="utf-8")

if SAIDA.exists():
    SAIDA.unlink()
subprocess.run(["zip", "-Xrq", str(SAIDA), "."], cwd=UNZ, check=True)
print("gerado:", SAIDA, SAIDA.stat().st_size, "bytes")
