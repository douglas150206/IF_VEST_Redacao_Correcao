/** Últimas correções do aluno, com nota e percentual de cópia. */

import { useEffect, useState } from "react";

import { api, ErroApi, type ItemHistorico } from "../api";
import { Icone } from "./Icone";
import { Modal } from "./Modal";

interface Props {
  aberto: boolean;
  aoFechar: () => void;
}

function formatarData(iso: string): string {
  // O SQLite devolve "2026-08-11 19:48:21" (UTC, sem timezone).
  const data = new Date(iso.replace(" ", "T") + "Z");
  return Number.isNaN(data.getTime())
    ? iso
    : data.toLocaleDateString("pt-BR", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
      });
}

function classeCopia(pct: number): string {
  if (pct === 0) return "nivel-pill nivel-alto";
  if (pct < 25) return "nivel-pill nivel-medio";
  return "nivel-pill nivel-baixo";
}

export function ModalHistorico({ aberto, aoFechar }: Props) {
  const [itens, setItens] = useState<ItemHistorico[] | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    if (!aberto) return;
    let ativo = true;
    setItens(null);
    setErro(null);
    api
      .historico()
      .then((d) => ativo && setItens(d))
      .catch((e) =>
        ativo &&
        setErro(e instanceof ErroApi ? e.message : "Erro ao carregar o histórico."),
      );
    return () => {
      ativo = false;
    };
  }, [aberto]);

  return (
    <Modal
      aberto={aberto}
      aoFechar={aoFechar}
      largo
      titulo={
        <>
          <Icone nome="documento" /> Histórico de correções
        </>
      }
      acoes={
        <button type="button" className="btn-secondary" onClick={aoFechar}>
          Fechar
        </button>
      }
    >
      <p>
        Últimas redações corrigidas, com a nota estimada e o percentual de cópia dos
        textos de apoio.
      </p>

      {erro && <div className="erro">{erro}</div>}
      {!erro && itens === null && <p className="hint">Carregando...</p>}
      {itens?.length === 0 && (
        <p className="hint">Você ainda não corrigiu nenhuma redação.</p>
      )}

      {itens?.map((item) => (
        <div
          key={item.id}
          style={{
            border: "1px solid #e9ebe9",
            borderRadius: 5,
            padding: "11px 14px",
            marginBottom: 8,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 10,
          }}
        >
          <div>
            <div style={{ fontSize: 13, fontWeight: 600 }}>
              {item.tema ?? "Sem tema"}
            </div>
            <div style={{ fontSize: 12, color: "#757b81", marginTop: 2 }}>
              {formatarData(item.criado_em)}
            </div>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <span className={classeCopia(item.plagio_percentual)}>
              {item.plagio_percentual === 0
                ? "Sem cópia"
                : `Cópia ${item.plagio_percentual}%`}
            </span>
            <span
              style={{ fontSize: 16, fontWeight: 700, color: "#185c22", whiteSpace: "nowrap" }}
            >
              {item.nota_total ?? "—"}
              <span style={{ fontSize: 11, color: "#757b81", fontWeight: 400 }}>
                /1000
              </span>
            </span>
          </div>
        </div>
      ))}
    </Modal>
  );
}
