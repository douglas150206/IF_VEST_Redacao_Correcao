/** Painel de detecção de cópia dos textos de apoio. */

import type { Plagio } from "../api";
import { Icone, type NomeIcone } from "./Icone";

interface Props {
  plagio: Plagio;
}

export function PainelPlagio({ plagio }: Props) {
  if (!plagio.total_palavras) return null;

  const pct = plagio.percentual_copiado;
  let classe: string;
  let icone: NomeIcone;
  let titulo: string;
  let descricao: string;

  if (pct === 0) {
    classe = "plagio-ok";
    icone = "check";
    titulo = "Sem cópia dos textos de apoio";
    descricao =
      "Nenhum trecho copiado literalmente dos textos de apoio foi detectado — o texto é de autoria própria.";
  } else if (pct < 25) {
    classe = "plagio-warn";
    icone = "alerta";
    titulo = `Cópia dos textos de apoio: ${pct}%`;
    descricao =
      "Foram encontrados trechos copiados dos textos de apoio. Pela regra do ENEM, esses trechos não contam como produção própria e a nota já reflete essa penalização. Reescreva-os com suas palavras.";
  } else {
    classe = "plagio-danger";
    icone = "bloqueio";
    titulo = `Cópia dos textos de apoio: ${pct}%`;
    descricao =
      "Grande parte da redação é cópia literal dos textos de apoio. No ENEM isso reduz drasticamente a nota, e a cópia total zera a redação. Reescreva os trechos destacados com argumentação própria.";
  }

  const trechos = plagio.trechos_copiados.slice(0, 6);

  return (
    <section className={`plagio-card ${classe}`}>
      <div className="plagio-title">
        <Icone nome={icone} className="ico-md" />
        {titulo}
      </div>
      <div className="plagio-bar-bg">
        <div className="plagio-bar-fill" style={{ width: `${pct}%` }} />
      </div>
      <p className="plagio-sub">{descricao}</p>
      {trechos.length > 0 && (
        <>
          <div className="plagio-trechos-titulo">Trechos copiados detectados:</div>
          {trechos.map((t, i) => (
            <div key={i} className="plagio-trecho">
              “{t.texto}”
            </div>
          ))}
        </>
      )}
    </section>
  );
}
