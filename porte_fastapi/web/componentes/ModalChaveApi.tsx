/** Cadastro da chave de API própria do aluno. */

import { useState } from "react";

import { api, ErroApi, URL_CHAVES, URL_CREDITOS } from "../api";
import { Icone } from "./Icone";
import { Modal } from "./Modal";

interface Props {
  aberto: boolean;
  temChave: boolean;
  aoFechar: () => void;
  /** Chamado depois de salvar ou remover, para recarregar o status. */
  aoMudar: () => void;
}

export function ModalChaveApi({ aberto, temChave, aoFechar, aoMudar }: Props) {
  const [chave, setChave] = useState("");
  const [erro, setErro] = useState<string | null>(null);
  const [salvando, setSalvando] = useState(false);

  async function salvar() {
    setErro(null);
    setSalvando(true);
    try {
      await api.salvarChave(chave.trim());
      setChave("");
      aoMudar();
      aoFechar();
    } catch (e) {
      setErro(e instanceof ErroApi ? e.message : "Erro de conexão.");
    } finally {
      setSalvando(false);
    }
  }

  async function remover() {
    if (!confirm("Remover sua chave de API? O limite mensal será restaurado.")) return;
    setSalvando(true);
    try {
      await api.removerChave();
      aoMudar();
      aoFechar();
    } catch (e) {
      setErro(e instanceof ErroApi ? e.message : "Erro de conexão.");
    } finally {
      setSalvando(false);
    }
  }

  return (
    <Modal
      aberto={aberto}
      aoFechar={aoFechar}
      titulo={
        <>
          <Icone nome="chave" /> Usar minha chave de API
        </>
      }
      acoes={
        <>
          <button type="button" className="btn-secondary" onClick={aoFechar}>
            Cancelar
          </button>
          <button
            type="button"
            className="btn-primary"
            style={{ flex: 1 }}
            onClick={salvar}
            disabled={salvando || chave.trim() === ""}
          >
            Salvar chave
          </button>
        </>
      }
    >
      <p>
        Ao esgotar as correções gratuitas do mês, o sistema só continua com a sua
        própria chave. Com ela o uso é <strong>ilimitado</strong> e você paga
        apenas o que usar.
      </p>

      <div className="passos">
        <div className="passo">
          <strong>Compre créditos</strong> em{" "}
          <a href={URL_CREDITOS} target="_blank" rel="noopener noreferrer">
            console.anthropic.com/settings/billing
          </a>{" "}
          (é preciso cartão internacional).
        </div>
        <div className="passo">
          <strong>Crie a chave</strong> em{" "}
          <a href={URL_CHAVES} target="_blank" rel="noopener noreferrer">
            console.anthropic.com/settings/keys
          </a>{" "}
          → <strong>Create Key</strong>.
        </div>
        <div className="passo">
          <strong>Copie e cole abaixo</strong> o código que começa com{" "}
          <strong>sk-ant-</strong>. Sem créditos comprados, a chave não funciona.
        </div>
      </div>

      <div className="field">
        <label htmlFor="corretor-chave">Sua chave de API</label>
        <input
          id="corretor-chave"
          type="password"
          placeholder="sk-ant-..."
          value={chave}
          onChange={(e) => setChave(e.target.value)}
          autoComplete="off"
        />
      </div>

      {erro && <div className="erro">{erro}</div>}

      {temChave && (
        <div style={{ marginTop: 10, textAlign: "center" }}>
          <button
            type="button"
            onClick={remover}
            disabled={salvando}
            style={{
              background: "none",
              border: "none",
              color: "#a41317",
              fontFamily: "inherit",
              fontSize: 12,
              fontWeight: 600,
              textDecoration: "underline",
              cursor: "pointer",
            }}
          >
            Remover chave cadastrada
          </button>
        </div>
      )}
    </Modal>
  );
}
