# Artigo — esqueleto de trabalho

> Estrutura conforme o **template oficial** `TEMPLATE 13.08.2026-OTH.docx`.
> O texto final vai para esse template em Word, sem alterar as margens.
>
> Convenções: **[ESCREVER]** ainda não redigido · **[BLOQUEADO]** depende de
> dado que não temos · **[VERIFICAR]** afirmação sem fonte confirmada.
>
> Alvo: 13 a 18 páginas em Arial 10, espaço 1,5 → cerca de **6.000 palavras**.

---

## TÍTULO DO ARTIGO

**Português** — centralizado, negrito, tudo em maiúsculo:

> CONFIABILIDADE E LIMITES DE UM SISTEMA DE CORREÇÃO AUTOMÁTICA DE REDAÇÕES DO
> ENEM BASEADO EM MODELOS DE LINGUAGEM

**Inglês** — negrito e itálico:

> *Reliability and limits of a large language model-based automated essay
> scoring system for the Brazilian ENEM examination*

**Espanhol** — negrito e itálico:

> *Confiabilidad y límites de un sistema de corrección automática de
> redacciones del ENEM basado en modelos de lenguaje*

---

## DADOS DOS AUTORES

**Deixar EM BRANCO na submissão inicial** — avaliação cega. Preencher só na
versão final, após aprovação.

Formato exigido: nome completo, instituição, titulação. Nada além disso.
Exemplo do template: `João Souza, UNIPP, mestre.`

**Pendente:** definir autoria (você sozinho ou com a Profa. Ana Paula) e obter
ORCID.

---

## RESUMO · ABSTRACT · RESUMEN — 250 palavras cada **[ESCREVER POR ÚLTIMO]**

Estruturado, nesta ordem: **objetivo, método, resultados, conclusões.**
Espaço simples, justificado, Arial 10.

Redigir **do zero**, sem reaproveitar frases do resumo do JECET — a revista roda
verificador de similaridade e trata autoplágio como impedimento.

**PALAVRAS-CHAVE** (separadas por ponto final, conforme o template):

> Correção automática de redações. Modelos de linguagem. ENEM. Confiabilidade.
> Detecção de cópia. Avaliação educacional.

**KEYWORDS:**

> Automated essay scoring. Large language models. ENEM. Reliability. Copy
> detection. Educational assessment.

**PALABRAS CLAVE:**

> Corrección automática de redacciones. Modelos de lenguaje. ENEM.
> Confiabilidad. Detección de copia. Evaluación educativa.

---

## INTRODUÇÃO — sem número — ~800 palavras **[ESCREVER]**

O template exige quatro elementos **explícitos**. Não podem ficar implícitos.

### Problema

A devolutiva de redação é escassa porque depende de corretor humano
especializado, e a escassez é desigual: quem paga cursinho recebe correção
frequente, quem não paga recebe pouca ou nenhuma. Modelos de linguagem tornaram
tecnicamente trivial construir um corretor automático — mas **não se sabe se o
que ele produz é medida**.

### Justificativa

Sistemas de correção automática já estão em uso com estudantes reais, inclusive
em plataformas públicas. Se um instrumento de avaliação não for confiável, ele
não devolve informação: devolve ruído com aparência de nota. Medir isso antes de
expor estudantes é condição para uso responsável — e é o que este trabalho faz,
num sistema construído como projeto de extensão e disponibilizado gratuitamente.

### Objetivo geral

Avaliar a confiabilidade e os limites de um sistema de correção automática de
redações do ENEM baseado em modelos de linguagem.

### Objetivos específicos

1. Medir a variação da nota atribuída à mesma redação entre execuções idênticas.
2. Verificar se essa variação depende do modelo utilizado ou das características
   da redação avaliada.
3. Medir a precisão e o recall do detector de trechos copiados dos textos
   motivadores.
4. Identificar como a regra de anulação por cópia é aplicada na prática.

### Perguntas de pesquisa

- **PP1.** Dada a mesma redação, quanto a nota varia entre execuções idênticas?
- **PP2.** A nota atribuída concorda com a de avaliadores humanos? **[BLOQUEADO]**
- **PP3.** O detector de cópia acerta quais palavras foram copiadas?

