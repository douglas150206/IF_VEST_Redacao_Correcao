"""Testes do módulo de correção.

Cobrem duas coisas:

1. Paridade do antiplágio com o `plagio.js` original — os valores esperados
   foram gerados rodando a implementação em Node sobre os mesmos textos.
2. As rotas, com um usuário falso e a chamada à IA substituída, para que a
   suíte rode sem chave de API e sem custo.

    pytest testes/
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

# Precisa vir antes de importar o módulo: a config lê o ambiente no import.
_BANCO = Path(tempfile.gettempdir()) / "corretor_teste.db"
_BANCO.unlink(missing_ok=True)
os.environ["CORRETOR_BANCO"] = str(_BANCO)
os.environ["CORRETOR_LIMITE_MENSAL"] = "3"
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-chave-falsa-para-teste"

import pytest  # noqa: E402
from fastapi import FastAPI, Request  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from corretor import auth, banco, rotas  # noqa: E402
from corretor.esquemas import Competencia, CorrecaoIA  # noqa: E402
from corretor.plagio import detectar_copia  # noqa: E402


# ── Paridade com o plagio.js original ────────────────────────────────────────

APOIO_SAUDE = (
    "A Organização Mundial da Saúde aponta que os transtornos de ansiedade e a "
    "depressão figuram entre as principais causas de afastamento do trabalho no "
    "mundo. O ritmo acelerado da vida contemporânea contribui para o adoecimento "
    "psíquico."
)

CASOS_PARIDADE = [
    # (nome, apoio, redação, percentual, copiadas, total, nº de trechos)
    (
        "sem copia",
        "A Organizacao Mundial da Saude aponta que os transtornos de ansiedade e a "
        "depressao figuram entre as principais causas de afastamento do trabalho no "
        "mundo inteiro.",
        "Vivemos um tempo em que o cuidado com a mente deixou de ser tabu. Escolas, "
        "empresas e familias precisam construir espacos de escuta para que jovens "
        "encontrem apoio antes do adoecimento.",
        0, 0, 31, 0,
    ),
    (
        "copia parcial com acentos e pontuacao",
        APOIO_SAUDE,
        "Segundo dados recentes, a Organização Mundial da Saúde aponta que os "
        "transtornos de ansiedade e a depressão figuram entre as principais causas de "
        "afastamento do trabalho no mundo. Diante disso, cabe ao poder público ampliar "
        "a rede de atendimento psicológico gratuito nas periferias.",
        58, 25, 43, 1,
    ),
    (
        "copia total",
        "Pesquisas recentes indicam que o uso excessivo de redes sociais esta associado "
        "ao aumento da ansiedade e da baixa autoestima, sobretudo entre adolescentes "
        "brasileiros de todas as regioes.",
        "Pesquisas recentes indicam que o uso excessivo de redes sociais esta associado "
        "ao aumento da ansiedade e da baixa autoestima, sobretudo entre adolescentes "
        "brasileiros de todas as regioes.",
        100, 28, 28, 1,
    ),
    (
        "texto curto demais",
        "Texto curto.",
        "Outro texto curto aqui.",
        0, 0, 4, 0,
    ),
    (
        "apoio vazio",
        "",
        "A leitura amplia o repertorio sociocultural do estudante e permite que ele "
        "compreenda melhor o mundo em que vive, formando cidadaos criticos.",
        0, 0, 22, 0,
    ),
    (
        "exatamente sete palavras iguais",
        "o acesso ao livro ainda e um privilegio",
        "Sabemos que o acesso ao livro ainda e um privilegio para muitos brasileiros.",
        62, 8, 13, 1,
    ),
    (
        "seis palavras iguais fica abaixo do limite",
        "o acesso ao livro ainda e um privilegio",
        "Sabemos que o acesso ao livro ainda e importante para muitos brasileiros.",
        0, 0, 12, 0,
    ),
    (
        "espacos multiplos e quebras de linha",
        "Especialistas defendem a educacao midiatica como ferramenta central de "
        "enfrentamento da desinformacao no ambiente digital contemporaneo.",
        "Especialistas   defendem\n\na educacao midiatica\tcomo ferramenta central de "
        "enfrentamento da desinformacao no ambiente digital contemporaneo.",
        100, 16, 16, 1,
    ),
]


@pytest.mark.parametrize(
    "nome,apoio,redacao,percentual,copiadas,total,n_trechos", CASOS_PARIDADE
)
def test_paridade_antiplagio(
    nome, apoio, redacao, percentual, copiadas, total, n_trechos
):
    r = detectar_copia(redacao, apoio)
    assert r.percentual_copiado == percentual, nome
    assert r.palavras_copiadas == copiadas, nome
    assert r.total_palavras == total, nome
    assert len(r.trechos_copiados) == n_trechos, nome


def test_nota_total_e_recalculada_quando_nao_fecha():
    """Visto em produção: competências somando 640 com nota_total 680."""
    correcao = CorrecaoIA(
        nota_total=680,
        competencias=[
            Competencia(numero=1, titulo="C1", nota=160, nivel="alto", feedback="."),
            Competencia(numero=2, titulo="C2", nota=120, nivel="medio", feedback="."),
            Competencia(numero=3, titulo="C3", nota=80, nivel="baixo", feedback="."),
            Competencia(numero=4, titulo="C4", nota=120, nivel="medio", feedback="."),
            Competencia(numero=5, titulo="C5", nota=160, nivel="alto", feedback="."),
        ],
        melhorias=[],
    )
    assert correcao.nota_total == 640


def test_nota_total_zero_por_copia_continua_zero():
    correcao = CorrecaoIA(
        nota_total=0,
        competencias=[
            Competencia(numero=n, titulo=f"C{n}", nota=0, nivel="baixo", feedback=".")
            for n in range(1, 6)
        ],
        melhorias=[],
    )
    assert correcao.nota_total == 0


def test_trechos_vem_do_maior_para_o_menor():
    apoio = (
        "Bibliotecas publicas e escolares enfrentam falta de investimento e de acervo "
        "atualizado. Em muitas cidades o acesso ao livro ainda e um privilegio, o que "
        "aprofunda desigualdades educacionais e culturais no pais."
    )
    redacao = (
        "Bibliotecas publicas e escolares enfrentam falta de investimento e de acervo "
        "atualizado. Isso precisa mudar com urgencia por meio de politicas publicas bem "
        "desenhadas. Em muitas cidades o acesso ao livro ainda e um privilegio, o que "
        "aprofunda desigualdades educacionais e culturais no pais."
    )
    r = detectar_copia(redacao, apoio)
    assert len(r.trechos_copiados) == 2
    tamanhos = [t.palavras for t in r.trechos_copiados]
    assert tamanhos == sorted(tamanhos, reverse=True)


# ── Rotas ────────────────────────────────────────────────────────────────────

ALUNO = auth.UsuarioAtual(id=1, nome="Aluno Teste", email="aluno@ifsp.edu.br")
PROFESSOR = auth.UsuarioAtual(
    id=2, nome="Professora Teste", email="prof@ifsp.edu.br", professor=True
)

CORRECAO_FALSA = CorrecaoIA(
    nota_total=760,
    competencias=[
        Competencia(
            numero=n,
            titulo=f"Competência {n}",
            nota=160 if n != 3 else 120,
            nivel="alto" if n != 3 else "medio",
            feedback="Comentário de teste.",
        )
        for n in range(1, 6)
    ],
    melhorias=["Sugestão um.", "Sugestão dois."],
)

REDACAO = (
    "A valorização da leitura é um desafio persistente no Brasil contemporâneo, e "
    "enfrentá-lo exige a atuação conjunta da escola, da família e do poder público, "
    "de modo que o livro deixe de ser privilégio de poucos estudantes."
)


@pytest.fixture
def cliente(monkeypatch):
    """App isolado, banco limpo, usuário controlável e IA substituída."""
    _BANCO.unlink(missing_ok=True)
    banco.criar_tabelas()

    atual: list[auth.UsuarioAtual] = [ALUNO]

    async def provedor(_: Request) -> auth.UsuarioAtual:
        return atual[0]

    auth.usar_provedor_de_usuario(provedor)
    monkeypatch.setattr(rotas, "corrigir_redacao", lambda *a, **k: CORRECAO_FALSA)

    app = FastAPI()
    app.include_router(rotas.router)
    with TestClient(app) as c:
        c.entrar_como = lambda u: atual.__setitem__(0, u)  # type: ignore[attr-defined]
        yield c


def test_status_inicial_do_aluno(cliente):
    r = cliente.get("/api/redacao/status")
    assert r.status_code == 200
    dados = r.json()
    assert dados["tem_chave_propria"] is False
    assert dados["redacoes_usadas"] == 0
    assert dados["redacoes_limite"] == 3
    assert dados["redacoes_restantes"] == 3
    assert dados["professor"] is False


def test_aluno_nao_gerencia_temas(cliente):
    r = cliente.post(
        "/api/redacao/temas",
        json={"titulo": "Tema", "textos_apoio": "x" * 60},
    )
    assert r.status_code == 403


def test_professor_gerencia_temas(cliente):
    cliente.entrar_como(PROFESSOR)
    apoio = "Texto de apoio suficientemente longo para passar na validação. " * 2

    criado = cliente.post(
        "/api/redacao/temas", json={"titulo": "Leitura no Brasil", "textos_apoio": apoio}
    )
    assert criado.status_code == 201
    tema_id = criado.json()["id"]

    assert len(cliente.get("/api/redacao/temas").json()) == 1

    editado = cliente.put(
        f"/api/redacao/temas/{tema_id}",
        json={"titulo": "Leitura no Brasil (rev.)", "textos_apoio": apoio},
    )
    assert editado.status_code == 200
    assert editado.json()["titulo"] == "Leitura no Brasil (rev.)"

    assert cliente.delete(f"/api/redacao/temas/{tema_id}").status_code == 200
    assert cliente.get("/api/redacao/temas").json() == []


def test_tema_com_apoio_curto_e_recusado(cliente):
    cliente.entrar_como(PROFESSOR)
    r = cliente.post(
        "/api/redacao/temas", json={"titulo": "Tema", "textos_apoio": "curto"}
    )
    assert r.status_code == 400


def test_redacao_curta_e_recusada(cliente):
    r = cliente.post("/api/redacao/corrigir", json={"redacao": "muito curta"})
    assert r.status_code == 400


def test_corrigir_devolve_nota_e_plagio(cliente):
    r = cliente.post("/api/redacao/corrigir", json={"redacao": REDACAO})
    assert r.status_code == 200
    dados = r.json()
    assert dados["nota_total"] == 760
    assert len(dados["competencias"]) == 5
    assert dados["plagio"]["percentual_copiado"] == 0
    assert cliente.get("/api/redacao/status").json()["redacoes_usadas"] == 1


def test_corrigir_detecta_copia_do_tema(cliente):
    cliente.entrar_como(PROFESSOR)
    apoio = (
        "Em muitas cidades brasileiras o acesso ao livro ainda e um privilegio de "
        "poucos, o que aprofunda as desigualdades educacionais do pais."
    )
    tema_id = cliente.post(
        "/api/redacao/temas", json={"titulo": "Leitura", "textos_apoio": apoio}
    ).json()["id"]

    cliente.entrar_como(ALUNO)
    copiada = (
        "Em muitas cidades brasileiras o acesso ao livro ainda e um privilegio de "
        "poucos, o que aprofunda as desigualdades educacionais do pais. Por isso o "
        "tema merece atencao."
    )
    r = cliente.post(
        "/api/redacao/corrigir", json={"redacao": copiada, "tema_id": tema_id}
    )
    assert r.status_code == 200
    plagio = r.json()["plagio"]
    assert plagio["percentual_copiado"] > 50
    assert plagio["trechos_copiados"]


def test_tema_inexistente(cliente):
    r = cliente.post(
        "/api/redacao/corrigir", json={"redacao": REDACAO, "tema_id": 9999}
    )
    assert r.status_code == 404


def test_limite_mensal_bloqueia_e_chave_propria_libera(cliente):
    for _ in range(3):
        assert cliente.post("/api/redacao/corrigir", json={"redacao": REDACAO}).status_code == 200

    bloqueado = cliente.post("/api/redacao/corrigir", json={"redacao": REDACAO})
    assert bloqueado.status_code == 429
    assert cliente.get("/api/redacao/status").json()["redacoes_restantes"] == 0

    assert cliente.post(
        "/api/redacao/chave", json={"api_key": "sk-ant-minha-chave"}
    ).status_code == 200

    status_com_chave = cliente.get("/api/redacao/status").json()
    assert status_com_chave["tem_chave_propria"] is True
    assert status_com_chave["redacoes_limite"] is None
    assert cliente.post("/api/redacao/corrigir", json={"redacao": REDACAO}).status_code == 200

    assert cliente.delete("/api/redacao/chave").status_code == 200
    assert cliente.get("/api/redacao/status").json()["tem_chave_propria"] is False


def test_chave_invalida_e_recusada(cliente):
    r = cliente.post("/api/redacao/chave", json={"api_key": "chave-qualquer"})
    assert r.status_code == 400


def test_historico_do_usuario_e_isolado(cliente):
    cliente.post("/api/redacao/corrigir", json={"redacao": REDACAO})
    historico = cliente.get("/api/redacao/historico").json()
    assert len(historico) == 1
    assert historico[0]["nota_total"] == 760

    cliente.entrar_como(PROFESSOR)
    assert cliente.get("/api/redacao/historico").json() == []
