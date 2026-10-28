"""Gera um prompt ancorado em redações reais já corrigidas por humanos.

Por que ancoragem e não mais critério
-------------------------------------
Duas tentativas de calibrar por descrição falharam, e a medição explica por
quê: o problema não é a régua estar deslocada (viés é +16, quase zero), é o
sistema concordar pouco com o humano (QWK 0,50 contra 0,60–0,73 do estado da
arte). Curva de correção não resolve, porque transformação monótona reescala
mas não reordena.

O que resta é melhorar o julgamento. E a técnica conhecida para calibrar
avaliador é mostrar casos, não adjetivos. "Estrutura sintática boa e poucos
desvios" vale 160 — mas poucos é quanto? Um corretor humano treinado responde
isso porque corrigiu milhares de redações; o modelo só tem a frase. Exemplo
real com nota oficial dá a referência que a descrição não dá.

Cuidado com contaminação
------------------------
As âncoras saem do split de **desenvolvimento**. As 25 redações de avaliação
saem do split de **teste**. Se as duas coisas se misturassem, o resultado
mediria memorização, não calibração.

Uso:
    python gerar_ancoras.py            # gera e mostra o resumo
    python gerar_ancoras.py --ver      # mostra o prompt inteiro
"""

from __future__ import annotations

import argparse
import ast
import csv
import random
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CORPUS = AQUI / "corpus" / "essay-br"
DESTINO = AQUI.parent / "porte_fastapi" / "corretor" / "ancoras.py"
SEMENTE = 20261026

# Notas-alvo das âncoras, escolhidas para cobrir a escala de ponta a ponta.
# A faixa baixa recebe duas âncoras porque é onde o erro medido é maior.
ALVOS = [160, 320, 480, 640, 840]

# Redações perto da mediana de tamanho são mais representativas e gastam menos
# contexto que as muito longas.
TAMANHO_IDEAL = 280

NOMES = {
    1: "domínio da norma culta",
    2: "compreensão da proposta",
    3: "seleção e organização de argumentos",
    4: "mecanismos de coesão",
    5: "proposta de intervenção",
}


def _lista(campo: str) -> list:
    try:
        v = ast.literal_eval(campo)
        return v if isinstance(v, list) else [campo]
    except (ValueError, SyntaxError):
        return [campo]


def escolher() -> list[dict]:
    with (CORPUS / "development.csv").open(encoding="utf-8") as f:
        pool = list(csv.DictReader(f))

    rng = random.Random(SEMENTE)
    rng.shuffle(pool)

    escolhidas, usadas = [], set()
    for alvo in ALVOS:
        candidatas = [
            r for r in pool
            if r["title"] not in usadas and abs(int(r["score"]) - alvo) <= 40
        ]
        if not candidatas:
            continue
        # Entre as de nota próxima do alvo, a de tamanho mais perto da mediana.
        melhor = min(
            candidatas,
            key=lambda r: abs(len(" ".join(_lista(r["essay"])).split()) - TAMANHO_IDEAL),
        )
        usadas.add(melhor["title"])
        escolhidas.append(melhor)
    return sorted(escolhidas, key=lambda r: int(r["score"]))


def montar(ancoras: list[dict]) -> str:
    blocos = []
    for i, r in enumerate(ancoras, start=1):
        texto = " ".join(_lista(r["essay"])).strip()
        comp = [int(x) for x in _lista(r["competence"])]
        notas = "\n".join(
            f"  Competência {n} ({NOMES[n]}): {c}" for n, c in enumerate(comp, start=1)
        )
        blocos.append(
            f"### Exemplo {i} — nota total {r['score']}\n\n"
            f"Tema: {r['title']}\n\n"
            f"Redação:\n{texto}\n\n"
            f"Notas atribuídas por avaliador humano:\n{notas}\n"
            f"  Total: {r['score']}"
        )

    exemplos = "\n\n---\n\n".join(blocos)

    return f'''"""Prompt ancorado em redações reais corrigidas por humanos.

GERADO POR `pesquisa/gerar_ancoras.py` — não editar à mão.

As {len(ancoras)} redações de referência vêm do split de desenvolvimento do
Essay-BR (MARINHO; ANCHIETA; MOURA, 2021), licença MIT. As notas são as
atribuídas pelos avaliadores daquele corpus.

As redações de avaliação saem do split de teste, que é disjunto deste — sem
contaminação entre as âncoras e o que se mede.
"""

from .corretor import PROMPT_SISTEMA as _BASE

_ANCORAS = """

## REDAÇÕES DE REFERÊNCIA

Abaixo estão redações reais já corrigidas por avaliadores humanos, cobrindo a
escala de ponta a ponta. Use-as como régua: antes de fechar cada competência,
compare a redação que você está avaliando com estes exemplos e pergunte de qual
delas ela está mais perto naquela competência específica.

A descrição de um nível é ambígua por natureza — "poucos desvios" não diz
quantos. Os exemplos resolvem essa ambiguidade. Quando a sua avaliação
discordar do que os exemplos sugerem, confie neles.

{exemplos}

## FIM DAS REDAÇÕES DE REFERÊNCIA

Volte agora à redação que lhe foi enviada para corrigir. Os exemplos acima são
régua de calibração, não o texto a avaliar.
"""

PROMPT_ANCORADO = _BASE + _ANCORAS
'''


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ver", action="store_true", help="imprime o prompt inteiro")
    args = ap.parse_args()

    ancoras = escolher()
    if not ancoras:
        print("não encontrei âncoras — confira o corpus")
        return 1

    print(f"{len(ancoras)} âncoras escolhidas do split de desenvolvimento:\n")
    print(f"  {'nota':>5}  {'palavras':>8}  competências          tema")
    for r in ancoras:
        comp = [int(x) for x in _lista(r["competence"])]
        palavras = len(" ".join(_lista(r["essay"])).split())
        print(f"  {r['score']:>5}  {palavras:>8}  {str(comp):<21} {r['title'][:34]}")

    codigo = montar(ancoras)
    DESTINO.write_text(codigo, encoding="utf-8")

    palavras_prompt = len(codigo.split())
    print(f"\nescrito em {DESTINO.relative_to(AQUI.parent)}")
    print(f"acréscimo ao prompt: ~{palavras_prompt} palavras "
          f"(~{int(palavras_prompt * 1.6)} tokens)")
    print("\nO bloco de âncoras é fixo entre requisições — vale ativar cache de")
    print("prompt no system, senão ele é cobrado inteiro em toda correção.")

    if args.ver:
        print("\n" + "=" * 72)
        print(codigo)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
