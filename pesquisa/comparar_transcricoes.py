"""Mede a divergência entre a transcrição manual e a automática.

Para interpretar o experimento sobre entrada automática é preciso saber quanto
ruído ela introduz. Se as duas transcrições forem quase iguais, uma eventual
queda na nota não vem do reconhecimento; se divergirem muito, vem.

A métrica é a distância de edição em nível de palavra, normalizada pelo
tamanho do texto manual — ou seja, que fração das palavras precisaria ser
inserida, removida ou trocada para transformar uma na outra.

A comparação é feita sobre as palavras normalizadas (minúsculas, sem acento e
sem pontuação), porque diferença de acentuação entre as duas transcrições é
ruído de leitura e não divergência de conteúdo. O efeito dessas diferenças
sobre a Competência I é medido depois, pela nota.

Uso:
    python comparar_transcricoes.py
"""

from __future__ import annotations

import re
import statistics
import sys
import unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

from experimento_simulado import CORPUS, _CABECALHO, carregar_transcricoes  # noqa: E402

_SO_ALFANUM = re.compile(r"[^a-z0-9]")


def normalizar(palavra: str) -> str:
    return _SO_ALFANUM.sub("", unicodedata.normalize("NFD", palavra.lower()))


def palavras(texto: str) -> list[str]:
    return [p for p in (normalizar(x) for x in texto.split()) if p]


def distancia(a: list[str], b: list[str]) -> int:
    """Distância de edição (Levenshtein) em nível de palavra."""
    anterior = list(range(len(b) + 1))
    for i, pa in enumerate(a, start=1):
        atual = [i]
        for j, pb in enumerate(b, start=1):
            atual.append(min(anterior[j] + 1,        # remoção
                             atual[j - 1] + 1,       # inserção
                             anterior[j - 1] + (pa != pb)))  # troca
        anterior = atual
    return anterior[-1]


def carregar_automaticas() -> dict[str, str]:
    arquivo = CORPUS / "transcricao_automatica.txt"
    texto = arquivo.read_text(encoding="utf-8")
    marcas = list(_CABECALHO.finditer(texto))
    saida = {}
    for i, m in enumerate(marcas):
        fim = marcas[i + 1].start() if i + 1 < len(marcas) else len(texto)
        corpo = texto[m.end():fim].replace("=" * 70, "").strip()
        saida[m.group(1).replace(" ", "").upper()] = corpo
    return saida


def main() -> int:
    manuais = carregar_transcricoes()
    automaticas = carregar_automaticas()
    comuns = sorted(set(manuais) & set(automaticas))

    print(f"redações nas duas transcrições: {len(comuns)}\n")
    print(f"{'redação':<12}{'manual':>8}{'auto':>7}{'edições':>9}{'divergência':>13}")
    print("-" * 50)

    taxas = []
    for p in comuns:
        a, b = palavras(manuais[p]), palavras(automaticas[p])
        if not a:
            continue
        d = distancia(a, b)
        taxa = d / len(a)
        taxas.append(taxa)
        print(f"{p:<12}{len(a):>8}{len(b):>7}{d:>9}{taxa:>12.1%}")

    if taxas:
        print(f"\ndivergência média: {statistics.mean(taxas):.1%}")
        print(f"mediana:           {statistics.median(taxas):.1%}")
        print(f"pior caso:         {max(taxas):.1%}")
        print(f"\nconcordância média entre as duas transcrições: "
              f"{1 - statistics.mean(taxas):.1%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
