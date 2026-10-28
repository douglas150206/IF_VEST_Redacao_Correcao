# Experimentos para o artigo

## Experimento 1 — confiabilidade teste-reteste

**Pergunta:** dada a mesma redação, quanto a nota varia entre execuções idênticas?

Isso mede **consistência**, não acurácia. O corpus não tem gabarito oficial, então
nada aqui diz que as notas estão certas — diz se o sistema responde a mesma coisa
quando perguntado duas vezes, que é pré-requisito para qualquer uso avaliativo.

### Método

6 redações × 2 modelos × 10 repetições = **120 correções**. Mesmo prompt, mesma
`max_tokens` (8000), mesma montagem de entrada do módulo de produção; varia só o
modelo. Corpus com gradiente de cópia dos textos motivadores, com o percentual
**medido pelo detector**, não estimado.

```bash
python experimento_confiabilidade.py --estimar        # tamanho da corrida
python experimento_confiabilidade.py --repeticoes 10  # roda
python analisar.py                                    # tabelas do artigo
```

### Resultado 1 — os dois modelos são indistinguíveis em confiabilidade

| Modelo | Amplitude média | CV médio |
|---|---|---|
| claude-opus-5 | 60,0 pontos | 5,8% |
| claude-sonnet-4-5 | 60,0 pontos | 5,5% |

Não há diferença de confiabilidade entre os modelos testados. **Duas conclusões
anteriores deste projeto afirmavam o contrário** — uma em cada direção — e as duas
vinham de amostras pequenas (n=1 e n=3). Ficam registradas como exemplo de por que
n pequeno não sustenta afirmação sobre variância.

### Resultado 2 — a variância acompanha a ambiguidade, não o modelo

| Cópia medida | Redação | CV opus-5 | CV sonnet-4-5 | Respostas idênticas (opus) |
|---|---|---|---|---|
| 0% | R1 (alta) | 0,0% | 3,0% | 10/10 |
| 0% | R2 (média) | 0,0% | 5,1% | 10/10 |
| 0% | R3 (baixa) | 5,5% | 4,5% | 6/10 |
| **29%** | R5 | **12,0%** | **14,8%** | **4/10** |
| **45%** | R6 | **11,4%** | 0,0% | **3/10** |
| 70% | R4 | 0,0% | 0,0% | 10/10 |

A dispersão é máxima na faixa de **cópia parcial** e desaparece nos extremos. O
sistema é decidido justamente onde a decisão é fácil, e vacila onde um corretor
humano também deliberaria — só que sem sinalizar essa incerteza ao aluno.

### Resultado 3 — a regra de cópia é degrau, não rampa

| Cópia medida | Zerou (opus-5) | Zerou (sonnet-4-5) | Nota média (opus) |
|---|---|---|---|
| 0% | 0/10 | 0/10 | 376–960 |
| 29% | 0/10 | 0/10 | 556 |
| 45% | 0/10 | 0/10 | 380 |
| 70% | **10/10** | **10/10** | 0 |

O prompt pede penalização proporcional ao percentual copiado e zeramento quando a
redação é "essencialmente cópia". O modelo implementa isso como função degrau: nada
zera até 45%, tudo zera em 70%. Há penalização gradual na nota (380 contra 960),
mas o zeramento é binário e o limiar não é controlado por ninguém — está implícito
no julgamento do modelo, apesar de o detector fornecer o percentual exato.

**Implicação de projeto:** o limiar deveria ser regra determinística em código, não
julgamento do modelo.

### Resultado 4 — viés sistemático de leniência entre modelos

`claude-opus-5` atribui em média **+55 pontos** a mais que `claude-sonnet-4-5`,
mais alto em 5 das 6 redações (empate na que ambos zeraram). Não é ruído: a direção
é consistente. Trocar de modelo desloca a nota de todos os alunos em cerca de meia
competência.

### Resultado 5 — copiar compensa mais que escrever mal

R5 (29% copiado, texto bem escrito porque copiado) obteve **556**; R3 (0% de cópia,
texto original fraco) obteve **376**. O aluno que copia um terço do texto motivador
é melhor avaliado que o que escreve mal com as próprias palavras. Isso é um
problema de validade do instrumento, e vale discussão no artigo.

### Anomalia registrada

