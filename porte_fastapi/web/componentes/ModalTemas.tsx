/** Gestão de temas e textos de apoio — só aparece para professores. */

import { useEffect, useState } from "react";

import { api, ErroApi, type Tema } from "../api";
import { Icone } from "./Icone";
import { Modal } from "./Modal";

interface Props {
  aberto: boolean;
  aoFechar: () => void;
  /** Chamado após qualquer alteração, para recarregar a lista da tela. */
  aoMudar: () => void;
}

const MIN_APOIO = 50;

export function ModalTemas({ aberto, aoFechar, aoMudar }: Props) {
  const [temas, setTemas] = useState<Tema[]>([]);
  const [editando, setEditando] = useState<number | null>(null);
  const [titulo, setTitulo] = useState("");
  const [apoio, setApoio] = useState("");
  const [erro, setErro] = useState<string | null>(null);
  const [salvando, setSalvando] = useState(false);

  useEffect(() => {
    if (aberto) recarregar();
  }, [aberto]);

  async function recarregar() {
    try {
      setTemas(await api.temas());
    } catch (e) {
      setErro(e instanceof ErroApi ? e.message : "Erro ao carregar os temas.");
    }
  }

  function limpar() {
    setEditando(null);
    setTitulo("");
    setApoio("");
    setErro(null);
  }

  async function salvar() {
    setErro(null);
    if (!titulo.trim()) {
      setErro("Informe o título do tema.");
      return;
    }
    if (apoio.trim().length < MIN_APOIO) {
      setErro(`Os textos de apoio precisam ter ao menos ${MIN_APOIO} caracteres.`);
      return;
    }
    setSalvando(true);
    try {
      const dados = { titulo: titulo.trim(), textos_apoio: apoio.trim() };
      if (editando === null) await api.criarTema(dados);
      else await api.atualizarTema(editando, dados);
      limpar();
      await recarregar();
      aoMudar();
    } catch (e) {
      setErro(e instanceof ErroApi ? e.message : "Erro ao salvar.");
    } finally {
      setSalvando(false);
    }
  }

  async function excluir(tema: Tema) {
    if (!confirm(`Excluir o tema "${tema.titulo}"? Correções já feitas não são afetadas.`))
      return;
    try {
      await api.removerTema(tema.id);
      if (editando === tema.id) limpar();
      await recarregar();
      aoMudar();
    } catch (e) {
      setErro(e instanceof ErroApi ? e.message : "Erro ao excluir.");
    }
  }

  return (
    <Modal
      aberto={aberto}
      aoFechar={aoFechar}
      largo
      titulo={
        <>
          <Icone nome="documento" /> Gerenciar temas
        </>
      }
      acoes={
        <button type="button" className="btn-secondary" onClick={aoFechar}>
          Fechar
        </button>
      }
    >
      <p>Cadastre, edite ou remova os temas e seus textos de apoio.</p>

      <div className="field">
        <label htmlFor="corretor-tema-titulo">
          {editando === null ? "Novo tema" : "Editando tema"}
        </label>
        <input
          id="corretor-tema-titulo"
          type="text"
          placeholder="Título do tema"
          value={titulo}
          onChange={(e) => setTitulo(e.target.value)}
          style={{ marginBottom: 8 }}
        />
        <textarea
          className="txt"
          placeholder={`Textos de apoio (mínimo de ${MIN_APOIO} caracteres)...`}
          value={apoio}
          onChange={(e) => setApoio(e.target.value)}
          style={{ minHeight: 110 }}
        />
      </div>

      {erro && <div className="erro">{erro}</div>}

      <div className="modal-btns" style={{ marginTop: 8 }}>
        {editando !== null && (
          <button type="button" className="btn-secondary" onClick={limpar}>
            Cancelar edição
          </button>
        )}
        <button
          type="button"
          className="btn-primary"
          style={{ flex: 1 }}
          onClick={salvar}
          disabled={salvando}
        >
          {editando === null ? "Adicionar tema" : "Salvar alterações"}
        </button>
      </div>

      <div className="divider" style={{ margin: "1rem 0" }} />
      <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 8 }}>
        Temas cadastrados
      </div>

      {temas.length === 0 && <p className="hint">Nenhum tema cadastrado.</p>}
      {temas.map((tema) => (
        <div
          key={tema.id}
          style={{
            border: "1px solid #e9ebe9",
            borderRadius: 5,
            padding: "11px 14px",
            marginBottom: 8,
            display: "flex",
            alignItems: "flex-start",
            justifyContent: "space-between",
            gap: 10,
          }}
        >
          <div style={{ fontSize: 13, fontWeight: 600 }}>{tema.titulo}</div>
          <div style={{ display: "flex", gap: 6, flexShrink: 0 }}>
            <button
              type="button"
              className="btn-acao contorno"
              style={{ padding: "5px 11px", fontSize: 12 }}
              onClick={() => {
                setEditando(tema.id);
                setTitulo(tema.titulo);
                setApoio(tema.textos_apoio);
                setErro(null);
              }}
            >
              Editar
            </button>
            <button
              type="button"
              className="btn-acao contorno"
              style={{ padding: "5px 11px", fontSize: 12, color: "#a41317" }}
              onClick={() => excluir(tema)}
            >
              Excluir
            </button>
          </div>
        </div>
      ))}
    </Modal>
  );
}
