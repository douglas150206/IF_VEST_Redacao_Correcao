"""Correção competência por competência, cada uma com seu procedimento.

Por que tentar isto
-------------------
Hoje o sistema julga as cinco competências numa única chamada. A medição no
simulado mostra que isso funciona para umas e falha completamente para outras:

    C3  QWK 0,750   |   C2  0,490   |   C1  0,333   |   C4  0,000   |   C5  0,000

C4 e C5 em zero não é concordância baixa, é concordância nenhuma: o sistema não
está avaliando o que as corretoras avaliam.

Duas hipóteses, e este experimento testa as duas juntas:

1. **Carga.** Julgar cinco critérios diferentes sobre o mesmo texto numa
   passada só divide a atenção. Uma chamada por competência deixa o modelo
   examinar o texto inteiro sob um critério de cada vez.

2. **Procedimento em vez de impressão.** Esta é a aposta principal. A grade do
   INEP não pede impressão geral: pede contagem. A Competência V, em especial,
   define o nível *como* o número de elementos válidos da proposta. Se o modelo
   enumerar ação, agente, modo, efeito e detalhamento um a um antes de pontuar,
   a nota deixa de ser julgamento e vira aritmética. O mesmo vale, em menor
   grau, para C1 (contar desvios) e C4 (listar conectivos e repetições).

A tentativa anterior com a grade do INEP falhou, mas aplicava os cinco
critérios de uma vez e pedia rigor genérico. Aqui cada chamada recebe só os
descritores da sua competência e um roteiro do que examinar antes de decidir.

Fica declarado que o experimento muda duas coisas ao mesmo tempo (uma chamada
por competência e procedimento explícito), então um resultado positivo não diz
qual das duas causou. Com n = 8 não há amostra para separar; se funcionar, a
separação fica para depois.

Uso:
    python experimento_por_competencia.py --listar
    python experimento_por_competencia.py
    python experimento_por_competencia.py --competencias 4 5
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import anthropic
from pydantic import BaseModel, Field

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "porte_fastapi"))
sys.path.insert(0, str(AQUI))

from corretor.config import config  # noqa: E402,F401
from experimento_simulado import (  # noqa: E402
    ESFORCO, NIVEIS, TEMA, carregar_notas, carregar_transcricoes, qwk,
)

MODELO_PADRAO = "claude-opus-5"
MAX_TOKENS = 4000

NOMES = {
    1: "domínio da modalidade escrita formal",
    2: "compreensão da proposta e repertório",
    3: "seleção e organização de argumentos",
    4: "mecanismos linguísticos de coesão",
    5: "proposta de intervenção",
}


class NotaCompetencia(BaseModel):
    """Resposta de uma chamada: uma competência, com o exame que a sustenta."""

    exame: str = Field(
        description="O que você encontrou no texto ao aplicar o roteiro, "
                    "citando trechos concretos. É aqui que a contagem acontece."
    )
    nivel: int = Field(description="Nível de 0 a 5.")
    nota: int = Field(description="Nota: 0, 40, 80, 120, 160 ou 200.")
    justificativa: str = Field(description="2 a 3 frases ligando o exame ao nível.")


# ── Um prompt por competência: descritores da grade + roteiro de exame ───────

BASE = """\
Você é corretor de redações do ENEM e vai avaliar **uma única competência**.

Ignore as outras quatro. Não pondere a qualidade geral do texto: uma redação
excelente pode ir mal nesta competência e uma redação fraca pode ir bem.

Nível e pontos: 0=0 · 1=40 · 2=80 · 3=120 · 4=160 · 5=200.

Faça o exame pedido no roteiro **antes** de escolher o nível, e escreva o que
encontrou no campo `exame`. O nível tem que decorrer do que você contou, não de
impressão geral. Em dúvida entre dois níveis, atribua o menor.

"""

PROMPTS = {
    1: BASE + """\
## COMPETÊNCIA I — domínio da modalidade escrita formal

| Nível | Descritor |
|---|---|
| 0 | Estrutura sintática inexistente, independentemente da quantidade de desvios |
| 1 | Estrutura sintática deficitária COM muitos desvios |
| 2 | Estrutura sintática deficitária OU muitos desvios |
| 3 | Estrutura sintática regular E alguns desvios |
| 4 | Estrutura sintática boa E poucos desvios |
| 5 | Estrutura sintática excelente (no máximo uma falha) E no máximo dois desvios |

