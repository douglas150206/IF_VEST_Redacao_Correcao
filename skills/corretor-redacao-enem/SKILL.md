---
name: corretor-redacao-enem
description: Corrige redações do ENEM nas cinco competências aplicando a Grade Específica de Avaliação usada internamente pelo INEP, com detecção automática de cópia dos textos motivadores. Use sempre que alguém pedir para corrigir, avaliar, pontuar ou dar nota a uma redação do ENEM ou de simulado; para conferir se uma nota atribuída está de acordo com os critérios do INEP; para comparar a correção de uma IA com a de um corretor humano e analisar a divergência; ou para verificar se uma redação copiou os textos motivadores. Use também quando a pessoa só colar o texto de uma redação e perguntar "que nota isso tira?", "está bom?" ou "o que precisa melhorar?", mesmo sem mencionar ENEM ou competências explicitamente.
---

# Correção de redação do ENEM

Esta skill aplica a **Grade Específica de Avaliação** — o documento operacional
que o INEP usa internamente, mais detalhado que a Cartilha do Participante
publicada para estudantes. A diferença que importa está nos **tetos
obrigatórios**: regras que impedem a nota de subir mesmo quando o texto parece
bom em outros aspectos. São eles que separam uma correção calibrada de uma
correção branda.

## Por que o rigor importa aqui

Corretores automáticos tendem a ser mais generosos que corretores humanos
treinados. Em testes com amostras reais corrigidas por corretoras do INEP, a
correção automática ficou em média de 40 a 80 pontos acima da oficial, e o erro
foi maior justamente nas redações fracas — casos de nota oficial 320 receberam
de 520 a 600.

Isso prejudica quem a ferramenta deveria ajudar. Um aluno que merece 520 e ouve
580 conclui que está mais perto do que está, e a devolutiva perde o valor
diagnóstico que é a razão de existir dela.

Então: **em dúvida entre dois níveis, atribua o menor.** Não arredonde para cima
por esforço, boa intenção ou tema bem escolhido. Um texto mediano mas correto é
nível 3, não 4.

## Fluxo

1. **Verifique a hierarquia de anulação** antes de qualquer pontuação. Se uma
   das situações se aplicar, as cinco competências recebem 0 e a correção
   termina aí, com a explicação do motivo.
2. **Detecte cópia** dos textos motivadores, quando eles estiverem disponíveis.
   Use o script `scripts/detectar_copia.py` em vez de estimar a olho — a
   detecção por n-gramas encontra correspondência literal que a leitura humana
   deixa passar, e devolve o percentual exato.
3. **Pontue cada competência**, aplicando os tetos obrigatórios.
4. **Escreva a devolutiva**, apontando evidência concreta do texto.

## Escala

Cada competência recebe um nível inteiro de 0 a 5, convertido em pontos de 40
em 40:

| Nível | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| Pontos | 0 | 40 | 80 | 120 | 160 | 200 |

A nota total é a soma das cinco. Não existe valor intermediário — não atribua
100 ou 150.

Os operadores nos descritores não são intercambiáveis: **E** exige as duas
condições, **OU** basta uma, **E/OU** admite qualquer combinação.

## Competência I — domínio da norma culta

| Nível | Descritor |
|---|---|
| 0 | Estrutura sintática inexistente (independentemente da quantidade de desvios) |
| 1 | Estrutura sintática deficitária **COM** muitos desvios |
| 2 | Estrutura sintática deficitária **OU** muitos desvios |
| 3 | Estrutura sintática regular **E** alguns desvios |
| 4 | Estrutura sintática boa **E** poucos desvios |
| 5 | Estrutura sintática excelente (no máximo uma falha) **E** no máximo dois desvios |

## Competência II — compreensão da proposta

Esta competência não admite nível 0. Redação que receberia 0 aqui é fuga ao
tema, e nesse caso não é corrigida — ver hierarquia de anulação.

| Nível | Descritor |
|---|---|
| 1 | Tangência ao tema **OU** aglomerado caótico de palavras **OU** traços constantes de outros tipos textuais |
| 2 | Abordagem completa **E** (2 partes do texto **OU** 3 partes com 2 embrionárias **OU** conclusão finalizada por ideia incompleta) |
| 3 | Abordagem completa **E** 3 partes (1 pode ser embrionária) **E** repertório baseado nos motivadores **E/OU** não legitimado **E/OU** legitimado mas não pertinente |
| 4 | Abordagem completa **E** 3 partes (nenhuma embrionária) **E** repertório legitimado e pertinente, **SEM** uso produtivo |
| 5 | Abordagem completa **E** 3 partes (nenhuma embrionária) **E** repertório legitimado e pertinente, **COM** uso produtivo |

**Tetos obrigatórios:**
- Muitos trechos de cópia → **não passa do nível 2**.
- Corpo do texto com até 8 linhas → **não passa do nível 3**.
- Mais de 8 linhas sem que se reconheçam as 3 partes → **não passa do nível 3**.

## Competência III — seleção e organização de argumentos

| Nível | Descritor |
|---|---|
| 0 | Aglomerado caótico de palavras, independentemente da abordagem do tema |
| 1 | Projeto de texto sem foco temático ou com foco distorcido |
| 2 | Projeto com muitas falhas **E** sem desenvolvimento, ou desenvolvimento de apenas uma informação, fato ou opinião |
| 3 | Projeto com algumas falhas **E** desenvolvimento com algumas lacunas |
| 4 | Projeto com poucas falhas **E** desenvolvimento com poucas lacunas |
| 5 | Projeto estratégico **E** desenvolvimento em todo o texto (admitem-se deslizes pontuais) |

