# -*- coding: utf-8 -*-
"""Conteúdo do artigo para a RECIMA21. Marcação inline: _itálico_."""

TITULOS = [
    "CORREÇÃO AUTOMÁTICA DE REDAÇÕES DO ENEM COM MODELOS DE LINGUAGEM DE "
    "GRANDE ESCALA: CONFIABILIDADE TESTE-RETESTE E DETECÇÃO DE CÓPIA DOS "
    "TEXTOS MOTIVADORES",

    "AUTOMATED ESSAY SCORING FOR THE BRAZILIAN NATIONAL HIGH SCHOOL EXAM "
    "(ENEM) WITH LARGE LANGUAGE MODELS: TEST-RETEST RELIABILITY AND "
    "DETECTION OF COPYING FROM SOURCE TEXTS",

    "CORRECCIÓN AUTOMÁTICA DE REDACCIONES DEL ENEM CON MODELOS DE LENGUAJE "
    "DE GRAN ESCALA: FIABILIDAD TEST-RETEST Y DETECCIÓN DE COPIA DE LOS "
    "TEXTOS MOTIVADORES",
]

RESUMO = (
    "A redação do Exame Nacional do Ensino Médio (ENEM) é avaliada por uma matriz "
    "de cinco competências e depende de correção humana em larga escala, o que "
    "restringe a oferta de prática com devolutiva na educação básica. Este artigo "
    "apresenta o desenvolvimento e a avaliação empírica de um sistema web de "
    "correção automática de redações no modelo ENEM, construído sobre um modelo "
    "de linguagem de grande escala de propósito geral e acoplado a um detector "
    "determinístico de cópia dos textos motivadores baseado em _shingles_ de sete "
    "palavras. Investigou-se se as notas produzidas são consistentes o bastante "
    "para sustentar uso avaliativo e de que modo o sistema opera a regra de "
    "desconsideração dos trechos copiados. Realizou-se experimento de "
    "confiabilidade teste-reteste com seis redações de um mesmo tema, submetidas "
    "dez vezes a dois modelos sob parâmetros idênticos, totalizando 120 "
    "correções. Os resultados apontam amplitude média de 60,0 pontos e "
    "coeficiente de variação médio de 5,8% e 5,5%, sem diferença entre os "
    "modelos; a dispersão concentra-se nas redações de cópia parcial, chegando a "
    "14,8%, e desaparece nos extremos; o zeramento comporta-se como função "
    "degrau, sem ocorrência até 45% de cópia medida e com dez em dez ocorrências "
    "a 74%; e há viés sistemático de leniência de +55 pontos de um modelo sobre o "
    "outro. Conclui-se que o artefato é adequado ao uso formativo, mas não ao uso "
    "somativo isolado, e que o limiar de zeramento deve ser regra determinística "
    "em código, e não julgamento do modelo."
)

PALAVRAS_CHAVE = (
    "Correção automática de redações. Modelos de linguagem de grande escala. ENEM. "
    "Confiabilidade teste-reteste. Detecção de cópia."
)

ABSTRACT = (
    "The essay component of the Brazilian National High School Exam (ENEM) is "
    "assessed through a five-competency rubric and depends on large-scale human "
    "rating, which limits the availability of practice with feedback in basic "
    "education. This paper presents the development and empirical evaluation of a "
    "web system for automated ENEM essay scoring, built on a general-purpose large "
    "language model and coupled with a deterministic detector of copying from the "
    "prompt's source texts based on seven-word _shingles_. The research problem is "
    "whether the scores produced by such an arrangement are consistent enough to "
    "support assessment use, and how the system enacts the rule that disregards "
    "copied excerpts. A test-retest reliability experiment was carried out with six "
    "essays on a single topic, submitted ten times to two models under identical "
    "parameters, totalling 120 scoring runs. Results show a mean range of 60.0 points "
    "and mean coefficients of variation of 5.8% and 5.5%, with no reliability "
    "difference between models; dispersion concentrates on partially copied essays, "
    "reaching 14.8%, and vanishes at both extremes; zeroing for copying behaves as a "
    "step function, with no occurrence up to 45% measured copying and ten out of ten "
    "occurrences at 74%; and there is a systematic leniency bias of +55 points of one "
    "model over the other. We conclude that the artefact is suitable for formative "
    "use with feedback, but not for stand-alone summative use, and that the zeroing "
    "threshold should be a deterministic rule in code rather than a model judgement."
)

KEYWORDS = (
    "Automated essay scoring. Large language models. ENEM. Test-retest reliability. "
    "Copy detection."
)

RESUMEN = (
    "La redacción del Examen Nacional de Enseñanza Media (ENEM) se evalúa "
    "mediante una matriz de cinco competencias y depende de corrección humana a "
    "gran escala, lo que restringe la práctica con devolución en la educación "
    "básica. Este artículo presenta el desarrollo y la evaluación empírica de un "
    "sistema web de corrección automática de redacciones en el modelo ENEM, "
    "construido sobre un modelo de lenguaje de gran escala de propósito general y "
    "acoplado a un detector determinista de copia de los textos motivadores "
    "basado en _shingles_ de siete palabras. Se investigó si las notas son lo "
    "bastante consistentes para sostener un uso evaluativo y cómo el sistema "
    "aplica la regla de desconsideración de los fragmentos copiados. Se realizó "
    "un experimento de fiabilidad test-retest con seis redacciones de un mismo "
    "tema, sometidas diez veces a dos modelos bajo parámetros idénticos, "
    "totalizando 120 correcciones. Los resultados indican amplitud media de 60,0 "
    "puntos y coeficientes de variación medios de 5,8% y 5,5%, sin diferencia "
    "entre modelos; la dispersión se concentra en las redacciones de copia "
    "parcial, llegando a 14,8%, y desaparece en los extremos; la anulación se "
    "comporta como función escalonada, sin ocurrencia hasta 45% de copia y con "
    "diez de diez en 74%; y hay sesgo sistemático de lenidad de +55 puntos de un "
    "modelo sobre el otro. Se concluye que el artefacto es adecuado para el uso "
    "formativo, pero no para el sumativo aislado, y que el umbral de anulación "
    "debe ser regla determinista en código, y no juicio del modelo."
)

PALABRAS_CLAVE = (
    "Corrección automática de redacciones. Modelos de lenguaje de gran escala. ENEM. "
    "Fiabilidad test-retest. Detección de copia."
)

# ─── Dados dos autores ──────────────────────────────────────────────────────
# A revista exige AVALIAÇÃO CEGA na primeira submissão: este bloco só entra na
# versão final, gerada com `python3 montar.py --final`.
# Formato exigido pelo template: "Nome Completo, Instituição, titulação."
# ("Não incluir outras informações!!")

AUTORES = [
    "Douglas Hiroiti Kadomoto, IFSP, graduando em Análise e Desenvolvimento de "
    "Sistemas.",
    "Ana Paula Abrantes de Castro Shiguemori, IFSP, doutora.",
]

CEGO = ("[DADOS DOS AUTORES — campo deixado em branco para a avaliação cega; "
        "preencher somente na versão final, com nome completo, instituição e "
        "titulação de cada autor.]")

# ─── Corpo do artigo ────────────────────────────────────────────────────────
# ("h1", texto) título de seção; ("h2", texto) subtítulo; ("p", texto) parágrafo;
# ("cap", texto) legenda acima do quadro/tabela; ("fonte", texto) fonte abaixo;
# ("tbl", chave) tabela; ("cit", texto) citação longa recuada; ("ref", texto) referência.

