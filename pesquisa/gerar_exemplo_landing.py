"""Gera uma correção real para exibir na landing page do projeto.

A página mostra um exemplo de correção. Em vez de inventar notas e devolutiva,
este script roda uma correção de verdade sobre uma redação do corpus e salva
tudo — inclusive o texto com os trechos copiados marcados palavra a palavra.

Uso:  python gerar_exemplo_landing.py [ID]   (padrão: R5, com 29% de cópia)
"""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path

import anthropic

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "porte_fastapi"))

from corretor.config import config  # noqa: E402,F401  (carrega o .env)
from corretor.corretor import PROMPT_SISTEMA, montar_prompt  # noqa: E402
from corretor.esquemas import CorrecaoIA  # noqa: E402
from corretor.plagio import TAMANHO_SHINGLE_PADRAO, detectar_copia, tokenizar  # noqa: E402


def marcar_copia_em_html(redacao: str, apoio: str) -> str:
    """Devolve o texto da redação com <mark> nas palavras copiadas.

    Repete a marcação token a token do detector porque `detectar_copia` entrega
    os trechos já agrupados, e para destacar no texto original é preciso saber
    quais palavras individuais foram marcadas.
    """
    n = TAMANHO_SHINGLE_PADRAO
    apoio_tokens = tokenizar(apoio)
    tokens = tokenizar(redacao)
    if len(apoio_tokens) < n or len(tokens) < n:
        return html.escape(redacao)

    shingles = {
        " ".join(t.norm for t in apoio_tokens[i : i + n])
        for i in range(len(apoio_tokens) - n + 1)
    }
    copiado = [False] * len(tokens)
    for i in range(len(tokens) - n + 1):
        if " ".join(t.norm for t in tokens[i : i + n]) in shingles:
            for j in range(i, i + n):
                copiado[j] = True

    # Monta palavra a palavra, abrindo e fechando <mark> nas transições. As tags
    # entram coladas na palavra para não gerar espaço duplo na renderização.
    partes: list[str] = []
    dentro = False
    for token, marcada in zip(tokens, copiado):
        palavra = html.escape(token.original)
        if marcada and not dentro:
            palavra = "<mark>" + palavra
            dentro = True
        elif not marcada and dentro:
            partes[-1] += "</mark>"
            dentro = False
        partes.append(palavra)
    if dentro:
        partes[-1] += "</mark>"
    return " ".join(partes)


def main() -> int:
    alvo = sys.argv[1] if len(sys.argv) > 1 else "R5"
    corpus = json.loads((AQUI / "corpus" / "redacoes.json").read_text(encoding="utf-8"))
    tema = corpus["tema"]
    redacao = next((r for r in corpus["redacoes"] if r["id"] == alvo), None)
    if redacao is None:
        raise SystemExit(f"redação {alvo} não encontrada no corpus")

    plagio = detectar_copia(redacao["texto"], tema["textos_apoio"])
    print(f"{alvo}: {plagio.percentual_copiado}% copiado "
          f"({plagio.palavras_copiadas}/{plagio.total_palavras} palavras)")

    destino = AQUI / "resultados" / "exemplo_landing.json"

    # Refaz só a marcação do texto, reaproveitando a correção já salva. Serve
    # para ajustar a apresentação sem pagar outra chamada à API.
    if "--sem-api" in sys.argv:
        if not destino.is_file():
            raise SystemExit("não há exemplo salvo para reaproveitar")
        salvo = json.loads(destino.read_text(encoding="utf-8"))
        salvo["texto_marcado_html"] = marcar_copia_em_html(
            redacao["texto"], tema["textos_apoio"])
        destino.write_text(json.dumps(salvo, ensure_ascii=False, indent=2),
                           encoding="utf-8")
        print("marcação regenerada sem chamar a API.")
        return 0

    print("chamando a API (uma correção)...")
    cliente = anthropic.Anthropic()
    resposta = cliente.messages.parse(
        model=config.modelo,
        max_tokens=config.max_tokens,
        system=PROMPT_SISTEMA,
        messages=[{"role": "user", "content": montar_prompt(
            redacao["texto"], tema["titulo"], tema["textos_apoio"], plagio)}],
        output_format=CorrecaoIA,
        output_config={"effort": config.esforco},
    )
    correcao: CorrecaoIA = resposta.parsed_output
    if correcao is None:
        raise SystemExit(f"correção não concluída: {resposta.stop_reason}")

    saida = {
        "redacao_id": alvo,
        "modelo": config.modelo,
        "tema": tema["titulo"],
        "texto_original": redacao["texto"],
        "texto_marcado_html": marcar_copia_em_html(redacao["texto"], tema["textos_apoio"]),
        "plagio": {
            "percentual": plagio.percentual_copiado,
            "palavras_copiadas": plagio.palavras_copiadas,
            "total_palavras": plagio.total_palavras,
            "trechos": [{"texto": t.texto, "palavras": t.palavras}
                        for t in plagio.trechos_copiados],
        },
        "correcao": {
            "nota_total": correcao.nota_total,
            "competencias": [
                {"numero": c.numero, "titulo": c.titulo, "nota": c.nota,
                 "nivel": c.nivel, "feedback": c.feedback}
                for c in sorted(correcao.competencias, key=lambda x: x.numero)
            ],
            "melhorias": correcao.melhorias,
        },
        "tokens": {"entrada": resposta.usage.input_tokens,
                   "saida": resposta.usage.output_tokens},
    }

    destino.write_text(json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nnota final: {correcao.nota_total}")
    for c in saida["correcao"]["competencias"]:
        print(f"  C{c['numero']}: {c['nota']:>3}  {c['feedback'][:88]}")
    print(f"\nsalvo em {destino.relative_to(AQUI.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
