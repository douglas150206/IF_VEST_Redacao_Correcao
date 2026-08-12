/** Modal base: overlay, foco inicial, fechar no Esc e no clique fora. */

import { useEffect, useRef, type ReactNode } from "react";

interface Props {
  aberto: boolean;
  titulo: ReactNode;
  largo?: boolean;
  aoFechar: () => void;
  children: ReactNode;
  /** Rodapé com os botões de ação. */
  acoes?: ReactNode;
}

export function Modal({ aberto, titulo, largo, aoFechar, children, acoes }: Props) {
  const caixa = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!aberto) return;
    const aoTeclar = (e: KeyboardEvent) => {
      if (e.key === "Escape") aoFechar();
    };
    document.addEventListener("keydown", aoTeclar);
    caixa.current?.focus();
    return () => document.removeEventListener("keydown", aoTeclar);
  }, [aberto, aoFechar]);

  if (!aberto) return null;

  return (
    <div
      className="corretor-modal-overlay"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) aoFechar();
      }}
    >
      <div
        ref={caixa}
        className={`corretor-modal${largo ? " largo" : ""}`}
        role="dialog"
        aria-modal="true"
        tabIndex={-1}
      >
        <h3>{titulo}</h3>
        {children}
        {acoes && <div className="modal-btns">{acoes}</div>}
      </div>
    </div>
  );
}