### Fechamento

Como o texto está organizado.

> **[VERIFICAR]** — o problema precisa de fonte para a desigualdade de acesso a
> devolutiva de redação no Brasil. Ver lacuna 1 em `referencias.md`.

---

## 1 – REFERENCIAL TEÓRICO — ~1.500 palavras

### 1.1 Da regressão aos modelos de linguagem — ~400 palavras **[ESCREVER]**

Page (1966) inaugura a área com o Project Essay Grade e estabelece a distinção
que ainda organiza o problema: *trins*, os traços intrínsecos que se quer medir,
e *proxes*, as aproximações computáveis que de fato se medem. Attali e Burstein
(2006) e o e-rater representam a geração de extração de atributos mais
regressão. A virada para modelos de linguagem elimina a engenharia de atributos,
mas **não elimina a distância entre trin e prox** — apenas a torna opaca.

### 1.2 A redação do ENEM e a regra de cópia — ~300 palavras **[ESCREVER]**

As cinco competências, a escala de 0 a 200 por competência, o total de 1.000
pontos. A regra de que trechos copiados dos textos motivadores não contam como
produção do participante (INEP, 2024). É essa regra que justifica a existência
do detector — e é ela que o experimento 3 põe à prova.

### 1.3 Confiabilidade e validade — ~400 palavras **[ESCREVER]**

A distinção que organiza o artigo inteiro. Um instrumento pode ser perfeitamente
confiável e completamente inválido: uma balança descalibrada que marca sempre
3 kg a mais é perfeitamente confiável e não mede peso. Confiabilidade é
condição necessária e insuficiente. Perelman (2014) argumenta que os sistemas de
correção automática medem *proxies* — extensão do texto, frequência de palavras
raras — e não o construto "capacidade de escrever".

> **[VERIFICAR]** — falta fonte de teoria da medida em avaliação educacional,
> não só de processamento de linguagem. Lacuna 3 em `referencias.md`.

### 1.4 Correção automática em português — ~400 palavras **[ESCREVER]**

Marinho, Anchieta e Moura (2021) e o Essay-BR: 4.570 redações de estudantes
brasileiros avaliadas por especialistas nas cinco competências, sob licença MIT.
Barbosa, Silveira e Mauá (2025) estabelecem o estado da arte no conjunto, com
QWK entre 0,60 e 0,73 por competência, e concluem que nenhuma arquitetura domina
sempre. É contra esse número que a PP2 se compara.

---

## 2 – METODOLOGIA — ~1.300 palavras

### 2.1 O sistema avaliado — ~350 palavras **[ESCREVER]**

Aplicação web; correção nas cinco competências com devolutiva textual por
competência; detector determinístico de cópia alimentando o prompt do modelo.
Descrever no nível que permite replicação.

> **Sigilo:** não citar o endereço do repositório nem o da página do projeto.
> Ambos identificam o autor e quebram a avaliação cega.

### 2.2 O detector de cópia — ~250 palavras **[ESCREVER]**

*Shingles* de sete palavras. Normalização por NFD, removendo acentuação,
pontuação e caixa antes de comparar. Constrói-se o conjunto de todas as
sequências de sete palavras dos textos de apoio; percorre-se a redação marcando
as sequências já presentes nesse conjunto; palavras marcadas contíguas formam
trechos. O percentual e os trechos são entregues ao modelo.

### 2.3 Experimento 1 — confiabilidade teste-reteste — ~300 palavras **[ESCREVER]**

6 redações × 2 modelos × 10 repetições = **120 correções**. Mesmo prompt, mesma
`max_tokens` (8.000), mesma montagem de entrada; varia apenas o modelo. O corpus
cobre um gradiente de cópia **medido pelo detector**, não estimado: 0%, 0%, 0%,
29%, 45% e 70%.

Declarar aqui: as redações foram escritas pelo autor para o experimento; não há
seres humanos nem dados sensíveis envolvidos, portanto não se aplica a exigência
de aprovação por comitê de ética.

### 2.4 Experimento 2 — concordância com nota humana **[BLOQUEADO]**