CORPO = [
("h1", "INTRODUÇÃO"),

("p", "A redação do Exame Nacional do Ensino Médio (ENEM) ocupa posição singular na "
 "educação básica brasileira: é a única prova do exame que exige produção textual "
 "autoral, vale mil pontos e é avaliada por uma matriz de cinco competências, cada "
 "uma pontuada em faixas de quarenta pontos entre zero e duzentos (BRASIL, 2024). "
 "Essa arquitetura de avaliação, aplicada anualmente a milhões de participantes, "
 "depende de um contingente numeroso de avaliadores treinados, de dupla correção "
 "independente e de procedimentos de terceira correção quando as notas divergem além "
 "de limites definidos. O custo e a complexidade logística desse arranjo têm um "
 "efeito colateral pouco discutido: no cotidiano escolar, o estudante raramente "
 "consegue escrever e receber devolutiva na frequência necessária para aprender a "
 "escrever. Corrigir uma redação segundo as cinco competências, com comentário "
 "qualificado por competência, é trabalho demorado, e um professor com muitas turmas "
 "não tem como fazê-lo semanalmente."),

("p", "É nessa lacuna que a correção automática de redações — designada na literatura "
 "internacional como _automated essay scoring_ — se apresenta como possibilidade. "
 "Trata-se de campo com mais de meio século de história, iniciado com a proposta "
 "pioneira de Page (1966) e consolidado em sistemas comerciais de larga escala "
 "baseados em traços linguísticos mensuráveis (ATTALI; BURSTEIN, 2006; SHERMIS; "
 "BURSTEIN, 2013). A emergência recente dos modelos de linguagem de grande escala, "
 "ou _Large Language Models_ (BROWN et al., 2020), alterou radicalmente o custo de "
 "entrada: onde antes era preciso treinar um modelo específico sobre milhares de "
 "redações anotadas, hoje é possível obter avaliação por competências e comentário "
 "em linguagem natural a partir de uma instrução textual bem formulada, sem qualquer "
 "treinamento próprio (MIZUMOTO; EGUCHI, 2023; YANCEY et al., 2023)."),

("p", "Essa facilidade, no entanto, deslocou o problema em vez de resolvê-lo. Um modelo "
 "generativo de propósito geral produz texto por amostragem probabilística "
 "(HOLTZMAN et al., 2020), o que significa que a mesma entrada pode gerar saídas "
 "diferentes. Quando a saída é uma nota, essa variabilidade deixa de ser "
 "característica desejável de fluência e passa a ser ruído de medida. A literatura "
 "sobre uso de modelos de linguagem como juízes de qualidade já registrou "
 "instabilidade e vieses de posição e de verbosidade em tarefas de julgamento "
 "(ZHENG et al., 2023), e a crítica à correção automática acumulada nas últimas "
 "décadas alerta que sistemas podem premiar aquilo que sabem medir, e não aquilo que "
 "importa (PERELMAN, 2013). Some-se a isso a advertência de Bender et al. (2021) "
 "sobre a opacidade dos grandes modelos e o problema fica delineado: adotar um "
 "corretor automático sem medir seu comportamento é transferir a um sistema opaco "
 "uma decisão que afeta a trajetória escolar de estudantes."),

("p", "Há ainda um aspecto específico do ENEM que a literatura internacional não "
 "contempla. A proposta de redação do exame é acompanhada de textos motivadores, e a "
 "regra oficial determina que trechos copiados desses textos não sejam computados "
 "como produção do participante, podendo levar à anulação quando a redação for "
 "essencialmente cópia (BRASIL, 2024). Um corretor automático que ignore essa regra "
 "não apenas erra a nota: ensina ao estudante, pela devolutiva, que copiar o texto "
 "motivador é estratégia aceitável."),

("p", "Formula-se, assim, o problema de pesquisa: um sistema de correção automática de "
 "redações construído sobre um modelo de linguagem de grande escala de propósito "
 "geral produz notas suficientemente consistentes para sustentar uso avaliativo, e "
 "de que modo esse sistema implementa a regra de desconsideração da cópia dos textos "
 "motivadores?"),

("p", "O objetivo geral deste trabalho é desenvolver um sistema web de correção "
 "automática de redações no modelo ENEM, dotado de detecção de cópia dos textos "
 "motivadores, e avaliar empiricamente sua confiabilidade teste-reteste. Como "
 "objetivos específicos, propõe-se: (a) implementar o artefato, contemplando "
 "autenticação, banco de temas com textos motivadores, correção pelas cinco "
 "competências com devolutiva, histórico e perfil de professor; (b) implementar e "
 "integrar à correção um detector determinístico de cópia por _shingles_; (c) medir "
 "a dispersão das notas atribuídas ao mesmo texto sob repetição idêntica; (d) "
 "comparar dois modelos quanto à confiabilidade e ao nível de severidade; (e) "
 "caracterizar o comportamento da regra de zeramento em função do percentual de "
 "cópia medido; e (f) derivar implicações de projeto e limites de uso pedagógico a "
 "partir das evidências obtidas."),

("p", "A justificativa do estudo tem três dimensões. Do ponto de vista pedagógico, "
 "ampliar a oferta de prática com devolutiva é medida de equidade, porque atinge "
 "sobretudo estudantes sem acesso a cursinho ou a professor particular. Do ponto de "
 "vista técnico, a adoção de modelos de linguagem por estudantes já é fato "
 "consumado, ocorrendo em geral sem qualquer validação, sem registro de "
 "variabilidade e sem tratamento da regra de cópia; documentar empiricamente esse "
 "comportamento é condição para discuti-lo. Do ponto de vista ético, a literatura em "
 "avaliação educacional é explícita quanto ao fato de que confiabilidade é "
 "pré-requisito de validade, e não sua garantia (AERA; APA; NCME, 2014): um "
 "instrumento que responde coisas diferentes à mesma pergunta não pode fundamentar "
 "decisão sobre ninguém. Medir essa consistência, antes de propor qualquer uso "
 "institucional, é o mínimo exigível."),

("p", "O artigo está organizado em quatro seções além desta introdução. A primeira "
 "apresenta o referencial teórico, percorrendo a matriz de competências do ENEM, a "
 "trajetória da correção automática, o uso de modelos de linguagem como avaliadores, "
 "a noção de confiabilidade e a técnica de detecção de similaridade empregada. A "
 "segunda descreve a metodologia, incluindo a arquitetura do artefato e o "
 "delineamento experimental. A terceira apresenta e discute os resultados. A quarta "
 "sintetiza as conclusões e aponta a agenda de continuidade."),

# ─── 1 ───
("h1", "1 – REFERENCIAL TEÓRICO"),

("h2", "1.1 A redação do ENEM e a matriz de cinco competências"),

("p", "A avaliação da redação do ENEM é estruturada em cinco competências, descritas na "
 "cartilha oficial do participante (BRASIL, 2024) e sintetizadas no Quadro 1. Cada "
 "competência é pontuada em seis níveis discretos — 0, 40, 80, 120, 160 e 200 —, e a "
 "nota final é a soma das cinco, limitada a mil pontos. A granularidade de quarenta "
 "pontos é relevante para a análise que se segue: qualquer variação inferior a esse "
 "valor é impossível na escala, e uma variação de oitenta pontos na nota final "
 "corresponde ao deslocamento de dois níveis em uma competência, ou de um nível em "
 "duas competências distintas."),

("cap", "Quadro 1 – Matriz de competências da redação do ENEM"),
("tbl", "competencias"),
("fonte", "Fonte: elaborado pelos autores com base em Brasil (2024)."),

("p", "A matriz é acompanhada de um conjunto de situações que conduzem à atribuição de "
 "nota zero, entre as quais figura a cópia de textos motivadores. O documento "
 "oficial estabelece que os trechos copiados dos textos da proposta sejam "
 "desconsiderados para efeito de cômputo da produção do participante, o que produz "
 "dois efeitos distintos: a penalização proporcional, quando a cópia é parcial, e a "
 "anulação, quando a redação se reduz essencialmente à reprodução dos textos "
 "motivadores (BRASIL, 2024). Essa dupla natureza — gradual em uma faixa, binária em "
 "outra — é justamente o ponto em que o comportamento de um corretor automático "
 "precisa ser verificado, e não presumido."),

("h2", "1.2 Da contagem de traços aos modelos neurais"),

("p", "A correção automática de redações nasce com Page (1966), que propôs prever a nota "
 "humana a partir de indicadores superficiais mensuráveis, como extensão do texto e "
 "média de comprimento das palavras. A proposta foi revisitada por Wresch (1993), "
 "que apontou, ainda nos anos 1990, o problema central do campo: correlacionar-se "
 "com a nota humana não é o mesmo que avaliar o que o avaliador humano avalia. A "
 "geração seguinte de sistemas, da qual o _e-rater_ é o exemplo mais documentado "
 "(ATTALI; BURSTEIN, 2006), ampliou consideravelmente o conjunto de traços — "
 "gramática, uso, mecânica, desenvolvimento, organização, vocabulário — e passou a "
 "operar em avaliações de larga escala. Shermis e Burstein (2013) sistematizam esse "
 "estágio do campo e suas aplicações."),

("p", "A crítica mais contundente a essa geração de sistemas foi formulada por Perelman "
 "(2013), que demonstrou ser possível obter notas altas com textos deliberadamente "
 "vazios, porém longos e lexicalmente sofisticados. O argumento não é acessório: ele "
 "estabelece que a validade de um corretor automático não se demonstra por "
 "correlação agregada com notas humanas, e sim pelo exame do que o sistema faz em "
 "casos adversariais específicos. É a mesma lógica que orienta o desenho "
 "experimental adotado neste trabalho, no qual se constrói deliberadamente um "
 "gradiente de cópia para observar o comportamento do sistema em cada faixa."),

("p", "Em língua portuguesa, o campo é consideravelmente menos desenvolvido. Amorim e "
 "Veloso (2017) apresentam uma das primeiras análises multiaspecto de correção "
 "automática para o português brasileiro, e Marinho, Anchiêta e Pardo (2022) "
 "disponibilizam o _Essay-BR_, corpus de redações no modelo ENEM com notas por "
 "competência, que se tornou referência para trabalhos posteriores. A existência "
 "desse corpus é relevante para a agenda de continuidade descrita ao final deste "
 "artigo, ainda que ele não tenha sido utilizado no experimento aqui relatado."),

("h2", "1.3 Modelos de linguagem de grande escala como avaliadores"),

("p", "Os modelos de linguagem de grande escala introduzem uma descontinuidade técnica no "
 "campo. Brown et al. (2020) demonstraram que modelos suficientemente grandes "
 "executam tarefas novas a partir de poucos exemplos, ou mesmo apenas de uma "
 "descrição textual da tarefa, sem ajuste de parâmetros. Aplicada à correção de "
 "redações, essa propriedade dispensa a etapa de treinamento supervisionado sobre "
 "corpus anotado que dominava o campo: basta descrever a matriz de competências e os "
 "critérios em uma instrução."),

("p", "Os resultados relatados são encorajadores. Mizumoto e Eguchi (2023) verificaram "
 "concordância substancial entre notas de um modelo de linguagem e notas humanas em "
 "redações de inglês como língua estrangeira, e Yancey et al. (2023) obtiveram "
 "desempenho competitivo na classificação de redações curtas na escala do Quadro "
 "Europeu Comum de Referência. Em ambos os casos, contudo, a métrica reportada é de "
 "concordância com o gabarito, e não de estabilidade do próprio sistema sob "
 "repetição — distinção que este trabalho toma como central."),

("p", "A razão para esperar instabilidade é arquitetural. A geração de texto por esses "
 "modelos envolve amostragem sobre uma distribuição de probabilidade, e as "
 "estratégias de decodificação usualmente empregadas introduzem aleatoriedade "
 "deliberada para evitar degeneração do texto (HOLTZMAN et al., 2020). Zheng et al. "
 "(2023), ao investigarem o uso de modelos de linguagem como juízes, documentaram "
 "não apenas variabilidade, mas vieses sistemáticos de posição, verbosidade e "
 "autoafinidade. Bender et al. (2021), por sua vez, argumentam que a escala desses "
 "modelos torna opacos os critérios efetivamente aplicados, o que, no contexto "
 "avaliativo, significa que a justificativa apresentada ao estudante pode não "
 "corresponder ao processo que gerou a nota."),

("h2", "1.4 Confiabilidade como pré-requisito da validade"),

("p", "Na teoria da medida educacional, confiabilidade designa a consistência dos "
 "resultados de um instrumento, e validade designa o grau em que as interpretações "
 "propostas para esses resultados são sustentadas por evidência (AERA; APA; NCME, "
 "2014). A relação entre as duas é assimétrica: a confiabilidade é condição "
 "necessária, porém não suficiente, para a validade. Um instrumento perfeitamente "
 "consistente pode medir de forma estável a coisa errada; um instrumento "
 "inconsistente, porém, não pode medir coisa alguma de forma defensável."),

("p", "A confiabilidade teste-reteste é a forma mais direta de verificar essa condição em "
 "um sistema computacional: aplica-se o mesmo instrumento ao mesmo objeto, em "
 "condições idênticas, e observa-se a dispersão do resultado. Em correção humana, o "
 "análogo é a concordância entre avaliadores, tradicionalmente medida por índices de "
 "concordância ponderada (COHEN, 1968). Em correção automática determinística, a "
 "questão sequer se coloca, porque o mesmo texto produz sempre a mesma nota. É "
 "precisamente a introdução de um componente estocástico no centro do instrumento "
 "que torna a medição de confiabilidade obrigatória — e é isso que distingue o "
 "arranjo aqui investigado dos sistemas da geração anterior."),

("h2", "1.5 Detecção de similaridade textual por _shingles_"),

("p", "A identificação de trechos copiados entre dois documentos é problema clássico de "
 "recuperação de informação. A técnica de _shingling_, formalizada por Broder "
 "(1997), consiste em representar cada documento pelo conjunto de todas as suas "
 "subsequências contíguas de _n_ itens e estimar a semelhança entre documentos pela "
 "sobreposição desses conjuntos. Aplicada a palavras em vez de caracteres, a técnica "
 "captura exatamente o fenômeno de interesse no contexto do ENEM: a transcrição "
 "literal de sequências do texto motivador."),

("p", "A escolha do tamanho da sequência define o comportamento do detector. Valores "
 "pequenos produzem falsos positivos, porque sequências curtas de palavras funcionais "
 "recorrem naturalmente em qualquer texto sobre o mesmo assunto; valores grandes "
 "reduzem a sensibilidade a paráfrases mínimas. Trata-se, portanto, de parâmetro de "
 "projeto sujeito a verificação empírica, e não de constante universal. A vantagem "
 "decisiva da técnica, para os fins deste trabalho, é ser inteiramente "
 "determinística: dado o mesmo par de textos, o percentual de cópia é sempre o "
 "mesmo, o que permite usá-lo como variável independente confiável no experimento."),

("h2", "1.6 Avaliação formativa e o lugar da devolutiva"),

("p", "A distinção entre avaliação formativa e somativa é decisiva para delimitar o uso "
 "legítimo de um corretor automático. Luckesi (2011) contrapõe a avaliação que "
 "classifica à avaliação que subsidia a aprendizagem, e Freire (1996) situa a "
 "devolutiva como ato dialógico, e não como veredito. Antunes (2003), ao tratar "
 "especificamente do ensino de língua portuguesa, sustenta que a escrita se aprende "
 "escrevendo e reescrevendo, o que pressupõe ciclos frequentes de produção e "
 "retorno — exatamente o que a correção humana em larga escala não consegue "
 "oferecer."),

("p", "Holmes, Bialik e Fadel (2019) organizam as aplicações de inteligência artificial "
 "em educação e destacam que os ganhos mais consistentes se dão em sistemas de apoio "
 "e prática, não em substituição do juízo docente. É nesse enquadramento que o "
 "artefato descrito a seguir se situa: instrumento de ensaio e devolutiva, "
 "subordinado ao professor, e não dispositivo de certificação."),

# ─── 2 ───
("h1", "2 – METODOLOGIA"),

("h2", "2.1 Natureza e delineamento da pesquisa"),

("p", "Quanto à natureza, trata-se de pesquisa aplicada; quanto aos objetivos, "
 "exploratória e descritiva; quanto aos procedimentos, combina construção de "
 "artefato computacional e experimento (GIL, 2017). O desenho articula dois "
 "momentos. No primeiro, desenvolveu-se um sistema web funcional de correção "
 "automática de redações no modelo ENEM. No segundo, o próprio sistema foi submetido "
 "a um experimento de confiabilidade teste-reteste, no qual a entrada é mantida "
 "constante e se observa a dispersão da saída."),

("p", "Cabe delimitar com precisão o que o experimento mede. Mede-se consistência, isto "
 "é, a variação da nota atribuída ao mesmo texto sob condições idênticas. Não se "
 "mede acurácia, porque o corpus utilizado não possui notas oficiais de referência. "
 "Essa delimitação não é uma ressalva acessória: é o que separa uma afirmação "
 "sustentada pelos dados de uma extrapolação indevida, e orienta a redação de toda a "
 "seção de resultados."),

("h2", "2.2 O artefato: arquitetura e funcionalidades"),

("p", "O sistema foi implementado inicialmente em Node.js com o _framework_ Express, "
 "persistência em SQLite e interface web em página única. A autenticação emprega "
 "_JSON Web Tokens_ com senhas armazenadas sob _hash_ de Bcrypt. As funcionalidades "
 "implementadas são: cadastro e autenticação de usuários; banco de temas com textos "
 "motivadores, gerido por usuários com perfil de professor; submissão de redação "
 "sobre tema do banco ou sobre tema livre; correção pelas cinco competências com "
 "devolutiva por competência e sugestões de melhoria; detecção de cópia dos textos "
 "motivadores; histórico de correções por usuário; e controle de cota mensal de "
 "correções gratuitas, com possibilidade de uso de chave de interface de programação "
 "própria."),

("p", "Posteriormente, o _backend_ foi portado para Python com o _framework_ FastAPI, "
 "visando à integração como módulo de um sistema institucional mais amplo. Nessa "
 "versão, a identidade e o papel do usuário passam a ser fornecidos pelo sistema "
 "hospedeiro, eliminando a duplicação de autenticação, e a resposta do modelo passa a "
 "ser obtida por saída estruturada, o que dispensa a análise sintática de texto livre "
 "e elimina o risco de resposta malformada. O algoritmo de detecção de cópia foi "
 "portado de forma fiel, com verificação de equivalência numérica contra a "
 "implementação original, inclusive quanto à regra de arredondamento. O módulo "
 "portado é acompanhado de vinte testes automatizados que não consomem a interface de "
 "programação externa, cobrindo os estados do detector, o controle de permissões, a "
 "cota mensal e o isolamento do histórico entre usuários. É essa versão do sistema "
 "que foi instrumentada para o experimento."),

("h2", "2.3 Detecção de cópia dos textos motivadores"),

("p", "O detector implementa a técnica de _shingles_ de palavras (BRODER, 1997) com "
 "sequências de sete palavras. O procedimento tem quatro etapas. Primeiro, ambos os "
 "textos são segmentados em unidades e normalizados: conversão para caixa baixa, "
 "decomposição canônica com remoção de diacríticos e supressão de pontuação e "
 "símbolos, de modo que variações de acentuação e pontuação não mascarem a cópia. "
 "Segundo, constrói-se o conjunto de todas as sequências de sete palavras "
 "normalizadas presentes nos textos motivadores. Terceiro, percorre-se a redação e, "
 "sempre que uma sequência de sete palavras pertence a esse conjunto, todas as "
 "palavras da sequência são marcadas como copiadas. Quarto, palavras marcadas "
 "contíguas são agrupadas em trechos legíveis, apresentados ao usuário em sua forma "
 "original."),

("p", "O percentual de cópia é a razão entre palavras marcadas e total de palavras da "
 "redação. O valor de sete palavras foi adotado como equilíbrio entre falsos "
 "positivos, frequentes em sequências curtas de palavras funcionais, e perda de "
 "sensibilidade a paráfrases mínimas; a determinação empírica do valor ótimo consta "
 "da agenda de continuidade. O ponto relevante para o experimento é que o detector é "
 "determinístico, de modo que o percentual de cópia de cada redação do corpus é "
 "medido, e não estimado."),

("h2", "2.4 A instrução de correção e a regra de penalização"),

("p", "A instrução fornecida ao modelo descreve as cinco competências com seus títulos "
 "oficiais, restringe as notas por competência aos seis níveis válidos e determina o "
 "formato da resposta. Quanto à cópia, a instrução estabelece que os trechos "
 "detectados não sejam computados como produção do participante; que a penalização "
 "seja proporcional ao percentual copiado, incidindo principalmente sobre as "
 "Competências II e III; que a nota total seja zerada quando a redação for "
 "essencialmente cópia sem elaboração própria relevante; e que a ocorrência seja "
 "comentada na devolutiva, com orientação de reescrita."),

("p", "A entrada enviada ao modelo é montada com o título do tema, os textos "
 "motivadores, a lista dos trechos copiados efetivamente detectados, acompanhada do "
 "percentual medido, e o texto da redação. Registre-se, desde já, uma decisão de "
 "projeto que os resultados irão questionar: o limiar de zeramento não é uma regra "
 "em código, mas uma expressão qualitativa — “essencialmente cópia” — cuja "
 "interpretação é delegada ao modelo, ainda que o percentual exato esteja disponível "
 "e pudesse ser usado como critério determinístico."),

("h2", "2.5 Delineamento do experimento"),

("p", "O experimento adota delineamento fatorial completo com repetição: seis redações × "
 "dois modelos × dez repetições, totalizando 120 correções. Todas as execuções "
 "utilizaram a mesma instrução de sistema, o mesmo limite de oito mil _tokens_ de "
 "resposta, o mesmo nível de esforço de raciocínio e a mesma rotina de montagem de "
 "entrada do módulo de produção — o que é essencial, pois garante que o objeto "
 "medido é o sistema real, e não uma reimplementação simplificada. A única variável "
 "manipulada entre condições é o modelo."),

("p", "Os dois modelos comparados foram _claude-opus-5_ e _claude-sonnet-4-5_, ambos do "
 "mesmo fornecedor, correspondentes respectivamente ao modelo adotado na versão "
 "portada e ao modelo da versão original do sistema. A comparação interessa por duas "
 "razões práticas: a substituição de modelo é operação trivial em sistemas desse "
 "tipo, frequentemente motivada por custo, e é preciso saber que efeito essa "
 "substituição produz sobre a nota do estudante."),

("h2", "2.6 Corpus"),

("p", "O corpus reúne seis redações sobre o tema “Caminhos para combater a desinformação "
 "na internet”, acompanhado de três textos motivadores. As redações foram escritas "
 "especificamente para o experimento, de modo a cobrir simultaneamente um gradiente "
 "de qualidade e um gradiente de cópia dos textos motivadores. O percentual de cópia "
 "indicado no Quadro 2 é o valor medido pelo detector descrito na seção 2.3, e não "
 "uma estimativa do autor do corpus."),

("cap", "Quadro 2 – Caracterização do corpus experimental"),
("tbl", "corpus"),
("fonte", "Fonte: elaborado pelos autores (2026)."),

("p", "A composição do corpus responde ao desenho: as redações R1, R2 e R3 isolam o "
 "efeito da qualidade textual sem cópia; R5, R6 e R4 constroem o gradiente de cópia "
 "em 29%, 45% e 74%. A cobertura da faixa intermediária é deliberada, pois é nela "
 "que a regra do ENEM exige penalização proporcional, e não decisão binária."),

("h2", "2.7 Métricas"),

("p", "Para cada combinação de redação e modelo, calcularam-se a média e o desvio-padrão "
 "amostral das dez notas totais, a amplitude, o coeficiente de variação — razão entre "
 "desvio-padrão e média, expressa em percentual — e a frequência da nota modal, "
 "registrada como número de respostas idênticas em dez. Calcularam-se ainda a "
 "frequência de zeramento por redação e modelo e a diferença entre as médias dos dois "
 "modelos por redação. O coeficiente de variação foi adotado como medida principal "
 "por ser adimensional, o que permite comparar a dispersão entre redações de níveis "
 "de nota muito distintos; a amplitude é reportada em conjunto por ser diretamente "
 "interpretável na escala de quarenta pontos das competências."),

# ─── 3 ───
("h1", "3 – RESULTADOS E DISCUSSÃO"),

("p", "O experimento consumiu 120 correções, 151.937 _tokens_ de saída e 44 minutos de "
 "processamento. Nenhuma execução falhou ou retornou resposta malformada, o que "
 "corrobora, em caráter secundário, a decisão de projeto de adotar saída estruturada "
 "na versão portada. Os resultados são apresentados em cinco recortes: "
 "confiabilidade agregada, dispersão por redação, comportamento da regra de cópia, "
 "viés entre modelos e um achado de validade."),

("h2", "3.1 Os dois modelos são indistinguíveis quanto à confiabilidade"),

("p", "Agregando as seis redações, _claude-opus-5_ apresentou amplitude média de 60,0 "
 "pontos e coeficiente de variação médio de 5,8%; _claude-sonnet-4-5_ apresentou "
 "amplitude média de 60,0 pontos e coeficiente de variação médio de 5,5%. A "
 "diferença de 0,3 ponto percentual entre os coeficientes, calculados sobre seis "
 "redações cada, não sustenta afirmação de superioridade de qualquer um dos modelos quanto "
 "à estabilidade."),

("p", "O resultado merece registro metodológico. Em etapas anteriores deste mesmo "
 "projeto, com amostras de uma e de três repetições, foram formuladas duas "
 "conclusões opostas sobre qual modelo seria mais estável — e ambas foram "
 "desmentidas pela corrida completa. A lição é a que a estatística elementar já "
 "prescreve: amostras pequenas não sustentam afirmações sobre variância, e a "
 "tentação de concluir a partir de duas ou três execuções é particularmente forte "
 "justamente porque cada execução é lenta e custosa."),

("p", "Convém dimensionar o achado na escala do instrumento. Uma amplitude média de 60,0 "
 "pontos sobre um total de mil corresponde a 6% da escala, mas, sobretudo, "
 "corresponde a uma vez e meia o passo de quarenta pontos de uma competência. Na "
 "prática, dois estudantes com desempenho idêntico podem receber notas que diferem "
 "em um ou dois níveis de competência — diferença que, em um processo seletivo, não "
 "é desprezível, e que em uso formativo é aceitável desde que declarada."),

("h2", "3.2 A dispersão acompanha a ambiguidade, não o modelo"),

("p", "A Tabela 1 desagrega a dispersão por redação e modelo. A leitura por linha revela "
 "um padrão que o valor agregado oculta."),

("cap", "Tabela 1 – Dispersão das notas por redação e modelo (dez repetições por célula)"),
("tbl", "dispersao"),
("fonte", "Fonte: elaborada pelos autores (2026)."),

("p", "Nas redações sem cópia e nos extremos do gradiente, o sistema é estável: "
 "_claude-opus-5_ devolveu a mesma nota nas dez repetições para R1, R2 e R4, com "
 "coeficiente de variação nulo. Nas redações de cópia parcial, a dispersão salta: "
 "12,0% em R5 e 11,4% em R6 para _claude-opus-5_, e 14,8% em R5 para "
 "_claude-sonnet-4-5_. A contagem de respostas idênticas mostra o mesmo fenômeno de "
 "outro ângulo: de dez em dez em R1 e R2, cai para quatro em dez em R5 e três em dez "
 "em R6."),

("p", "A interpretação é direta e tem consequência de projeto. O sistema é decidido "
 "justamente onde a decisão é fácil — um texto claramente bom, um texto claramente "
 "copiado — e vacila onde um avaliador humano também deliberaria, que é a faixa de "
 "cópia parcial. Essa correspondência entre a dispersão do sistema e a ambiguidade "
 "intrínseca do caso é, em certo sentido, um bom sinal de que o modelo está "
 "respondendo ao conteúdo. O problema não está em vacilar, mas em não sinalizar a "
 "vacilação: a resposta apresentada ao estudante tem a mesma forma assertiva quer "
 "provenha de uma célula com coeficiente de variação nulo, quer provenha de uma "
 "célula com 14,8%. Um sistema honesto com o usuário deveria expressar essa "
 "incerteza, seja por intervalo, seja por reexecução com agregação."),

("p", "Observe-se ainda o caso de R6 sob _claude-sonnet-4-5_: dez repetições idênticas em "
 "280 pontos, coeficiente de variação nulo, enquanto o outro modelo, na mesma "
 "redação, oscilou entre 320 e 440. A estabilidade, isoladamente, não informa sobre "
 "correção: um modelo pode ser consistentemente severo. É o que a discussão da seção "
 "3.4 evidencia."),

("h2", "3.3 A regra de cópia opera como função degrau"),

("p", "A Tabela 2 apresenta a frequência de zeramento em função do percentual de cópia "
 "medido pelo detector."),

("cap", "Tabela 2 – Frequência de zeramento em função da cópia medida"),
("tbl", "zeramento"),
("fonte", "Fonte: elaborada pelos autores (2026)."),

("p", "O padrão é inequívoco e idêntico nos dois modelos: nenhuma nota zerada até 45% de "
 "cópia medida, e zeramento em dez de dez repetições a 74%. Não há faixa de "
 "transição observável entre esses dois pontos. A instrução pedia penalização "
 "proporcional ao percentual copiado e zeramento quando a redação fosse "
 "“essencialmente cópia”; o modelo implementou a primeira parte e converteu a "
 "segunda em uma função degrau cujo limiar se situa em algum ponto do intervalo "
 "entre 45% e 74%, não determinado por este experimento."),

("p", "A penalização gradual, essa sim, existe e é substancial: sob _claude-opus-5_, R1 "
 "obteve média de 960 pontos, enquanto R6, com 45% de cópia, obteve 380. O problema "
 "não é a ausência de penalização, e sim a localização do limiar de anulação. "
 "Ninguém decidiu onde ele está: ele está implícito no julgamento do modelo, "
 "reproduzindo a interpretação que o modelo faz da expressão “essencialmente cópia”. "
 "Um estudante com 60% de cópia pode ou não ser anulado, e o sistema não tem como "
 "responder qual dos dois desfechos ocorrerá."),

("p", "A implicação de projeto é imediata e foi incorporada à agenda de continuidade: "
 "havendo um detector determinístico que fornece o percentual exato, o limiar de "
 "anulação deve ser regra explícita em código, auditável e ajustável por quem "
 "responde pedagogicamente pelo instrumento, cabendo ao modelo a avaliação "
 "qualitativa das competências. Delegar ao modelo uma decisão binária de alto "
 "impacto que pode ser expressa como comparação numérica é transferir "
 "desnecessariamente uma decisão de política avaliativa para um componente opaco "
 "(BENDER et al., 2021)."),

("h2", "3.4 Viés sistemático de severidade entre modelos"),

("p", "A Tabela 3 confronta as médias dos dois modelos redação a redação."),

("cap", "Tabela 3 – Diferença de nota média entre os modelos, por redação"),
("tbl", "vies"),
("fonte", "Fonte: elaborada pelos autores (2026)."),

("p", "_claude-opus-5_ atribuiu, em média, 55 pontos a mais que _claude-sonnet-4-5_, "
 "sendo mais alto em cinco das seis redações — o empate ocorre exatamente na redação "
 "que ambos zeraram, em que não há margem para divergir. A direção é constante em "
 "todas as redações em que há diferença, o que afasta a hipótese de ruído aleatório "
 "e caracteriza viés sistemático de severidade."),

("p", "A magnitude tem significado prático. Uma diferença de 55 pontos equivale a mais de "
 "um nível de competência e é comparável à própria amplitude média de variação do "
 "sistema. Em outras palavras, trocar o modelo — operação que, do ponto de vista de "
 "engenharia, é a alteração de uma variável de ambiente, tipicamente motivada por "
 "custo — desloca a nota de todos os estudantes em cerca de uma competência e meia. "
 "Se o sistema for usado ao longo de um semestre e o modelo for substituído no meio "
 "do percurso, o estudante observará uma queda ou um ganho de desempenho que não "
 "corresponde a nada que ele tenha feito. Daí decorre uma segunda implicação de "
 "projeto: a identificação do modelo e de seus parâmetros deve ser registrada junto "
 "de cada correção no histórico, e a substituição de modelo deve ser tratada como "
 "evento que exige recalibração, não como detalhe de configuração."),

("p", "Note-se, por fim, que a diferença não é uniforme entre redações: vai de 24 pontos "
 "em R1 a 100 pontos em R6. O viés é maior nas redações de nota mais baixa e nas de "
 "cópia parcial, o que sugere que os modelos divergem mais justamente nos casos "
 "limítrofes — o mesmo território em que a dispersão intramodelo também é máxima."),

("h2", "3.5 Um problema de validade: copiar compensa mais do que escrever mal"),

("p", "O achado mais relevante do ponto de vista pedagógico não está em nenhuma métrica "
 "de dispersão, e sim no confronto entre duas linhas da Tabela 2. A redação R5, com "
 "29% de cópia literal dos textos motivadores, obteve média de 556 pontos sob "
 "_claude-opus-5_. A redação R3, inteiramente original, porém de argumentação "
 "frágil, obteve 376 pontos. A diferença de 180 pontos favorece o texto parcialmente "
 "copiado."),

("p", "O mecanismo é compreensível: o trecho copiado é, por construção, bem escrito, "
 "coeso e pertinente ao tema, porque provém de um texto editado profissionalmente. "
 "Ao avaliar Competência I, que trata do domínio da norma culta, e Competência IV, "
 "que trata dos mecanismos de coesão, o sistema encontra evidência de qualidade que "
 "não é produção do participante — e a penalização instruída, concentrada nas "
 "Competências II e III, não compensa integralmente esse ganho indevido."),

("p", "Trata-se de um problema de validade no sentido estrito (AERA; APA; NCME, 2014): a "
 "nota não sustenta a interpretação pretendida, que é a de mensurar a competência "
 "de escrita do participante. E é a materialização, em contexto brasileiro e com "
 "modelos atuais, da crítica de Perelman (2013): o sistema premia aquilo que sabe "
 "reconhecer. O efeito pedagógico é perverso, porque a devolutiva ensina, pelo "
 "resultado, que reproduzir o texto motivador rende mais do que escrever mal com as "
 "próprias palavras — exatamente o oposto do que a regra do ENEM pretende (BRASIL, "
 "2024)."),

("p", "A correção plausível não é apenas aumentar a penalização instruída, medida cuja "
 "calibragem é ela própria incerta, mas excluir os trechos detectados do texto "
 "submetido à avaliação das competências, de modo que o sistema avalie somente o que "
 "o participante de fato escreveu, apresentando ao estudante, separadamente, o "
 "relatório de cópia. Essa alteração transforma a regra de desconsideração em "
 "operação determinística sobre a entrada, em vez de recomendação dirigida ao "
 "julgamento do modelo."),

("h2", "3.6 Uma anomalia entre sessões"),

("p", "Durante o estudo-piloto, com três repetições, a redação R4 recebeu de "
 "_claude-opus-5_ as notas 120, 0 e 200. Na corrida completa, com dez repetições, a "
 "mesma redação recebeu zero nas dez execuções. Mesmo texto, mesma instrução, mesmo "
 "modelo e mesmos parâmetros; o que difere entre as duas observações é apenas a "
 "sessão de execução, separada por alguns dias."),

("p", "Não há, com os dados disponíveis, explicação para essa discrepância, e este artigo "
 "abstém-se de propor uma. O registro tem valor metodológico: ele indica que a "
 "variabilidade pode existir não apenas entre chamadas dentro de uma mesma sessão, "
 "que é o que o delineamento adotado mede, mas também entre sessões separadas no "
 "tempo — hipótese que exigiria um delineamento com coleta distribuída ao longo de "
 "semanas para ser testada. Enquanto isso não for feito, os valores de coeficiente "
 "de variação reportados devem ser lidos como limite inferior da variabilidade "
 "total do sistema, e não como sua medida completa."),

("h2", "3.7 Limitações"),

("p", "As limitações do estudo são as seguintes. Primeira, as redações foram escritas "
 "para o experimento; não são redações reais do ENEM e não possuem nota oficial, o "
 "que impede qualquer afirmação sobre acurácia — a confiabilidade, por medir "
 "dispersão sobre o mesmo texto, não é afetada por essa condição. Segunda, dez "
 "repetições por célula descrevem adequadamente a dispersão, mas são insuficientes "
 "para teste de hipótese com poder adequado. Terceira, foram testados dois modelos "
 "de um único fornecedor, de modo que os resultados não se generalizam a modelos de "
 "outras famílias. Quarta, utilizou-se um único tema, e o efeito do tema sobre a "
 "dispersão não foi isolado. Quinta, como discutido em 3.6, a coleta concentrou-se "
 "em uma única sessão por condição. Sexta, o detector de cópia teve seu percentual "
 "utilizado como variável independente, mas sua própria precisão e sua revocação não "
 "foram medidas contra cópia injetada de forma controlada."),

# ─── 4 ───
("h1", "4 – CONSIDERAÇÕES FINAIS"),

("p", "Este trabalho desenvolveu um sistema web de correção automática de redações no "
 "modelo ENEM, com detecção determinística de cópia dos textos motivadores, e "
 "submeteu esse sistema a um experimento de confiabilidade teste-reteste de 120 "
 "correções. Retomando o problema de pesquisa, as evidências permitem três respostas "
 "delimitadas."),

("p", "Quanto à consistência, o sistema apresenta amplitude média de 60,0 pontos e "
 "coeficiente de variação médio em torno de 5,5% a 5,8%, sem diferença de "
 "estabilidade entre os dois modelos testados. Essa magnitude é compatível com uso "
 "formativo, em que o valor da correção está na devolutiva por competência e na "
 "possibilidade de reescrita, e incompatível com uso somativo isolado, em que a nota "
 "produz consequência sobre o estudante. A dispersão não se distribui de modo "
 "uniforme: concentra-se nas redações de cópia parcial, onde chega a 14,8%, e "
 "desaparece nos casos inequívocos."),

("p", "Quanto à regra de cópia, o sistema aplica penalização gradual consistente, mas "
 "converte a anulação em função degrau cujo limiar não é determinado por ninguém, "
 "situando-se em algum ponto entre 45% e 74% de cópia medida. Uma vez que o detector "
 "fornece o percentual exato, essa decisão deve migrar para regra explícita em "
 "código."),

("p", "Quanto à substituição de modelo, verificou-se viés sistemático de severidade de "
 "55 pontos entre os dois modelos testados, equivalente a mais de um nível de "
 "competência. A escolha do modelo é, portanto, decisão de política avaliativa, e "
 "não apenas de custo operacional."),

("p", "Como contribuição para a prática, o estudo consolida três recomendações de "
 "projeto para sistemas dessa natureza: tornar determinístico em código todo limiar "
 "de consequência binária para o qual exista medida objetiva disponível; excluir os "
 "trechos copiados do texto submetido à avaliação das competências, em vez de "
 "solicitar ao modelo que os desconsidere; e registrar, junto de cada correção, a "
 "identificação do modelo e dos parâmetros utilizados, tratando a substituição de "
 "modelo como evento que demanda recalibração. Acrescenta-se uma recomendação de uso: "
 "a interface deve comunicar ao estudante que a nota é estimativa sujeita a variação, "
 "e não veredito, coerentemente com o enquadramento formativo defendido por Luckesi "
 "(2011) e Freire (1996)."),

("p", "Como contribuição metodológica, registra-se que duas conclusões anteriores deste "
 "mesmo projeto, formuladas a partir de uma e de três repetições, afirmavam "
 "superioridade de estabilidade de um modelo sobre o outro em direções opostas, e "
 "ambas foram desmentidas pela corrida completa. Avaliações de estabilidade de "
 "sistemas baseados em modelos generativos exigem repetição suficiente; a intuição "
 "obtida em poucas execuções é sistematicamente enganosa."),

("p", "A agenda de continuidade compreende quatro frentes. A primeira é a medição de "
 "concordância com nota oficial, utilizando corpus com notas por competência, como o "
 "_Essay-BR_ (MARINHO; ANCHIÊTA; PARDO, 2022), e adotando a métrica consagrada na "
 "área, o _quadratic weighted kappa_, derivada da concordância ponderada de Cohen "
 "(1968). A segunda é a caracterização do próprio detector de cópia em termos de "
 "precisão e revocação, com cópia injetada de forma controlada e variação sistemática "
 "do tamanho da sequência. A terceira é a replicação do experimento com coleta "
 "distribuída no tempo e múltiplos temas, para testar a hipótese de variabilidade "
 "entre sessões registrada na seção 3.6. A quarta é a avaliação da qualidade "
 "pedagógica da devolutiva, e não apenas da nota, mediante análise por professores de "
 "língua portuguesa — dimensão que nenhuma métrica de dispersão alcança e que é, em "
 "última instância, aquilo que justifica a existência do artefato."),
]