São duas dimensões independentes, e o nível depende das duas: **estrutura
sintática** (períodos completos, bem construídos, sem truncamento ou
justaposição indevida) e **desvios** (ortografia, acentuação, concordância,
regência, pontuação, uso de maiúsculas).

### Roteiro

1. Liste os desvios que encontrar, com o trecho de cada um. Conte-os.
2. Avalie a estrutura sintática: há períodos truncados, mal construídos ou
   incompreensíveis? Quantos?
3. Só então escolha o nível, dizendo quantos desvios e que estrutura justificam.

Atenção: "poucos" e "muitos" são relativos à extensão do texto. Numa redação de
30 linhas, dois ou três desvios é pouco; quinze é muito.""",

    2: BASE + """\
## COMPETÊNCIA II — compreensão da proposta e repertório

Esta competência não admite nível 0: redação que receberia 0 é fuga ao tema e
não é corrigida.

| Nível | Descritor |
|---|---|
| 1 | Tangência ao tema OU aglomerado caótico de palavras OU traços constantes de outro tipo textual |
| 2 | Abordagem completa E (2 partes do texto OU 3 partes com 2 embrionárias OU conclusão finalizada por ideia incompleta) |
| 3 | Abordagem completa E 3 partes (1 pode ser embrionária) E repertório baseado nos motivadores E/OU não legitimado E/OU legitimado mas não pertinente |
| 4 | Abordagem completa E 3 partes (nenhuma embrionária) E repertório legitimado e pertinente, SEM uso produtivo |
| 5 | Abordagem completa E 3 partes (nenhuma embrionária) E repertório legitimado e pertinente, COM uso produtivo |

As três partes são introdução, desenvolvimento e conclusão. "Embrionária"
significa presente mas sem desenvolvimento real. Repertório **legitimado** é
fonte identificável (obra, autor, lei, dado, fato histórico); **pertinente** é
ligado ao tema; **produtivo** é usado para sustentar o argumento, não apenas
mencionado.

### Roteiro

1. O texto aborda o tema completamente, tangencia, ou foge?
2. Identifique as três partes. Quais existem? Alguma é embrionária?
3. Liste os repertórios citados. Para cada um: é legitimado? É pertinente ao
   tema? É usado produtivamente ou só mencionado?
4. Escolha o nível a partir das três respostas.

**Teto obrigatório:** corpo do texto com até 8 linhas, ou mais de 8 linhas sem
que se reconheçam as 3 partes, não passa do nível 3.""",

    3: BASE + """\
## COMPETÊNCIA III — seleção e organização de argumentos

| Nível | Descritor |
|---|---|
| 0 | Aglomerado caótico de palavras |
| 1 | Projeto de texto sem foco temático ou com foco distorcido |
| 2 | Projeto com muitas falhas E sem desenvolvimento, ou desenvolvimento de apenas uma informação |
| 3 | Projeto com algumas falhas E desenvolvimento com algumas lacunas |
| 4 | Projeto com poucas falhas E desenvolvimento com poucas lacunas |
| 5 | Projeto estratégico E desenvolvimento em todo o texto (deslizes pontuais admitidos) |

**Projeto de texto** é o plano que se enxerga por trás da redação: o que a
introdução anuncia, o que cada parágrafo desenvolve, como a conclusão fecha.
**Desenvolvimento** é cada informação ou argumento ser elaborado, não apenas
afirmado.

### Roteiro

1. O que a introdução anuncia que o texto vai discutir? Transcreva.
2. Para cada parágrafo de desenvolvimento: ele trata de um dos pontos
   anunciados? O argumento é elaborado ou só afirmado?
3. Algum ponto anunciado ficou sem desenvolvimento? Algum parágrafo desenvolve
   coisa que não foi anunciada?
4. A conclusão fecha o que foi aberto?
5. Escolha o nível a partir dessas lacunas.

**Tetos obrigatórios:** texto tangente não passa do nível 1; contradição grave
não passa do nível 2.""",

    4: BASE + """\
## COMPETÊNCIA IV — mecanismos linguísticos de coesão

