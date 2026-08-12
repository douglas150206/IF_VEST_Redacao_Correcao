/** Explica o limite mensal. Abre sozinho ao entrar na tela e pelo botão do cartão. */

import { URL_CHAVES, URL_CREDITOS, type StatusUso } from "../api";
import { Icone, type NomeIcone } from "./Icone";
import { Modal } from "./Modal";

interface Props {
  aberto: boolean;
  status: StatusUso;
  aoFechar: () => void;
  aoAbrirChave: () => void;
}

export function ModalPlano({ aberto, status, aoFechar, aoAbrirChave }: Props) {
  const limite = status.redacoes_limite ?? 0;
  const restantes = status.redacoes_restantes ?? 0;
  const critico = restantes <= 3;

  let titulo: string;
  let icone: NomeIcone;
  if (restantes === 0) {
    titulo = `Suas ${limite} correções gratuitas deste mês acabaram`;
    icone = "bloqueio";
  } else if (critico) {
    titulo = `Restam apenas ${restantes} de ${limite} correções gratuitas`;
    icone = "alerta";
  } else {
    titulo = "Antes de começar: como funciona o seu limite";
    icone = "info";
  }

  return (
    <Modal
      aberto={aberto}
      aoFechar={aoFechar}
      largo
      titulo={
        <>
          <span style={{ color: critico ? "#cd191e" : "#2f9e41", display: "flex" }}>
            <Icone nome={icone} />
          </span>
          {titulo}
        </>
      }
      acoes={
        <>
          <button type="button" className="btn-secondary" onClick={aoFechar}>
            Entendi, começar
          </button>
          <button
            type="button"
            className="btn-primary"
            style={{ flex: 1 }}
            onClick={() => {
              aoFechar();
              aoAbrirChave();
            }}
          >
            Cadastrar minha chave agora
          </button>
        </>
      }
    >
      <div className={`destaque${critico ? " alerta" : ""}`}>
        <strong>Você tem {limite} correções gratuitas por mês.</strong>
        <br />
        Depois disso o sistema bloqueia até o mês virar — a não ser que você compre
        créditos no site da Anthropic e cadastre a{" "}
        <strong>sua própria chave de API</strong> aqui.
      </div>

      <div className="passos">
        <div className="passo">
          Corrija <strong>até {limite} redações por mês sem pagar nada</strong>. O
          contador fica visível no topo da tela e zera todo dia 1º.
        </div>
        <div className="passo">
          Ao chegar no limite, o botão de corrigir é bloqueado. Para continuar no
          mesmo mês, siga os passos 3 e 4.
        </div>
        <div className="passo">
          Compre créditos em{" "}
          <a href={URL_CREDITOS} target="_blank" rel="noopener noreferrer">
            console.anthropic.com/settings/billing
          </a>
          .
        </div>
        <div className="passo">
          Crie sua chave em{" "}
          <a href={URL_CHAVES} target="_blank" rel="noopener noreferrer">
            console.anthropic.com/settings/keys
          </a>
          , copie o código que começa com <strong>sk-ant-</strong> e cole aqui no
          sistema. A partir daí seu uso fica <strong>ilimitado</strong>.
        </div>
      </div>
    </Modal>
  );
}
