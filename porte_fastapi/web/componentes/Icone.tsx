/** Ícones em traço, sem dependência externa e sem emoji. */

// `ReactNode` em vez de `JSX.Element` para funcionar tanto no React 18
// (JSX global) quanto no React 19 (JSX exportado do pacote).
import type { ReactNode } from "react";

export type NomeIcone =
  | "info"
  | "alerta"
  | "bloqueio"
  | "check"
  | "chave"
  | "cartao"
  | "caneta"
  | "documento"
  | "melhoria"
  | "chevron";

const DESENHOS: Record<NomeIcone, ReactNode> = {
  info: (
    <>
      <circle cx="12" cy="12" r="9.5" />
      <line x1="12" y1="16.5" x2="12" y2="11" />
      <line x1="12" y1="7.8" x2="12.01" y2="7.8" />
    </>
  ),
  alerta: (
    <>
      <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
      <line x1="12" y1="9.5" x2="12" y2="13.5" />
      <line x1="12" y1="17" x2="12.01" y2="17" />
    </>
  ),
  bloqueio: (
    <>
      <circle cx="12" cy="12" r="9.5" />
      <line x1="5.3" y1="5.3" x2="18.7" y2="18.7" />
    </>
  ),
  check: (
    <>
      <path d="M21.5 11.1V12a9.5 9.5 0 1 1-5.63-8.68" />
      <polyline points="21.5 4.5 12 14.01 9.2 11.2" />
    </>
  ),
  chave: (
    <>
      <circle cx="7.5" cy="15.5" r="4.8" />
      <path d="M11 12 21 2" />
      <path d="m16.5 6.5 3 3 3-3-3-3" />
    </>
  ),
  cartao: (
    <>
      <rect x="2" y="4.5" width="20" height="15" rx="2" />
      <line x1="2" y1="10" x2="22" y2="10" />
      <line x1="6" y1="15" x2="10" y2="15" />
    </>
  ),
  caneta: (
    <>
      <path d="M12 20h9" />
      <path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z" />
    </>
  ),
  documento: (
    <>
      <path d="M14 2.5H6.5a2 2 0 0 0-2 2v15a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2.5 14 8 19.5 8" />
      <line x1="15.5" y1="13" x2="8.5" y2="13" />
      <line x1="15.5" y1="17" x2="8.5" y2="17" />
    </>
  ),
  melhoria: (
    <>
      <polyline points="22.5 6.5 13.5 15.5 8.5 10.5 1.5 17.5" />
      <polyline points="16.5 6.5 22.5 6.5 22.5 12.5" />
    </>
  ),
  chevron: <polyline points="6 9 12 15 18 9" />,
};

interface Props {
  nome: NomeIcone;
  /** `ico` (acompanha o texto) ou `ico-md` (18px, para títulos). */
  className?: string;
}

export function Icone({ nome, className = "ico" }: Props) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
    >
      {DESENHOS[nome]}
    </svg>
  );
}
