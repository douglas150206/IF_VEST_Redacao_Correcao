# RELATÓRIO FINAL - IFSP

**Título:** Correção automática de redações do ENEM com modelos de linguagem: desenvolvimento, avaliação de confiabilidade e calibração contra avaliadores humanos

**Bolsista:**
Douglas Hiroiti Kadomoto
Telefone: (11) 95318-1806
E-mail: douglas.kadomoto@aluno.ifsp.edu.br

**Instituição de vínculo da bolsa:**
Instituto Federal de Educação, Ciência e Tecnologia de São Paulo – IFSP
Rua Pedro Vicente, 625 – Canindé – São Paulo-SP
CEP: 01109-010
Telefone: (11) 3775-4570
E-mail: prp@ifsp.edu.br

**Professora orientadora:**
Profa. Ana Paula Abrantes de Castro Shiguemori
Telefone: (12) 99726-7505
E-mail: anapaula.acs@ifsp.edu.br

Campus: IFSP – Campus Jacareí
Período de vigência: 11/2025 até 11/2026

---

## RESUMO

A redação é o único item discursivo do Exame Nacional do Ensino Médio (ENEM) e vale até mil pontos, distribuídos em cinco competências. Sua correção depende de avaliador humano especializado, o que limita a quantidade de devolutivas que cada estudante recebe ao longo da preparação. Este projeto construiu um sistema web gratuito de correção automática nessas cinco competências, com devolutiva textual por competência e detecção determinística de trechos copiados dos textos motivadores. Construído o sistema, o projeto voltou-se para a pergunta que decide se ele pode ser usado com estudantes: o instrumento mede corretamente? Conduziram-se cinco experimentos controlados, totalizando mais de trezentas correções. Os dois primeiros mediram consistência e o comportamento do detector de cópia. O terceiro comparou as notas do sistema com as de duas avaliadoras treinadas que corrigiram as redações de um simulado do cursinho, estabelecendo pela primeira vez uma referência externa: as duas avaliadoras concordam entre si com kappa ponderado quadrático de 0,867, e o sistema alcançava 0,514. O diagnóstico foi específico — o sistema acerta redações boas e superestima as fracas em 180 a 260 pontos, porque nunca atribui nota abaixo de 560, enquanto as avaliadoras atribuem 40 e 60 por competência. O quarto experimento testou quatro formas de calibração e produziu um achado contraintuitivo: toda intervenção que detalha os critérios no prompt **piora** a correção na faixa baixa. O quinto experimento mostrou o que funciona: incluir no prompt redações reais já corrigidas, inclusive de nota baixa, elevou a concordância de 0,514 para 0,703 e reduziu em 39% o erro nas redações fracas. A melhoria foi implementada no sistema como módulo configurável.

**Palavras-chave:** Correção automática de redações. ENEM. Modelos de linguagem. Concordância entre avaliadores. Calibração. Tecnologia educacional.

---

## APRESENTAÇÃO (INTRODUÇÃO, JUSTIFICATIVA E OBJETIVOS)

### Introdução

A redação do ENEM é avaliada em cinco competências, cada uma pontuada de 0 a 200, somando até mil pontos. Diferentemente das questões objetivas, ela exige leitura integral por avaliador treinado, que precisa julgar domínio da norma culta, compreensão da proposta, organização argumentativa, articulação textual e elaboração de proposta de intervenção. Esse trabalho não pode ser automatizado por gabarito, e é justamente aí que se forma o gargalo: corrigir uma redação custa tempo qualificado, e tempo qualificado é escasso.

A consequência prática recai sobre o estudante. Quem frequenta cursinho particular escreve e recebe correção com regularidade; quem não frequenta escreve pouco e recebe devolutiva raramente, quando recebe. Como a competência em escrita se desenvolve por prática acompanhada de retorno, a desigualdade de acesso à correção se converte em desigualdade de desempenho no exame.

A ideia deste projeto nasceu dessa observação, no contexto de um cursinho vinculado ao campus. Com o amadurecimento dos modelos de linguagem de grande porte, tornou-se tecnicamente viável construir um corretor automático capaz de produzir não apenas uma nota, mas uma devolutiva textual explicando o que justificou a pontuação em cada competência — que é a parte formativa da correção, aquela de que o estudante efetivamente aprende.

