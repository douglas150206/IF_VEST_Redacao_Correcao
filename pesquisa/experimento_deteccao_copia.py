"""Experimento 3 — precisão e recall do detector de cópia.

O experimento 1 mediu a nota que o modelo atribui. Este mede o componente
determinístico do sistema: o algoritmo de shingles que marca trechos copiados
dos textos de apoio.

A vantagem de medir este componente é que existe gabarito exato. Nós injetamos
a cópia, então sabemos, palavra por palavra, quais deveriam ser marcadas. Não
há juízo humano no meio — a métrica é aritmética.

Três testes:

  A. Detecção por tamanho do trecho. Injeta um trecho literal de L palavras e
     verifica quantas o detector marca. Como o shingle tem 7 palavras, a
     expectativa teórica é degrau: nada abaixo de 7, tudo a partir de 7.

  B. Resistência a edição trivial. Pega um trecho literal longo e substitui
     k palavras espalhadas. Mede quanto a detecção cai. Responde: basta o
     aluno trocar uma palavra aqui e ali para escapar?

  C. Falso positivo em texto original. Roda o detector nas redações sem cópia.
     Qualquer palavra marcada é falso positivo, porque o gabarito é zero.

Uso:
    python experimento_deteccao_copia.py
    python experimento_deteccao_copia.py --json resultados/deteccao.json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent

# Carrega plagio.py pelo caminho, sem passar pelo pacote `corretor` — o
# __init__ dele importa FastAPI, que este experimento não precisa. O módulo de
# detecção usa só a biblioteca padrão, então roda isolado.
_CAMINHO_PLAGIO = RAIZ.parent / "porte_fastapi" / "corretor" / "plagio.py"
_spec = importlib.util.spec_from_file_location("plagio", _CAMINHO_PLAGIO)
plagio = importlib.util.module_from_spec(_spec)
# @dataclass resolve anotações via sys.modules, então o módulo precisa estar
# registrado antes de executar.
sys.modules["plagio"] = plagio
_spec.loader.exec_module(plagio)

TAMANHO_SHINGLE_PADRAO = plagio.TAMANHO_SHINGLE_PADRAO
detectar_copia = plagio.detectar_copia
normalizar_palavra = plagio.normalizar_palavra
tokenizar = plagio.tokenizar

CORPUS = RAIZ / "corpus" / "redacoes.json"

# Candidatas a palavra substituta no teste B. A escolhida é a primeira que não
# aparece nos textos de apoio — se aparecesse, a substituição poderia manter o
# shingle válido e contaminar a medida.
CANDIDATAS_SUBSTITUTAS = [
    "outrossim",
    "porquanto",
    "amiude",
    "conquanto",
    "destarte",
    "zyxwvu",
]


@dataclass
class Medida:
    """Contagem palavra a palavra de acertos e erros do detector."""

    verdadeiros_positivos: int
    falsos_positivos: int
    falsos_negativos: int

    @property
    def precisao(self) -> float | None:
        marcadas = self.verdadeiros_positivos + self.falsos_positivos
        return self.verdadeiros_positivos / marcadas if marcadas else None

    @property
    def recall(self) -> float | None:
        reais = self.verdadeiros_positivos + self.falsos_negativos
        return self.verdadeiros_positivos / reais if reais else None

    @property
    def f1(self) -> float | None:
        p, r = self.precisao, self.recall
        if p is None or r is None or p + r == 0:
            return None
        return 2 * p * r / (p + r)


def carregar_corpus() -> tuple[str, list[dict]]:
    dados = json.loads(CORPUS.read_text(encoding="utf-8"))
    return dados["tema"]["textos_apoio"], dados["redacoes"]


def escolher_substituta(apoio: str) -> str:
    """Palavra que não existe nos textos de apoio, para quebrar o shingle."""
    normas_apoio = {t.norm for t in tokenizar(apoio)}
    for candidata in CANDIDATAS_SUBSTITUTAS:
        if normalizar_palavra(candidata) not in normas_apoio:
            return candidata
    raise RuntimeError("nenhuma candidata a substituta serve para este apoio")


def avaliar(
    palavras_redacao: list[str],
    indices_injetados: set[int],
    apoio: str,
) -> Medida:
    """Compara o que o detector marcou com o gabarito exato da injeção.

    O detector devolve trechos em texto; para comparar palavra a palavra,
    remontamos quais posições ele marcou refazendo a varredura de shingles
    sobre a mesma tokenização que ele usa.
    """
    tokens = tokenizar(" ".join(palavras_redacao))
    apoio_tokens = tokenizar(apoio)
    n = TAMANHO_SHINGLE_PADRAO

    marcado = [False] * len(tokens)
    if len(apoio_tokens) >= n and len(tokens) >= n:
        shingles_apoio = {
            " ".join(t.norm for t in apoio_tokens[i : i + n])
            for i in range(len(apoio_tokens) - n + 1)
        }
        for i in range(len(tokens) - n + 1):
            gram = " ".join(t.norm for t in tokens[i : i + n])
            if gram in shingles_apoio:
                for j in range(i, i + n):
                    marcado[j] = True

    vp = fp = fn = 0
    for i in range(len(tokens)):
        injetada = i in indices_injetados
        if marcado[i] and injetada:
            vp += 1
        elif marcado[i] and not injetada:
            fp += 1
        elif not marcado[i] and injetada:
            fn += 1
    return Medida(vp, fp, fn)


def injetar(
    hospedeira: list[str],
    trecho: list[str],
    posicao: int,
) -> tuple[list[str], set[int]]:
    """Insere o trecho na posição dada e devolve o texto e os índices injetados."""
    novo = hospedeira[:posicao] + trecho + hospedeira[posicao:]
    indices = set(range(posicao, posicao + len(trecho)))
    return novo, indices


def teste_a(apoio: str, redacoes: list[dict]) -> list[dict]:
    """Detecção em função do tamanho do trecho copiado."""
    apoio_palavras = apoio.split()
    tamanhos = [3, 4, 5, 6, 7, 8, 10, 15, 20, 30]
    # Redações originais como hospedeiras (as que o detector mede 0% de cópia).
    hospedeiras = [r for r in redacoes if r["id"] in {"R1", "R2", "R3"}]

    linhas = []
    for tamanho in tamanhos:
        acumulado = Medida(0, 0, 0)
        for redacao in hospedeiras:
            palavras = redacao["texto"].split()
            # Três posições de injeção: início, meio e fim do corpo do texto.
            for fracao in (0.25, 0.5, 0.75):
                posicao = int(len(palavras) * fracao)
                # Recorta o trecho de um ponto do apoio que caiba inteiro.
                inicio_apoio = 20
                trecho = apoio_palavras[inicio_apoio : inicio_apoio + tamanho]
                if len(trecho) < tamanho:
                    continue
                texto, indices = injetar(palavras, trecho, posicao)
                m = avaliar(texto, indices, apoio)
                acumulado.verdadeiros_positivos += m.verdadeiros_positivos
                acumulado.falsos_positivos += m.falsos_positivos
                acumulado.falsos_negativos += m.falsos_negativos
        linhas.append(
            {
                "palavras_copiadas": tamanho,
                "precisao": acumulado.precisao,
                "recall": acumulado.recall,
                "f1": acumulado.f1,
                **asdict(acumulado),
            }
        )
    return linhas


def teste_b(apoio: str, redacoes: list[dict]) -> list[dict]:
    """Quanto a detecção cai quando o aluno troca algumas palavras."""
    apoio_palavras = apoio.split()
    substituta = escolher_substituta(apoio)
    tamanho_trecho = 30
    trecho_base = apoio_palavras[20 : 20 + tamanho_trecho]
    hospedeiras = [r for r in redacoes if r["id"] in {"R1", "R2", "R3"}]

    linhas = []
    for substituicoes in range(0, 6):
        trecho = trecho_base[:]
        if substituicoes:
            # Substituições espalhadas por igual ao longo do trecho.
            passo = tamanho_trecho / (substituicoes + 1)
            for k in range(1, substituicoes + 1):
                trecho[int(passo * k) - 1] = substituta

        acumulado = Medida(0, 0, 0)
        for redacao in hospedeiras:
            palavras = redacao["texto"].split()
            posicao = len(palavras) // 2
            texto, indices = injetar(palavras, trecho, posicao)
            m = avaliar(texto, indices, apoio)
            acumulado.verdadeiros_positivos += m.verdadeiros_positivos
            acumulado.falsos_positivos += m.falsos_positivos
            acumulado.falsos_negativos += m.falsos_negativos

        uma_a_cada = round(tamanho_trecho / substituicoes, 1) if substituicoes else None
        linhas.append(
            {
                "substituicoes": substituicoes,
                "uma_palavra_a_cada": uma_a_cada,
                "precisao": acumulado.precisao,
                "recall": acumulado.recall,
                **asdict(acumulado),
            }
        )
    return linhas


def teste_c(apoio: str, redacoes: list[dict]) -> list[dict]:
    """Falso positivo: redações sem cópia devem marcar zero palavras."""
    linhas = []
    for redacao in redacoes:
        resultado = detectar_copia(redacao["texto"], apoio)
        linhas.append(
            {
                "redacao": redacao["id"],
                "percentual_detectado": resultado.percentual_copiado,
                "palavras_marcadas": resultado.palavras_copiadas,
                "total_palavras": resultado.total_palavras,
            }
        )
    return linhas


def pct(valor: float | None) -> str:
    return "—" if valor is None else f"{valor * 100:5.1f}%"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, help="salva os resultados em JSON")
    args = parser.parse_args()

    apoio, redacoes = carregar_corpus()

    a = teste_a(apoio, redacoes)
    b = teste_b(apoio, redacoes)
    c = teste_c(apoio, redacoes)

    print(f"shingle = {TAMANHO_SHINGLE_PADRAO} palavras\n")

    print("TESTE A — detecção por tamanho do trecho copiado")
    print("-" * 72)
    print(f"{'palavras copiadas':>18} {'precisão':>10} {'recall':>10} {'F1':>10}")
    for linha in a:
        print(
            f"{linha['palavras_copiadas']:>18} {pct(linha['precisao']):>10} "
            f"{pct(linha['recall']):>10} {pct(linha['f1']):>10}"
        )

    print("\nTESTE B — resistência a substituição de palavras (trecho de 30 palavras)")
    print("-" * 72)
    print(f"{'substituições':>14} {'1 a cada':>10} {'precisão':>10} {'recall':>10}")
    for linha in b:
        cada = linha["uma_palavra_a_cada"]
        print(
            f"{linha['substituicoes']:>14} {(cada if cada else '—'):>10} "
            f"{pct(linha['precisao']):>10} {pct(linha['recall']):>10}"
        )

    print("\nTESTE C — falso positivo nas redações do corpus")
    print("-" * 72)
    print(f"{'redação':>8} {'% detectado':>12} {'marcadas':>10} {'total':>8}")
    for linha in c:
        print(
            f"{linha['redacao']:>8} {linha['percentual_detectado']:>11}% "
            f"{linha['palavras_marcadas']:>10} {linha['total_palavras']:>8}"
        )

    if args.json:
        destino = args.json if args.json.is_absolute() else RAIZ / args.json
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(
            json.dumps(
                {
                    "tamanho_shingle": TAMANHO_SHINGLE_PADRAO,
                    "teste_a_tamanho": a,
                    "teste_b_substituicao": b,
                    "teste_c_falso_positivo": c,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"\nsalvo em {destino}")


if __name__ == "__main__":
    main()