REFERENCIAS = [
"AERA — AMERICAN EDUCATIONAL RESEARCH ASSOCIATION; APA — AMERICAN PSYCHOLOGICAL "
"ASSOCIATION; NCME — NATIONAL COUNCIL ON MEASUREMENT IN EDUCATION. Standards for "
"educational and psychological testing. Washington, DC: AERA, 2014.",

"AMORIM, Evelin; VELOSO, Adriano. A multi-aspect analysis of automatic essay scoring "
"for Brazilian Portuguese. In: PROCEEDINGS OF THE STUDENT RESEARCH WORKSHOP AT THE "
"15TH CONFERENCE OF THE EUROPEAN CHAPTER OF THE ASSOCIATION FOR COMPUTATIONAL "
"LINGUISTICS. Valencia: Association for Computational Linguistics, 2017. p. 94-102.",

"ANTUNES, Irandé. Aula de português: encontro & interação. São Paulo: Parábola, 2003.",

"ATTALI, Yigal; BURSTEIN, Jill. Automated essay scoring with e-rater V.2. Journal of "
"Technology, Learning, and Assessment, v. 4, n. 3, p. 1-30, 2006.",

"BENDER, Emily M.; GEBRU, Timnit; McMILLAN-MAJOR, Angelina; SHMITCHELL, Shmargaret. "
"On the dangers of stochastic parrots: can language models be too big? In: "
"PROCEEDINGS OF THE 2021 ACM CONFERENCE ON FAIRNESS, ACCOUNTABILITY, AND "
"TRANSPARENCY. New York: ACM, 2021. p. 610-623.",

"BRASIL. Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira. "
"A redação no Enem 2024: cartilha do participante. Brasília: Inep, 2024.",

"BRODER, Andrei Z. On the resemblance and containment of documents. In: PROCEEDINGS "
"OF THE COMPRESSION AND COMPLEXITY OF SEQUENCES. Washington, DC: IEEE Computer "
"Society, 1997. p. 21-29.",

"BROWN, Tom B. et al. Language models are few-shot learners. In: ADVANCES IN NEURAL "
"INFORMATION PROCESSING SYSTEMS 33. Red Hook: Curran Associates, 2020. p. 1877-1901.",

"COHEN, Jacob. Weighted kappa: nominal scale agreement with provision for scaled "
"disagreement or partial credit. Psychological Bulletin, v. 70, n. 4, p. 213-220, "
"1968.",

"FREIRE, Paulo. Pedagogia da autonomia: saberes necessários à prática educativa. São "
"Paulo: Paz e Terra, 1996.",

"GIL, Antonio Carlos. Como elaborar projetos de pesquisa. 6. ed. São Paulo: Atlas, "
"2017.",

"HOLMES, Wayne; BIALIK, Maya; FADEL, Charles. Artificial intelligence in education: "
"promises and implications for teaching and learning. Boston: Center for Curriculum "
"Redesign, 2019.",

"HOLTZMAN, Ari; BUYS, Jan; DU, Li; FORBES, Maxwell; CHOI, Yejin. The curious case of "
"neural text degeneration. In: INTERNATIONAL CONFERENCE ON LEARNING REPRESENTATIONS, "
"8., 2020, Addis Ababa. Proceedings [...]. Addis Ababa: ICLR, 2020.",

"LUCKESI, Cipriano Carlos. Avaliação da aprendizagem escolar: estudos e proposições. "
"22. ed. São Paulo: Cortez, 2011.",

"MARINHO, Jeziel C.; ANCHIÊTA, Rafael T.; PARDO, Thiago A. S. Essay-BR: a Brazilian "
"corpus of essays. Journal of Information and Data Management, v. 13, n. 1, p. "
"65-76, 2022.",

"MIZUMOTO, Atsushi; EGUCHI, Masaki. Exploring the potential of using an AI language "
"model for automated essay scoring. Research Methods in Applied Linguistics, v. 2, "
"n. 2, 100050, 2023.",

"PAGE, Ellis B. The imminence of grading essays by computer. Phi Delta Kappan, v. 47, "
"n. 5, p. 238-243, 1966.",

"PERELMAN, Les. Critique of Mark D. Shermis & Ben Hamner, “Contrasting state-of-the-art "
"automated scoring of essays: analysis”. Journal of Writing Assessment, v. 6, n. 1, "
"p. 1-27, 2013.",

"SHERMIS, Mark D.; BURSTEIN, Jill (ed.). Handbook of automated essay evaluation: "
"current applications and new directions. New York: Routledge, 2013.",

"WRESCH, William. The imminence of grading essays by computer — 25 years later. "
"Computers and Composition, v. 10, n. 2, p. 45-58, 1993.",

"YANCEY, Kevin P.; LAFLAIR, Geoffrey; VERARDI, Anthony; BURSTEIN, Jill. Rating short "
"L2 essays on the CEFR scale with GPT-4. In: PROCEEDINGS OF THE 18TH WORKSHOP ON "
"INNOVATIVE USE OF NLP FOR BUILDING EDUCATIONAL APPLICATIONS. Toronto: Association "
"for Computational Linguistics, 2023. p. 576-584.",

"ZHENG, Lianmin et al. Judging LLM-as-a-judge with MT-Bench and Chatbot Arena. In: "
"ADVANCES IN NEURAL INFORMATION PROCESSING SYSTEMS 36. Red Hook: Curran Associates, "
"2023. p. 46595-46623.",
]

