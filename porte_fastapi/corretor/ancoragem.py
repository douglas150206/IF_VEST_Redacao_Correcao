"""Ancoragem da correção em redações já corrigidas por avaliador humano.

O problema que isto resolve
---------------------------
Medido contra as corretoras do simulado: o sistema acerta redação boa e erra
de 180 a 260 pontos nas fracas, sempre para cima. Ele nunca desceu de 560,
enquanto as corretoras atribuem 40 e 60 por competência.

A causa não é falta de critério — é falta de régua. O modelo sabe o que é
"poucos desvios", mas não quanto isso vale. Quatro tentativas de melhorar o
critério no prompt pioraram o resultado: critério mais detalhado dá ao modelo
mais motivos para pontuar.

O que funcionou foi mostrar exemplos. Redações reais, com a nota que as
corretoras deram, incluindo as de nota baixa:

    concordância com as corretoras (QWK)   0,514 -> 0,703
    erro nas redações fracas                 -39%
    menor nota atribuída                   560 -> 400

Para referência: duas corretoras humanas concordam entre si em 0,867, e o
melhor resultado publicado para português fica entre 0,60 e 0,73.

Como ligar
----------
Aponte CORRETOR_ANCORAS para um arquivo JSON com as redações de referência.
Sem a variável, o comportamento é o de hoje, sem ancoragem — de modo que
ligar e desligar é mudança de ambiente, não de código.

Formato do arquivo:

    {
      "tema": "Os desafios para o enfrentamento da ...",
      "ancoras": [
        {
          "texto": "...",
          "competencias": [100, 40, 60, 140, 40],
          "total": 380
        }
      ]
    }

O que escolher como âncora
--------------------------
Quatro pontos aprendidos ao medir:

1. **Cubra a parte de baixo.** O sistema falha embaixo, e é lá que a
   referência faz diferença. Metade das âncoras deve ter nota abaixo de 500.
2. **Use notas das mesmas corretoras** que avaliam os alunos. Âncoras de outro
   corpus, com outros avaliadores, foram testadas e não funcionaram: o ganho
   vem de aprender *aquela* régua, não uma régua qualquer.
3. **Cubra a escala.** Só exemplos fracos fazem o sistema achar que tudo é
   ruim; é preciso o contraponto.
4. **Texto confiável.** Âncora com erro de transcrição ensina a régua errada.

Sobre o uso de redações de aluno
--------------------------------
As âncoras entram no prompt de um sistema que outros alunos usam. Se forem
redações de estudantes reais, isso exige autorização de quem coordena o
projeto — é decisão pedagógica e de uso de dados, não de engenharia. O arquivo
fica fora do repositório por isso.

Uma alternativa que dispensa a autorização: redações escritas para servir de
referência, corrigidas pelas mesmas corretoras. O que torna a âncora eficaz é
carregar a nota delas, não ser de aluno real. Isso não foi medido.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

NOMES_COMPETENCIAS = {
    1: "domínio da norma culta",
    2: "compreensão da proposta",
    3: "seleção e organização de argumentos",
    4: "mecanismos de coesão",
    5: "proposta de intervenção",
}

_ABERTURA = """

## REDAÇÕES DE REFERÊNCIA

As redações abaixo foram corrigidas pelas mesmas avaliadoras que avaliam estes
estudantes. Use-as como régua.

Repare especialmente nas notas baixas. A escala vai de 0 a 200 por competência
e **a parte de baixo é usada de verdade**: notas 40 e 80 aparecem em redações
com problemas reais de argumentação ou de proposta. Não existe piso implícito
em 120. Uma redação fraca recebe nota de redação fraca.

Antes de fechar cada competência, compare a redação enviada com estas
referências e pergunte de qual delas ela está mais perto naquela competência.
Quando a sua impressão discordar do que as referências indicam, confie nelas.
"""

_FECHAMENTO = """

## FIM DAS REFERÊNCIAS

