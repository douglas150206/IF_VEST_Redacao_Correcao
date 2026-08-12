"""Exemplo mínimo de como montar o corretor num app FastAPI.

Rode com:  uvicorn exemplo_app:app --reload
Docs em:   http://localhost:8000/docs

O provedor de usuário abaixo é FALSO — serve só para ver as rotas funcionando.
No IFvest, troque-o pelo `get_current_user` de vocês (ver corretor/auth.py).
"""

from fastapi import FastAPI, Request

from corretor import UsuarioAtual, criar_tabelas, router, usar_provedor_de_usuario

app = FastAPI(title="IFvest — exemplo com o corretor de redação")


async def provedor_falso(request: Request) -> UsuarioAtual:
    """Substitua por: return await get_current_user(request)."""
    ehprofessor = request.headers.get("X-Papel") == "professor"
    return UsuarioAtual(
        id=2 if ehprofessor else 1,
        nome="Professora Demo" if ehprofessor else "Aluno Demo",
        email="demo@ifsp.edu.br",
        professor=ehprofessor,
    )


@app.on_event("startup")
def iniciar() -> None:
    criar_tabelas()
    usar_provedor_de_usuario(provedor_falso)


app.include_router(router)
