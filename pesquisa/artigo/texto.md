# Manuscrito — texto redigido

> Este arquivo é o **texto do artigo**, não o plano. O plano fica em
> `artigo.md`. Conforme cada seção é redigida, ela entra aqui na forma final.
>
> Ao transportar para o template Word: Arial 10, espaço 1,5 a partir da
> introdução, títulos de seção em negrito e caixa alta.

---

## CONFIABILIDADE E LIMITES DE UM SISTEMA DE CORREÇÃO AUTOMÁTICA DE REDAÇÕES DO ENEM BASEADO EM MODELOS DE LINGUAGEM

*Reliability and limits of a large language model-based automated essay scoring system for the Brazilian ENEM examination*

*Confiabilidad y límites de un sistema de corrección automática de redacciones del ENEM basado en modelos de lenguaje*

---

## INTRODUÇÃO

*[a escrever]*

## 1 – REFERENCIAL TEÓRICO

*[a escrever]*

## 2 – METODOLOGIA

*[a escrever]*

---

## 3 – RESULTADOS E DISCUSSÃO

### 3.1 A variação da nota acompanha a ambiguidade do caso, não o modelo

A primeira pergunta de pesquisa indaga quanto a nota varia quando a mesma
redação é submetida repetidas vezes ao sistema, sem que nada mude na entrada. A
Tabela 1 apresenta o coeficiente de variação obtido em dez execuções idênticas
para cada combinação de redação e modelo, acompanhado do número de vezes em que
a nota se repetiu exatamente.

**Tabela 1 — Dispersão da nota atribuída à mesma redação (n = 10 por célula)**

| Cópia medida | Redação | CV — opus-5 | CV — sonnet-4-5 | Respostas idênticas (opus-5) |
|---|---|---|---|---|
| 0% | R1 | 0,0% | 3,0% | 10/10 |
| 0% | R2 | 0,0% | 5,1% | 10/10 |
| 0% | R3 | 5,5% | 4,5% | 6/10 |
| 29% | R5 | 12,0% | 14,8% | 4/10 |
| 45% | R6 | 11,4% | 0,0% | 3/10 |
| 70% | R4 | 0,0% | 0,0% | 10/10 |

Fonte: elaborado pelo autor.

O primeiro achado é o que **não** aparece na tabela. Não há relação entre a
dispersão e o modelo empregado. Agregando as seis redações, os dois modelos
apresentam amplitude média rigorosamente idêntica, conforme a Tabela 2.

**Tabela 2 — Dispersão agregada por modelo (120 correções)**

| Modelo | Amplitude média | Coeficiente de variação médio |
|---|---|---|
| claude-opus-5 | 60,0 pontos | 5,8% |
| claude-sonnet-4-5 | 60,0 pontos | 5,5% |

Fonte: elaborado pelo autor.

A diferença de 0,3 ponto percentual entre os coeficientes médios não sustenta
qualquer afirmação sobre superioridade de um modelo em consistência. Este
resultado merece registro porque contraria a expectativa corrente de que
modelos maiores produziriam avaliações mais estáveis. Convém observar que, em
fases preliminares desta mesma investigação, conduzidas com três repetições ou
menos, chegou-se duas vezes a conclusões opostas entre si sobre qual modelo
seria mais estável. Ambas se desfizeram quando o número de repetições aumentou.
O episódio ilustra por que amostras pequenas não sustentam afirmação sobre
variância, e é relatado aqui deliberadamente.

O que a Tabela 1 revela, em contrapartida, é um padrão associado à **redação**,
não ao modelo. Nas redações sem qualquer cópia detectada e de qualidade
claramente definida (R1 e R2), o sistema repetiu a mesma nota nas dez execuções.
Na redação integralmente comprometida por cópia (R4, com 70%), o mesmo ocorreu:
dez notas idênticas. A dispersão concentra-se na faixa intermediária. Na R5, com
29% de cópia, o coeficiente de variação atinge 12,0%, e apenas quatro das dez
execuções produziram a mesma nota. Na R6, com 45%, o valor é 11,4%, com somente
três repetições coincidentes.

Trata-se de um comportamento coerente com o de um avaliador humano: casos
extremos são decididos com facilidade, casos intermediários exigem deliberação e
produzem desacordo. A diferença decisiva é que o corretor humano, ao deliberar,
sabe que está em dúvida — e o sistema não comunica essa condição. A nota
devolvida ao estudante tem exatamente a mesma aparência de definitividade
quando é reprodutível e quando não é. Um mesmo texto pode receber 440 ou 640
pontos conforme o instante da submissão, e nada na interface distingue esse caso
daquele em que a nota se repetiria indefinidamente.

