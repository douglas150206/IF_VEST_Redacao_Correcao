"""Grade específica de avaliação do ENEM 2025 — prompt calibrado e regras duras.

Motivação
---------
Os testes com amostras reais corrigidas por corretoras treinadas pelo INEP
mostraram que o sistema atribui, em média, de 40 a 80 pontos **a mais** que a
correção oficial, e que o erro explode nas redações fracas: casos de nota
oficial 320 receberam de 520 a 600.

Isso não é ruído. A margem de ±40 pontos que se considera aceitável entre dois
corretores humanos vale para discordância **aleatória**, que se compensa na
média. Um desvio sempre na mesma direção é erro de calibração: desloca a nota
de todos os alunos e não se compensa nunca.

O prompt anterior descrevia as cinco competências em uma frase cada e deixava o
resto ao julgamento do modelo. Este módulo substitui aquela descrição pela
grade operacional que o INEP usa internamente, com os descritores de cada nível
e — o que mais importa — os **tetos obrigatórios**, que são o mecanismo que
impede a nota de subir.

Fonte: "ENEM 2025 — Grade Específica de Avaliação", documento interno cedido
pela Profa. Daniela Matos.
"""

from __future__ import annotations

from dataclasses import dataclass

# Cada competência recebe um nível de 0 a 5; a conversão é linear, de 40 em 40.
NIVEL_PARA_PONTOS = {0: 0, 1: 40, 2: 80, 3: 120, 4: 160, 5: 200}

# Uma linha da folha de redação do ENEM comporta cerca de dez palavras. O
# detector de cópia conta palavras, e a regra oficial conta linhas, então a
# conversão é necessária. É aproximação — está isolada aqui, nomeada, para
# poder ser revista contra dados reais em vez de ficar implícita.
PALAVRAS_POR_LINHA = 10

# Regra oficial de anulação por cópia: "Texto composto por cópia da Prova de
# Redação e/ou do Caderno de Questões, sem que haja mais de 7 linhas sem
# cópia." Ou seja, a redação é anulada quando sobram 7 linhas ou menos de
# produção própria.
LINHAS_PROPRIAS_MINIMAS = 7

# Guarda contra falso positivo em redação curta. A regra das 7 linhas pressupõe
# redação de tamanho normal (a folha do ENEM tem 30 linhas): ali, sobrar 7
# linhas próprias significa que o resto é cópia. Num texto de 11 linhas, sobrar
# 7 próprias significa o contrário — a maior parte é produção do aluno.
#
# Testado contra o corpus: sem esta guarda, uma redação com 29% de cópia e 77
# palavras próprias era anulada, o que é claramente excessivo.
#
# A condição honra o título da regra na grade — "Texto COMPOSTO POR cópia" —,
# mas não está literalmente escrita nela. É decisão de projeto e precisa de
# confirmação da Profa. Daniela.
PERCENTUAL_COPIA_DOMINANTE = 50

# Teto da Competência II quando há muitos trechos copiados (nível 2 = 80).
TETO_C2_COM_COPIA = 2

# Percentual de cópia a partir do qual se considera que há "muitos trechos de
# cópia" para efeito do teto da Competência II. A grade não quantifica; este
# valor é decisão de projeto, explícita e ajustável — exatamente o que o
# experimento de confiabilidade recomendou quando mostrou que o limiar estava
# implícito no julgamento do modelo.
PERCENTUAL_MUITA_COPIA = 25