A facilidade de construção, no entanto, traz um risco. Um sistema que devolve uma nota numérica com aparência de precisão induz confiança, e essa confiança precisa ser verificada antes de o sistema ser colocado diante dos estudantes. Um instrumento de avaliação que responde de forma diferente à mesma redação não devolve informação: devolve ruído com aparência de nota. Pior ainda é o instrumento que responde de forma consistente e errada. Por isso o projeto não se encerrou na construção do sistema e incorporou uma etapa experimental extensa.

Essa etapa revelou-se mais longa e mais produtiva do que o previsto inicialmente. Partiu da verificação de consistência interna, avançou para a comparação com avaliadores humanos reais e terminou na identificação e correção de uma falha específica do sistema. Os elementos envolvidos são, portanto, quatro: o sistema construído; os modelos de linguagem que atribuem as notas; um corpus de redações elaborado para teste controlado; e um conjunto de redações de simulado do próprio cursinho, corrigidas por duas avaliadoras treinadas, que forneceu a referência externa contra a qual o sistema pôde ser medido.

### Justificativa

O projeto se justifica em três frentes.

**a) Frente social.** Oferecer gratuitamente uma ferramenta de correção com devolutiva por competência amplia o acesso à prática de escrita acompanhada, especialmente para estudantes que não dispõem de cursinho particular. O sistema foi desenvolvido com identidade visual institucional e disponibilizado sem custo para estudantes e professores.

**b) Frente técnica.** Sistemas de correção automática já operam com estudantes reais, inclusive em plataformas públicas. A literatura internacional relata resultados bastante variáveis de concordância entre modelos de linguagem e avaliadores humanos, e há poucos estudos voltados à língua portuguesa. Documentar empiricamente o comportamento de um sistema dessa natureza, incluindo suas falhas e o que efetivamente as corrige, é contribuição útil para quem pretende construir ou adotar ferramentas semelhantes.

**c) Frente formativa.** A regra do ENEM determina que trechos copiados dos textos motivadores não contam como produção do participante. Um corretor automático que ignore essa regra ensina ao estudante exatamente o comportamento que o exame penaliza. A implementação e a verificação do detector de cópia atendem a essa exigência pedagógica.

### Objetivo geral

Construir um sistema web de correção automática de redações do ENEM baseado em modelos de linguagem, verificar sua confiabilidade e sua concordância com avaliadores humanos, e corrigir as falhas identificadas.

### Objetivos específicos

1. Construir uma aplicação web que atribua nota nas cinco competências do ENEM e produza devolutiva textual para cada uma delas;
2. Construir um algoritmo determinístico de detecção de trechos copiados dos textos motivadores e integrá-lo ao fluxo de correção;
3. Verificar a variação da nota atribuída à mesma redação entre execuções idênticas do sistema;
4. Comparar a dispersão das notas produzidas por dois modelos de linguagem distintos;
5. Identificar de que forma a regra de anulação por cópia é efetivamente aplicada pelo sistema;
6. Verificar a precisão e o recall do detector de cópia mediante injeção controlada de trechos copiados;
7. Medir a concordância entre as notas do sistema e as de avaliadoras treinadas, e estabelecer o limite superior da tarefa pela concordância entre as próprias avaliadoras;
8. Identificar em que faixa da escala o sistema erra e por quê;
9. Testar formas de calibração e medir seu efeito;
10. Implementar no sistema a correção que se mostrar eficaz e propor recomendações de projeto.

### Perguntas que o estudo procura responder

1. Dada a mesma redação, quanto a nota varia entre execuções idênticas do sistema?
2. Essa variação depende do modelo de linguagem utilizado ou das características da redação avaliada?
3. O detector de cópia identifica corretamente quais palavras foram copiadas dos textos motivadores?
4. A regra de anulação por cópia é aplicada de forma proporcional ou abrupta?
5. A nota atribuída pelo sistema concorda com a de avaliadoras treinadas, e quanto duas avaliadoras concordam entre si?
6. Que intervenção melhora a concordância, e quanto?

---

## DESENVOLVIMENTO (METODOLOGIA E ANÁLISE)

### 1. O sistema construído

O sistema é uma aplicação web em que o estudante informa o tema, os textos motivadores e a redação. O servidor executa, nessa ordem, três etapas: detecção determinística de cópia, montagem da requisição ao modelo de linguagem incluindo o resultado dessa detecção, e validação estrutural da resposta antes de devolvê-la à interface.

A devolutiva apresentada ao estudante contém a nota de cada uma das cinco competências, a nota total, um comentário textual por competência explicando o que justificou a pontuação, e a lista dos trechos identificados como copiados, destacados no corpo da redação.

