# Calibração contra a grade do INEP

## O problema medido

Testes do Caio com amostras reais, corrigidas por corretoras treinadas pelo
INEP e cedidas pela Profa. Daniela Matos:

| Situação | Oficial | Sistema |
|---|---|---|
| Média geral | — | **+40 a +80 pontos** |
| Redações fracas | 320 | **520 a 600** |

## Por que "está dentro da tolerância" é a conclusão errada

A Profa. Daniela informou as margens aceitas na prática:

- até **40 pontos** de diferença entre dois corretores;
- até **80 pontos** entre competências;
- até **100 pontos** na nota final.

Essas margens valem para **discordância aleatória** entre dois humanos. Um
corretor que ora erra 40 para cima, ora 40 para baixo, tem média correta — o
erro se compensa e a nota do conjunto continua justa.

O que foi medido aqui é diferente em natureza: o desvio é **sempre na mesma
direção**. Isso é viés, não ruído. Não se compensa, desloca a nota de todos os
alunos e faz a devolutiva perder valor diagnóstico — o aluno que merece 520
ouve 580 e conclui que está mais perto do que está.

Portanto a métrica correta não é "a diferença cabe na tolerância?", e sim duas
métricas separadas:

- **erro médio com sinal** (viés) — tem que tender a zero;
- **erro absoluto médio** (acurácia) — esse sim se compara com os 40 pontos.

E o caso de 320 virando 520 está fora de qualquer tolerância, inclusive dos 100
pontos da nota final.

## O que mudou

O prompt anterior descrevia cada competência em uma linha e deixava o resto ao
julgamento do modelo. `grade_inep.py` substitui isso pela grade operacional do
INEP, com três mecanismos novos:

**1. Descritores por nível.** Cada competência agora tem os seis descritores
oficiais, com os operadores E / OU / E-OU preservados, e a instrução explícita
de que são limiares de corte, não metas — em dúvida entre dois níveis, atribuir
o menor.

**2. Tetos obrigatórios.** É o mecanismo que efetivamente segura a nota, e não
existia antes:

| Competência | Teto | Condição |
|---|---|---|
| II | nível 2 (80) | muitos trechos de cópia |
| II | nível 3 (120) | corpo com até 8 linhas, ou 3 partes não reconhecíveis |
| III | nível 1 (40) | texto tangente ao tema |
| III | nível 2 (80) | contradição grave |
| IV | nível 2 (80) | texto em monobloco |
| V | nível 2 (80) | estrutura condicional, ou ausência do elemento AÇÃO |

**3. Hierarquia de anulação**, verificada antes de pontuar.

## A regra de cópia agora é cálculo, não julgamento

Esta é a mudança mais relevante para a pesquisa do projeto.

O experimento de confiabilidade mostrou que a anulação por cópia operava como
função degrau com limiar implícito no julgamento do modelo: nada era anulado
até 45% de cópia, tudo era anulado em 70%, e o ponto de virada não estava
escrito em lugar nenhum do código.

A grade do INEP define a regra objetivamente:

> Texto composto por cópia da Prova de Redação e/ou do Caderno de Questões,
> **sem que haja mais de 7 linhas sem cópia**.

Ou seja, não é percentual: conta-se quanto resta de produção própria. Restando
7 linhas ou menos, anula. Isso é computável a partir do detector que já existe,
e `avaliar_regras_de_copia()` faz exatamente isso.

Fica uma aproximação declarada: o detector conta palavras e a regra conta
linhas. A constante `PALAVRAS_POR_LINHA = 10` faz a conversão e está isolada e
nomeada, para poder ser revista contra dados reais — em vez de ficar implícita,
que era o problema original.

### Uma guarda que o teste obrigou a acrescentar

A primeira versão aplicava a regra das 7 linhas literalmente, e **anulou a R5**,
que tem apenas 29% de cópia e 77 palavras próprias. Resultado errado.