**Tetos obrigatórios:**
- Texto tangente ao tema → **não passa do nível 1**.
- Contradição grave → **não passa do nível 2**.

## Competência IV — mecanismos de coesão

| Nível | Descritor |
|---|---|
| 0 | Ausência de articulação: palavras **E/OU** períodos desconexos em todo o texto |
| 1 | Presença rara de elementos coesivos **E/OU** excessivas repetições **E/OU** excessivas inadequações |
| 2 | Presença pontual **E/OU** muitas repetições **E/OU** muitas inadequações |
| 3 | Presença regular **E/OU** algumas repetições **E/OU** algumas inadequações |
| 4 | Presença constante **E/OU** poucas repetições **E/OU** poucas inadequações |
| 5 | Presença expressiva **E** repetições raras ou ausentes **E** sem inadequação |

**Teto obrigatório:**
- Texto em monobloco, sem divisão em parágrafos → **não passa do nível 2**.

## Competência V — proposta de intervenção

Conta-se quantos dos cinco elementos estão presentes e válidos: **ação**,
**agente**, **modo ou meio** de execução, **efeito ou finalidade**, e
**detalhamento** de um dos anteriores.

| Nível | Descritor |
|---|---|
| 0 | Ausência de proposta **OU** proposta que desrespeita os direitos humanos **OU** proposta não relacionada ao assunto |
| 1 | Tangenciamento do tema **OU** apenas elemento(s) nulo(s) **OU** 1 elemento válido |
| 2 | 2 elementos válidos |
| 3 | 3 elementos válidos |
| 4 | 4 elementos válidos |
| 5 | 5 elementos válidos |

**Tetos obrigatórios:**
- Estrutura condicional ("se o governo fizesse...") com 2 ou mais elementos → **não passa do nível 2**.
- Proposta sem o elemento **AÇÃO** → **não passa do nível 2**.

## Hierarquia de anulação

Verifique nesta ordem. Qualquer uma zera as cinco competências.

1. **Formas elementares** — desenho ou emoticon, número isolado sem função
   evidente, sinal gráfico isolado, anulação proposital (risco ou rasura
   indicando desejo de anular), texto ilegível, ou texto predominantemente em
   língua estrangeira sem que restem mais de 7 linhas em português.
2. **Cópia** — texto composto por cópia dos textos motivadores, sem que reste
   mais de 7 linhas de produção própria.
3. **Fuga ao tema** — não trata do tema nem do assunto proposto.
4. **Não atendimento ao tipo textual** — escrito integral ou
   predominantemente em tipo diferente do dissertativo-argumentativo.
5. **Parte desconectada** — impropério, ofensa, zombaria, reflexão sobre a
   prova, recado, oração, mensagem política, ou trecho sobre outro assunto,
   desconectados do projeto de texto.

Ao analisar texto digitado, note que vários itens do grupo 1 (desenho, texto
ilegível, rasura) não são detectáveis — diga isso em vez de afirmar que não
ocorreram.

Sobre **identificação do participante** no corpo do texto: na grade oficial ela
é parte desconectada e anula. Em simulados, bancas frequentemente decidem não
anular por isso. Quando encontrar identificação, sinalize e pergunte qual regra
vale, em vez de anular silenciosamente.

## Detecção de cópia

Rode o script em vez de julgar a olho:

```bash
python scripts/detectar_copia.py --redacao redacao.txt --apoio motivadores.txt
```

Ele devolve o percentual copiado, os trechos encontrados, as linhas de produção
própria e se a regra de anulação se aplica. Aceita também `--texto` e `--apoio-texto`
para passar o conteúdo direto na linha de comando.

Duas coisas que o script **não** faz, e que exigem leitura sua:

- Ele detecta apenas **cópia literal**. Trocar quatro palavras num trecho de
  trinta já derruba a detecção a zero. Se o texto parecer copiado mas o script
  não acusar, confie na leitura e registre a suspeita.
- Ele não distingue cópia de **citação legítima**. Um trecho entre aspas, com
  atribuição, é repertório, não cópia. Verifique antes de penalizar.

## Formato da devolutiva

Para cada competência, informe o nível, os pontos e de 2 a 3 frases de
justificativa que **citem evidência concreta** — um trecho, uma construção, uma
ausência específica. Observação genérica que serviria para qualquer redação não
ajuda ninguém a melhorar.

Quando aplicar um teto obrigatório, diga qual foi e por quê. O aluno precisa
saber que a nota foi limitada por uma regra, não por julgamento de qualidade.

Feche com a nota total e as duas ou três mudanças que mais elevariam a nota,
em ordem de impacto.

## Comparar duas correções

Quando a tarefa for comparar uma correção automática com a de um corretor
humano, ou duas correções humanas, leia `references/comparar-correcoes.md`.
As margens de tolerância e a distinção entre viés e ruído estão lá, e aplicá-las
errado leva à conclusão oposta da correta.

## Procedência

Grade Específica de Avaliação do ENEM 2025, documento interno cedido pela
Profa. Daniela Matos ao projeto IFvest — Redação + IA, do IFSP Campus Jacareí.

Este arquivo e o módulo `porte_fastapi/corretor/grade_inep.py` do sistema são
duas versões da mesma grade: um para uso interativo, outro para o prompt de
produção. **Ao ajustar um critério, atualize os dois**, ou a equipe e o sistema
passam a corrigir com réguas diferentes sem ninguém perceber.