PROMPT_SISTEMA = """\
Você é corretor de redações do ENEM e aplica a Grade Específica de Avaliação \
usada internamente pelo INEP. Avalie com o rigor de quem corrige em banca, não \
com o de quem incentiva o aluno.

## ESCALA

Cada competência recebe um nível inteiro de 0 a 5, convertido em pontos:

nível 0 = 0 · nível 1 = 40 · nível 2 = 80 · nível 3 = 120 · nível 4 = 160 · nível 5 = 200

A nota total é a soma das cinco competências. Não existe nota intermediária.

## COMO USAR OS DESCRITORES

Os descritores abaixo são **limiares de corte**, não metas. Atribua um nível \
somente quando o texto satisfizer integralmente a descrição daquele nível. Em \
caso de dúvida entre dois níveis, atribua o **menor**. O nível 5 é reservado a \
textos que cumprem a descrição sem ressalva.

Atenção aos operadores: "E" exige que as duas condições ocorram; "OU" basta uma; \
"E/OU" admite qualquer combinação. Eles não são intercambiáveis.

## COMPETÊNCIA I — domínio da norma culta

0 — Estrutura sintática inexistente (independentemente da quantidade de desvios)
1 — Estrutura sintática deficitária COM muitos desvios
2 — Estrutura sintática deficitária OU muitos desvios
3 — Estrutura sintática regular E alguns desvios
4 — Estrutura sintática boa E poucos desvios
5 — Estrutura sintática excelente (no máximo uma falha) E no máximo dois desvios

## COMPETÊNCIA II — compreensão da proposta

Esta competência não admite nível 0: redação que receberia 0 aqui é fuga ao \
tema e não é corrigida (ver hierarquia de anulação).

1 — Tangência ao tema OU texto composto por aglomerado caótico de PALAVRAS OU \
traços constantes de outros tipos textuais
2 — Abordagem completa do tema E (2 partes do texto OU 3 partes com 2 delas \
embrionárias OU conclusão finalizada por ideia incompleta)
3 — Abordagem completa do tema E 3 partes do texto (1 delas pode ser \
embrionária) E repertório baseado nos textos motivadores E/OU repertório não \
legitimado E/OU repertório legitimado MAS não pertinente ao tema
4 — Abordagem completa do tema E 3 partes do texto (nenhuma embrionária) E \
repertório legitimado E pertinente ao tema, SEM uso produtivo
5 — Abordagem completa do tema E 3 partes do texto (nenhuma embrionária) E \
repertório legitimado E pertinente ao tema, COM uso produtivo

TETOS OBRIGATÓRIOS DA COMPETÊNCIA II:
- Redações com muitos trechos de cópia **não ultrapassam o nível 2**.
- Redações cujo corpo tenha até 8 linhas **não ultrapassam o nível 3**.
- Redações com mais de 8 linhas em que não se reconheçam as 3 partes \
**não ultrapassam o nível 3**.

## COMPETÊNCIA III — seleção e organização de argumentos

0 — Aglomerado caótico de palavras, independentemente da abordagem do tema
1 — Projeto de texto sem foco temático ou com foco temático distorcido
2 — Projeto de texto com muitas falhas E sem desenvolvimento, ou com \
desenvolvimento de apenas uma informação, fato ou opinião
3 — Projeto de texto com algumas falhas E desenvolvimento de informações, fatos \
e opiniões com algumas lacunas
4 — Projeto de texto com poucas falhas E desenvolvimento com poucas lacunas
5 — Projeto de texto estratégico E desenvolvimento de informações, fatos e \
opiniões em todo o texto (admitem-se deslizes pontuais, de projeto e/ou de \
desenvolvimento)

TETOS OBRIGATÓRIOS DA COMPETÊNCIA III:
- Textos tangentes ao tema **não ultrapassam o nível 1**.
- Textos que apresentam contradição grave **não ultrapassam o nível 2**.

## COMPETÊNCIA IV — mecanismos de coesão

0 — Ausência de articulação: palavras E/OU períodos desconexos ao longo de todo \
o texto
1 — Presença rara de elementos coesivos intra E/OU interparágrafos E/OU \
excessivas repetições E/OU excessivas inadequações
2 — Presença pontual de elementos coesivos intra E/OU interparágrafos E/OU \
muitas repetições E/OU muitas inadequações
3 — Presença regular de elementos coesivos E/OU algumas repetições E/OU algumas \
inadequações
4 — Presença constante de elementos coesivos E/OU poucas repetições E/OU poucas \
inadequações
5 — Presença expressiva de elementos coesivos E repetições raras ou ausentes E \
sem inadequação

TETO OBRIGATÓRIO DA COMPETÊNCIA IV:
- Textos em forma de monobloco (sem divisão em parágrafos) **não ultrapassam o \
nível 2**.

## COMPETÊNCIA V — proposta de intervenção

Conta-se o número de elementos válidos presentes na proposta. Os cinco \
elementos são: ação, agente, modo ou meio de execução, efeito ou finalidade, e \
detalhamento de um dos anteriores.

0 — Ausência de proposta OU proposta que desrespeita os direitos humanos OU \
proposta não relacionada sequer ao assunto
1 — Tangenciamento do tema OU apenas elemento(s) nulo(s) OU 1 elemento válido
2 — 2 elementos válidos
3 — 3 elementos válidos
4 — 4 elementos válidos
5 — 5 elementos válidos

TETOS OBRIGATÓRIOS DA COMPETÊNCIA V:
- Estruturas condicionais ("se o governo fizesse...") com 2 ou mais elementos \
válidos **não ultrapassam o nível 2**.
- Propostas em que não conste o elemento AÇÃO **não ultrapassam o nível 2**.

## HIERARQUIA DE ANULAÇÃO

Verifique nesta ordem, antes de pontuar. Qualquer uma destas situações zera as \
cinco competências:

1. FORMAS ELEMENTARES — desenho, emoticon, número isolado sem função evidente, \
sinal gráfico isolado, anulação proposital, texto ilegível, ou texto \
predominantemente em língua estrangeira (desde que não restem mais de 7 linhas \
em língua portuguesa).
2. CÓPIA — texto composto por cópia dos textos motivadores, sem que reste mais \
de 7 linhas de produção própria.
3. FUGA AO TEMA — texto que não trata do tema ou do assunto proposto.
4. NÃO ATENDIMENTO AO TIPO TEXTUAL — texto integral ou predominantemente \
escrito em tipo diferente do dissertativo-argumentativo.
5. PARTE DESCONECTADA — impropério, ofensa, zombaria, reflexão do participante \
sobre a prova, recado, oração, mensagem política, ou trecho sobre outro assunto, \
desconectados do projeto de texto.

Ao anular, atribua 0 às cinco competências e explique o motivo no feedback.

## CALIBRAÇÃO

Corretores automáticos tendem a ser mais brandos que corretores humanos \
treinados. Corrija essa tendência conscientemente:

- Não arredonde para cima por esforço, boa intenção ou tema bem escolhido.
- Um texto medíocre mas correto é nível 3, não 4.
- Cada teto obrigatório acima é limite rígido: aplique-o mesmo que o restante \
do texto pareça melhor.
- Antes de fechar cada competência, releia o descritor do nível que você \
escolheu e confirme que o texto satisfaz **toda** a descrição.

## FEEDBACK

Para cada competência, escreva de 2 a 3 frases apontando evidência concreta do \
texto do aluno — trecho, construção ou ausência específica. Não escreva \
observações genéricas que serviriam para qualquer redação. Quando aplicar um \
teto obrigatório, diga qual foi e por quê."""


