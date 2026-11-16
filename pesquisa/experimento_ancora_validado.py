"""Ancoragem local com conjunto de âncoras separado do de teste.

O que muda em relação à primeira tentativa
-------------------------------------------
O primeiro teste de ancoragem local deu QWK 0,368 -> 0,560 e quebrou o piso,
mas sobre 8 redações e com validação *leave-one-out*: tirando uma, as âncoras
ainda cobriam quase todo o corpus, o que torna a estimativa otimista.

Com o lote 3 transcrito são 17 redações, e dá para fazer a separação de
verdade: cinco viram âncoras fixas e **nunca são avaliadas**; as outras doze
formam o conjunto de teste. Nenhuma redação de teste aparece no prompt que a
corrige.

Os dois braços — prompt de produção e prompt ancorado — rodam sobre as mesmas
doze, na mesma execução, para que a diferença não venha de amostra diferente.

Escolha das âncoras
-------------------
Cinco redações cobrindo a escala, com peso na parte de baixo, que é onde o
sistema falha. Todas saem do grupo de transcrição confiável: as três redações
de letra difícil (marcadas no arquivo de transcrição) ficam fora das âncoras,
porque âncora com erro de leitura ensina a régua errada. Duas delas seguem no
conjunto de teste, onde o erro de transcrição é apenas ruído.

Uso:
    python experimento_ancora_validado.py --listar
    python experimento_ancora_validado.py
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

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "porte_fastapi"))
sys.path.insert(0, str(AQUI))

from corretor.config import config  # noqa: E402,F401
from corretor.corretor import PROMPT_SISTEMA, montar_prompt  # noqa: E402
from corretor.esquemas import CorrecaoIA  # noqa: E402
from corretor.plagio import detectar_copia  # noqa: E402
from experimento_simulado import (  # noqa: E402
    ESFORCO, MAX_TOKENS, NIVEIS, TEMA, carregar_notas, carregar_transcricoes,
    comparar,
)

MODELO_PADRAO = "claude-opus-5"

# Âncoras fixas, identificadas pela nota humana e não pelo prontuário: este
# arquivo é versionado em repositório público, e prontuário é dado pessoal de
# aluno. O empate em 800 é resolvido pela ordem do identificador, de modo que a
# seleção continua determinística e reproduzível.
#
# Duas das cinco estão na faixa baixa, porque é lá que o sistema não desce.
# Nenhuma destas notas coincide com a das três redações de transcrição duvidosa
# (500, 560 e 760), então a seleção por nota já as mantém fora das âncoras —
# âncora com erro de leitura ensinaria a régua errada.
NOTAS_ANCORA = [380, 460, 620, 800, 900]


def escolher_ancoras(notas: dict[str, dict], disponiveis: list[str]) -> list[str]:
    escolhidas = []
    for alvo in NOTAS_ANCORA:
        candidatas = sorted(p for p in disponiveis
                            if p not in escolhidas and notas[p]["total"] == alvo)
        if candidatas:
            escolhidas.append(candidatas[0])
    return escolhidas

NOMES = {
    1: "domínio da norma culta",
    2: "compreensão da proposta",
    3: "seleção e organização de argumentos",
    4: "mecanismos de coesão",
    5: "proposta de intervenção",
}


def montar_bloco(ancoras: list[dict]) -> str:
    blocos = []
    for i, a in enumerate(sorted(ancoras, key=lambda x: x["total"]), start=1):
        notas = "\n".join(
            f"  Competência {n} ({NOMES[n]}): {v}"
            for n, v in enumerate(a["final"], start=1)
        )
        blocos.append(
            f"### Referência {i} — nota final {a['total']}\n\n"
            f"{a['texto']}\n\n"
            f"Notas atribuídas pelas corretoras:\n{notas}\n  Total: {a['total']}"
        )

    return """

## REDAÇÕES DE REFERÊNCIA DESTE CURSINHO

As redações abaixo foram corrigidas pelas mesmas corretoras que avaliam os
alunos daqui, sobre o mesmo tema. Use-as como régua.