No piloto (n=3), a R4 recebeu 120, 0 e 200 do `claude-opus-5`. Na corrida completa
(n=10), a mesma redação recebeu 0 nas dez vezes. Mesmo texto, mesmo prompt, mesmo
modelo, sessões diferentes. Não temos explicação e não vamos inventar uma — fica
registrado como indício de que a variabilidade pode existir **entre sessões**, e não
só entre chamadas, o que exigiria um desenho experimental com coleta distribuída no
tempo.

### Limitações

- **As redações foram escritas para o experimento.** Não são do ENEM e não têm nota
  oficial. Para confiabilidade isso não invalida (mede-se dispersão sobre o mesmo
  texto), mas impede qualquer afirmação sobre acurácia.
- n=10 por célula. Suficiente para descrever dispersão, insuficiente para teste de
  hipótese com poder adequado.
- Dois modelos de um único fornecedor.
- Um único tema. O efeito do tema não foi isolado.

### Custo

120 correções, 151.937 tokens de saída, 44 minutos de processamento.

## Experimento 3 — precisão e recall do detector de cópia

**Pergunta:** o componente determinístico do sistema acerta quais palavras foram
copiadas?

Diferente do experimento 1, aqui existe **gabarito exato**: nós injetamos a
cópia, então sabemos palavra por palavra o que deveria ser marcado. A métrica é
aritmética, sem juízo humano no meio.

```bash
python experimento_deteccao_copia.py --json resultados/deteccao_copia.json
```

### Método

Trechos literais dos textos de apoio são inseridos em redações originais (R1,
R2, R3 — as que o detector mede 0%), em três posições distintas de cada uma.
Compara-se, palavra a palavra, o que o detector marcou com o que foi injetado.

### Resultado 1 — a detecção é degrau exato no tamanho do shingle

| Palavras copiadas | Precisão | Recall |
|---|---|---|
| 3 a 6 | — | **0,0%** |
| 7 | 100,0% | **100,0%** |
| 8 | 98,6% | 100,0% |
| 10 | 98,9% | 100,0% |
| 15 a 30 | 100,0% | 100,0% |

Abaixo de 7 palavras o detector não vê **nada**; a partir de 7 ele vê **tudo**.
Isso é consequência direta do parâmetro, não defeito de implementação — mas tem
efeito prático: quem copia em pedaços de seis palavras é invisível.

A precisão abaixo de 100% em 8 e 10 palavras vem de efeito de borda: uma janela
que atravessa a emenda entre a redação e o trecho injetado pode casar por
coincidência e marcar uma palavra vizinha que era original.

### Resultado 2 — uma edição trivial derruba a detecção

Trecho copiado de 30 palavras, com substituições espalhadas:

| Substituições | Uma a cada | Precisão | Recall |
|---|---|---|---|
| 0 | — | 100,0% | 100,0% |
| 1 | 30 palavras | 100,0% | 96,7% |
| 2 | 15 palavras | 100,0% | 93,3% |
| 3 | 10 palavras | 100,0% | **50,0%** |
| 4 | 7,5 palavras | — | **0,0%** |
| 5 | 6 palavras | — | 0,0% |

**Trocar 4 palavras em 30 zera a detecção.** Como nenhuma janela de 7 palavras
permanece intacta, o algoritmo não encontra nada — e o aluno recebe 0% de cópia
com um texto 87% copiado.

A precisão nunca cai: o detector **erra sempre para o mesmo lado**. Ele não
acusa quem não copiou; ele deixa passar quem copiou. Para uso avaliativo essa é
a direção menos danosa, mas o sistema não pode ser apresentado como barreira
contra cópia — ele detecta cópia literal e só.

### Resultado 3 — nenhum falso positivo

| Redação | % detectado | Palavras marcadas |
|---|---|---|
| R1 (original) | 0% | 0 de 251 |
| R2 (original) | 0% | 0 de 189 |
| R3 (original) | 0% | 0 de 124 |
| R5 | 29% | 32 de 109 |
| R6 | 45% | 65 de 145 |
| R4 | 70% | 65 de 93 |

Nenhuma palavra de texto original foi marcada. Coincidência de sete palavras
seguidas em português é rara o bastante para não gerar ruído neste corpus.

**Implicação de projeto:** o tamanho do shingle é o parâmetro que define o que o
sistema consegue ver, e hoje ele é uma constante escolhida sem justificativa
empírica. Reduzi-lo aumenta a sensibilidade e o risco de falso positivo; a
curva desse trade-off não foi levantada.

### Limitações

- Um único par de redação e textos de apoio. Corpus maior daria estimativa mais
  firme da taxa de falso positivo.
