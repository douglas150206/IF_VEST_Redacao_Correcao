"""Módulo de correção de redação do ENEM, para plugar no sistema IFvest.

Uso mínimo:

    from fastapi import FastAPI
    from corretor import router, criar_tabelas, usar_provedor_de_usuario

    app = FastAPI()
    criar_tabelas()
    usar_provedor_de_usuario(meu_provedor)   # ver corretor/auth.py
    app.include_router(router)
"""

from .auth import UsuarioAtual, usar_provedor_de_usuario, usuario_atual, usuario_professor
from .banco import criar_tabelas
from .config import config
from .plagio import detectar_copia
from .rotas import router

__all__ = [
    "UsuarioAtual",
    "config",
    "criar_tabelas",
    "detectar_copia",
    "router",
    "usar_provedor_de_usuario",
    "usuario_atual",
    "usuario_professor",
]