Uma primeira versão foi construída em Node.js com Express e banco SQLite. Posteriormente, o sistema foi portado para Python com FastAPI e interface em React, de modo a permitir sua integração ao sistema geral do cursinho, desenvolvido nessa pilha tecnológica. A equivalência entre as duas implementações foi verificada por um conjunto de comparação automatizado, que confirmou resultado idêntico, campo a campo, nos componentes determinísticos.

Por se tratar de serviço gratuito custeado institucionalmente, o sistema aplica um limite de dez correções mensais por usuário, exibido de forma explícita na interface por meio de um indicador que decresce a cada uso. Esgotado o limite, o usuário pode cadastrar sua própria chave de acesso à interface de programação do fornecedor do modelo, hipótese em que passa a arcar diretamente com o custo e deixa de ter limite.

### 2. O detector de cópia

A detecção de cópia emprega a técnica de n-gramas de palavras, também denominada *shingles*. Constrói-se o conjunto de todas as sequências de sete palavras consecutivas presentes nos textos motivadores; em seguida, percorre-se a redação do estudante e marca-se toda sequência de sete palavras que já pertença a esse conjunto. Palavras marcadas e contíguas são agrupadas em trechos legíveis, apresentados ao estudante.

Antes da comparação, cada palavra passa por normalização: conversão para minúsculas, decomposição Unicode para separar os acentos das letras e remoção de tudo que não seja letra ou dígito. Dessa forma, "Educação," e "educacao" tornam-se equivalentes, e a detecção não é burlada por alteração de pontuação ou de acentuação.

O percentual copiado e a lista de trechos são entregues ao modelo junto com a redação, acompanhados da instrução de que a penalização seja proporcional ao percentual identificado e de que a redação seja anulada quando for essencialmente cópia. Trata-se, portanto, de um componente determinístico alimentando uma decisão probabilística — arranjo cuja consequência o primeiro experimento viria a revelar.

### 3. Desenho experimental

Foram conduzidos cinco experimentos, em sequência, cada um respondendo a uma pergunta deixada aberta pelo anterior.

| Experimento | Pergunta | Corpus | Correções |
|---|---|---|---|
| 1 | O sistema repete a mesma nota? | 6 redações próprias | 120 |
| 2 | O detector acerta o que foi copiado? | injeção controlada | — |
| 3 | A nota concorda com a de avaliador humano? | Essay-BR e simulado | 33 |
| 4 | Que calibração melhora a concordância? | simulado | 112 |
| 5 | A melhoria se confirma com teste independente? | simulado | 24 |

Os experimentos 1 e 2 medem o sistema contra ele mesmo. Os experimentos 3, 4 e 5 o medem contra avaliadores humanos, e por isso dependeram de um corpus com notas oficiais, descrito adiante.

### 4. Experimento 1 — confiabilidade teste-reteste

O experimento mede consistência, não acurácia. A pergunta é se o sistema responde a mesma coisa quando questionado duas vezes sobre o mesmo texto, condição necessária para qualquer uso avaliativo.

Elaborou-se um corpus de seis redações sobre um mesmo tema, cobrindo faixas distintas de qualidade e de cópia dos textos motivadores. O percentual de cópia de cada uma foi medido pelo próprio detector, e não estimado: 0% para três redações, 29%, 45% e 70% para as demais. Cada redação foi submetida dez vezes a dois modelos de linguagem, totalizando 120 correções. Manteve-se constante o prompt, o limite de tokens e a montagem da entrada; variou-se apenas o modelo.

Registre-se que as redações deste corpus foram escritas pelo próprio bolsista. Não houve participação de seres humanos como sujeitos de pesquisa nesta etapa.

### 5. Experimento 2 — precisão e recall do detector de cópia

Enquanto a nota atribuída pelo modelo não dispõe de gabarito neste corpus, a detecção de cópia admite verificação exata: como os trechos copiados foram injetados de forma controlada pelo próprio experimento, sabe-se palavra por palavra o que deveria ter sido marcado. A métrica é aritmética, sem juízo humano intermediário.

Trechos literais dos textos motivadores, de tamanhos variando entre três e trinta palavras, foram inseridos nas três redações originais do corpus, em três posições distintas de cada uma. Em seguida, mediu-se a precisão (das palavras marcadas, quantas eram de fato copiadas) e o recall (das palavras copiadas, quantas foram marcadas). Um segundo teste aplicou substituições pontuais de palavras dentro de um trecho copiado de trinta palavras, para verificar a resistência do detector a edição trivial.

