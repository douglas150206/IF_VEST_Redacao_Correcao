/** Escolha do tema: do banco (com textos de apoio) ou personalizado. */

import { useState } from "react";

import type { Tema } from "../api";
import { Icone } from "./Icone";

export interface TemaEscolhido {
  tema_id?: number;
  tema?: string;
  textos_apoio?: string;
}

interface Props {
  temas: Tema[];
  valor: string;
  aoMudar: (valor: string) => void;
  tituloCustom: string;
  aoMudarTituloCustom: (v: string) => void;
  apoioCustom: string;
  aoMudarApoioCustom: (v: string) => void;
}

export function SeletorDeTema({
  temas,
  valor,
  aoMudar,
  tituloCustom,
  aoMudarTituloCustom,
  apoioCustom,
  aoMudarApoioCustom,
}: Props) {
  const [apoioAberto, setApoioAberto] = useState(true);
  const temaSelecionado = temas.find((t) => String(t.id) === valor);

  return (
    <div style={{ marginBottom: "1rem" }}>
      <label className="lbl" htmlFor="corretor-tema">
        Tema da redação
      </label>
      <select
        id="corretor-tema"
        className="txt"
        value={valor}
        onChange={(e) => aoMudar(e.target.value)}
      >
        <option value="">— Selecione um tema —</option>
        {temas.map((t) => (
          <option key={t.id} value={String(t.id)}>
            {t.titulo}
          </option>
        ))}
        <option value="custom">Tema personalizado (colar textos de apoio)</option>
      </select>

      {temaSelecionado && (
        <div className="apoio-box">
          <button
            type="button"
            className="apoio-head"
            onClick={() => setApoioAberto((a) => !a)}
            aria-expanded={apoioAberto}
          >
            <span>
              <Icone nome="documento" /> Textos de apoio deste tema
            </span>
            <span>{apoioAberto ? "Ocultar" : "Mostrar"}</span>
          </button>
          {apoioAberto && (
            <div className="apoio-content">{temaSelecionado.textos_apoio}</div>
          )}
        </div>
      )}

      {valor === "custom" && (
        <div style={{ marginTop: 12 }}>
          <input
            className="txt"
            type="text"
            placeholder="Título do tema personalizado"
            value={tituloCustom}
            onChange={(e) => aoMudarTituloCustom(e.target.value)}
            style={{ marginBottom: 10 }}
          />
          <textarea
            className="txt"
            placeholder="Cole aqui os textos de apoio (motivadores) deste tema..."
            value={apoioCustom}
            onChange={(e) => aoMudarApoioCustom(e.target.value)}
            style={{ minHeight: 120 }}
          />
        </div>
      )}

      <p className="hint">
        Os textos de apoio são usados para leitura e para detectar cópia na sua
        redação.
      </p>
    </div>
  );
}

/** Traduz a seleção da tela no corpo esperado por POST /corrigir. */
export function montarTema(
  valor: string,
  tituloCustom: string,
  apoioCustom: string,
): TemaEscolhido {
  if (valor === "custom") {
    return {
      tema: tituloCustom.trim() || undefined,
      textos_apoio: apoioCustom.trim() || undefined,
    };
  }
  if (valor) return { tema_id: Number(valor) };
  return {};
}
