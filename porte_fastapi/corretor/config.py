"""Configuração do módulo de correção.

Tudo vem de variável de ambiente, com padrão sensato. Nenhum segredo no código.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    # Banco SQLite. Aponte para o mesmo arquivo do IFvest se quiser tudo junto;
    # as tabelas do corretor têm prefixo próprio e não colidem.
    banco: Path = Path(os.getenv("CORRETOR_BANCO", "corretor.db"))

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