### 6. Experimento 3 — concordância com avaliadores humanos

Os dois primeiros experimentos deixaram em aberto a pergunta decisiva: as notas estão certas? Respondê-la exige gabarito, que o corpus próprio não possui.

Duas fontes foram utilizadas. A primeira é o **Essay-BR** (MARINHO; ANCHIETA; MOURA, 2021), corpus público sob licença permissiva com 4.570 redações de estudantes brasileiros avaliadas por especialistas nas cinco competências. A segunda, e mais relevante, é o conjunto de redações do **simulado do próprio cursinho**, cedido pela coordenação: 71 redações corrigidas por **duas avaliadoras independentes**, com nota por competência de cada uma.

A existência de duas avaliadoras é metodologicamente decisiva, porque permite medir o **limite superior da tarefa**. Nenhum sistema automático pode concordar com "a nota verdadeira" mais do que duas avaliadoras treinadas concordam entre si, pois onde elas divergem não existe nota verdadeira única.

A métrica adotada é o **kappa ponderado quadrático** (COHEN, 1968), padrão na área de correção automática por penalizar o erro proporcionalmente ao quadrado da distância entre os níveis. Reportam-se também o **viés** (erro médio com sinal, que mede se o sistema é sistematicamente generoso ou severo) e o **erro absoluto médio**. A distinção importa: um avaliador que erra 40 pontos para os dois lados é aceitável, porque o erro se compensa; um que erra 40 pontos sempre para cima desloca a nota de todos os estudantes.

As redações do simulado estavam disponíveis apenas como digitalização de manuscrito. Dezoito delas foram transcritas para texto, com marcação explícita das palavras lidas com baixa confiança.

### 7. Experimento 4 — quatro tentativas de calibração

Identificado o problema pelo experimento 3, testaram-se quatro intervenções, todas medidas sobre o mesmo conjunto:

**a) Grade específica do INEP no prompt.** Substituição da descrição genérica das competências pela grade operacional usada internamente pelo INEP, cedida pela coordenação, com os descritores de cada nível e os tetos obrigatórios.

**b) Ancoragem com redações de corpus externo.** Inclusão no prompt de cinco redações do Essay-BR com suas notas.

**c) Correção competência por competência.** Cinco chamadas separadas, cada uma com os descritores de uma única competência e um roteiro de exame a cumprir antes de pontuar.

**d) Recalibração por curva.** Ajuste de uma função (linear e isotônica) convertendo a nota do sistema na nota humana, com validação cruzada *leave-one-out*.

### 8. Experimento 5 — ancoragem em redações do próprio cursinho

A quinta intervenção partiu do padrão observado nas quatro anteriores. Cinco redações do simulado, com as notas atribuídas pelas avaliadoras, foram incluídas no prompt como referência — duas delas de nota baixa, faixa em que o sistema falha.

O desenho separa **âncoras** de **teste**: as cinco redações de referência nunca são avaliadas, e as doze restantes, que formam o conjunto de teste, não aparecem no prompt que as corrige. Os dois braços — prompt de produção e prompt ancorado — rodam sobre as mesmas doze redações, na mesma execução, de modo que a diferença observada não possa vir de amostras distintas.

As âncoras foram escolhidas entre as transcrições de leitura confiável, pois âncora com erro de transcrição ensinaria ao modelo uma régua incorreta.

### 9. Análise dos resultados

#### 9.1 A variação da nota acompanha a ambiguidade do caso, não o modelo

| Cópia medida | Redação | CV — opus-5 | CV — sonnet-4-5 | Notas idênticas (opus-5) |
|---|---|---|---|---|
| 0% | R1 | 0,0% | 3,0% | 10/10 |
| 0% | R2 | 0,0% | 5,1% | 10/10 |
| 0% | R3 | 5,5% | 4,5% | 6/10 |
| 29% | R5 | 12,0% | 14,8% | 4/10 |
| 45% | R6 | 11,4% | 0,0% | 3/10 |
| 70% | R4 | 0,0% | 0,0% | 10/10 |

Tabela 1 — Dispersão da nota atribuída à mesma redação (n = 10 por célula). Fonte: elaborado pelo autor.

O primeiro achado é o que não aparece na tabela: não há relação entre a dispersão e o modelo empregado. Agregando as seis redações, os dois modelos apresentaram amplitude média rigorosamente idêntica, de 60,0 pontos, com coeficientes de variação médios de 5,8% e 5,5%.