Volte agora à redação enviada para correção. As acima são régua, não o texto a
avaliar.
"""


class ErroDeAncoragem(Exception):
    """Arquivo de âncoras ausente ou malformado."""


@dataclass(frozen=True)
class Ancora:
    texto: str
    competencias: list[int]
    total: int

    def render(self, numero: int) -> str:
        notas = "\n".join(
            f"  Competência {n} ({NOMES_COMPETENCIAS[n]}): {v}"
            for n, v in enumerate(self.competencias, start=1)
        )
        return (f"### Referência {numero} — nota final {self.total}\n\n"
                f"{self.texto.strip()}\n\n"
                f"Notas atribuídas pelas avaliadoras:\n{notas}\n"
                f"  Total: {self.total}")


def carregar(caminho: Path) -> list[Ancora]:
    """Lê e valida o arquivo de âncoras.

    Valida de propósito: uma âncora com nota fora da escala ou com número
    errado de competências ensinaria ao modelo uma régua inválida, e o efeito
    disso só apareceria na nota dos alunos.
    """
    if not caminho.is_file():
        raise ErroDeAncoragem(f"arquivo de âncoras não encontrado: {caminho}")
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except json.JSONDecodeError as erro:
        raise ErroDeAncoragem(f"JSON inválido em {caminho}: {erro}") from erro

    brutas = dados.get("ancoras")
    if not isinstance(brutas, list) or not brutas:
        raise ErroDeAncoragem("o arquivo não tem a lista 'ancoras'")

    ancoras = []
    for i, a in enumerate(brutas, start=1):
        comps = a.get("competencias")
        if not isinstance(comps, list) or len(comps) != 5:
            raise ErroDeAncoragem(f"âncora {i}: 'competencias' deve ter 5 valores")
        # A escala do ENEM é de 40 em 40, mas a nota de referência costuma ser
        # a média de dois avaliadores, e aí aparecem valores intermediários
        # (120 e 80 viram 100). Aceitar múltiplos de 20 cobre os dois casos.
        #
        # Arredondar para a escala estrita seria pior: os empates caem sempre
        # para o mesmo lado e rebaixam todas as âncoras — num teste, cinco
        # âncoras perderam de 40 a 100 pontos cada, o que ensinaria o modelo a
        # corrigir abaixo das avaliadoras. A medição que validou a ancoragem
        # usou as médias como estão.
        if any(not (0 <= c <= 200 and c % 20 == 0) for c in comps):
            raise ErroDeAncoragem(
                f"âncora {i}: nota inválida em {comps}. Esperado valores de 0 a "
                "200, múltiplos de 20."
            )
        texto = (a.get("texto") or "").strip()
        if len(texto.split()) < 50:
            raise ErroDeAncoragem(f"âncora {i}: texto ausente ou curto demais")
        total = a.get("total", sum(comps))
        if total != sum(comps):
            raise ErroDeAncoragem(
                f"âncora {i}: total {total} não confere com a soma {sum(comps)}"
            )
        ancoras.append(Ancora(texto=texto, competencias=comps, total=total))

    baixas = sum(1 for a in ancoras if a.total < 500)
    if not baixas:
        raise ErroDeAncoragem(
            "nenhuma âncora com nota abaixo de 500. O sistema falha justamente "
            "na faixa baixa; sem exemplo dela a ancoragem não corrige o problema."
        )
    return ancoras


def montar_bloco(ancoras: list[Ancora]) -> str:
    """Monta o trecho que vai para o fim do prompt de sistema."""
    corpo = "\n\n---\n\n".join(
        a.render(i) for i, a in enumerate(sorted(ancoras, key=lambda x: x.total), 1)
    )
    return _ABERTURA + "\n" + corpo + _FECHAMENTO


def aplicar(prompt_sistema: str, caminho: Path | None) -> str:
    """Devolve o prompt com as âncoras, ou inalterado se não houver arquivo.

    Sem `caminho`, devolve o prompt como está: a ancoragem é opcional e o
    sistema funciona sem ela, com o comportamento medido de QWK 0,514.
    """
    if caminho is None:
        return prompt_sistema
    return prompt_sistema + montar_bloco(carregar(caminho))
