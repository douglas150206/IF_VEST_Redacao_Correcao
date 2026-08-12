/**
 * Tela de correção de redação — o componente que o IFvest monta na sua rota.
 *
 *     import { CorretorDeRedacao } from "./corretor/CorretorDeRedacao";
 *     import "./corretor/corretor.css";
 *
 *     <Route path="/redacao" element={<CorretorDeRedacao />} />
 *
 * Não desenha cabeçalho nem navegação: isso é do layout de vocês.
 */

import { useEffect, useMemo, useRef, useState } from "react";

import { URL_CHAVES, URL_CREDITOS } from "./api";
import { CartaoPlano } from "./componentes/CartaoPlano";
import { Icone } from "./componentes/Icone";
import { ModalChaveApi } from "./componentes/ModalChaveApi";
import { ModalHistorico } from "./componentes/ModalHistorico";
import { ModalPlano } from "./componentes/ModalPlano";
import { ModalTemas } from "./componentes/ModalTemas";
import { ResultadoCorrecao } from "./componentes/ResultadoCorrecao";
import { montarTema, SeletorDeTema } from "./componentes/SeletorDeTema";
import { useCorretor } from "./useCorretor";

const MIN_CARACTERES = 100;

const MENSAGENS_PROGRESSO = [
  "Enviando redação...",
  "Competência I — Norma culta...",
  "Competência II — Tema e argumentos...",
  "Competência III — Organização de ideias...",
  "Competência IV — Coesão textual...",
  "Competência V — Proposta de intervenção...",
  "Calculando nota final...",
];
const PROGRESSO = [8, 22, 38, 53, 67, 82, 95];

function useProgresso(ativo: boolean) {
  const [passo, setPasso] = useState(0);
  useEffect(() => {
    if (!ativo) {
      setPasso(0);
      return;
    }
    const id = setInterval(
      () => setPasso((p) => Math.min(p + 1, MENSAGENS_PROGRESSO.length - 1)),
      1800,
    );
    return () => clearInterval(id);
  }, [ativo]);
  return passo;
}

