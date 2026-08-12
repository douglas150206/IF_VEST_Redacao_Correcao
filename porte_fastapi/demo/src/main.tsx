/**
 * App de demonstração — serve para ver os componentes funcionando antes de
 * integrar ao IFvest. Não faz parte do que vai para produção.
 *
 * O seletor de papel no topo existe só aqui: ele manda o header `X-Papel`, que
 * o provedor falso do `exemplo_app.py` lê. No IFvest o papel virá do perfil.
 */

import { StrictMode, useState } from "react";
import { createRoot } from "react-dom/client";

import { configurarApi } from "../../web/api";
import { CorretorDeRedacao } from "../../web/CorretorDeRedacao";

import "../../web/corretor.css";
import "./demo.css";

let papel: "aluno" | "professor" = "aluno";

configurarApi({
  aoMontarRequisicao: (): Record<string, string> =>
    papel === "professor" ? { "X-Papel": "professor" } : {},
});

function Demo() {
  const [atual, setAtual] = useState<"aluno" | "professor">("aluno");
  // `key` força a remontagem quando o papel muda, para recarregar o status.
  const trocar = (novo: "aluno" | "professor") => {
    papel = novo;
    setAtual(novo);
  };

  return (
    <>
      {/* Simula o cabeçalho que o layout do IFvest vai fornecer. O componente
          do corretor não desenha isto de propósito — senão haveria dois. */}
      <header className="cabecalho-simulado">
        <img src="/logo-ifsp.png" alt="Instituto Federal de São Paulo" />
      </header>

      <div className="barra-demo">
        <strong>Demonstração</strong>
        <span>entrar como:</span>
        <button
          className={atual === "aluno" ? "ativo" : ""}
          onClick={() => trocar("aluno")}
        >
          Aluno
        </button>
        <button
          className={atual === "professor" ? "ativo" : ""}
          onClick={() => trocar("professor")}
        >
          Professor
        </button>
        <span className="obs">
          no IFvest o papel vem do login — esta barra não existe em produção
        </span>
      </div>
      <main className="area-demo">
        <CorretorDeRedacao key={atual} />
      </main>
    </>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <Demo />
  </StrictMode>,
);