A causa é que a regra pressupõe redação de tamanho normal. A folha do ENEM tem
30 linhas; ali, sobrar 7 linhas próprias significa que o resto é cópia. Num
texto de 11 linhas, sobrar 7 próprias significa o contrário.

A guarda acrescentada exige que a cópia seja dominante
(`PERCENTUAL_COPIA_DOMINANTE = 50`) além da produção própria ser insuficiente.
Isso honra o título da regra na grade — "Texto **composto por** cópia" — mas
**não está literalmente escrito nela**. É decisão de projeto e vale confirmar
com a Profa. Daniela.

Resultado sobre o corpus, com a guarda:

| Redação | Cópia | Palavras próprias | Linhas próprias | Decisão |
|---|---|---|---|---|
| R1 | 0% | 251 | 25 | sem ajuste |
| R2 | 0% | 189 | 18 | sem ajuste |
| R3 | 0% | 124 | 12 | sem ajuste |
| R5 | 29% | 77 | 7 | teto C2 = 80 |
| R6 | 45% | 80 | 8 | teto C2 = 80 |
| R4 | 70% | 28 | 2 | **anula** |

O comportamento da R4 coincide com o que o modelo já fazia (anulava nas dez
execuções), mas agora é regra auditável em código, com limiar escrito, e não
julgamento implícito que variava entre sessões.

O teto aplicado à R5 ataca diretamente o problema de validade que o experimento
identificou: a R5 (29% copiada, bem escrita porque copiada) tirava 556 e
superava a R3 (original, fraca, 376). Com a Competência II limitada a 80, essa
inversão diminui.

O limiar de "muitos trechos de cópia" para o teto da Competência II
(`PERCENTUAL_MUITA_COPIA = 25`) é decisão de projeto, não da grade. A grade não
quantifica. Está explícito e ajustável de propósito.

## Como medir se funcionou

**Não aplique isto em produção sem medir.** Trocar o prompt sem medição é
substituir um viés conhecido por um desconhecido.

O harness já existe: `pesquisa/experimento_confiabilidade.py` roda a mesma
redação N vezes e tabula a dispersão. Para esta calibração ele precisa de uma
mudança: comparar com gabarito em vez de consigo mesmo.

O que falta é o conjunto de dados, e ele existe — **peça ao Caio as redações
com as notas oficiais por competência**. Com isso dá para rodar:

1. **Linha de base.** Prompt atual sobre as N redações, uma passada.
2. **Calibrado.** Mesmo conjunto, prompt novo.
3. **Comparar**, por competência e no total:
   - erro médio com sinal (o viés — tem que cair perto de zero);
   - erro absoluto médio (comparar com os 40 pontos);
   - quantas redações ficam fora da margem de 100 pontos na nota final;
   - o caso específico das redações fracas, que é onde o erro era maior.

Uma regra de método: **mude uma coisa por vez.** Não troque o modelo na mesma
rodada em que troca o prompt, ou não se saberá o que causou a diferença. O
experimento já mediu que trocar de modelo sozinho desloca a nota em cerca de 55
pontos.

## Implicação para o artigo

Este conjunto de dados resolve a pergunta de pesquisa que estava bloqueada.

O artigo da RECIMA21 tinha a PP2 — "a nota atribuída concorda com a de
avaliadores humanos?" — sem resposta, por falta de corpus com nota oficial. As
amostras da Profa. Daniela são exatamente isso, e com uma vantagem sobre o
Essay-BR: são redações do contexto real do cursinho, corrigidas por corretoras
treinadas pelo INEP.

Vale pedir autorização de uso para pesquisa e registrar a procedência.

## Custo

O prompt novo tem cerca de 1.800 tokens e é fixo em toda requisição. Vale ativar
cache de prompt no bloco de sistema — ele passa a ser cobrado como leitura de
cache a partir da segunda chamada:

```python
system=[{
    "type": "text",
    "text": PROMPT_SISTEMA,
    "cache_control": {"type": "ephemeral"},
}]
```

Confira `usage.cache_read_input_tokens` depois: se vier zero em chamadas
repetidas, alguma coisa está invalidando o prefixo.