- A substituição usa uma palavra fixa e ausente do apoio, o que é o pior caso
  para o detector. Paráfrase real varia sintaxe também, e tende a ser ainda mais
  difícil de detectar.

## Experimento 2 — concordância com nota humana

**Pergunta:** a nota que o sistema atribui concorda com a de avaliadores
humanos?

Os experimentos 1 e 3 mediam o sistema contra ele mesmo. Este é o primeiro que
usa gabarito, e é o que faltava: sem referência externa, dá para ver a nota
mudar, mas não para saber se mudou na direção certa.

```bash
python experimento_concordancia.py --n 25 --prompt atual
python metricas_concordancia.py
```

### Método

Corpus **Essay-BR** (MARINHO; ANCHIETA; MOURA, 2021), licença MIT, split de
teste com 686 redações e nota por competência atribuída por avaliadores
humanos. Amostra de 25 redações, estratificada por faixa de nota com peso nas
faixas baixas, onde o erro relatado pela equipe de testes era maior. Semente
fixa, de modo que todas as variantes de prompt vejam exatamente as mesmas
redações.

Duas métricas, e a distinção entre elas organiza a leitura:

- **Viés** (erro médio com sinal): mede se o sistema é sistematicamente
  generoso ou severo. Não se compensa entre alunos.
- **Erro absoluto médio**: mede a acurácia. É o que se compara com os 40 pontos
  aceitos entre dois corretores humanos.

### Resultado 1 — o problema não é leniência

| Métrica | Valor |
|---|---|
| Viés | **+16 pontos** |
| Erro absoluto médio | **115 pontos** |
| Fora da margem de 100 | 10 de 25 (40%) |

A hipótese de trabalho da equipe era que o sistema é brando. **A medição não
sustenta isso.** O viés é desprezível; o que existe é dispersão. Um corretor
com média correta e erro de 115 pontos é inútil do mesmo jeito, mas o conserto
é outro — viés se corrige deslocando a régua, dispersão exige melhorar o
julgamento.

### Resultado 2 — QWK de 0,50, moderadamente abaixo do estado da arte

| Competência | QWK | r |
|---|---|---|
| C1 (norma culta) | 0,381 | 0,434 |
| C2 (compreensão) | 0,422 | 0,434 |
| C3 (argumentação) | 0,558 | 0,594 |
| C4 (coesão) | 0,572 | 0,686 |
| C5 (proposta) | 0,566 | 0,585 |
| **média** | **0,500** | — |

Correlação de 0,636 na nota total. Barbosa, Silveira e Mauá (2025) relatam QWK
de 0,60 a 0,73 por competência **neste mesmo corpus**, com modelos ajustados —
estado da arte publicado em português.

Um sistema construído sem ajuste fino chegar a 0,50 situa o trabalho: está
moderadamente abaixo da literatura, não fora dela. Os 115 pontos de erro
absoluto são o que essa qualidade de concordância produz numa escala de 1.000
somando cinco competências.

### Resultado 3 — três tentativas de calibração, nenhuma melhora

| Variante | QWK | Erro absoluto | Viés |
|---|---|---|---|
| **Prompt de produção** | **0,500** | **115** | **+16** |
| Grade específica do INEP | 0,437 | 125 | +13 |
| Ancoragem com exemplos | 0,494 | 126 | +75 |

**Grade específica.** Substituir a descrição genérica das competências pela
grade operacional do INEP, com descritores por nível e tetos obrigatórios,
**piorou** o QWK. Os tetos degradaram justamente as competências onde atuam
(C4 de 28,8 para 43,2 de erro; C5 de 33,6 para 46,4) e a hierarquia de anulação
produziu um falso positivo — uma redação de 240 foi zerada — sem capturar as
duas anulações verdadeiras.

**Ancoragem.** Incluir cinco redações reais já corrigidas (160, 280, 480, 680,
880) como régua dentro do prompt manteve o QWK e **estourou o viés**, de +16
para +75. A causa é identificável: as âncoras foram escolhidas pela nota total,
sem verificar o perfil por competência, e a de 160 pontos tinha o perfil
atípico `[80, 80, 0, 0, 0]`.

Nenhuma dessas variantes foi para produção.

### Resultado 4 — recalibração não resolve, e o motivo importa

Ajustar uma curva corrigindo a escala (linear e isotônica, com validação
cruzada *leave-one-out*) **piorou** o erro, de 115 para 128–130.

