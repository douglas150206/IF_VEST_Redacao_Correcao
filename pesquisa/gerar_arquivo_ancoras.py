"""Gera o arquivo de âncoras que a produção consome.

Produz o JSON lido por `corretor.ancoragem`, a partir das mesmas cinco
redações que o experimento 5 usou e mediu (QWK 0,514 -> 0,703).

As notas finais do catálogo são a média de dois avaliadores, então aparecem
valores como 100 e 60, fora da escala estrita do ENEM. Elas vão para a âncora
**como estão**.

Arredondar foi tentado e descartado: os empates caem sempre para o mesmo lado
e rebaixam todas as âncoras — no teste, as cinco perderam de 40 a 100 pontos
cada, o que ensinaria o modelo a corrigir abaixo das avaliadoras. Além disso,
a medição que validou a ancoragem (QWK 0,703) usou as médias sem arredondar,
então arredondar aqui significaria publicar algo diferente do que foi medido.

O arquivo de saída fica em `corpus/simulado/`, que está fora do git, porque
contém redações de alunos com nota atribuída.

Uso:
    python gerar_arquivo_ancoras.py
    python gerar_arquivo_ancoras.py --saida /outro/caminho.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent / "porte_fastapi"))

from experimento_ancora_validado import NOTAS_ANCORA, escolher_ancoras  # noqa: E402
from experimento_simulado import TEMA, carregar_notas, carregar_transcricoes  # noqa: E402

PADRAO = AQUI / "corpus" / "simulado" / "ancoras.json"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--saida", type=Path, default=PADRAO)
    args = ap.parse_args()

    transcricoes = carregar_transcricoes()
    notas = carregar_notas()
    casadas = sorted(set(transcricoes) & set(notas))
    selecionadas = escolher_ancoras(notas, casadas)

    if len(selecionadas) < len(NOTAS_ANCORA):
        print(f"não achei redação para todas as notas-âncora {NOTAS_ANCORA}")
        return 1

    ancoras = []
    print(f"{'competências':>28}{'total':>8}{'palavras':>10}")
    print("-" * 46)
    for p in selecionadas:
        n = notas[p]
        comps = [int(c) for c in n["final"]]
        total = sum(comps)
        if total != n["total"]:
            print(f"aviso: soma {total} difere do total {n['total']} do catálogo")
        ancoras.append({"texto": transcricoes[p], "competencias": comps,
                        "total": total})
        print(f"{str(comps):>28}{total:>8}{len(transcricoes[p].split()):>10}")

    baixas = sum(1 for a in ancoras if a["total"] < 500)
    print(f"\n{len(ancoras)} âncoras, {baixas} delas abaixo de 500")

    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(
        json.dumps({"tema": TEMA, "ancoras": ancoras}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"escrito em {args.saida}")
    print("\nPara ligar na produção:")
    print(f'  CORRETOR_ANCORAS="{args.saida}"')
    print("\nO arquivo contém redações de alunos. Fora do git, e o uso em")
    print("produção depende de autorização de quem coordena o projeto.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
