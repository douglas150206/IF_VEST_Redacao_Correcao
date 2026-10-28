# Plano do artigo — RECIMA21

## A tese

O artigo **não** é "construímos um corretor de redações". Isso já foi feito, é
trabalho de engenharia e não passa em revisão como contribuição científica.

A tese é esta:

> Um sistema de correção automática por modelo de linguagem é **confiável onde a
> decisão é fácil e vacila onde a decisão é difícil** — exatamente o inverso do
> que se espera de um instrumento de avaliação. E o componente determinístico
> que deveria dar garantia (o detector de cópia) é derrotado por uma edição
> trivial.

O que sustenta essa tese são resultados negativos, medidos com método. **É isso
que dá o artigo.** Um trabalho que dissesse "funcionou bem" com n=3 seria
rejeitado; um que mede a própria falha e publica o número é defensável.

O ângulo de extensão também conta: o sistema está em uso, é gratuito, e as
limitações foram medidas antes de expor estudantes a elas.

## Título proposto

> Confiabilidade e limites de um sistema de correção automática de redações do
> ENEM baseado em modelos de linguagem

## Estrutura e orçamento de palavras

A RECIMA21 exige mínimo de 13 páginas em Arial 10, espaçamento 1,5. Isso dá algo
entre 5.500 e 6.500 palavras.

### 1. Introdução — ~700 palavras

Abre pelo problema educacional, não pela tecnologia: a devolutiva de redação é
escassa porque depende de corretor humano especializado, e a escassez é desigual.
Apresenta o sistema como resposta de extensão a esse problema, e então vira a
chave: antes de usar, é preciso saber se o instrumento mede. Fecha com as três
perguntas de pesquisa e a estrutura do texto.

**Perguntas de pesquisa:**
- **PP1.** Dada a mesma redação, quanto a nota varia entre execuções idênticas?
- **PP2.** A nota atribuída concorda com a nota de avaliadores humanos?
- **PP3.** O detector de cópia acerta quais palavras foram copiadas?

### 2. Referencial teórico — ~1.400 palavras

**2.1 Da regressão aos modelos de linguagem.** Page (1966) e a distinção entre
*trins* e *proxes*; Attali e Burstein (2006) e o e-rater; a virada para LLMs.

**2.2 A matriz do ENEM.** As cinco competências, a escala de 0 a 200, e a regra
de cópia dos textos motivadores (INEP). Justifica por que o detector existe.

**2.3 Confiabilidade e validade.** A distinção que organiza o artigo inteiro. Um
instrumento pode ser perfeitamente confiável e completamente inválido. Perelman
(2014) para a crítica de construto.

**2.4 Correção automática em português.** Essay-BR (Marinho, Anchieta e Moura,
2021) e o estado da arte de Barbosa, Silveira e Mauá (2025), com QWK de 0,60 a
0,73. É contra esse número que o experimento 2 se compara.

> **Lacuna:** faltam fontes para razão aluno/corretor no Brasil, teoria da medida
> e ética de IA na educação. Ver `referencias.md`.

### 3. Metodologia — ~1.200 palavras

**3.1 O sistema.** Aplicação web, correção nas cinco competências com devolutiva
textual, detector de cópia por *shingles* de 7 palavras alimentando o prompt.
Descrever o suficiente para replicação; o código é público.

**3.2 Experimento 1 — confiabilidade teste-reteste.** 6 redações × 2 modelos ×
10 repetições = 120 correções. Mesmo prompt, mesma `max_tokens`, mesma entrada;
varia só o modelo. Corpus com gradiente de cópia **medido pelo detector**.

**3.3 Experimento 2 — concordância com nota humana.** Essay-BR, QWK por
competência. *(Depende de dados — ver bloqueio abaixo.)*

**3.4 Experimento 3 — precisão e recall do detector.** Injeção controlada de
cópia, gabarito exato palavra a palavra, três testes: tamanho do trecho,
resistência a substituição, falso positivo.

### 4. Resultados e discussão — ~1.800 palavras

Os achados, em ordem de força:

1. **A variância acompanha a ambiguidade, não o modelo.** Os dois modelos têm
   amplitude média idêntica (60 pontos). Em cópia 0% ou 70%, dez respostas
   iguais; em cópia parcial, CV de 12% e apenas 3 a 4 respostas iguais em 10.
2. **A regra de anulação é degrau sem limiar escrito.** Nada zera até 45% de
   cópia, tudo zera em 70%. O limiar não existe no código — está implícito no
   julgamento do modelo, embora o detector forneça o percentual exato.
3. **O detector é derrotado por edição trivial.** Trocar 4 palavras em 30 leva o
   recall a zero. Precisão permanece 100%: o sistema erra sempre para o mesmo
   lado, deixando passar em vez de acusar.
4. **A detecção é degrau exato no parâmetro.** Zero abaixo de 7 palavras, 100% a
   partir de 7. O parâmetro define o que o sistema consegue ver, e foi escolhido
   sem justificativa empírica.
5. **Viés sistemático entre modelos.** +55 pontos de diferença média, na mesma
   direção em 5 das 6 redações. Trocar de modelo desloca a nota de todos.
6. **Copiar compensa mais que escrever mal.** R5 (29% copiada, bem escrita
   porque copiada) teve 556; R3 (original fraca) teve 376. Problema de validade
   do instrumento, não de implementação.
7. **Anomalia entre sessões.** No piloto a R4 recebeu 120, 0 e 200; na corrida
   completa, 0 nas dez vezes. Mesmo texto, mesmo modelo. Sem explicação — fica
   registrado como indício de variabilidade entre sessões.

A discussão amarra tudo na tese: confiável onde não importa, instável onde
importa.

### 5. Considerações finais e recomendações — ~600 palavras

Recomendações concretas, derivadas dos achados:
- O limiar de cópia deve ser regra determinística em código, não julgamento do
  modelo.
- A nota deve vir acompanhada de indicação de incerteza quando o caso é
  ambíguo.
- O sistema não pode ser apresentado como barreira contra cópia.
- Trocar o modelo exige recalibração, não é substituição transparente.

Limitações e trabalhos futuros.

### 6. Referências

## Bloqueios

**Experimento 2 não tem dados aqui.** Você rodou em outro chat; os arquivos não
estão nesta máquina. Sem os dados brutos (nota humana e nota do sistema, por
redação e por competência) não dá para calcular QWK nem reportar número.

Dois caminhos:
- **Com os dados:** o artigo responde PP1, PP2 e PP3, compara com Barbosa et al.
  e fica muito mais forte.
- **Sem os dados:** PP2 sai do artigo e vira trabalho futuro. A ausência de nota
  oficial volta a ser a limitação principal, declarada abertamente. O artigo
  ainda se sustenta, mas um parecerista vai perguntar por que não se usou o
  Essay-BR, que está público sob licença MIT.

## Correção registrada

O corpus tinha **70%** de cópia na R4, não 74%. O valor 74% pertence a outra
redação, usada no comparativo Node/Python (46 palavras, 34 copiadas), e foi
transcrito por engano para o experimento de confiabilidade. Corrigido em
`pesquisa/README.md` e em `docs/index.html`.

**Pendente:** o resumo do JECET (`resumo_jecet.docx` e a versão que você já
montou no template) ainda diz 74%. Precisa ser corrigido antes de enviar.
