/**
 * Cliente e tipos da API de correção de redação.
 *
 * Os tipos espelham os modelos Pydantic de `corretor/esquemas.py` — se um campo
 * mudar lá, o TypeScript acusa aqui.
 *
 * Integração: por padrão as requisições saem com `credentials: "include"` e sem
 * cabeçalho de autenticação, o que já funciona se o IFvest usa cookie de sessão.
 * Se vocês usam token no header, chame `configurarApi` uma vez no bootstrap:
 *
 *     configurarApi({ aoMontarRequisicao: () => ({ Authorization: `Bearer ${token()}` }) });
 *
 * Ou, melhor ainda, passe o fetch/cliente de vocês:
 *
 *     configurarApi({ fetch: meuFetchAutenticado });
 */

// ── Tipos (espelho de corretor/esquemas.py) ─────────────────────────────────

export type Nivel = "alto" | "medio" | "baixo";

export interface Competencia {
  numero: number;
  titulo: string;
  nota: number;
  nivel: Nivel;
  feedback: string;
}

export interface TrechoCopiado {
  texto: string;
  palavras: number;
}

export interface Plagio {
  percentual_copiado: number;
  palavras_copiadas: number;
  total_palavras: number;
  trechos_copiados: TrechoCopiado[];
}

export interface Correcao {
  nota_total: number;
  competencias: Competencia[];
  melhorias: string[];
  plagio: Plagio;
}

export interface Tema {
  id: number;
  titulo: string;
  textos_apoio: string;
}

export interface StatusUso {
  usuario_id: number;
  nome: string;
  professor: boolean;
  tem_chave_propria: boolean;
  redacoes_usadas: number;
  /** `null` quando o uso é ilimitado (chave própria ou limite desligado). */
  redacoes_limite: number | null;
  redacoes_restantes: number | null;
}

export interface ItemHistorico {
  id: number;
  tema: string | null;
  criado_em: string;
  plagio_percentual: number;
  nota_total: number | null;
}

export interface PedidoCorrecao {
  redacao: string;
  tema?: string;
  tema_id?: number;
  textos_apoio?: string;
}

// ── Configuração ────────────────────────────────────────────────────────────

interface OpcoesApi {
  baseUrl: string;
  fetch: typeof fetch;
  aoMontarRequisicao?: () => Record<string, string>;
}

const opcoes: OpcoesApi = {
  baseUrl: "/api/redacao",
  fetch: (...args) => globalThis.fetch(...args),
};

export function configurarApi(parcial: Partial<OpcoesApi>): void {
  Object.assign(opcoes, parcial);
}

/** Erro de API com o status HTTP preservado — 429 significa limite atingido. */
export class ErroApi extends Error {
  constructor(
    readonly status: number,
    mensagem: string,
  ) {
    super(mensagem);
    this.name = "ErroApi";
  }

  get limiteAtingido(): boolean {
    return this.status === 429;
  }
}

async function requisitar<T>(
  caminho: string,
  init: RequestInit = {},
): Promise<T> {
  const resposta = await opcoes.fetch(`${opcoes.baseUrl}${caminho}`, {
    credentials: "include",
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...opcoes.aoMontarRequisicao?.(),
      ...init.headers,
    },
  });

  if (!resposta.ok) {
    // FastAPI devolve {"detail": "..."} nos HTTPException.
    let detalhe = `Erro ${resposta.status}`;
    try {
      const corpo = await resposta.json();
      if (typeof corpo?.detail === "string") detalhe = corpo.detail;
    } catch {
      /* resposta sem corpo JSON — mantém a mensagem padrão */
    }
    throw new ErroApi(resposta.status, detalhe);
  }

  if (resposta.status === 204) return undefined as T;
  return (await resposta.json()) as T;
}

// ── Chamadas ────────────────────────────────────────────────────────────────

export const api = {
  status: () => requisitar<StatusUso>("/status"),

  temas: () => requisitar<Tema[]>("/temas"),

  criarTema: (dados: { titulo: string; textos_apoio: string }) =>
    requisitar<Tema>("/temas", { method: "POST", body: JSON.stringify(dados) }),

  atualizarTema: (id: number, dados: { titulo: string; textos_apoio: string }) =>
    requisitar<Tema>(`/temas/${id}`, {
      method: "PUT",
      body: JSON.stringify(dados),
    }),

  removerTema: (id: number) =>
    requisitar<{ mensagem: string }>(`/temas/${id}`, { method: "DELETE" }),

  corrigir: (pedido: PedidoCorrecao) =>
    requisitar<Correcao>("/corrigir", {
      method: "POST",
      body: JSON.stringify(pedido),
    }),

  historico: () => requisitar<ItemHistorico[]>("/historico"),

  salvarChave: (api_key: string) =>
    requisitar<{ mensagem: string }>("/chave", {
      method: "POST",
      body: JSON.stringify({ api_key }),
    }),

  removerChave: () =>
    requisitar<{ mensagem: string }>("/chave", { method: "DELETE" }),
};

// ── Links úteis, usados nas telas de limite ─────────────────────────────────

export const URL_CREDITOS = "https://console.anthropic.com/settings/billing";
export const URL_CHAVES = "https://console.anthropic.com/settings/keys";
