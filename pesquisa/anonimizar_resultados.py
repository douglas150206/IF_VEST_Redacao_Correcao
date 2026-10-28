"""Troca prontuários por pseudônimos nos resultados do simulado.

O repositório é público. As redações do simulado são de alunos reais do campus
e vêm identificadas por prontuário, que é dado pessoal. Os números da pesquisa
não dependem de saber quem escreveu o quê — dependem de poder distinguir uma
redação da outra e reencontrar a mesma ao longo das rodadas.

Por isso cada prontuário vira um pseudônimo estável (S01, S02, ...), atribuído
por ordem alfabética para que a mesma redação receba sempre o mesmo rótulo em
qualquer arquivo e em qualquer execução.

A tabela de correspondência fica em `corpus/simulado/`, que é ignorado pelo
git. Quem tem o corpus consegue voltar ao prontuário; quem clona o repositório
público vê apenas S01 a S08.

Uso:
    python anonimizar_resultados.py --conferir   # mostra o que mudaria
    python anonimizar_resultados.py
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RESULTADOS = AQUI / "resultados"
MAPA = AQUI / "corpus" / "simulado" / "pseudonimos.json"

PRONTUARIO = re.compile(r"\b([A-Z]{2}\s?\d{6,})\b")


def coletar(arquivos: list[Path]) -> set[str]:
    achados: set[str] = set()
    for a in arquivos:
        achados |= {m.group(1).replace(" ", "")
                    for m in PRONTUARIO.finditer(a.read_text(encoding="utf-8"))}
    return achados


def carregar_mapa() -> dict[str, str]:
    if MAPA.is_file():
        return json.loads(MAPA.read_text(encoding="utf-8"))
    return {}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--conferir", action="store_true",
                    help="mostra o que mudaria, sem escrever")
    args = ap.parse_args()

    arquivos = sorted(RESULTADOS.glob("simulado_*.json"))
    if not arquivos:
        print("nenhum resultado do simulado encontrado")
        return 0

    mapa = carregar_mapa()
    encontrados = coletar(arquivos)
    novos = sorted(p for p in encontrados if p not in mapa)
    for i, p in enumerate(novos, start=len(mapa) + 1):
        mapa[p] = f"S{i:02d}"

    print(f"arquivos: {len(arquivos)}   prontuários distintos: {len(encontrados)}")
    for p in sorted(encontrados):
        print(f"  {p} → {mapa[p]}")

    if args.conferir:
        print("\n(--conferir: nada foi escrito)")
        return 0

    for a in arquivos:
        texto = a.read_text(encoding="utf-8")
        for pront, pseudo in mapa.items():
            # Cobre a forma com e sem espaço ("XX 1234567" e "XX1234567").
            espacado = f"{pront[:2]} {pront[2:]}"
            texto = texto.replace(pront, pseudo).replace(espacado, pseudo)
        a.write_text(texto, encoding="utf-8")
        print(f"anonimizado: {a.name}")

    MAPA.parent.mkdir(parents=True, exist_ok=True)
    MAPA.write_text(json.dumps(mapa, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\ntabela de correspondência: {MAPA.relative_to(AQUI.parent)}")
    print("(fica fora do git — é o único lugar que liga pseudônimo a prontuário)")

    restantes = coletar(arquivos)
    if restantes:
        print(f"\nAVISO: ainda há {len(restantes)} prontuário(s) nos arquivos: {restantes}")
        return 1
    print("\nconferido: nenhum prontuário restou nos resultados")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