export function CorretorDeRedacao() {
  const {
    status,
    temas,
    correcao,
    carregando,
    enviando,
    erro,
    limiteAtingido,
    bloqueado,
    corrigir,
    recarregarStatus,
    recarregarTemas,
  } = useCorretor();

  const [redacao, setRedacao] = useState("");
  const [tema, setTema] = useState("");
  const [tituloCustom, setTituloCustom] = useState("");
  const [apoioCustom, setApoioCustom] = useState("");
  const [erroLocal, setErroLocal] = useState<string | null>(null);

  // Um modal por vez: guardar um booleano por modal deixava dois overlays
  // empilharem se dois fossem abertos na mesma interação.
  type Modal = null | "plano" | "chave" | "historico" | "temas";
  const [modal, setModal] = useState<Modal>(null);
  const fecharModal = () => setModal(null);
  const jaExplicou = useRef(false);

  const passo = useProgresso(enviando);
  const resultadoRef = useRef<HTMLDivElement>(null);

  // Explica o limite uma vez por visita, para quem ainda não tem chave própria.
  useEffect(() => {
    if (!status || jaExplicou.current) return;
    jaExplicou.current = true;
    if (!status.tem_chave_propria && status.redacoes_limite !== null) {
      setModal("plano");
    }
  }, [status]);

  useEffect(() => {
    if (correcao) resultadoRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [correcao]);

  const palavras = useMemo(
    () => redacao.trim().split(/\s+/).filter(Boolean).length,
    [redacao],
  );

  async function enviar() {
    setErroLocal(null);
    if (redacao.trim().length < MIN_CARACTERES) {
      setErroLocal(
        `Por favor, insira uma redação com pelo menos ${MIN_CARACTERES} caracteres.`,
      );
      return;
    }
    await corrigir({
      redacao: redacao.trim(),
      ...montarTema(tema, tituloCustom, apoioCustom),
    });
  }

  if (carregando) {
    return (
      <div className="corretor">
        <p className="hint">Carregando...</p>
      </div>
    );
  }

  if (!status) {
    return (
      <div className="corretor">
        <div className="error-box">
          {erro ?? "Não foi possível carregar a tela de correção."}
        </div>
      </div>
    );
  }

  const restantes = status.redacoes_restantes;
  const rotuloBotao = bloqueado
    ? `Limite de ${status.redacoes_limite} por mês atingido — cadastre sua chave de API`
    : status.tem_chave_propria || status.redacoes_limite === null
      ? "Corrigir redação"
      : `Corrigir redação — restam ${restantes} de ${status.redacoes_limite} gratuitas`;

  return (
    <div className="corretor">
      <header className="titulo-pagina">
        <h1>Corretor de Redação ENEM</h1>
        <p>
          Avaliação nas cinco competências do ENEM, com nota estimada e verificação
          de cópia dos textos de apoio.
        </p>
        <div className="plano-acoes" style={{ marginTop: 12 }}>
          <button
            type="button"
            className="btn-acao contorno"
            onClick={() => setModal("historico")}
          >
            <Icone nome="documento" /> Meu histórico
          </button>
          {status.professor && (
            <button
              type="button"
              className="btn-acao contorno"
              onClick={() => setModal("temas")}
            >
              <Icone nome="documento" /> Gerenciar temas
            </button>
          )}
        </div>
      </header>

      <CartaoPlano
        status={status}
        aoAbrirChave={() => setModal("chave")}
        aoAbrirExplicacao={() => setModal("plano")}
      />

      <div className="card">
        <SeletorDeTema
          temas={temas}
          valor={tema}
          aoMudar={setTema}
          tituloCustom={tituloCustom}
          aoMudarTituloCustom={setTituloCustom}
          apoioCustom={apoioCustom}
          aoMudarApoioCustom={setApoioCustom}
        />

        <label className="lbl" htmlFor="corretor-redacao">
          Texto da redação
        </label>
        <textarea
          id="corretor-redacao"
          className="txt"
          placeholder="Cole ou digite a redação aqui..."
          value={redacao}
          onChange={(e) => setRedacao(e.target.value)}
        />
        <div className="char-count">{palavras} palavras</div>
      </div>

      <div className="badges">
        <span className="badge">Competência I — Norma culta</span>
        <span className="badge">Competência II — Tema</span>
        <span className="badge">Competência III — Argumentação</span>
        <span className="badge">Competência IV — Coesão</span>
        <span className="badge">Competência V — Proposta</span>
      </div>

      <button
        type="button"
        className="btn-corrigir"
        onClick={enviar}
        disabled={bloqueado || enviando}
      >
        <Icone nome={bloqueado ? "bloqueio" : "caneta"} />
        {enviando ? "Corrigindo..." : rotuloBotao}
      </button>

      {(erroLocal || erro) && <div className="error-box">{erroLocal ?? erro}</div>}

      {(limiteAtingido || bloqueado) && (
        <div className="limit-box">
          <strong>
            Limite de {status.redacoes_limite} correções gratuitas atingido neste
            mês.
          </strong>
          <br />
          Para corrigir mais redações agora, é necessário usar créditos próprios:
          <br />
          <strong>1.</strong> Compre créditos em{" "}
          <a href={URL_CREDITOS} target="_blank" rel="noopener noreferrer">
            console.anthropic.com/settings/billing
          </a>
          <br />
          <strong>2.</strong> Crie sua chave em{" "}
          <a href={URL_CHAVES} target="_blank" rel="noopener noreferrer">
            console.anthropic.com/settings/keys
          </a>{" "}
          e cadastre-a no sistema.
          <br />
          <button
            type="button"
            className="btn-acao principal"
            style={{ marginTop: 10 }}
            onClick={() => setModal("chave")}
          >
            <Icone nome="chave" /> Cadastrar minha chave de API
          </button>
          <br />
          <span style={{ fontSize: 12 }}>
            Sem chave própria, as correções gratuitas voltam no dia 1º do próximo
            mês.
          </span>
        </div>
      )}

      <div ref={resultadoRef}>
        {enviando && (
          <div className="results">
            <div className="loading">
              <div className="spinner-wrap">
                <div className="spinner-outer" />
                <div className="spinner-inner" />
              </div>
              <div className="loading-msg">{MENSAGENS_PROGRESSO[passo]}</div>
              <div className="loading-sub">
                Análise em andamento nas cinco competências
              </div>
              <div className="loading-progress-bg">
                <div
                  className="loading-progress-fill"
                  style={{ width: `${PROGRESSO[passo]}%` }}
                />
              </div>
            </div>
          </div>
        )}
        {!enviando && correcao && <ResultadoCorrecao correcao={correcao} />}
      </div>

      <ModalPlano
        aberto={modal === "plano"}
        status={status}
        aoFechar={fecharModal}
        aoAbrirChave={() => setModal("chave")}
      />
      <ModalChaveApi
        aberto={modal === "chave"}
        temChave={status.tem_chave_propria}
        aoFechar={fecharModal}
        aoMudar={recarregarStatus}
      />
      <ModalHistorico aberto={modal === "historico"} aoFechar={fecharModal} />
      {status.professor && (
        <ModalTemas
          aberto={modal === "temas"}
          aoFechar={fecharModal}
          aoMudar={recarregarTemas}
        />
      )}
    </div>
  );
}