Esse resultado contraria a expectativa de que modelos maiores produziriam avaliações mais estáveis. Cabe acrescentar que, em fases preliminares conduzidas com três repetições ou menos, chegou-se duas vezes a conclusões opostas entre si sobre qual modelo seria mais estável, e ambas se desfizeram quando o número de repetições aumentou. O episódio é relatado deliberadamente, por ilustrar que amostras pequenas não sustentam afirmação sobre variância.

O padrão que a Tabela 1 revela está associado à redação. Nas redações sem cópia e de qualidade claramente definida, o sistema repetiu a mesma nota nas dez execuções. A dispersão concentra-se na faixa intermediária: na R5, com 29% de cópia, o coeficiente de variação atinge 12,0% e apenas quatro das dez execuções produziram a mesma nota.

O comportamento é coerente com o de um avaliador humano: casos extremos são decididos com facilidade, casos intermediários exigem deliberação e produzem desacordo. A diferença decisiva é que o corretor humano, ao deliberar, sabe que está em dúvida, ao passo que o sistema não comunica essa condição.

#### 9.2 A regra de anulação por cópia opera como função degrau

| Cópia medida | Anulações (opus-5) | Anulações (sonnet-4-5) | Nota média (opus-5) |
|---|---|---|---|
| 0% | 0/10 | 0/10 | 376 a 960 |
| 29% | 0/10 | 0/10 | 556 |
| 45% | 0/10 | 0/10 | 380 |
| 70% | 10/10 | 10/10 | 0 |

Tabela 2 — Frequência de anulação por faixa de cópia. Fonte: elaborado pelo autor.

Existe penalização gradual na nota, mas a anulação é binária e ocorre em algum ponto entre 45% e 70% de cópia, sem que se possa determinar onde. O aspecto relevante não é o valor do limiar, mas sua localização: ele não está escrito em lugar algum do sistema. É emergente do julgamento do modelo.

A consequência é considerável, porque a anulação é a decisão de maior impacto que o sistema toma. Delegá-la a um componente não auditável, quando o detector determinístico já fornece o percentual exato que permitiria decidi-la em código, é escolha de projeto difícil de justificar.

#### 9.3 O componente determinístico falha onde parecia sólido

| Palavras copiadas | Precisão | Recall |
|---|---|---|
| 3 a 6 | — | 0,0% |
| 7 | 100,0% | 100,0% |
| 8 | 98,6% | 100,0% |
| 10 | 98,9% | 100,0% |
| 15 a 30 | 100,0% | 100,0% |

Tabela 3 — Precisão e recall por tamanho do trecho copiado. Fonte: elaborado pelo autor.

| Substituições | Uma palavra a cada | Precisão | Recall |
|---|---|---|---|
| 0 | — | 100,0% | 100,0% |
| 1 | 30 palavras | 100,0% | 96,7% |
| 2 | 15 palavras | 100,0% | 93,3% |
| 3 | 10 palavras | 100,0% | 50,0% |
| 4 | 7,5 palavras | — | 0,0% |

Tabela 4 — Efeito da substituição de palavras em trecho copiado de 30 palavras. Fonte: elaborado pelo autor.

A detecção é função degrau exata no tamanho do *shingle*: abaixo de sete palavras não identifica nada. E a substituição de quatro palavras em trinta reduz o recall a zero — um texto com 87% de conteúdo copiado é reportado como possuindo 0% de cópia.

Cabe destacar a assimetria dos erros. A precisão permaneceu em 100% em todas as condições, e nenhuma palavra foi marcada indevidamente nas redações originais. O detector erra sempre na mesma direção: não acusa quem não copiou, apenas deixa passar quem copiou. Para uso avaliativo essa é a direção menos danosa, mas impõe limite à forma como o sistema pode ser apresentado: ele detecta cópia literal, e nada além disso.

#### 9.4 O limite superior da tarefa: avaliadoras concordam em 0,867

| Competência | QWK entre avaliadoras | Diferença absoluta média | Notas idênticas |
|---|---|---|---|
| I — norma culta | 0,825 | 12,4 | 69% |
| II — compreensão | 0,916 | 10,1 | 79% |
| III — argumentação | 0,861 | 15,2 | 63% |
| IV — coesão | 0,852 | 13,0 | 69% |
| V — proposta | 0,877 | 18,6 | 59% |
| **Média** | **0,867** | — | — |

