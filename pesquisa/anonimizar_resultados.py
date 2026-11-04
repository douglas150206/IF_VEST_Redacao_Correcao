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

# Todo resultado que venha do corpus do simulado passa por aqui. Acrescente o
# padrão ao criar um experimento novo sobre esse corpus — um arquivo que escape
# desta lista vai para o repositório público com prontuário dentro.
PADROES = ("simulado_*.json", "por_competencia_*.json")


def coletar(arquivos: list[Path]) -> set[str]:
    achados: set[str] = set()
    for a in arquivos:
        achados |= {m.group(1).replace(" ", "")
                    for m in PRONTUARIO.finditer(a.read_text(encoding="utf-8"))}
    return achados


# Campos em que o modelo cita o texto do aluno para justificar a nota. São
# úteis para entender *por que* o sistema pontuou assim, mas contêm redação de
# estudante transcrita literalmente — não podem ir para o repositório público.
CAMPOS_COM_TEXTO_DE_ALUNO = ("exame", "justificativa", "feedback")

AVISO_REDIGIDO = ("[redigido: contém trecho da redação do aluno; a versão "
                  "completa está apenas na cópia local, fora do git]")


def redigir(no):
    """Percorre o JSON removendo os campos que citam o texto do aluno.

    O campo redigido pode ser uma string ou um dicionário por competência
    (`exame: {C1: ..., C5: ...}`), então o corte é pela chave, qualquer que
    seja o tipo do valor — uma versão anterior testava `isinstance(v, str)` e
    deixava passar justamente a forma aninhada, que é a que o experimento por
    competência produz.
    """
    if isinstance(no, dict):
        return {
            k: (AVISO_REDIGIDO if k in CAMPOS_COM_TEXTO_DE_ALUNO else redigir(v))
            for k, v in no.items()
        }
    if isinstance(no, list):
        return [redigir(x) for x in no]
    return no


def redigir_texto_de_aluno(arquivos: list[Path]) -> None:
    """Guarda a versão íntegra fora do git e deixa a redigida no lugar.

    O arquivo íntegro vai para `corpus/simulado/`, que é ignorado pelo git
    junto com o resto do corpus. O que fica em `resultados/` tem as notas, que
    é o que o registro da pesquisa precisa, sem a redação do aluno.
    """
    destino = MAPA.parent / "integros"
    for a in arquivos:
        dados = json.loads(a.read_text(encoding="utf-8"))
        limpo = redigir(dados)
        if limpo == dados:
            continue
        destino.mkdir(parents=True, exist_ok=True)
        (destino / a.name).write_text(
            json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        a.write_text(json.dumps(limpo, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"texto de aluno redigido em {a.name}; "
              f"íntegro em {(destino / a.name).relative_to(MAPA.parent.parent)}")


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

    arquivos = sorted({a for p in PADROES for a in RESULTADOS.glob(p)})
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

    redigir_texto_de_aluno(arquivos)

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