O motivo é instrutivo. O sistema de fato usa uma escala mais estreita que a
humana (desvio padrão 177 contra 236), mas com correlação de 0,64 a previsão
que minimiza o erro **encolhe** em direção à média, em vez de expandir. A reta
ajustada já estava perto do ótimo. Nenhuma transformação monótona ajuda:
curva reescala, não reordena.

**Implicação:** com concordância nesse nível, não há pós-processamento que
salve. Só melhora quem melhorar o julgamento.

### Resultado 5 — o ganho isolado ficou na Competência I

| | Produção | Ancorado |
|---|---|---|
| C1 — QWK | 0,381 | **0,450** |
| C1 — erro absoluto | 36,8 | **24,0** |

C1 era a competência mais fraca e foi a única que melhorou de forma visível com
ancoragem. É coerente: "poucos desvios" é o critério mais ambíguo da grade, e é
onde um exemplo concreto substitui melhor o adjetivo. Indica que a técnica
funciona quando a âncora é bem escolhida — e que a execução, não a ideia, foi o
problema.

### Limitações

- **n = 25.** Diferenças de QWK da ordem de 0,01 são ruído. Só dois efeitos têm
  tamanho suficiente para serem levados a sério: a melhora em C1 e o estouro do
  viés com âncoras ruins.
- **Amostra estratificada com peso nas faixas baixas.** A média geral não
  representa a população; por isso o relatório sempre quebra por faixa.
- **As notas são dos anotadores do Essay-BR**, não de banca oficial do ENEM nem
  da banca do cursinho. Servem para calibrar; a validação final tem que ser
  contra redações do contexto real de uso.
- **Duas redações do corpus têm nota humana 0** e o sistema deu 680 e 200. A de
  680 é, pelo texto, uma dissertação competente, com citação da Constituição e
  do Estatuto do Idoso. Não há no texto digitado motivo visível para anulação —
  ou a razão não sobreviveu à digitalização, ou é problema de rótulo. Essas
  duas respondem por boa parte do erro na faixa fraca.
- **Ruído de transcrição penaliza C1.** Na metade da amostra com mais defeitos
  de digitalização (espaço antes de pontuação, palavras partidas), o erro em C1
  é de −24,6; na metade limpa, −3,3. O corretor humano avaliou o manuscrito e
  não via esses defeitos; o sistema lê como desvio de norma culta.

### Custo

75 correções em três rodadas, cerca de US$ 5. Com cache de prompt ligado no
bloco de sistema, 5.566 tokens por correção passaram a ser lidos do cache.

## Experimento 4 — concordância no corpus do próprio cursinho

**Pergunta:** o que o sistema faz nas redações que os alunos daqui realmente
escreveram, corrigidas pelas corretoras que o cursinho usa?

O Essay-BR deu a primeira régua, mas é de outro contexto. Este experimento usa
o simulado do cursinho, e traz uma vantagem que nenhum corpus público tem:
**duas avaliadoras independentes por redação**.

```bash
python concordancia_humana.py          # o teto da tarefa, sem gastar API
python experimento_simulado.py         # sistema contra as corretoras
python experimento_ancora_local.py     # ancoragem com redações daqui
```

### O teto: duas corretoras concordam em QWK 0,867

| | QWK | Diferença absoluta média | Notas idênticas |
|---|---|---|---|
| C1 | 0,825 | 12,4 | 69% |
| C2 | 0,916 | 10,1 | 79% |
| C3 | 0,861 | 15,2 | 63% |
| C4 | 0,852 | 13,0 | 69% |
| C5 | 0,877 | 18,6 | 59% |
| **média** | **0,867** | — | — |

71 redações, correlação de 0,941 na nota total. Este número é o limite superior
da tarefa: nenhum sistema automático pode concordar com "a nota certa" mais do
que duas corretoras treinadas concordam entre si, porque onde elas discordam
não existe nota certa única.

**A tolerância informada precisa de correção.** A indicação prática era de até
40 pontos de diferença por competência entre corretores. Na prática, apenas
**1% das competências** (5 de 355) passa de 40 pontos; a diferença típica é de
10 a 19. Os 40 pontos são teto generoso, não comportamento real.

### Resultado 1 — o sistema não usa a parte de baixo da escala

Oito redações do lote 1, com transcrição e nota:

| Humano | Sistema | Diferença |
|---|---|---|
| 320 | 560 | **+240** |
| 380 | 560 | **+180** |
| 420 | 680 | **+260** |
| 760 | 600 | −160 |
| 800 | 800 | 0 |
| 840 | 800 | −40 |
| 880 | 760 | −120 |
| 880 | 880 | 0 |