Tabela 5 — Concordância entre as duas avaliadoras do simulado (71 redações). Fonte: elaborado pelo autor.

A correlação entre as notas totais das duas avaliadoras é de 0,941. Este é o teto contra o qual todo resultado do sistema deve ser lido.

Um achado secundário merece registro: a tolerância informada na prática — até 40 pontos de diferença por competência entre corretores — mostrou-se generosa em relação ao comportamento real. Apenas **1% das competências** (5 de 355) apresenta diferença superior a 40 pontos; a diferença típica é de 10 a 19.

#### 9.5 O sistema não utiliza a parte baixa da escala

| Nota das avaliadoras | Nota do sistema | Diferença |
|---|---|---|
| 320 | 560 | +240 |
| 380 | 560 | +180 |
| 420 | 680 | +260 |
| 760 | 600 | −160 |
| 800 | 800 | 0 |
| 840 | 800 | −40 |
| 880 | 760 | −120 |
| 880 | 880 | 0 |

Tabela 6 — Notas do sistema e das avaliadoras, oito redações do simulado. Fonte: elaborado pelo autor.

Nas redações de nota alta o sistema acerta; nas de nota baixa erra de 180 a 260 pontos, sempre para cima. O dado que explica o padrão: **em nenhuma redação o sistema atribuiu nota inferior a 560**, enquanto as avaliadoras atribuem 40 e 60 por competência.

O diagnóstico é específico, e difere da hipótese inicial de que o sistema seria genericamente generoso. O viés médio é próximo de zero; o erro está concentrado na faixa baixa. O modelo conhece os critérios, mas não dispõe de referência de magnitude: sabe o que é "poucos desvios", não quanto isso vale.

Medição complementar no Essay-BR, com amostra estratificada de 25 redações, confirmou o padrão e acrescentou que o erro absoluto médio é de 115 pontos, contra tolerância de 40 entre avaliadores humanos.

#### 9.6 Detalhar o critério piora a correção na faixa baixa

| Intervenção | Efeito nas redações fracas |
|---|---|
| Grade específica do INEP no prompt | piorou |
| Ancoragem com redações de corpus externo | piorou |
| Correção competência por competência | piorou muito |
| Recalibração por curva | piorou |

Tabela 7 — Efeito das quatro intervenções de calibração. Fonte: elaborado pelo autor.

Este é o achado mais relevante do trabalho, por ser contrário à intuição corrente.

A grade do INEP no prompt reduziu a concordância de 0,500 para 0,437 no Essay-BR. A correção por competência, com roteiro de exame detalhado, reduziu o kappa da Competência III de 0,750 para 0,286 e o da Competência V de 0,370 para 0,171, embora tenha produzido quatro acertos exatos nas redações de nota alta.

A explicação é consistente entre as três primeiras intervenções: **toda intervenção que leva o modelo a analisar mais empurra a redação fraca para cima**. Examinando a coesão de perto, o modelo encontra alguns conectivos e atribui nível 3; percorrendo a proposta elemento a elemento, encontra ação e agente e atribui nível 2. Critério mais detalhado fornece mais motivos para pontuar.

A quarta intervenção falha por razão distinta e igualmente instrutiva. Com correlação de 0,64 entre sistema e avaliador, a previsão que minimiza o erro quadrático **encolhe** em direção à média, em vez de expandir a escala. Além disso, nenhuma transformação monótona reordena pontos: curva reescala, não corrige ordenação. Onde a concordância é insuficiente, não há pós-processamento que a recupere.

#### 9.7 A ancoragem em exemplos corrigidos eleva a concordância para 0,703

| | QWK final | QWK vs avaliadora A | Viés | Erro absoluto | Menor nota |
|---|---|---|---|---|---|
| Prompt de produção | 0,514 | 0,441 | +10,0 | 106,7 | 560 |
| **Prompt ancorado** | **0,703** | **0,683** | **−11,7** | **95,0** | **400** |

Tabela 8 — Efeito da ancoragem, teste disjunto das âncoras (n = 12). Fonte: elaborado pelo autor.

O valor de 0,703 situa-se dentro da faixa de 0,60 a 0,73 relatada como estado da arte para o português por Barbosa, Silveira e Mauá (2025), obtida com modelos ajustados; aqui o resultado decorre apenas do conteúdo do prompt.

O viés praticamente se anulou e mudou de sinal, passando de levemente generoso a levemente conservador — para uso com estudante, errar para baixo é a direção menos danosa.

