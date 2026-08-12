"""Configuração do módulo de correção.

Tudo vem de variável de ambiente, com padrão sensato. Nenhum segredo no código.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _carregar_env() -> None:
    """Lê um arquivo .env da pasta do módulo ou de alguma pasta acima.

    Reaproveita o mesmo .env que o sistema em Node já usa, então a chave
    institucional não precisa ser duplicada em lugar nenhum. Variáveis já
    definidas no ambiente têm prioridade sobre o arquivo.
    """
    for pasta in [Path(__file__).resolve().parent, *Path(__file__).resolve().parents]:
        env = pasta / ".env"
        if not env.is_file():
            continue
        for linha in env.read_text(encoding="utf-8").splitlines():
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            chave, valor = linha.split("=", 1)
            os.environ.setdefault(chave.strip(), valor.strip().strip("\"'"))
        return


_carregar_env()


# Padrão ancorado na pasta do módulo, não no diretório de onde o processo subiu.
# Com um caminho relativo, `uvicorn` iniciado de outra pasta criava um banco
# vazio em lugar diferente — e o sistema parecia ter perdido os dados.
_BANCO_PADRAO = Path(__file__).resolve().parent.parent / "corretor.db"


@dataclass(frozen=True)
class Config:
    # Banco SQLite. Aponte CORRETOR_BANCO para o mesmo arquivo do IFvest se
    # quiser tudo junto; as tabelas do corretor têm prefixo próprio e não colidem.
    banco: Path = Path(os.getenv("CORRETOR_BANCO", _BANCO_PADRAO))

    # Chave institucional usada quando o aluno não tem chave própria.
    chave_institucional: str | None = os.getenv("ANTHROPIC_API_KEY")

    # Quantas correções gratuitas por mês antes de exigir chave própria.
    # Deixe 0 para desligar o limite (ex.: se a instituição bancar tudo).
    limite_mensal: int = int(os.getenv("CORRETOR_LIMITE_MENSAL", "10"))

    # Modelo e orçamento de tokens da chamada de correção.
    modelo: str = os.getenv("CORRETOR_MODELO", "claude-opus-5")
    max_tokens: int = int(os.getenv("CORRETOR_MAX_TOKENS", "8000"))
    # low | medium | high | xhigh | max — controla profundidade e custo.
    esforco: str = os.getenv("CORRETOR_ESFORCO", "medium")

    # Tamanho mínimo da redação aceita, em caracteres.
    min_caracteres_redacao: int = 100


config = Config()
