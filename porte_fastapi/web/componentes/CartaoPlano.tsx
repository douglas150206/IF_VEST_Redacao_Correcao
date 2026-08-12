/** Cartão sempre visível com quantas correções gratuitas restam no mês. */

import { URL_CREDITOS, type StatusUso } from "../api";
import { Icone } from "./Icone";

interface Props {
  status: StatusUso;
  aoAbrirChave: () => void;
  aoAbrirExplicacao: () => void;
}

export function CartaoPlano({ status, aoAbrirChave, aoAbrirExplicacao }: Props) {
  if (status.tem_chave_propria) {
    return (
      <section className="plano-card ilimitado">
        <div className="plano-head">
          <div className="plano-titulo">
            <Icone nome="chave" className="ico-md" />
            Chave de API própria ativa — uso ilimitado
          </div>
          <div className="plano-contador">
            {status.redacoes_usadas} correções este mês
          </div>
        </div>
        <p className="plano-texto">
          As correções são cobradas diretamente nos{" "}
          <strong>seus créditos da Anthropic</strong>. Se a chave for removida, a
          conta volta ao plano gratuito.
        </p>
        <div className="plano-acoes">
          <button type="button" className="btn-acao contorno" onClick={aoAbrirChave}>
            <Icone nome="chave" /> Gerenciar minha chave
          </button>
        </div>
      </section>
    );
  }

  // Limite desligado no servidor (CORRETOR_LIMITE_MENSAL=0): a instituição banca.
  if (status.redacoes_limite === null) {
    return (
      <section className="plano-card ok">
        <div className="plano-head">
          <div className="plano-titulo">
            <Icone nome="check" className="ico-md" />
            Correções liberadas pela instituição
          </div>
          <div className="plano-contador">
            {status.redacoes_usadas} correções este mês
          </div>
        </div>
        <p className="plano-texto">
          Você pode enviar redações sem limite mensal. Use com responsabilidade —
          cada correção consome créditos institucionais.
        </p>
      </section>
    );
  }

  const limite = status.redacoes_limite;
  const usadas = status.redacoes_usadas;
  const restantes = status.redacoes_restantes ?? 0;
  const estado = restantes === 0 ? "danger" : restantes <= 3 ? "warn" : "ok";
  const enfase = restantes === 0 ? "principal" : "contorno";

  const titulo =
    restantes === 0 ? (
      <>
        <Icone nome="bloqueio" className="ico-md" />
        Limite gratuito esgotado — {usadas}/{limite} correções usadas neste mês
      </>
    ) : restantes <= 3 ? (
      <>
        <Icone nome="alerta" className="ico-md" />
        Restam apenas {restantes} de {limite} correções gratuitas neste mês
      </>
    ) : (
      <>
        <Icone nome="info" className="ico-md" />
        Plano gratuito — {restantes} de {limite} correções restantes neste mês
      </>
    );

  const texto =
    restantes === 0 ? (
      <>
        As <strong>{limite} correções gratuitas</strong> deste mês já foram
        utilizadas. Para corrigir a <strong>próxima redação agora</strong>, é
        necessário <strong>comprar créditos no site da Anthropic</strong> e
        cadastrar a <strong>sua própria chave de API</strong>. Sem isso, o envio
        fica bloqueado até o dia 1º do próximo mês.
      </>
    ) : restantes <= 3 ? (
      <>
        Quando as {limite} correções acabarem, a próxima{" "}
        <strong>só será processada com créditos próprios</strong>. Compre créditos
        e cadastre sua chave com antecedência para não interromper os estudos.
      </>
    ) : (
      <>
        Cada conta tem <strong>{limite} correções gratuitas por mês</strong> (o
        contador reinicia todo dia 1º). Depois disso, é preciso{" "}
        <strong>comprar créditos no site da Anthropic</strong> e cadastrar a{" "}
        <strong>sua própria chave de API</strong> para continuar no mesmo mês.
      </>
    );

  return (
    <section className={`plano-card ${estado}`}>
      <div className="plano-head">
        <div className="plano-titulo">{titulo}</div>
        <div className="plano-contador">
          {usadas} de {limite} usadas
        </div>
      </div>

      <div
        className={`plano-blocos${restantes === 0 ? " esgotado" : ""}`}
        role="img"
        aria-label={`${usadas} de ${limite} correções usadas neste mês`}
      >
        {Array.from({ length: limite }, (_, i) => (
          <div
            key={i}
            className={
              i < usadas
                ? "plano-bloco usado"
                : `plano-bloco${estado === "ok" ? "" : " warn"}`
            }
          />
        ))}
      </div>

      <p className="plano-texto">{texto}</p>

      <div className="plano-acoes">
        <a
          className={`btn-acao ${enfase}`}
          href={URL_CREDITOS}
          target="_blank"
          rel="noopener noreferrer"
        >
          <Icone nome="cartao" /> Comprar créditos na Anthropic
        </a>
        <button type="button" className={`btn-acao ${enfase}`} onClick={aoAbrirChave}>
          <Icone nome="chave" /> Cadastrar minha chave de API
        </button>
        <button type="button" className="btn-acao contorno" onClick={aoAbrirExplicacao}>
          <Icone nome="info" /> Como funciona o limite
        </button>
      </div>
    </section>
  );
}
