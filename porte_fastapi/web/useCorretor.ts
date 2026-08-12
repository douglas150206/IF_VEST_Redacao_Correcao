/** Estado da tela de correção: status de uso, temas e envio da redação. */

import { useCallback, useEffect, useState } from "react";

import {
  api,
  ErroApi,
  type Correcao,
  type PedidoCorrecao,
  type StatusUso,
  type Tema,
} from "./api";

export interface EstadoCorretor {
  status: StatusUso | null;
  temas: Tema[];
  correcao: Correcao | null;
  carregando: boolean;
  enviando: boolean;
  erro: string | null;
  limiteAtingido: boolean;
  /** `true` quando o envio deve ser bloqueado na interface. */
  bloqueado: boolean;
  corrigir: (pedido: PedidoCorrecao) => Promise<void>;
  recarregarStatus: () => Promise<void>;
  recarregarTemas: () => Promise<void>;
  limparErro: () => void;
}

export function useCorretor(): EstadoCorretor {
  const [status, setStatus] = useState<StatusUso | null>(null);
  const [temas, setTemas] = useState<Tema[]>([]);
  const [correcao, setCorrecao] = useState<Correcao | null>(null);
  const [carregando, setCarregando] = useState(true);
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [limiteAtingido, setLimiteAtingido] = useState(false);

  const recarregarStatus = useCallback(async () => {
    const novo = await api.status();
    setStatus(novo);
    // Se o limite foi liberado (chave cadastrada), some o aviso de bloqueio.
    if (novo.tem_chave_propria || (novo.redacoes_restantes ?? 1) > 0) {
      setLimiteAtingido(false);
    }
  }, []);

  const recarregarTemas = useCallback(async () => {
    setTemas(await api.temas());
  }, []);

  useEffect(() => {
    let ativo = true;
    (async () => {
      try {
        const [s, t] = await Promise.all([api.status(), api.temas()]);
        if (!ativo) return;
        setStatus(s);
        setTemas(t);
      } catch (e) {
        if (ativo) {
          setErro(
            e instanceof ErroApi ? e.message : "Não foi possível carregar a tela.",
          );
        }
      } finally {
        if (ativo) setCarregando(false);
      }
    })();
    return () => {
      ativo = false;
    };
  }, []);

  const corrigir = useCallback(
    async (pedido: PedidoCorrecao) => {
      setErro(null);
      setLimiteAtingido(false);
      setCorrecao(null);
      setEnviando(true);
      try {
        const resultado = await api.corrigir(pedido);
        setCorrecao(resultado);
        await recarregarStatus();
      } catch (e) {
        if (e instanceof ErroApi && e.limiteAtingido) {
          setLimiteAtingido(true);
          await recarregarStatus();
        } else {
          setErro(e instanceof ErroApi ? e.message : "Erro de conexão.");
        }
      } finally {
        setEnviando(false);
      }
    },
    [recarregarStatus],
  );

  const bloqueado =
    status !== null &&
    !status.tem_chave_propria &&
    status.redacoes_limite !== null &&
    (status.redacoes_restantes ?? 0) === 0;

  return {
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
    limparErro: () => setErro(null),
  };
}
