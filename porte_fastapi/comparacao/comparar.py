"""Compara o backend Node (Express) com o backend Python (FastAPI).

Serve para provar, antes de desligar o Node, que o porte se comporta igual.

O que é comparado com rigor (determinístico, sem custo de API):
  - códigos HTTP das validações e das regras de permissão
  - contador de uso e o bloqueio por limite mensal
  - CRUD de temas
  - o bloco de antiplágio devolvido pela correção

O que NÃO dá para comparar por igualdade: a nota e o texto do feedback. São
saída de modelo de linguagem, variam entre execuções até no mesmo backend. Para
esses campos o script confere a ESTRUTURA (5 competências, notas na escala do
ENEM, nota_total = soma) e imprime os dois resultados lado a lado para você
julgar se estão na mesma faixa.

Uso:

    # só as regras — não chama a IA, não gasta crédito
    python comparar.py

    # inclui N correções de verdade nos dois backends (gasta crédito 2N vezes)
    python comparar.py --com-ia 1

    # endereços diferentes do padrão
    python comparar.py --node http://localhost:3005 --py http://localhost:8000

Pré-requisitos: os dois servidores no ar. O script cria uma conta de teste no
Node (veja LIMPEZA no final da saída).
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any

EMAIL_TESTE = "comparacao@local.test"
SENHA_TESTE = "comparacao123"

APOIO = (
    "TEXTO I\nA circulação de notícias falsas cresceu de forma expressiva com a "
    "popularização das redes sociais e dos aplicativos de mensagem. Conteúdos "
    "enganosos se espalham mais rápido que checagens e correções, moldando "
    "opiniões e comportamentos.\n\n"
    "TEXTO II\nEspecialistas defendem a educação midiática como ferramenta central "
    "de enfrentamento: ensinar o cidadão a verificar fontes, identificar vieses e "
    "desconfiar de manchetes sensacionalistas é tão importante quanto punir quem "
    "produz desinformação."
)

REDACAO_LIMPA = (
    "A desinformação tornou-se um dos principais desafios das democracias "
    "contemporâneas. Quando a mentira circula mais rápido que a checagem, o debate "
    "público perde a base comum de fatos sobre a qual qualquer acordo seria "
    "possível. Nesse cenário, a escola assume papel decisivo: cabe a ela formar "
    "leitores capazes de desconfiar da manchete fácil e de rastrear a origem "
    "daquilo que compartilham. Portanto, o Ministério da Educação deve incluir "
    "educação midiática no currículo do ensino médio, por meio de oficinas "
    "permanentes de checagem de fatos, a fim de que o estudante brasileiro chegue "
    "à vida adulta preparado para distinguir informação de propaganda."
)

REDACAO_COPIADA = (
    "A circulação de notícias falsas cresceu de forma expressiva com a "
    "popularização das redes sociais e dos aplicativos de mensagem. Conteúdos "
    "enganosos se espalham mais rápido que checagens e correções, moldando "
    "opiniões e comportamentos. Por isso o tema merece atenção das autoridades "
    "brasileiras neste momento histórico."
)


# ── HTTP mínimo, sem dependências ────────────────────────────────────────────

@dataclass
class Resposta:
    status: int
    corpo: Any


def pedir(
    url: str,
    metodo: str = "GET",
    dados: dict | None = None,
    cabecalhos: dict[str, str] | None = None,
) -> Resposta:
    corpo = json.dumps(dados).encode() if dados is not None else None
    req = urllib.request.Request(url, data=corpo, method=metodo)
    req.add_header("Content-Type", "application/json")
    for k, v in (cabecalhos or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            bruto = r.read().decode()
            return Resposta(r.status, json.loads(bruto) if bruto else None)
    except urllib.error.HTTPError as e:
        bruto = e.read().decode()
        try:
            return Resposta(e.code, json.loads(bruto) if bruto else None)
        except json.JSONDecodeError:
            return Resposta(e.code, bruto)
    except urllib.error.URLError as e:
        raise SystemExit(f"Não consegui falar com {url}: {e.reason}")


# ── Relatório ────────────────────────────────────────────────────────────────

@dataclass
class Relatorio:
    ok: int = 0
    falhas: list[str] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)

    def conferir(self, nome: str, node: Any, py: Any) -> None:
        if node == py:
            self.ok += 1
            print(f"  [ok]    {nome:<46} {node}")
        else:
            self.falhas.append(f"{nome}: Node={node!r} Python={py!r}")
            print(f"  [DIFERE] {nome:<45} Node={node!r}  Python={py!r}")

    def afirmar(self, nome: str, condicao: bool, detalhe: str = "") -> None:
        if condicao:
            self.ok += 1
            print(f"  [ok]    {nome}")
        else:
            self.falhas.append(f"{nome}: {detalhe}")
            print(f"  [FALHA] {nome} — {detalhe}")

    def avisar(self, texto: str) -> None:
        self.avisos.append(texto)
        print(f"  [nota]  {texto}")


# ── Clientes ─────────────────────────────────────────────────────────────────

class ClienteNode:
    """Backend Express. Tem login próprio, então precisa de conta."""

    def __init__(self, base: str) -> None:
        self.base = base.rstrip("/")
        self.token: str | None = None

    def entrar(self) -> None:
        r = pedir(
            f"{self.base}/api/auth/cadastro",
            "POST",
            {"nome": "Comparação", "email": EMAIL_TESTE, "senha": SENHA_TESTE},
        )
        if r.status == 409:  # já existe de uma execução anterior
            r = pedir(
                f"{self.base}/api/auth/login",
                "POST",
                {"email": EMAIL_TESTE, "senha": SENHA_TESTE},
            )
        if r.status not in (200, 201):
            raise SystemExit(f"Login no Node falhou: {r.status} {r.corpo}")
        self.token = r.corpo["token"]

    @property
    def _h(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}

    def status(self) -> Resposta:
        return pedir(f"{self.base}/api/usuario/status", cabecalhos=self._h)

    def corrigir(self, dados: dict) -> Resposta:
        return pedir(f"{self.base}/api/corrigir", "POST", dados, self._h)

    def temas(self) -> Resposta:
        return pedir(f"{self.base}/api/temas", cabecalhos=self._h)

    def criar_tema(self, dados: dict) -> Resposta:
        return pedir(f"{self.base}/api/temas", "POST", dados, self._h)

    def salvar_chave(self, chave: str) -> Resposta:
        return pedir(
            f"{self.base}/api/usuario/api-key", "POST", {"api_key": chave}, self._h
        )

    def historico(self) -> Resposta:
        return pedir(f"{self.base}/api/usuario/historico", cabecalhos=self._h)


class ClientePython:
    """Backend FastAPI. A identidade vem do provedor do app hospedeiro.

    Contra o `exemplo_app.py`, o papel é escolhido pelo header X-Papel.
    Se vocês já plugaram no login do IFvest, troque `cabecalhos` pelo token real.
    """

    def __init__(self, base: str, professor: bool = False) -> None:
        self.base = base.rstrip("/") + "/api/redacao"
        self.professor = professor

    @property
    def _h(self) -> dict[str, str]:
        return {"X-Papel": "professor"} if self.professor else {}

    def status(self) -> Resposta:
        return pedir(f"{self.base}/status", cabecalhos=self._h)

    def corrigir(self, dados: dict) -> Resposta:
        return pedir(f"{self.base}/corrigir", "POST", dados, self._h)

    def temas(self) -> Resposta:
        return pedir(f"{self.base}/temas", cabecalhos=self._h)

    def criar_tema(self, dados: dict) -> Resposta:
        return pedir(f"{self.base}/temas", "POST", dados, self._h)

    def salvar_chave(self, chave: str) -> Resposta:
        return pedir(f"{self.base}/chave", "POST", {"api_key": chave}, self._h)

    def historico(self) -> Resposta:
        return pedir(f"{self.base}/historico", cabecalhos=self._h)


# ── Fases ────────────────────────────────────────────────────────────────────

def fase_validacoes(node: ClienteNode, py: ClientePython, rel: Relatorio) -> None:
    print("\n1. Validações de entrada (nenhuma chega à IA)")

    curta = {"redacao": "curta demais"}
    rel.conferir("redação curta → 400", node.corrigir(curta).status, py.corrigir(curta).status)

    inexistente = {"redacao": REDACAO_LIMPA, "tema_id": 999999}
    rel.conferir(
        "tema inexistente → 404",
        node.corrigir(inexistente).status,
        py.corrigir(inexistente).status,
    )

    rel.conferir(
        "chave de API malformada → 400",
        node.salvar_chave("chave-invalida").status,
        py.salvar_chave("chave-invalida").status,
    )


def fase_permissoes(node: ClienteNode, base_py: str, rel: Relatorio) -> None:
    print("\n2. Permissão de professor")

    tema = {"titulo": "Comparação", "textos_apoio": APOIO}
    aluno_py = ClientePython(base_py, professor=False)
    rel.conferir(
        "aluno criando tema → 403",
        node.criar_tema(tema).status,
        aluno_py.criar_tema(tema).status,
    )

    prof_py = ClientePython(base_py, professor=True)
    criado = prof_py.criar_tema(tema)
    rel.afirmar(
        "professor cria tema → 201",
        criado.status == 201,
        f"Python devolveu {criado.status}",
    )
    rel.avisar(
        "no Node o papel vem do código de professor; no Python vem do IFvest — "
        "os 403 batem, o caminho feliz não é comparável 1:1"
    )


def fase_status(node: ClienteNode, py: ClientePython, rel: Relatorio) -> None:
    print("\n3. Formato do status de uso")

    n = node.status().corpo
    p = py.status().corpo

    rel.conferir("tem chave própria", bool(n["tem_chave_propria"]), p["tem_chave_propria"])
    rel.conferir("limite mensal", n["redacoes_limite"], p["redacoes_limite"])
    rel.conferir("correções usadas", n["redacoes_usadas"], p["redacoes_usadas"])
    rel.conferir("correções restantes", n["redacoes_restantes"], p["redacoes_restantes"])


def _validar_estrutura(nome: str, c: dict, rel: Relatorio) -> None:
    comps = c.get("competencias", [])
    rel.afirmar(f"{nome}: 5 competências", len(comps) == 5, f"veio {len(comps)}")
    rel.afirmar(
        f"{nome}: competências numeradas de 1 a 5",
        sorted(x["numero"] for x in comps) == [1, 2, 3, 4, 5],
        str([x.get("numero") for x in comps]),
    )
    escala = {0, 40, 80, 120, 160, 200}
    fora = [x["nota"] for x in comps if x["nota"] not in escala]
    rel.afirmar(f"{nome}: notas na escala do ENEM", not fora, f"fora da escala: {fora}")
    soma = sum(x["nota"] for x in comps)
    rel.afirmar(
        f"{nome}: nota_total = soma das competências",
        soma == c["nota_total"],
        f"soma={soma} nota_total={c['nota_total']}",
    )
    rel.afirmar(
        f"{nome}: níveis válidos",
        all(x["nivel"] in {"alto", "medio", "baixo"} for x in comps),
        "nível fora de alto/medio/baixo",
    )


def _plagio(corpo: dict) -> dict:
    """Normaliza o bloco de plágio: Node usa camelCase, Python snake_case."""
    p = corpo["plagio"]
    if "percentualCopiado" in p:
        return {
            "percentual": p["percentualCopiado"],
            "copiadas": p["palavrasCopiadas"],
            "total": p["totalPalavras"],
            "trechos": [t["texto"] for t in p["trechosCopiados"]],
        }
    return {
        "percentual": p["percentual_copiado"],
        "copiadas": p["palavras_copiadas"],
        "total": p["total_palavras"],
        "trechos": [t["texto"] for t in p["trechos_copiados"]],
    }


def fase_correcao(
    node: ClienteNode, py: ClientePython, rel: Relatorio, rodadas: int
) -> None:
    print(f"\n4. Correção de verdade ({rodadas} redação(ões) em cada backend)")
    print("   ATENÇÃO: esta fase consome créditos de API nos dois lados.\n")

    for i in range(1, rodadas + 1):
        for rotulo, redacao in (
            ("texto próprio", REDACAO_LIMPA),
            ("texto copiado", REDACAO_COPIADA),
        ):
            pedido = {"redacao": redacao, "tema": "Desinformação", "textos_apoio": APOIO}
            print(f"  rodada {i} — {rotulo}")

            rn = node.corrigir(pedido)
            rp = py.corrigir(pedido)
            if rn.status != 200 or rp.status != 200:
                rel.afirmar(
                    f"rodada {i} {rotulo}: as duas correções responderam 200",
                    False,
                    f"Node={rn.status} {rn.corpo} / Python={rp.status} {rp.corpo}",
                )
                continue

            # Determinístico: o antiplágio tem que bater exatamente.
            pn, pp = _plagio(rn.corpo), _plagio(rp.corpo)
            rel.conferir(f"  antiplágio % ({rotulo})", pn["percentual"], pp["percentual"])
            rel.conferir(f"  palavras copiadas ({rotulo})", pn["copiadas"], pp["copiadas"])
            rel.conferir(f"  total de palavras ({rotulo})", pn["total"], pp["total"])
            rel.conferir(f"  trechos copiados ({rotulo})", pn["trechos"], pp["trechos"])

            # Não determinístico: confere estrutura e mostra lado a lado.
            _validar_estrutura(f"  Node ({rotulo})", rn.corpo, rel)
            _validar_estrutura(f"  Python ({rotulo})", rp.corpo, rel)

            nn, np_ = rn.corpo["nota_total"], rp.corpo["nota_total"]
            print(f"     nota Node={nn}  Python={np_}  (diferença {abs(nn - np_)})")
            print(
                "     notas por competência  Node="
                f"{[c['nota'] for c in sorted(rn.corpo['competencias'], key=lambda x: x['numero'])]}"
                "  Python="
                f"{[c['nota'] for c in sorted(rp.corpo['competencias'], key=lambda x: x['numero'])]}"
            )
            if abs(nn - np_) > 200:
                rel.avisar(
                    f"diferença de {abs(nn - np_)} pontos entre os backends — "
                    "esperado até certo ponto (a IA varia), mas vale repetir para ver "
                    "se é viés sistemático ou ruído"
                )


def main() -> int:
    p = argparse.ArgumentParser(description="Compara os backends Node e Python.")
    p.add_argument("--node", default="http://localhost:3005")
    p.add_argument("--py", default="http://localhost:8000")
    p.add_argument(
        "--com-ia",
        type=int,
        default=0,
        metavar="N",
        help="roda N correções reais em cada backend (consome créditos)",
    )
    args = p.parse_args()

    print(f"Node:   {args.node}")
    print(f"Python: {args.py}")

    node = ClienteNode(args.node)
    node.entrar()
    py = ClientePython(args.py)

    rel = Relatorio()
    fase_validacoes(node, py, rel)
    fase_permissoes(node, args.py, rel)
    fase_status(node, py, rel)
    if args.com_ia:
        fase_correcao(node, py, rel, args.com_ia)
    else:
        print("\n4. Correção de verdade — PULADA (use --com-ia N para incluir)")

    print("\n" + "=" * 72)
    print(f"comparações iguais: {rel.ok}")
    if rel.avisos:
        print(f"observações: {len(rel.avisos)}")
    if rel.falhas:
        print(f"DIVERGÊNCIAS: {len(rel.falhas)}")
        for f in rel.falhas:
            print(f"  - {f}")
    else:
        print("nenhuma divergência nos itens determinísticos")

    print(
        f"\nLIMPEZA: o script criou a conta {EMAIL_TESTE} no banco do Node. "
        "Para remover:\n"
        '  sqlite3 database.db "DELETE FROM correcoes WHERE usuario_id = '
        f"(SELECT id FROM usuarios WHERE email='{EMAIL_TESTE}'); "
        f"DELETE FROM usuarios WHERE email='{EMAIL_TESTE}';\""
    )

    return 1 if rel.falhas else 0


if __name__ == "__main__":
    sys.exit(main())
