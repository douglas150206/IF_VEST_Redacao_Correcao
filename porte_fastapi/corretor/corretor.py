"""Chamada à API da Anthropic para corrigir a redação.

Usa structured outputs: o modelo é obrigado a devolver exatamente o formato de
`CorrecaoIA`, então não existe o passo de limpar crases de markdown nem risco de
JSON malformado — o SDK já entrega um objeto Pydantic validado.
"""

from __future__ import annotations

import anthropic

from .config import config
from .esquemas import CorrecaoIA
from .plagio import ResultadoPlagio

PROMPT_SISTEMA = """Você é um corretor especializado em redações do ENEM. \
Avalie a redação nas 5 competências do ENEM.

As cinco competências, nesta ordem:
1. Domínio da norma culta da língua portuguesa
2. Compreensão da proposta e aplicação de conceitos de diversas áreas
3. Seleção, relação e organização de informações e argumentos
4. Conhecimento dos mecanismos linguísticos de coesão textual
5. Proposta de intervenção respeitando os direitos humanos

Cada competência recebe 0, 40, 80, 120, 160 ou 200 pontos, e nota_total é a soma \
das cinco (máximo 1000).

REGRA SOBRE OS TEXTOS DE APOIO (siga rigorosamente, como no ENEM real):
- Quando forem fornecidos os textos de apoio (motivadores) e/ou uma lista de \
"TRECHOS COPIADOS" detectados, trate cópia literal dos textos de apoio como algo \
que NÃO é produção do participante.
- Desconsidere os trechos copiados ao avaliar a argumentação: eles não somam \
repertório nem contam como desenvolvimento próprio.
- Quanto maior o percentual copiado, maior a penalização, principalmente nas \
Competências II e III.
- Se a redação for essencialmente cópia dos textos de apoio (percentual muito \
alto, sem elaboração própria relevante), atribua 0 a TODAS as cinco competências \
— a nota total é sempre a soma delas — e explique no feedback que se trata de \
cópia.
- Comente a ocorrência de cópia no feedback das competências afetadas e inclua \
uma sugestão de melhoria orientando o aluno a reescrever os trechos copiados com \
as próprias palavras.

O feedback de cada competência deve ter de 2 a 3 frases e apontar evidências \
concretas do texto do aluno, não observações genéricas."""


class ErroDeCorrecao(Exception):
    """Falha ao obter a correção. `status` vira o HTTP status da rota."""

    def __init__(self, mensagem: str, status: int = 502) -> None:
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.status = status


def montar_prompt(
    redacao: str,
    titulo_tema: str | None,
    textos_apoio: str | None,
    plagio: ResultadoPlagio,
) -> str:
    partes: list[str] = []
    if titulo_tema:
        partes.append(f"Tema: {titulo_tema}")
    if textos_apoio:
        partes.append(f"Textos de apoio:\n{textos_apoio}")
    if plagio.trechos_copiados:
        lista = "\n".join(
            f'{i}. "{t.texto}"'
            for i, t in enumerate(plagio.trechos_copiados[:10], start=1)
        )
        partes.append(
            "TRECHOS COPIADOS dos textos de apoio (detecção automática — "
            f"{plagio.percentual_copiado}% da redação é cópia literal). "
            "Desconsidere-os como produção do participante e penalize conforme "
            f"a regra do ENEM:\n{lista}"
        )
    partes.append(f"Redação:\n{redacao.strip()}")
    return "\n\n".join(partes)


def corrigir_redacao(
    redacao: str,
    titulo_tema: str | None,
    textos_apoio: str | None,
    plagio: ResultadoPlagio,
    api_key: str,
) -> CorrecaoIA:
    """Envia a redação ao modelo e devolve a correção já validada."""
    cliente = anthropic.Anthropic(api_key=api_key)

    try:
        resposta = cliente.messages.parse(
            model=config.modelo,
            max_tokens=config.max_tokens,
            system=PROMPT_SISTEMA,
            messages=[
                {
                    "role": "user",
                    "content": montar_prompt(redacao, titulo_tema, textos_apoio, plagio),
                }
            ],
            output_format=CorrecaoIA,
            # O SDK mescla o formato aqui dentro, preservando o esforço.
            output_config={"effort": config.esforco},
        )
    except anthropic.AuthenticationError as erro:
        raise ErroDeCorrecao(
            "Chave de API inválida ou sem permissão. Verifique a chave cadastrada.",
            status=502,
        ) from erro
    except anthropic.RateLimitError as erro:
        raise ErroDeCorrecao(
            "A API está com muitas requisições no momento. Tente novamente em instantes.",
            status=503,
        ) from erro
    except anthropic.APIStatusError as erro:
        # Cobre 400 (ex.: saldo insuficiente), 404 e 5xx do provedor.
        raise ErroDeCorrecao(
            f"A API recusou a requisição (HTTP {erro.status_code}).", status=502
        ) from erro
    except anthropic.APIConnectionError as erro:
        raise ErroDeCorrecao(
            "Não foi possível falar com a API. Verifique a conexão do servidor.",
            status=503,
        ) from erro

    # Com structured outputs a resposta vem no formato pedido; `refusal` é o
    # único caso em que o conteúdo pode não seguir o schema.
    if resposta.stop_reason == "refusal":
        raise ErroDeCorrecao(
            "O modelo recusou avaliar este conteúdo. Revise o texto enviado.",
            status=422,
        )
    if resposta.stop_reason == "max_tokens":
        raise ErroDeCorrecao(
            "A correção excedeu o limite de tokens da requisição. "
            "Aumente CORRETOR_MAX_TOKENS.",
            status=502,
        )

    correcao = resposta.parsed_output
    if correcao is None:
        raise ErroDeCorrecao("A resposta do modelo veio fora do formato esperado.")
    return correcao
