/** Nota final, as cinco competências e as sugestões de melhoria. */

import type { Correcao, Nivel } from "../api";
import { Icone } from "./Icone";
import { PainelPlagio } from "./PainelPlagio";

const ROTULO_NIVEL: Record<Nivel, string> = {
  alto: "Alto",
  medio: "Médio",
  baixo: "Baixo",
};

function nivelGeral(nota: number): Nivel {
  if (nota >= 700) return "alto";
  if (nota >= 400) return "medio";
  return "baixo";
}

const ROTULO_GERAL: Record<Nivel, string> = {
  alto: "Desempenho alto",
  medio: "Desempenho médio",
  baixo: "Desempenho baixo",
};

interface Props {
  correcao: Correcao;
}

export function ResultadoCorrecao({ correcao }: Props) {
  const geral = nivelGeral(correcao.nota_total);

  return (
    <section className="results">
      <PainelPlagio plagio={correcao.plagio} />

      <div className="nota-total-card">
        <div>
          <div className="nota-rotulo">Nota final estimada</div>
          <div className="nota-linha">
            <div className="nota-value">{correcao.nota_total}</div>
            <div className="nota-max">/ 1000</div>
          </div>
        </div>
        <span className={`nivel-pill nivel-${geral}`}>{ROTULO_GERAL[geral]}</span>
      </div>

      <div className="comp-grid">
        {correcao.competencias.map((c) => (
          <article key={c.numero} className="comp-card">
            <div className="comp-header">
              <h3 className="comp-title">
                Competência {c.numero} — {c.titulo}
              </h3>
              <div className="comp-right">
                <div className="comp-nota">
                  {c.nota}
                  <span> / 200</span>
                </div>
                <span className={`nivel-pill nivel-${c.nivel}`}>
                  {ROTULO_NIVEL[c.nivel]}
                </span>
              </div>
            </div>
            <div className="progress-bg">
              <div
                className="progress-fill"
                style={{ width: `${(c.nota / 200) * 100}%` }}
              />
            </div>
            <p className="comp-feedback">{c.feedback}</p>
          </article>
        ))}
      </div>

      {correcao.melhorias.length > 0 && (
        <>
          <div className="divider" />
          <div>
            <h3 className="melhorias-title">
              <Icone nome="melhoria" className="ico-md" />
              Sugestões de melhoria
            </h3>
            {correcao.melhorias.map((m, i) => (
              <div key={i} className="melhoria-item">
                <div className="melhoria-dot" />
                <div className="melhoria-text">{m}</div>
              </div>
            ))}
          </div>
        </>
      )}

      <p className="nota-rodape">
        Avaliação gerada automaticamente por inteligência artificial, com base nos
        critérios das cinco competências do ENEM. A nota é uma estimativa de estudo
        e não substitui a correção oficial nem a avaliação do professor.
      </p>
    </section>
  );
}