| Nota das avaliadoras | Prompt de produção | Prompt ancorado |
|---|---|---|
| 320 | 560 | **400** |
| 420 | 720 | 680 |
| 500 | 480 | **500** |
| 560 | 680 | **620** |
| 700 | 600 | **680** |
| 760 | 800 | 860 |
| 760 | 600 | 600 |
| 800 | 760 | 720 |
| 840 | 800 | 740 |
| 880 | 760 | 760 |
| 880 | 880 | 820 |
| 940 | 840 | 840 |

Tabela 9 — Comparação redação a redação. Fonte: elaborado pelo autor.

Nas três redações de nota inferior a 560, o erro absoluto caiu de **186,7 para 113,3 pontos** — redução de 39%, exatamente no caso que motivou a investigação.

O padrão é consistente: as cinco redações entre 320 e 700 melhoraram **todas, sem exceção**; as de nota alta pioraram ligeiramente. O sistema tornou-se mais conservador em toda a escala, e como o erro na faixa baixa era grande e na faixa alta era pequeno, o saldo é favorável. Essa consistência sustenta a conclusão mais do que o valor agregado, dado o tamanho da amostra.

#### 9.8 Resultados complementares

Dois resultados secundários merecem registro.

**Transcrição automática.** As dezoito redações foram também transcritas por modelo de visão, sem revisão humana, para verificar se o reconhecimento de manuscrito degradaria o resultado. A concordância entre a transcrição manual e a automática é de **96,5%**, com divergência mediana de 2,6%. O reconhecimento não constitui, portanto, o gargalo que se temia.

**Custo.** A ancoragem acrescenta cerca de 2.700 tokens fixos a cada requisição. Com cache de prompt habilitado no bloco de sistema, 5.566 tokens por correção passaram a ser lidos do cache, compensando o acréscimo.

### 10. Implementação no sistema

A ancoragem foi implementada como módulo de produção (`corretor/ancoragem.py`), e não permanece restrita ao ambiente experimental. O módulo lê as redações de referência de um arquivo de configuração, valida a estrutura e as notas, e compõe o bloco acrescentado ao prompt.

O acionamento se dá por variável de ambiente. Na ausência dela, o sistema opera com o comportamento anterior, o que permite ativar e desativar a calibração sem alteração de código. A validação recusa configurações inválidas com mensagem explícita — incluindo o caso em que nenhuma âncora de nota baixa é fornecida, situação em que a calibração não cumpriria sua função.

As regras de cópia derivadas da grade do INEP também foram implementadas em código, substituindo o julgamento implícito do modelo por decisão auditável.

---

## CONCLUSÃO (RESULTADOS DA PESQUISA)

### 1. Resultados alcançados

Os dez objetivos específicos foram cumpridos.

**O sistema foi construído** e encontra-se em funcionamento, em duas implementações equivalentes verificadas por conjunto de comparação automatizado.

**O detector de cópia foi construído, integrado e caracterizado** com gabarito exato: detecção em degrau no tamanho do *shingle*, recall nulo após substituição de quatro palavras em trinta, e nenhum falso positivo.

**A confiabilidade foi medida** em 120 correções, estabelecendo-se que a dispersão acompanha a ambiguidade do caso, não o modelo, e que a troca de modelo introduz viés sistemático de 55 pontos.

**A concordância com avaliadores humanos foi medida**, e com ela o limite superior da tarefa: duas avaliadoras treinadas concordam entre si com kappa de 0,867, enquanto o sistema alcançava 0,514.

**A falha foi localizada**: o sistema não utiliza a parte baixa da escala, nunca atribuindo nota inferior a 560, e por isso superestima as redações fracas em 180 a 260 pontos.

**Quatro formas de calibração foram testadas e descartadas**, com a causa identificada em cada caso.

**Uma forma de calibração foi validada e implementada**: a ancoragem em redações corrigidas elevou a concordância de 0,514 para 0,703 e reduziu em 39% o erro nas redações fracas.

### 2. Contribuição principal

O achado de maior interesse é contrário à intuição que orienta boa parte do trabalho prático com esses sistemas: **explicitar e detalhar os critérios de avaliação no prompt piora a correção na parte baixa da escala**. Quatro intervenções distintas confirmaram o efeito, e a explicação é consistente — critério detalhado fornece ao modelo mais motivos para atribuir pontos, e o efeito é mais intenso justamente onde há menos a creditar.