# ─── Tabelas ────────────────────────────────────────────────────────────────
TABELAS = {
"competencias": {
    "widths": [1500, 4000, 3004],
    "rows": [
        ["Competência", "Descrição oficial", "Pontuação"],
        ["I", "Demonstrar domínio da modalidade escrita formal da língua portuguesa",
         "0 a 200, em faixas de 40"],
        ["II", "Compreender a proposta de redação e aplicar conceitos das várias áreas "
         "de conhecimento para desenvolver o tema, dentro dos limites estruturais do "
         "texto dissertativo-argumentativo em prosa", "0 a 200, em faixas de 40"],
        ["III", "Selecionar, relacionar, organizar e interpretar informações, fatos, "
         "opiniões e argumentos em defesa de um ponto de vista",
         "0 a 200, em faixas de 40"],
        ["IV", "Demonstrar conhecimento dos mecanismos linguísticos necessários para a "
         "construção da argumentação", "0 a 200, em faixas de 40"],
        ["V", "Elaborar proposta de intervenção para o problema abordado, respeitando "
         "os direitos humanos", "0 a 200, em faixas de 40"],
        ["", "Nota final (soma das cinco competências)", "0 a 1.000"],
    ],
},
"corpus": {
    "widths": [1100, 1500, 1500, 4404],
    "rows": [
        ["Redação", "Extensão (palavras)", "Cópia medida (%)", "Característica"],
        ["R1", "251", "0", "Texto original; argumentação bem desenvolvida"],
        ["R2", "189", "0", "Texto original; argumentação mediana"],
        ["R3", "124", "0", "Texto original; argumentação frágil"],
        ["R5", "109", "29", "Cópia parcial dos textos motivadores"],
        ["R6", "145", "45", "Cópia parcial dos textos motivadores"],
        ["R4", "93", "74", "Predominantemente cópia dos textos motivadores"],
    ],
},
"dispersao": {
    "widths": [1000, 900, 2200, 900, 800, 904, 1800],
    "rows": [
        ["Redação", "Cópia (%)", "Modelo", "Média", "DP", "CV (%)",
         "Respostas idênticas"],
        ["R1", "0", "claude-opus-5", "960", "0,0", "0,0", "10/10"],
        ["R1", "0", "claude-sonnet-4-5", "936", "28,0", "3,0", "7/10"],
        ["R2", "0", "claude-opus-5", "600", "0,0", "0,0", "10/10"],
        ["R2", "0", "claude-sonnet-4-5", "544", "28,0", "5,1", "7/10"],
        ["R3", "0", "claude-opus-5", "376", "20,7", "5,5", "6/10"],
        ["R3", "0", "claude-sonnet-4-5", "284", "12,6", "4,5", "9/10"],
        ["R5", "29", "claude-opus-5", "556", "66,5", "12,0", "4/10"],
        ["R5", "29", "claude-sonnet-4-5", "496", "73,5", "14,8", "6/10"],
        ["R6", "45", "claude-opus-5", "380", "43,2", "11,4", "3/10"],
        ["R6", "45", "claude-sonnet-4-5", "280", "0,0", "0,0", "10/10"],
        ["R4", "74", "claude-opus-5", "0", "0,0", "0,0", "10/10"],
        ["R4", "74", "claude-sonnet-4-5", "0", "0,0", "0,0", "10/10"],
    ],
},
"zeramento": {
    "widths": [1300, 1000, 1550, 1550, 1552, 1552],
    "rows": [
        ["Cópia medida (%)", "Redação", "Zerou (opus-5)", "Zerou (sonnet-4-5)",
         "Nota média (opus-5)", "Nota média (sonnet-4-5)"],
        ["0", "R1", "0/10", "0/10", "960", "936"],
        ["0", "R2", "0/10", "0/10", "600", "544"],
        ["0", "R3", "0/10", "0/10", "376", "284"],
        ["29", "R5", "0/10", "0/10", "556", "496"],
        ["45", "R6", "0/10", "0/10", "380", "280"],
        ["74", "R4", "10/10", "10/10", "0", "0"],
    ],
},
"vies": {
    "widths": [1300, 1400, 1934, 1934, 1936],
    "rows": [
        ["Redação", "Cópia (%)", "Média opus-5", "Média sonnet-4-5",
         "Diferença (pontos)"],
        ["R1", "0", "960", "936", "+24"],
        ["R2", "0", "600", "544", "+56"],
        ["R3", "0", "376", "284", "+92"],
        ["R5", "29", "556", "496", "+60"],
        ["R6", "45", "380", "280", "+100"],
        ["R4", "74", "0", "0", "0"],
        ["Média das diferenças", None, None, None, "+55"],
    ],
},
}