Essay-BR, QWK por competência, comparação com Barbosa, Silveira e Mauá (2025).

**Falta o arquivo de resultados.** Sem nota humana e nota do sistema por redação
e por competência, não há como calcular nem reportar. Se não vier, esta
subseção sai e a PP2 vira trabalho futuro.

### 2.5 Experimento 3 — precisão e recall do detector — ~400 palavras **[ESCREVER]**

Aqui existe **gabarito exato**: a cópia é injetada, então sabe-se palavra por
palavra o que deveria ser marcado. Trechos literais dos textos de apoio são
inseridos nas redações originais (R1, R2, R3), em três posições de cada uma.
Três testes: tamanho do trecho copiado, resistência à substituição de palavras,
e falso positivo em texto original.

---

## 3 – RESULTADOS E DISCUSSÃO — ~2.000 palavras **[ESCREVER]**

Uma seção só, conforme o template. Cada resultado é apresentado e discutido no
mesmo movimento. **Toda tabela precisa ser mencionada e discutida no texto** —
exigência explícita do template.

### 3.1 A variância acompanha a ambiguidade, não o modelo

**Este é o achado central do artigo.**

**Tabela 1 — Dispersão da nota por redação e modelo (n = 10)**

| Cópia medida | Redação | CV opus-5 | CV sonnet-4-5 | Idênticas (opus) |
|---|---|---|---|---|
| 0% | R1 | 0,0% | 3,0% | 10/10 |
| 0% | R2 | 0,0% | 5,1% | 10/10 |
| 0% | R3 | 5,5% | 4,5% | 6/10 |
| 29% | R5 | **12,0%** | **14,8%** | **4/10** |
| 45% | R6 | **11,4%** | 0,0% | **3/10** |
| 70% | R4 | 0,0% | 0,0% | 10/10 |

**Tabela 2 — Agregado por modelo**

| Modelo | Amplitude média | CV médio |
|---|---|---|
| claude-opus-5 | 60,0 pontos | 5,8% |
| claude-sonnet-4-5 | 60,0 pontos | 5,5% |

Amplitude média idêntica entre os dois modelos. A dispersão é máxima na faixa de
cópia parcial e desaparece nos extremos. O sistema é decidido onde a decisão é
fácil e vacila onde um corretor humano também deliberaria — só que sem sinalizar
essa incerteza ao aluno.

### 3.2 A regra de anulação é degrau sem limiar escrito

**Tabela 3 — Frequência de anulação por faixa de cópia**

| Cópia medida | Zerou (opus-5) | Zerou (sonnet-4-5) | Nota média (opus) |
|---|---|---|---|
| 0% | 0/10 | 0/10 | 376 a 960 |
| 29% | 0/10 | 0/10 | 556 |
| 45% | 0/10 | 0/10 | 380 |
| 70% | **10/10** | **10/10** | 0 |

Nada zera até 45% de cópia; tudo zera em 70%. O limiar não existe em lugar
nenhum do código — está implícito no julgamento do modelo, apesar de o detector
fornecer o percentual exato. Decisão de alto impacto delegada a um componente
não auditável.

### 3.3 O componente determinístico é frágil onde parecia sólido

**Tabela 4 — Detecção por tamanho do trecho copiado**

| Palavras copiadas | Precisão | Recall |
|---|---|---|
| 3 a 6 | — | **0,0%** |
| 7 | 100,0% | **100,0%** |
| 8 | 98,6% | 100,0% |
| 10 | 98,9% | 100,0% |
| 15 a 30 | 100,0% | 100,0% |

**Tabela 5 — Efeito da substituição de palavras (trecho de 30 palavras)**

| Substituições | Uma a cada | Precisão | Recall |
|---|---|---|---|
| 0 | — | 100,0% | 100,0% |
| 1 | 30 palavras | 100,0% | 96,7% |
| 2 | 15 palavras | 100,0% | 93,3% |
| 3 | 10 palavras | 100,0% | **50,0%** |
| 4 | 7,5 palavras | — | **0,0%** |

