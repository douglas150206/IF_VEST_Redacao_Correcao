"""Detecção de cópia dos textos de apoio.

Porte fiel de `plagio.js` do sistema em Node. Compara a redação do aluno com os
textos de apoio do tema e identifica trechos copiados literalmente, no espírito
da regra do ENEM: trechos copiados dos textos motivadores não contam como
produção do participante.

Técnica: "shingles" (n-gramas de palavras). Constrói-se o conjunto de todas as
sequências de N palavras dos textos de apoio; depois percorre-se a redação e,
sempre que uma sequência de N palavras da redação já existe nesse conjunto,
aquelas palavras são marcadas como copiadas. Sequências marcadas e contíguas
são agrupadas em "trechos copiados".

Sem dependências externas — apenas a biblioteca padrão.
"""

from __future__ import annotations

import math
import re
import unicodedata
from dataclasses import dataclass

# Mesma regra do JS: remove tudo que não for letra ASCII minúscula ou dígito.
_SOMENTE_ALFANUM = re.compile(r"[^a-z0-9]")

TAMANHO_SHINGLE_PADRAO = 7


def normalizar_palavra(palavra: str) -> str:
    """Minúsculas, sem acentos e sem pontuação.

    Assim "Educação," e "educacao" passam a ser comparáveis. Equivale a
    `toLowerCase().normalize('NFD').replace(/[^a-z0-9]/g, '')` do JS: o NFD
    separa o acento da letra e o filtro descarta os acentos soltos.
    """
    decomposta = unicodedata.normalize("NFD", palavra.lower())
    return _SOMENTE_ALFANUM.sub("", decomposta)


@dataclass(frozen=True)
class Token:
    original: str  # forma original, para exibir os trechos ao usuário
    norm: str      # forma normalizada, para comparar


def tokenizar(texto: str | None) -> list[Token]:
    """Quebra o texto em tokens, descartando os que normalizam para vazio."""
    if not texto:
        return []
    tokens = (Token(original=p, norm=normalizar_palavra(p)) for p in texto.split())
    return [t for t in tokens if t.norm]


@dataclass(frozen=True)
class TrechoCopiado:
    texto: str
    palavras: int


@dataclass(frozen=True)
class ResultadoPlagio:
    percentual_copiado: int  # 0–100
    palavras_copiadas: int
    total_palavras: int
    trechos_copiados: list[TrechoCopiado]


def detectar_copia(
    redacao: str | None,
    textos_apoio: str | None,
    tamanho_shingle: int = TAMANHO_SHINGLE_PADRAO,
) -> ResultadoPlagio:
    """Detecta cópia da redação em relação aos textos de apoio."""
    apoio_tokens = tokenizar(textos_apoio)
    redacao_tokens = tokenizar(redacao)

    vazio = ResultadoPlagio(
        percentual_copiado=0,
        palavras_copiadas=0,
        total_palavras=len(redacao_tokens),
        trechos_copiados=[],
    )

    # Sem texto de apoio ou textos curtos demais → não há como comparar.
    if len(apoio_tokens) < tamanho_shingle or len(redacao_tokens) < tamanho_shingle:
        return vazio

    # 1) Conjunto de todas as sequências de N palavras dos textos de apoio.
    shingles_apoio = {
        " ".join(t.norm for t in apoio_tokens[i : i + tamanho_shingle])
        for i in range(len(apoio_tokens) - tamanho_shingle + 1)
    }

    # 2) Marca na redação toda palavra que faz parte de uma sequência copiada.
    copiado = [False] * len(redacao_tokens)
    for i in range(len(redacao_tokens) - tamanho_shingle + 1):
        gram = " ".join(t.norm for t in redacao_tokens[i : i + tamanho_shingle])
        if gram in shingles_apoio:
            for j in range(i, i + tamanho_shingle):
                copiado[j] = True

    # 3) Agrupa palavras copiadas contíguas em trechos legíveis.
    trechos: list[TrechoCopiado] = []
    inicio = -1
    for i in range(len(redacao_tokens) + 1):
        marcada = i < len(redacao_tokens) and copiado[i]
        if marcada and inicio == -1:
            inicio = i
        elif not marcada and inicio != -1:
            texto = " ".join(t.original for t in redacao_tokens[inicio:i])
            trechos.append(TrechoCopiado(texto=texto, palavras=i - inicio))
            inicio = -1

    palavras_copiadas = sum(copiado)
    total_palavras = len(redacao_tokens)

    # Math.round do JS arredonda .5 para cima; round() do Python usa
    # arredondamento bancário (2.5 -> 2). floor(x + 0.5) reproduz o JS.
    percentual = math.floor((palavras_copiadas / total_palavras) * 100 + 0.5)

    # Trechos maiores primeiro (mais relevantes para exibir).
    # sort() do Python é estável, igual ao Array.prototype.sort do V8.
    trechos.sort(key=lambda t: t.palavras, reverse=True)

    return ResultadoPlagio(
        percentual_copiado=percentual,
        palavras_copiadas=palavras_copiadas,
        total_palavras=total_palavras,
        trechos_copiados=trechos,
    )
