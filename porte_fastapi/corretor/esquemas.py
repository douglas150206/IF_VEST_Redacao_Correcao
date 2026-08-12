"""Modelos Pydantic — contrato da API e formato exigido da IA.

`CorrecaoIA` é usada como structured output na chamada à Anthropic: o modelo é
obrigado a devolver exatamente esse formato, o que elimina o passo de limpar
crases de markdown e fazer JSON.parse na mão.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

Nivel = Literal["alto", "medio", "baixo"]


# ── Formato devolvido pela IA (structured output) ────────────────────────────

class Competencia(BaseModel):
    numero: int = Field(description="Número da competência, de 1 a 5.")
    titulo: str = Field(description="Título da competência do ENEM.")
    nota: int = Field(description="Nota da competência: 0, 40, 80, 120, 160 ou 200.")
    nivel: Nivel
    feedback: str = Field(description="2 a 3 frases de feedback sobre esta redação.")


class CorrecaoIA(BaseModel):
    nota_total: int = Field(description="Soma das cinco competências, máximo 1000.")
    competencias: list[Competencia]
    melhorias: list[str] = Field(description="Sugestões específicas de melhoria.")

    @model_validator(mode="after")
    def _nota_total_e_sempre_a_soma(self) -> "CorrecaoIA":
        """No ENEM a nota total é, por definição, a soma das competências.

        O modelo às vezes devolve um total que não fecha com as partes (visto em
        produção: competências somando 640 com nota_total 680). Como as notas por
        competência são o julgamento substantivo, o total é recalculado a partir
        delas — assim a tela nunca mostra uma conta que não bate.

        A regra de zerar por cópia é aplicada zerando as competências, então
        continua funcionando: a soma dá 0 naturalmente.
        """
        soma = sum(c.nota for c in self.competencias)
        if self.competencias and self.nota_total != soma:
            self.nota_total = soma
        return self


# ── Detecção de cópia ────────────────────────────────────────────────────────

class TrechoCopiadoOut(BaseModel):
    texto: str
    palavras: int


class PlagioOut(BaseModel):
    percentual_copiado: int
    palavras_copiadas: int
    total_palavras: int
    trechos_copiados: list[TrechoCopiadoOut]


# ── Entrada e saída das rotas ────────────────────────────────────────────────

class CorrigirIn(BaseModel):
    redacao: str
    tema: str | None = None
    tema_id: int | None = None
    textos_apoio: str | None = None


class CorrecaoOut(CorrecaoIA):
    plagio: PlagioOut


class TemaIn(BaseModel):
    titulo: str
    textos_apoio: str


class TemaOut(BaseModel):
    id: int
    titulo: str
    textos_apoio: str


class StatusOut(BaseModel):
    usuario_id: int
    nome: str
    professor: bool
    tem_chave_propria: bool
    redacoes_usadas: int
    redacoes_limite: int | None
    redacoes_restantes: int | None


class HistoricoItem(BaseModel):
    id: int
    tema: str | None
    criado_em: str
    plagio_percentual: int
    nota_total: int | None


class ChaveIn(BaseModel):
    api_key: str


class Mensagem(BaseModel):
    mensagem: str
