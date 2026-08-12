"""Ponto único de integração com o login do IFvest.

O corretor não tem cadastro, login nem tabela de usuários próprios: ele recebe
o usuário já autenticado pelo sistema geral. Para plugar, chame
`usar_provedor_de_usuario()` uma vez no startup da aplicação, passando uma
função que traduz a requisição no usuário logado de vocês.

Exemplo, se o IFvest já tem um `get_current_user`:

    from corretor.auth import UsuarioAtual, usar_provedor_de_usuario

    async def provedor(request):
        u = await get_current_user(request)          # o de vocês
        return UsuarioAtual(
            id=u.id,
            nome=u.nome,
            email=u.email,
            professor=u.papel == "professor",
        )

    usar_provedor_de_usuario(provedor)

Se preferir manter o `Depends` de vocês, dá para ignorar este módulo e
sobrescrever a dependência direto no FastAPI:

    app.dependency_overrides[usuario_atual] = a_dependencia_de_voces
"""

from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Union

from fastapi import Depends, HTTPException, Request, status


@dataclass(frozen=True)
class UsuarioAtual:
    """O mínimo que o corretor precisa saber sobre quem está usando."""

    id: int
    nome: str = ""
    email: str = ""
    professor: bool = False


ProvedorDeUsuario = Callable[[Request], Union[UsuarioAtual, Awaitable[UsuarioAtual]]]

_provedor: ProvedorDeUsuario | None = None


def usar_provedor_de_usuario(fn: ProvedorDeUsuario) -> None:
    """Registra a função que resolve o usuário logado. Chame no startup."""
    global _provedor
    _provedor = fn


async def usuario_atual(request: Request) -> UsuarioAtual:
    if _provedor is None:
        raise RuntimeError(
            "Nenhum provedor de usuário configurado. Chame "
            "corretor.auth.usar_provedor_de_usuario(fn) no startup da aplicação "
            "— veja o exemplo no topo de corretor/auth.py."
        )
    resultado = _provedor(request)
    if inspect.isawaitable(resultado):
        resultado = await resultado
    if resultado is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Não autenticado.")
    return resultado


async def usuario_professor(
    usuario: UsuarioAtual = Depends(usuario_atual),
) -> UsuarioAtual:
    """Exige perfil de professor — usado nas rotas de gestão de temas."""
    if not usuario.professor:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Ação restrita a professores.")
    return usuario