QWK 0,368 contra a nota final. Nas redações boas o sistema acerta; nas fracas
erra de 180 a 260 pontos, sempre para cima. **Ele nunca desceu de 560**,
enquanto as corretoras desceram a 320 e deram competências valendo 40.

Isso reproduz com precisão o que a equipe de testes relatou de forma
qualitativa: redação de 320 recebendo de 520 a 600.

**Correção a uma conclusão anterior deste arquivo.** O experimento 2 concluiu,
a partir do Essay-BR, que o problema não era leniência e sim dispersão. No
corpus real, para redações fracas, **é leniência**. O Essay-BR embaralhava o
quadro: tinha dois casos de nota humana 0 sem motivo visível no texto e ruído
de transcrição que puxava as redações boas para baixo, e os dois efeitos se
cancelavam na média.

### Resultado 2 — ancoragem com redações locais é a primeira coisa que funciona

Âncoras tiradas do próprio simulado, duas de nota baixa e uma alta, com
validação *leave-one-out*: cada redação é avaliada por um prompt montado a
partir das outras sete.

| | Produção | Âncora Essay-BR | **Âncora local** |
|---|---|---|---|
| QWK vs nota final | 0,368 | 0,464 | **0,560** |
| QWK vs avaliadora A | 0,471 | 0,494 | **0,622** |
| QWK vs avaliadora B | 0,457 | 0,419 | **0,609** |
| Viés | +45 | +65 | **+32,5** |
| Erro absoluto | 125 | 125 | **97,5** |
| Menor nota atribuída | 560 | 560 | **480** |

**O piso cedeu.** Duas das três redações fracas melhoraram 80 pontos; a de 420
não se moveu. As redações boas não quebraram.

Três diferenças em relação à ancoragem que falhou no experimento 2:

1. As âncoras vêm do próprio cursinho, corrigidas pelas corretoras de
   referência, e não de outro corpus com outras anotadoras.
2. **Duas das três âncoras são de nota baixa**, com competências valendo 40. As
   âncoras do Essay-BR cobriam a escala de forma equilibrada, mas o problema
   estava concentrado embaixo.
3. O bloco diz explicitamente que não existe piso implícito em 120.

### Resultado 3 — ancoragem resolve a Competência I

| C1 | Produção | Âncora Essay-BR | Âncora local |
|---|---|---|---|
| QWK | 0,333 | 1,000 | 1,000 |
| Erro absoluto | 25,0 | 15,0 | 12,5 |

Somado ao Essay-BR, onde C1 também foi a única competência a melhorar
(0,381 → 0,450), são três medições independentes na mesma direção. É o achado
mais robusto do conjunto, e é coerente: "poucos desvios" é o critério mais
ambíguo da grade, e exemplo concreto substitui adjetivo melhor que definição.

### Limitações

- **n = 8.** QWK com oito pontos se move muito com uma redação. O valor 0,560
  não é confiável; o que é confiável é o piso ter cedido, porque se verifica
  caso a caso.
- **Estimativa otimista.** Com apenas 8 redações, deixar uma de fora ainda
  deixa as âncoras cobrindo quase todo o corpus. Em uso real as âncoras viriam
  de um conjunto separado, e o ganho tende a ser menor.
- **Uma das três redações fracas não melhorou.**
- **Os textos motivadores do simulado não vieram**, então o detector de cópia
  não rodou e o prompt não recebeu textos de apoio. Nenhuma das oito é cópia,
  mas a entrada não é idêntica à de produção.
- **O tema foi inferido** do conteúdo das redações. O enunciado oficial não
  acompanhou o lote.
- **A nota final é a média das duas avaliadoras**, então cai fora da escala de
  40 em 40 (aparecem 100 e 60). Por isso o relatório compara também contra cada
  avaliadora separadamente.
- **Só o lote 1 foi transcrito**: 8 de 71 redações. As outras 63 têm nota e
  estão como imagem nos lotes 2 a 6.

### Encaminhamento

A ancoragem local é a primeira mudança que merece ir para produção, mas precisa
de validação com n maior antes. O gargalo deixou de ser calibração e passou a
ser **transcrição**: com os lotes 2 a 6 em texto, dá para separar um conjunto de
âncoras de um conjunto de teste de verdade. O módulo de OCR já integrado ao
sistema do IFvest é o caminho natural para isso.