O que corrige o problema não é descrição, mas comparação: exemplos de redações reais com a nota que avaliadores treinados lhes atribuíram, incluindo exemplos de nota baixa. A diferença entre as duas abordagens é a diferença entre dizer ao modelo o que avaliar e mostrar-lhe quanto cada coisa vale.

Esse resultado importa para além deste sistema, porque a prática corrente ao ajustar corretores automáticos é refinar a descrição do critério.

### 3. Recomendações de projeto

1. **Calibrar por exemplo, não por critério.** Manter no prompt um conjunto de redações corrigidas pelos mesmos avaliadores que atendem os estudantes, cobrindo a escala e incluindo obrigatoriamente exemplos de nota baixa.
2. **Implementar o limiar de anulação por cópia como regra determinística em código**, com valor justificado e auditável.
3. **Acompanhar a nota de indicação de incerteza** quando o caso situar-se na faixa de baixa reprodutibilidade.
4. **Não apresentar o sistema como barreira contra cópia**, uma vez que detecta apenas cópia literal e é neutralizado por edição trivial.
5. **Preceder toda troca de modelo de recalibração** e comunicá-la aos usuários, em razão do viés sistemático identificado.
6. **Remedir periodicamente a concordância** contra avaliadores humanos, pois é a única verificação que detecta degradação do instrumento.

### 4. Limitações

**Tamanho da amostra.** O conjunto de teste do experimento final compreende doze redações, três delas de nota inferior a 560. O intervalo de confiança em torno de 0,703 é largo, e o que sustenta a conclusão é mais a consistência do padrão — todas as redações de 320 a 700 melhoraram — do que o valor agregado.

**Corpus de um único simulado e um único tema.** O efeito do tema não foi isolado.

**Dois modelos de um único fornecedor.**

**Transcrição.** Dezoito das 71 redações do simulado foram transcritas. Três delas, de letra de difícil leitura, contêm palavras lidas com margem de dúvida, o que afeta sobretudo a medição da Competência I.

**Uma redação resistiu à calibração**, mantendo erro de 260 pontos nas duas condições.

### 5. Encaminhamentos

A ativação da ancoragem em produção depende de duas providências externas a este trabalho: autorização da coordenação para o uso de redações de estudantes como referência dentro do sistema, e configuração da variável de ambiente no ambiente de produção. Registre-se que a autorização pode ser dispensada caso as redações de referência sejam elaboradas especificamente para esse fim e corrigidas pelas mesmas avaliadoras, hipótese não testada neste trabalho.

Permanecem como trabalho futuro: a transcrição das demais redações do simulado, que permitiria conjunto de teste maior; a verificação do desenho híbrido sugerido pelos resultados, combinando avaliação global para redações de nota alta e exame por competência para as demais; e o levantamento da curva que relaciona o tamanho do *shingle* à sensibilidade do detector.

Os resultados foram submetidos à I Jornada de Ensino, Ciência, Extensão e Tecnologia do IFSP – Campus Jacareí, e encontra-se em preparação artigo destinado a periódico científico.

---

## REFERÊNCIAS BIBLIOGRÁFICAS

ATTALI, Y.; BURSTEIN, J. Automated essay scoring with e-rater V.2. *Journal of Technology, Learning, and Assessment*, v. 4, n. 3, 2006.

BARBOSA, A.; SILVEIRA, I. C.; MAUÁ, D. D. An empirical analysis of large language models for automated cross-prompt essay trait scoring in Brazilian Portuguese. *Journal of the Brazilian Computer Society*, v. 31, n. 1, p. 857-870, 2025. DOI: 10.5753/jbcs.2025.5817.

COHEN, J. Weighted kappa: nominal scale agreement with provision for scaled disagreement or partial credit. *Psychological Bulletin*, v. 70, n. 4, p. 213-220, 1968.

INSTITUTO NACIONAL DE ESTUDOS E PESQUISAS EDUCACIONAIS ANÍSIO TEIXEIRA. *A redação no Enem 2024: cartilha do participante*. Brasília: INEP, 2024.

MARINHO, J. C.; ANCHIETA, R. T.; MOURA, R. S. *Essay-BR: a Brazilian corpus of essays*. arXiv:2105.09081, 2021.

PAGE, E. B. The imminence of grading essays by computer. *The Phi Delta Kappan*, v. 47, n. 5, p. 238-243, 1966.

PERELMAN, L. When "the state of the art" is counting words. *Assessing Writing*, v. 21, p. 104-111, 2014.

---

Assinatura do orientador: _________________________________________

Assinatura do bolsista: __________________________________________