### 3.2 A regra de anulação por cópia opera como função degrau

O sistema fornece ao modelo o percentual exato de cópia calculado pelo detector,
além dos trechos identificados, e instrui que a penalização seja proporcional,
com anulação quando a redação for essencialmente cópia. A Tabela 3 mostra como
essa instrução foi efetivamente aplicada.

**Tabela 3 — Frequência de anulação por faixa de cópia**

| Cópia medida | Anulações — opus-5 | Anulações — sonnet-4-5 | Nota média — opus-5 |
|---|---|---|---|
| 0% | 0/10 | 0/10 | 376 a 960 |
| 29% | 0/10 | 0/10 | 556 |
| 45% | 0/10 | 0/10 | 380 |
| 70% | 10/10 | 10/10 | 0 |

Fonte: elaborado pelo autor.

Existe penalização gradual na nota: a redação com 45% de cópia obteve média de
380 pontos, contra 960 da melhor redação original. Nesse aspecto, a instrução de
proporcionalidade foi cumprida. A anulação, porém, não é gradual. Ela é binária
e ocorre entre 45% e 70% de cópia, sem que se possa determinar em que ponto
desse intervalo o limiar se encontra.

O aspecto relevante não é o valor do limiar, mas sua localização. Ele **não está
escrito em lugar algum do sistema**. Não há constante no código, não há
parâmetro de configuração, não há documentação que o registre. O limiar é
emergente do julgamento do modelo, e o comportamento observado nos dois modelos
testados foi idêntico apenas por coincidência empírica — nada garante que se
mantenha em outra versão, em outro fornecedor ou mesmo em outra sessão.

A consequência prática é considerável. A anulação da redação é a decisão de
maior impacto que o sistema toma: converte uma nota que poderia ser de 400 ou
500 pontos em zero. Delegar essa decisão a um componente não auditável, quando o
detector determinístico já fornece o percentual exato que permitiria decidi-la
em código, é uma escolha de projeto difícil de justificar. Note-se que o mesmo
percentual que o modelo usa para julgar está disponível para uma regra explícita.

### 3.3 O componente determinístico falha onde parecia sólido

A terceira pergunta de pesquisa dirige-se ao detector de cópia. Diferentemente
da nota, que não possui gabarito neste corpus, a detecção admite verificação
exata: como os trechos copiados foram injetados de forma controlada, sabe-se
palavra por palavra o que deveria ter sido marcado.

A Tabela 4 apresenta o desempenho em função do tamanho do trecho copiado.

**Tabela 4 — Precisão e recall por tamanho do trecho copiado**

| Palavras copiadas | Precisão | Recall |
|---|---|---|
| 3 a 6 | — | 0,0% |
| 7 | 100,0% | 100,0% |
| 8 | 98,6% | 100,0% |
| 10 | 98,9% | 100,0% |
| 15 a 30 | 100,0% | 100,0% |

Fonte: elaborado pelo autor. A precisão não é definida quando o detector não
marca palavra alguma.

O comportamento é uma função degrau exata no tamanho do *shingle*. Abaixo de
sete palavras, o detector não identifica nada; a partir de sete, identifica
tudo. Isso decorre diretamente do parâmetro e não constitui defeito de
implementação, mas tem efeito prático imediato: um trecho de seis palavras
copiado literalmente é invisível ao sistema. A precisão ligeiramente inferior a
100% nos trechos de oito e dez palavras origina-se de efeito de borda, quando
uma janela que atravessa a emenda entre o texto original e o trecho injetado
coincide fortuitamente com o material de apoio, marcando uma palavra vizinha que
era de autoria do participante.

O resultado mais relevante, contudo, aparece na Tabela 5, que mede o que
acontece quando o trecho copiado sofre alterações pontuais.

**Tabela 5 — Efeito da substituição de palavras em trecho copiado de 30 palavras**

| Substituições | Uma palavra a cada | Precisão | Recall |
|---|---|---|---|
| 0 | — | 100,0% | 100,0% |
| 1 | 30 palavras | 100,0% | 96,7% |
| 2 | 15 palavras | 100,0% | 93,3% |
| 3 | 10 palavras | 100,0% | 50,0% |
| 4 | 7,5 palavras | — | 0,0% |
| 5 | 6 palavras | — | 0,0% |

Fonte: elaborado pelo autor.