Repare especialmente nas notas baixas. A escala vai de 0 a 200 por competência
e **a parte de baixo é usada de verdade**: notas 40 e 80 aparecem em redações
com problemas reais de argumentação ou de proposta. Não existe piso implícito
em 120. Uma redação fraca recebe nota de redação fraca.

Antes de fechar cada competência, compare a redação enviada com estas
referências e pergunte de qual delas ela está mais perto naquela competência.
Quando a sua impressão discordar do que as referências indicam, confie nelas.

""" + "\n\n---\n\n".join(blocos) + """

## FIM DAS REFERÊNCIAS

Volte agora à redação enviada para correção. As acima são régua, não o texto a
avaliar.
"""


def corrigir(cliente, modelo: str, redacao: str, sistema: str) -> dict:
    plagio = detectar_copia(redacao, "")
    prompt = montar_prompt(redacao, TEMA, None, plagio)
    resposta = cliente.messages.parse(
        model=modelo,
        max_tokens=MAX_TOKENS,
        system=[{"type": "text", "text": sistema,
                 "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": prompt}],
        output_format=CorrecaoIA,
        output_config={"effort": ESFORCO},
    )
    if resposta.parsed_output is None:
        raise RuntimeError(f"stop_reason={resposta.stop_reason}")
    c: CorrecaoIA = resposta.parsed_output
    return {
        "nota_total": c.nota_total,
        "competencias": [x.nota for x in sorted(c.competencias, key=lambda y: y.numero)],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--modelo", default=MODELO_PADRAO)
    ap.add_argument("--fonte", choices=("manual", "automatica"), default="manual",
                    help="qual transcrição usar; 'automatica' é a entrada de produção")
    ap.add_argument("--listar", action="store_true")
    args = ap.parse_args()

    transcricoes = carregar_transcricoes(args.fonte)
    notas = carregar_notas()
    casadas = sorted(set(transcricoes) & set(notas))

    selecionadas = escolher_ancoras(notas, casadas)
    if len(selecionadas) < len(NOTAS_ANCORA):
        obtidas = [notas[p]["total"] for p in selecionadas]
        print(f"não achei redação para todas as notas-âncora {NOTAS_ANCORA}; "
              f"obtive {obtidas}")
        return 1

    ancoras = [{"prontuario": p, "texto": transcricoes[p], **notas[p]}
               for p in selecionadas]
    teste = [p for p in casadas if p not in selecionadas]

    print(f"corpus: {len(casadas)} redações   transcrição: {args.fonte}")
    print(f"\nâncoras ({len(ancoras)}, nunca avaliadas):")
    for a in sorted(ancoras, key=lambda x: x["total"]):
        print(f"  {a['prontuario']}  {a['total']:>4}  {a['final']}")
    print(f"\nteste ({len(teste)}):")
    for p in sorted(teste, key=lambda x: notas[x]["total"]):
        print(f"  {p}  {notas[p]['total']:>4}")

    if args.listar:
        print("\n(--listar: nada foi chamado)")
        return 0

    sistemas = {"atual": PROMPT_SISTEMA,
                "ancorado": PROMPT_SISTEMA + montar_bloco(ancoras)}
    print(f"\nchamadas à API: {len(teste) * len(sistemas)}\n")

    cliente = anthropic.Anthropic()
    saidas: dict[str, list[dict]] = {k: [] for k in sistemas}
    total = len(teste) * len(sistemas)
    feito = 0

    for p in sorted(teste, key=lambda x: notas[x]["total"]):
        n = notas[p]
        for nome, sistema in sistemas.items():
            feito += 1
            print(f"  [{feito}/{total}] {p} {nome:<9} humano {n['total']:>4}",
                  end="", flush=True)
            inicio = time.monotonic()
            try:
                s = corrigir(cliente, args.modelo, transcricoes[p], sistema)
            except Exception as erro:  # noqa: BLE001
                print(f"  ERRO: {erro}")
                continue
            d = s["nota_total"] - n["total"]
            print(f"  → {s['nota_total']:>4}  ({d:+})  {round(time.monotonic()-inicio)}s")
            saidas[nome].append({
                "prontuario": p,
                "sistema_total": s["nota_total"],
                "sistema_comp": s["competencias"],
                "final": n["final"], "A": n["A"], "B": n["B"],
                "humano_total": n["total"],
            })

    print("\n" + "=" * 70)
    print(f"ANCORAGEM VALIDADA — teste disjunto das âncoras  (n = {len(teste)})")
    print("=" * 70)

    relatorio = {}
    for nome, res in saidas.items():
        if not res:
            continue
        relatorio[nome] = {ref: comparar(res, ref) for ref in ("final", "A", "B")}

    # Com poucos pares o QWK fica indefinido (variância zero numa das escalas).
    # Formatar None quebra, então o valor ausente vira traço.
    def num(v, casas=3):
        return "—" if v is None else f"{v:.{casas}f}"

    print(f"\n{'':<12}{'n':>4}{'QWK final':>11}{'QWK A':>9}{'QWK B':>9}"
          f"{'viés':>9}{'erro abs':>11}{'mín':>7}")
    print("-" * 72)
    for nome, res in saidas.items():
        if not res:
            continue
        r = relatorio[nome]
        menor = min(x["sistema_total"] for x in res)
        print(f"{nome:<12}{len(res):>4}{num(r['final']['qwk_medio']):>11}"
              f"{num(r['A']['qwk_medio']):>9}{num(r['B']['qwk_medio']):>9}"
              f"{r['final']['vies']:>+9.1f}"
              f"{r['final']['erro_absoluto']:>11.1f}{menor:>7}")

    if any(len(res) < len(teste) for res in saidas.values()):
        print("\nAVISO: a rodada não completou — os números acima são parciais")
        print("e não devem ser comparados com rodadas completas.")

    print("\nreferências: corretoras entre si QWK 0,867 · "
          "estado da arte publicado 0,60 a 0,73")

    if saidas["atual"] and len(saidas["atual"]) == len(saidas["ancorado"]):
        print(f"\n{'prontuário':<12}{'humano':>8}{'atual':>8}{'ancorado':>10}"
              f"{'Δ atual':>9}{'Δ anc.':>8}")
        print("-" * 55)
        for a, b in zip(saidas["atual"], saidas["ancorado"]):
            h = a["humano_total"]
            print(f"{a['prontuario']:<12}{h:>8}{a['sistema_total']:>8}"
                  f"{b['sistema_total']:>10}{a['sistema_total']-h:>+9}"
                  f"{b['sistema_total']-h:>+8}")

        fracas = [(a, b) for a, b in zip(saidas["atual"], saidas["ancorado"])
                  if a["humano_total"] < 560]
        if fracas:
            ea = statistics.mean(abs(a["sistema_total"] - a["humano_total"])
                                 for a, _ in fracas)
            eb = statistics.mean(abs(b["sistema_total"] - b["humano_total"])
                                 for _, b in fracas)
            print(f"\nsó as {len(fracas)} redações fracas (humano < 560):")
            print(f"  erro absoluto   atual {ea:.1f}   ancorado {eb:.1f}")

    saida = AQUI / "resultados"
    saida.mkdir(exist_ok=True)
    carimbo = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    arquivo = saida / f"simulado_ancora_validada_{args.fonte}_{carimbo}.json"
    arquivo.write_text(json.dumps({
        "gerado_em": carimbo,
        "fonte_do_texto": args.fonte,
        "metodo": "ancoragem local com conjunto de teste disjunto das âncoras",
        "ancoras": [{"prontuario": a["prontuario"], "total": a["total"],
                     "final": a["final"]} for a in ancoras],
        "parametros": {"modelo": args.modelo, "max_tokens": MAX_TOKENS,
                       "esforco": ESFORCO},
        "completo": all(len(res) == len(teste) for res in saidas.values()),
        "n_teste": len(teste),
        "relatorio": relatorio,
        "resultados": saidas,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\ndados salvos em {arquivo.relative_to(AQUI.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