| Nível | Descritor |
|---|---|
| 0 | Ausência de articulação: palavras E/OU períodos desconexos em todo o texto |
| 1 | Presença rara de elementos coesivos E/OU excessivas repetições E/OU excessivas inadequações |
| 2 | Presença pontual E/OU muitas repetições E/OU muitas inadequações |
| 3 | Presença regular E/OU algumas repetições E/OU algumas inadequações |
| 4 | Presença constante E/OU poucas repetições E/OU poucas inadequações |
| 5 | Presença expressiva E repetições raras ou ausentes E sem inadequação |

Contam tanto a coesão **interparágrafos** (o conectivo que abre cada parágrafo
e o liga ao anterior) quanto a **intraparágrafos** (conectivos, pronomes,
sinônimos e elipses dentro do parágrafo). **Inadequação** é conectivo usado com
sentido errado — "portanto" onde não há conclusão, "entretanto" onde não há
oposição.

### Roteiro

1. Liste o elemento coesivo que abre cada parágrafo, do segundo em diante. Se
   algum parágrafo começa sem conectivo, registre.
2. Dentro dos parágrafos, liste os elementos coesivos que encontrar.
3. Liste as repetições de palavra ou conectivo que chamem atenção.
4. Liste as inadequações: conectivo cujo sentido não corresponde à relação
   entre as ideias.
5. Conte: quantos elementos distintos, quantas repetições, quantas
   inadequações. Escolha o nível a partir dessas contagens.

**Teto obrigatório:** texto em monobloco, sem divisão em parágrafos, não passa
do nível 2.""",

    5: BASE + """\
## COMPETÊNCIA V — proposta de intervenção

Aqui o nível **é** o número de elementos válidos da proposta. Não é julgamento
de qualidade: é contagem.

Os cinco elementos:

- **Ação** — o que será feito. Sem ação, não há proposta.
- **Agente** — quem fará. Precisa ser identificável e capaz de executar.
- **Modo ou meio** — como será feito.
- **Efeito ou finalidade** — para quê, qual resultado esperado.
- **Detalhamento** — explicação adicional de um dos quatro anteriores, que vá
  além de repeti-lo.

| Nível | Descritor |
|---|---|
| 0 | Ausência de proposta OU proposta que desrespeita os direitos humanos OU proposta não relacionada ao assunto |
| 1 | Tangenciamento do tema OU apenas elementos nulos OU 1 elemento válido |
| 2 | 2 elementos válidos |
| 3 | 3 elementos válidos |
| 4 | 4 elementos válidos |
| 5 | 5 elementos válidos |

### Roteiro

1. Localize a proposta de intervenção. Transcreva o trecho. **Se o texto não
   tiver proposta, o nível é 0** — não procure uma proposta implícita.
2. Para cada um dos cinco elementos, diga se está presente e transcreva o
   trecho que o realiza. Se não estiver, diga que não está.
3. Conte os presentes. O nível é esse número.