A substituição de quatro palavras em trinta reduz o recall a zero. O mecanismo é
direto: quando nenhuma sequência de sete palavras permanece intacta, não há
correspondência a encontrar. Um texto com 87% de conteúdo copiado é reportado ao
sistema como possuindo 0% de cópia, e a regra de anulação discutida na seção
anterior jamais é acionada.

Cabe destacar a assimetria dos erros. A precisão permanece em 100% em todas as
condições testadas, e nenhuma palavra foi marcada indevidamente nas três
redações originais do corpus, que somam 564 palavras sem qualquer cópia. O
detector, portanto, **erra sempre na mesma direção**: ele não acusa quem não
copiou, apenas deixa passar quem copiou. Para um instrumento de uso avaliativo,
essa é a direção menos danosa, uma vez que o custo de acusar indevidamente um
estudante é superior ao de deixar de identificar uma cópia. Ainda assim, a
constatação impõe um limite à forma como o sistema pode ser apresentado: ele
detecta cópia literal, e nada além disso.

### 3.4 A avaliação recompensa mais a cópia do que a escrita própria deficiente

Um cruzamento entre os resultados expõe um problema que não é de implementação,
mas de validade do instrumento. A redação R5, com 29% de cópia dos textos
motivadores e razoavelmente bem escrita — precisamente porque a porção copiada
provém de texto profissionalmente redigido —, obteve média de 556 pontos. A
redação R3, integralmente original, sem qualquer cópia detectada, porém de
qualidade argumentativa fraca, obteve 376 pontos.

O estudante que copia aproximadamente um terço do texto motivador é, portanto,
avaliado de forma mais favorável do que aquele que escreve mal com as próprias
palavras. O sistema mede, em alguma medida, a qualidade textual do que está na
página, e não a produção do participante. Essa constatação conecta-se
diretamente à crítica de Perelman (2014), segundo a qual os sistemas de correção
automática avaliam *proxies* — extensão, vocabulário, fluência superficial — em
lugar do construto que declaram medir.

### 3.5 A substituição do modelo desloca sistematicamente as notas

O `claude-opus-5` atribuiu, em média, **55 pontos a mais** que o
`claude-sonnet-4-5`, sendo mais generoso em cinco das seis redações. A única
exceção é a R4, em que ambos anularam a redação e o empate é trivial. A
diferença por redação variou de 24 a 100 pontos.

A consistência da direção indica viés sistemático, e não ruído. Em termos
práticos, a substituição do modelo subjacente desloca a nota de todos os
estudantes em cerca de meia competência, sem que nada tenha mudado na redação ou
nos critérios. Uma troca de modelo — motivada por custo, disponibilidade ou
descontinuação de versão — não constitui, portanto, substituição transparente:
exige recalibração e, idealmente, comunicação aos usuários.

### 3.6 Registro de uma anomalia não explicada

Durante a fase piloto, conduzida com três repetições, a redação R4 recebeu do
`claude-opus-5` as notas 120, 0 e 200. Na execução completa, com dez repetições,
a mesma redação recebeu 0 nas dez vezes. Trata-se do mesmo texto, do mesmo
prompt e do mesmo modelo, em sessões realizadas em momentos distintos.

Não há explicação disponível para essa diferença, e nenhuma será proposta aqui.
O registro é feito porque constitui indício de que a variabilidade pode existir
**entre sessões**, e não apenas entre chamadas sucessivas dentro de uma mesma
sessão. Caso se confirme, o fenômeno teria implicação metodológica relevante:
estimativas de confiabilidade obtidas em coleta concentrada no tempo, como a
deste trabalho, subestimariam a variação real a que um estudante está sujeito.
Investigar a hipótese exigiria desenho experimental com coleta distribuída ao
longo de semanas.

### 3.7 Síntese dos resultados

Os achados convergem para uma caracterização única do instrumento. O sistema é
altamente reprodutível nos casos em que a decisão é evidente e perde
reprodutibilidade justamente nos casos em que a decisão é difícil. A regra de
maior impacto que ele aplica não está escrita em lugar algum e não pode ser
auditada. O componente determinístico, que deveria oferecer garantia, é
neutralizado por edição trivial. E a nota atribuída favorece o texto bem escrito
por terceiros em detrimento do texto próprio deficiente.

Em conjunto, isso descreve um instrumento **confiável onde a confiabilidade
pouco importa e instável onde ela seria decisiva** — o inverso do que se espera
de um dispositivo de avaliação educacional.

---

## 4 – CONSIDERAÇÕES FINAIS

*[a escrever]*

## REFERÊNCIAS

*[a montar a partir de `referencias.md`, apenas com o que for citado no texto]*
