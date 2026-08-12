"""Rotas do corretor de redação, prontas para serem montadas no app do IFvest.

    from corretor import router as corretor_router
    app.include_router(corretor_router)

Não há rotas de cadastro, login ou promoção a professor: identidade e papel vêm
do sistema geral, via `corretor.auth`.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from . import banco
from .auth import UsuarioAtual, usuario_atual, usuario_professor
from .config import config
from .corretor import ErroDeCorrecao, corrigir_redacao
from .esquemas import (
    ChaveIn,
    CorrecaoOut,
    CorrigirIn,
    HistoricoItem,
    Mensagem,
    PlagioOut,
    StatusOut,
    TemaIn,
    TemaOut,
)
from .plagio import ResultadoPlagio, detectar_copia

router = APIRouter(prefix="/api/redacao", tags=["Correção de redação"])


def _plagio_para_schema(p: ResultadoPlagio) -> PlagioOut:
    return PlagioOut(
        percentual_copiado=p.percentual_copiado,
        palavras_copiadas=p.palavras_copiadas,
        total_palavras=p.total_palavras,
        trechos_copiados=[
            {"texto": t.texto, "palavras": t.palavras} for t in p.trechos_copiados
        ],
    )


# ── Status de uso ────────────────────────────────────────────────────────────

@router.get("/status", response_model=StatusOut)
def status_do_usuario(usuario: UsuarioAtual = Depends(usuario_atual)) -> StatusOut:
    tem_chave = banco.buscar_chave(usuario.id) is not None
    usadas = banco.contar_correcoes_do_mes(usuario.id)
    ilimitado = tem_chave or config.limite_mensal <= 0
    return StatusOut(
        usuario_id=usuario.id,
        nome=usuario.nome,
        professor=usuario.professor,
        tem_chave_propria=tem_chave,
        redacoes_usadas=usadas,
        redacoes_limite=None if ilimitado else config.limite_mensal,
        redacoes_restantes=None if ilimitado else max(0, config.limite_mensal - usadas),
    )


# ── Chave de API própria do aluno ────────────────────────────────────────────

@router.post("/chave", response_model=Mensagem)
def salvar_chave(
    dados: ChaveIn, usuario: UsuarioAtual = Depends(usuario_atual)
) -> Mensagem:
    chave = dados.api_key.strip()
    if not chave.startswith("sk-ant-"):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Chave inválida. Deve começar com sk-ant-."
        )
    banco.salvar_chave(usuario.id, chave)
    return Mensagem(mensagem="Chave de API salva. Seu uso passa a ser ilimitado.")


@router.delete("/chave", response_model=Mensagem)
def remover_chave(usuario: UsuarioAtual = Depends(usuario_atual)) -> Mensagem:
    banco.remover_chave(usuario.id)
    limite = config.limite_mensal
    return Mensagem(
        mensagem=f"Chave removida. Limite de {limite} correções por mês restaurado."
    )


# ── Temas e textos de apoio ──────────────────────────────────────────────────

@router.get("/temas", response_model=list[TemaOut])
def listar_temas(_: UsuarioAtual = Depends(usuario_atual)) -> list[TemaOut]:
    return [TemaOut(**dict(linha)) for linha in banco.listar_temas()]


@router.post("/temas", response_model=TemaOut, status_code=status.HTTP_201_CREATED)
def criar_tema(
    dados: TemaIn, _: UsuarioAtual = Depends(usuario_professor)
) -> TemaOut:
    titulo, apoio = _validar_tema(dados)
    tema_id = banco.criar_tema(titulo, apoio)
    return TemaOut(id=tema_id, titulo=titulo, textos_apoio=apoio)


@router.put("/temas/{tema_id}", response_model=TemaOut)
def atualizar_tema(
    tema_id: int, dados: TemaIn, _: UsuarioAtual = Depends(usuario_professor)
) -> TemaOut:
    titulo, apoio = _validar_tema(dados)
    if not banco.atualizar_tema(tema_id, titulo, apoio):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tema não encontrado.")
    return TemaOut(id=tema_id, titulo=titulo, textos_apoio=apoio)


@router.delete("/temas/{tema_id}", response_model=Mensagem)
def remover_tema(
    tema_id: int, _: UsuarioAtual = Depends(usuario_professor)
) -> Mensagem:
    if not banco.remover_tema(tema_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tema não encontrado.")
    return Mensagem(mensagem="Tema removido.")


def _validar_tema(dados: TemaIn) -> tuple[str, str]:
    titulo = dados.titulo.strip()
    apoio = dados.textos_apoio.strip()
    if not titulo:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "O título do tema é obrigatório."
        )
    if len(apoio) < 50:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Inclua os textos de apoio (mínimo de 50 caracteres).",
        )
    return titulo, apoio


# ── Correção ─────────────────────────────────────────────────────────────────

@router.post("/corrigir", response_model=CorrecaoOut)
def corrigir(
    dados: CorrigirIn, usuario: UsuarioAtual = Depends(usuario_atual)
) -> CorrecaoOut:
    redacao = dados.redacao.strip()
    if len(redacao) < config.min_caracteres_redacao:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Redação muito curta. Mínimo de {config.min_caracteres_redacao} caracteres.",
        )

    # Tema pode vir do banco (tema_id) ou personalizado pelo aluno.
    titulo_tema = dados.tema.strip() if dados.tema else None
    textos_apoio = dados.textos_apoio.strip() if dados.textos_apoio else None
    tema_id: int | None = None
    if dados.tema_id is not None:
        tema = banco.buscar_tema(dados.tema_id)
        if tema is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Tema não encontrado.")
        tema_id = tema["id"]
        titulo_tema = tema["titulo"]
        textos_apoio = tema["textos_apoio"]

    plagio = detectar_copia(redacao, textos_apoio)

    # Quem tem chave própria não tem limite; os demais usam a chave institucional
    # dentro da cota mensal.
    chave_propria = banco.buscar_chave(usuario.id)
    if chave_propria is None and config.limite_mensal > 0:
        usadas = banco.contar_correcoes_do_mes(usuario.id)
        if usadas >= config.limite_mensal:
            raise HTTPException(
                status.HTTP_429_TOO_MANY_REQUESTS,
                f"Limite de {config.limite_mensal} correções por mês atingido. "
                "Cadastre sua própria chave de API para continuar neste mês.",
            )

    api_key = chave_propria or config.chave_institucional
    if not api_key:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Nenhuma chave de API configurada no servidor. "
            "Defina ANTHROPIC_API_KEY ou cadastre uma chave própria.",
        )

    try:
        correcao = corrigir_redacao(redacao, titulo_tema, textos_apoio, plagio, api_key)
    except ErroDeCorrecao as erro:
        raise HTTPException(erro.status, erro.mensagem) from erro

    resultado = CorrecaoOut(**correcao.model_dump(), plagio=_plagio_para_schema(plagio))
    banco.registrar_correcao(
        usuario_id=usuario.id,
        tema=titulo_tema,
        tema_id=tema_id,
        redacao=redacao,
        resultado=resultado.model_dump(),
        plagio_percentual=plagio.percentual_copiado,
    )
    return resultado


# ── Histórico ────────────────────────────────────────────────────────────────

@router.get("/historico", response_model=list[HistoricoItem])
def historico(usuario: UsuarioAtual = Depends(usuario_atual)) -> list[HistoricoItem]:
    return [HistoricoItem(**dict(linha)) for linha in banco.listar_historico(usuario.id)]