Trocar 4 palavras em 30 leva o recall a zero. A precisão nunca cai: o detector
erra sempre para o mesmo lado, deixando passar em vez de acusar. Para uso
avaliativo essa é a direção menos danosa, mas o sistema não pode ser apresentado
como barreira contra cópia.

Nenhum falso positivo nas três redações originais (0 de 251, 0 de 189, 0 de 124).

### 3.4 Copiar compensa mais que escrever mal

A R5 (29% copiada, bem escrita *porque* copiada) obteve 556; a R3 (original,
fraca) obteve 376. Problema de validade do instrumento, não de implementação.
Conecta direto com a crítica de Perelman (2014) sobre medir *proxies*.

### 3.5 Trocar de modelo não é substituição transparente

O `claude-opus-5` atribui em média **+55 pontos** a mais que o
`claude-sonnet-4-5`, sendo mais alto em 5 das 6 redações (empate na que ambos
zeraram). Não é ruído: a direção é consistente. Desloca a nota de todos os
alunos em cerca de meia competência.

### 3.6 Anomalia entre sessões

No piloto (n = 3) a R4 recebeu 120, 0 e 200 do `claude-opus-5`. Na corrida
completa (n = 10), a mesma redação recebeu 0 nas dez vezes. Mesmo texto, mesmo
prompt, mesmo modelo, sessões diferentes. **Não há explicação e não será
inventada uma.** Fica registrado como indício de variabilidade entre sessões, o
que exigiria desenho com coleta distribuída no tempo.

### 3.7 Síntese

Confiável onde não importa, instável onde importa. É o inverso do que se espera
de um instrumento de avaliação.

---

## 4 – CONSIDERAÇÕES FINAIS — ~700 palavras **[ESCREVER]**

**Recomendações de projeto, derivadas dos achados:**

1. O limiar de anulação por cópia deve ser regra determinística em código, com
   valor justificado e auditável — não julgamento do modelo.
2. A nota deve vir acompanhada de indicação de incerteza quando o caso cai na
   faixa ambígua.
3. O sistema não pode ser apresentado como barreira contra cópia. Ele detecta
   cópia literal, e só.
4. Trocar o modelo exige recalibração; não é substituição transparente.
5. O tamanho do *shingle* precisa de justificativa empírica, com a curva de
   sensibilidade contra falso positivo levantada.

**Limitações:** corpus escrito para o experimento e sem nota oficial; n = 10 por
célula, suficiente para descrever dispersão e insuficiente para teste de
hipótese com poder adequado; dois modelos de um único fornecedor; um único tema,
com o efeito do tema não isolado.

**Trabalhos futuros:** concordância com nota humana no Essay-BR; curva de
sensibilidade do detector; desenho com coleta distribuída no tempo.

### Declaração de uso de inteligência artificial

O template não prevê seção para isso, mas as normas da revista exigem. Entra
como **parágrafo final desta seção**, antes das referências. Precisa cobrir os
dois usos: a IA como **objeto** do estudo e a IA como **ferramenta** na
preparação do manuscrito. O autor permanece responsável pelo conteúdo final.

---

## REFERÊNCIAS

ABNT, ordem **alfabética e cronológica**, espaço simples dentro de cada
referência e 1,5 entre elas. DOI sempre que disponível.

**Atenção:** referência não citada no corpo do texto **será removida na
editoração**. Conferir a correspondência nos dois sentidos antes de enviar.

Lista verificada em `referencias.md`. Hoje: **7 confirmadas**, meta de 20 a 25.

---

## Status

| Seção | Situação | Palavras |
|---|---|---|
| Títulos (3 idiomas) | Pronto | — |
| Resumos (3 idiomas) | Escrever por último | 750 |
| Introdução | A escrever — falta 1 fonte | 800 |
| 1 Referencial teórico | A escrever — faltam fontes | 1.500 |
| 2 Metodologia | A escrever — 2.4 bloqueado | 1.300 |
| 3 Resultados e discussão | Dados prontos, texto a escrever | 2.000 |
| 4 Considerações finais | Argumento pronto, texto a escrever | 700 |
| Referências | 7 de ~25 | — |

Total projetado: ~6.300 palavras + tabelas → dentro da faixa de 13 a 18 páginas.
