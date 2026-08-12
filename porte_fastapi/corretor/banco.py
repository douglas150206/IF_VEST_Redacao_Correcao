"""Acesso ao SQLite.

As tabelas têm prefixo `corretor_` para conviverem no mesmo arquivo das tabelas
do IFvest sem colidir. `usuario_id` referencia a tabela de usuários de vocês —
como o corretor não conhece o nome dessa tabela, a FK não é declarada aqui.

Todo o SQL do módulo vive neste arquivo: se vocês usam SQLAlchemy, é o único
lugar que precisa ser reescrito.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone

from .config import config

ESQUEMA = """
CREATE TABLE IF NOT EXISTS corretor_temas (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  titulo       TEXT NOT NULL,
  textos_apoio TEXT NOT NULL,
  criado_em    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS corretor_correcoes (
  id                INTEGER PRIMARY KEY AUTOINCREMENT,
  usuario_id        INTEGER NOT NULL,   -- id do usuário no sistema do IFvest
  tema              TEXT,
  tema_id           INTEGER,
  redacao           TEXT NOT NULL,
  resultado         TEXT NOT NULL,      -- JSON com a correção completa
  plagio_percentual INTEGER NOT NULL DEFAULT 0,
  criado_em         TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_corretor_correcoes_usuario
  ON corretor_correcoes (usuario_id, criado_em);

-- Chave de API própria do aluno (quando ele custeia o próprio uso).
CREATE TABLE IF NOT EXISTS corretor_chaves (
  usuario_id  INTEGER PRIMARY KEY,
  api_key     TEXT NOT NULL,
  criado_em   TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


@contextmanager
def conexao() -> Iterator[sqlite3.Connection]:
    con = sqlite3.connect(config.banco)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def criar_tabelas() -> None:
    with conexao() as con:
        con.executescript(ESQUEMA)


def mes_atual() -> str:
    """Ex.: "2026-08" — em UTC, igual ao strftime('%Y-%m') do SQLite."""
    return datetime.now(timezone.utc).strftime("%Y-%m")


# ── Temas ────────────────────────────────────────────────────────────────────

def listar_temas() -> list[sqlite3.Row]:
    with conexao() as con:
        return con.execute(
            "SELECT id, titulo, textos_apoio FROM corretor_temas ORDER BY titulo"
        ).fetchall()


def buscar_tema(tema_id: int) -> sqlite3.Row | None:
    with conexao() as con:
        return con.execute(
            "SELECT id, titulo, textos_apoio FROM corretor_temas WHERE id = ?",
            (tema_id,),
        ).fetchone()


def criar_tema(titulo: str, textos_apoio: str) -> int:
    with conexao() as con:
        cur = con.execute(
            "INSERT INTO corretor_temas (titulo, textos_apoio) VALUES (?, ?)",
            (titulo, textos_apoio),
        )
        return int(cur.lastrowid)


def atualizar_tema(tema_id: int, titulo: str, textos_apoio: str) -> bool:
    with conexao() as con:
        cur = con.execute(
            "UPDATE corretor_temas SET titulo = ?, textos_apoio = ? WHERE id = ?",
            (titulo, textos_apoio, tema_id),
        )
        return cur.rowcount > 0


def remover_tema(tema_id: int) -> bool:
    with conexao() as con:
        cur = con.execute("DELETE FROM corretor_temas WHERE id = ?", (tema_id,))
        return cur.rowcount > 0


# ── Chave de API própria ─────────────────────────────────────────────────────

def buscar_chave(usuario_id: int) -> str | None:
    with conexao() as con:
        linha = con.execute(
            "SELECT api_key FROM corretor_chaves WHERE usuario_id = ?", (usuario_id,)
        ).fetchone()
        return linha["api_key"] if linha else None


def salvar_chave(usuario_id: int, api_key: str) -> None:
    with conexao() as con:
        con.execute(
            "INSERT INTO corretor_chaves (usuario_id, api_key) VALUES (?, ?) "
            "ON CONFLICT(usuario_id) DO UPDATE SET api_key = excluded.api_key",
            (usuario_id, api_key),
        )


def remover_chave(usuario_id: int) -> None:
    with conexao() as con:
        con.execute("DELETE FROM corretor_chaves WHERE usuario_id = ?", (usuario_id,))


# ── Correções ────────────────────────────────────────────────────────────────

def contar_correcoes_do_mes(usuario_id: int) -> int:
    with conexao() as con:
        linha = con.execute(
            "SELECT COUNT(*) AS total FROM corretor_correcoes "
            "WHERE usuario_id = ? AND strftime('%Y-%m', criado_em) = ?",
            (usuario_id, mes_atual()),
        ).fetchone()
        return int(linha["total"])


def registrar_correcao(
    usuario_id: int,
    tema: str | None,
    tema_id: int | None,
    redacao: str,
    resultado: dict,
    plagio_percentual: int,
) -> int:
    with conexao() as con:
        cur = con.execute(
            "INSERT INTO corretor_correcoes "
            "(usuario_id, tema, tema_id, redacao, resultado, plagio_percentual) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                usuario_id,
                tema,
                tema_id,
                redacao,
                json.dumps(resultado, ensure_ascii=False),
                plagio_percentual,
            ),
        )
        return int(cur.lastrowid)


def listar_historico(usuario_id: int, limite: int = 20) -> list[sqlite3.Row]:
    with conexao() as con:
        return con.execute(
            "SELECT id, tema, criado_em, plagio_percentual, "
            "       json_extract(resultado, '$.nota_total') AS nota_total "
            "FROM corretor_correcoes WHERE usuario_id = ? "
            "ORDER BY criado_em DESC LIMIT ?",
            (usuario_id, limite),
        ).fetchall()