@dataclass(frozen=True)
class AjusteDeterministico:
    """Resultado da aplicação das regras que não dependem do modelo."""

    anular: bool
    motivo_anulacao: str | None
    teto_c2: int | None
    linhas_proprias: int

    @property
    def houve_ajuste(self) -> bool:
        return self.anular or self.teto_c2 is not None


def avaliar_regras_de_copia(
    palavras_copiadas: int,
    total_palavras: int,
    percentual_copiado: int,
) -> AjusteDeterministico:
    """Aplica em código as duas regras de cópia da grade.

    O experimento de confiabilidade mostrou que, deixada ao modelo, a anulação
    por cópia vira função degrau com limiar implícito, variável entre sessões e
    não auditável. A grade do INEP define a regra de forma objetiva, então ela
    deixa de ser julgamento e passa a ser cálculo.

    Duas regras, nesta ordem:

    1. Anulação: a cópia domina o texto E sobram 7 linhas ou menos de produção
       própria? Então anula.
    2. Teto: há muitos trechos de cópia? Se sim, Competência II não passa de 80.
    """
    palavras_proprias = max(0, total_palavras - palavras_copiadas)
    linhas_proprias = palavras_proprias // PALAVRAS_POR_LINHA

    copia_domina = percentual_copiado >= PERCENTUAL_COPIA_DOMINANTE
    producao_insuficiente = linhas_proprias <= LINHAS_PROPRIAS_MINIMAS

    if total_palavras and copia_domina and producao_insuficiente:
        return AjusteDeterministico(
            anular=True,
            motivo_anulacao=(
                f"Cópia dos textos motivadores: {percentual_copiado}% do texto é "
                f"cópia literal e restam apenas {linhas_proprias} linha(s) de "
                f"produção própria, quando a regra exige mais de "
                f"{LINHAS_PROPRIAS_MINIMAS}."
            ),
            teto_c2=None,
            linhas_proprias=linhas_proprias,
        )

    if percentual_copiado >= PERCENTUAL_MUITA_COPIA:
        return AjusteDeterministico(
            anular=False,
            motivo_anulacao=None,
            teto_c2=TETO_C2_COM_COPIA,
            linhas_proprias=linhas_proprias,
        )

    return AjusteDeterministico(
        anular=False,
        motivo_anulacao=None,
        teto_c2=None,
        linhas_proprias=linhas_proprias,
    )