**Tetos obrigatórios:** estrutura condicional ("se o governo fizesse...") com 2
ou mais elementos não passa do nível 2; proposta sem o elemento AÇÃO não passa
do nível 2.""",
}


def avaliar(cliente, modelo: str, redacao: str, comp: int) -> NotaCompetencia:
    entrada = f"Tema: {TEMA}\n\nRedação:\n{redacao.strip()}"
    resposta = cliente.messages.parse(
        model=modelo,
        max_tokens=MAX_TOKENS,
        system=[{"type": "text", "text": PROMPTS[comp],
                 "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": entrada}],
        output_format=NotaCompetencia,
        output_config={"effort": ESFORCO},
    )
    if resposta.parsed_output is None:
        raise RuntimeError(f"stop_reason={resposta.stop_reason}")
    return resposta.parsed_output


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--modelo", default=MODELO_PADRAO)
    ap.add_argument("--competencias", nargs="+", type=int, default=[1, 2, 3, 4, 5])
    ap.add_argument("--listar", action="store_true")
    args = ap.parse_args()

    transcricoes = carregar_transcricoes()
    notas = carregar_notas()
    casadas = sorted(set(transcricoes) & set(notas))
    comps = sorted(set(args.competencias))

    print(f"redações: {len(casadas)}   competências: {comps}")
    print(f"chamadas à API: {len(casadas) * len(comps)}")
    if args.listar:
        print("\n(--listar: nada foi chamado)")
        return 0
    print()

    cliente = anthropic.Anthropic()
    resultados = []
    total = len(casadas) * len(comps)
    feito = 0

    for p in casadas:
        linha = {"prontuario": p, "humano": notas[p]["final"],
                 "humano_A": notas[p]["A"], "humano_B": notas[p]["B"],
                 "sistema": {}, "exame": {}}
        for c in comps:
            feito += 1
            print(f"  [{feito}/{total}] {p} C{c}", end="", flush=True)
            inicio = time.monotonic()
            try:
                r = avaliar(cliente, args.modelo, transcricoes[p], c)
            except Exception as erro:  # noqa: BLE001
                print(f"  ERRO: {erro}")
                continue
            humano = notas[p]["final"][c - 1]
            print(f"  → {r.nota:>3}  (humano {humano:>5.0f})  "
                  f"{round(time.monotonic() - inicio)}s")
            linha["sistema"][f"C{c}"] = r.nota
            linha["exame"][f"C{c}"] = r.exame
        resultados.append(linha)

    print("\n" + "=" * 66)
    print(f"CORREÇÃO POR COMPETÊNCIA  (n = {len(resultados)})")
    print("=" * 66)

    # Referência: a medição anterior, com as cinco numa chamada só.
    antes = {"C1": (0.333, 25.0), "C2": (0.386, 52.5), "C3": (0.750, 32.5),
             "C4": (0.000, 20.0), "C5": (0.370, 45.0)}

    print(f"\n{'comp.':<7}{'QWK antes':>11}{'QWK agora':>11}"
          f"{'erro antes':>12}{'erro agora':>12}")
    print("-" * 53)
    relatorio = {}
    for c in comps:
        chave = f"C{c}"
        pares = [(r["sistema"][chave], r["humano"][c - 1])
                 for r in resultados if chave in r["sistema"]]
        if not pares:
            continue
        s = [int(x) for x, _ in pares]
        h = [int(y) for _, y in pares]
        k = qwk(s, h, NIVEIS)
        erro = statistics.mean(abs(x - y) for x, y in zip(s, h))
        vies = statistics.mean(x - y for x, y in zip(s, h))
        relatorio[chave] = {"qwk": round(k, 3) if k is not None else None,
                            "erro_absoluto": round(erro, 1),
                            "vies": round(vies, 1), "n": len(pares)}
        ka, ea = antes[chave]
        seta = ""
        if k is not None:
            seta = "  melhor" if k > ka + 0.05 else ("  pior" if k < ka - 0.05 else "")
        print(f"{chave:<7}{ka:>11.3f}{(k if k is not None else 0):>11.3f}"
              f"{ea:>12.1f}{erro:>12.1f}{seta}")

    if len(comps) == 5:
        totais_s = [sum(r["sistema"][f"C{c}"] for c in comps)
                    for r in resultados if len(r["sistema"]) == 5]
        totais_h = [sum(r["humano"]) for r in resultados if len(r["sistema"]) == 5]
        if totais_s:
            difs = [a - b for a, b in zip(totais_s, totais_h)]
            print(f"\nNota total: viés {statistics.mean(difs):+.1f}   "
                  f"erro absoluto {statistics.mean(abs(d) for d in difs):.1f}")
            print("  (chamada única: viés +45,0   erro absoluto 125,0)")
            print(f"\n  menor nota atribuída: {min(totais_s)}")
            print("  (chamada única: 560 · ancoragem local: 480)")
            print(f"\n{'prontuário':<12}{'humano':>8}{'sistema':>9}{'dif':>7}")
            for r, ts, th in zip(resultados, totais_s, totais_h):
                print(f"{r['prontuario']:<12}{th:>8}{ts:>9}{ts - th:>+7}")

    saida = AQUI / "resultados"
    saida.mkdir(exist_ok=True)
    carimbo = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    arquivo = saida / f"por_competencia_{carimbo}.json"
    arquivo.write_text(json.dumps({
        "gerado_em": carimbo,
        "metodo": "uma chamada por competência, com roteiro de exame",
        "parametros": {"modelo": args.modelo, "competencias": comps,
                       "max_tokens": MAX_TOKENS, "esforco": ESFORCO},
        "relatorio": relatorio,
        "resultados": resultados,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\ndados salvos em {arquivo.relative_to(AQUI.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
