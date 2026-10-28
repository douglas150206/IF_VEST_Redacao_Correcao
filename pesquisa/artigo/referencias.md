# Referências do artigo

Regra deste arquivo: **nada entra sem verificação**. Cada entrada registra como
foi conferida. Referência não verificada fica na seção do fim e não pode ser
citada no texto até sair de lá.

Formato: ABNT (a RECIMA21 aceita ABNT, APA ou Vancouver).

---

## Verificadas

### Fundamentos da correção automática

**PAGE, E. B.** The imminence of grading essays by computer. *The Phi Delta
Kappan*, v. 47, n. 5, p. 238–243, 1966.
> Trabalho inaugural da área (Project Essay Grade). Introduz a distinção entre
> *trins* (traços intrínsecos que se quer medir) e *proxes* (aproximações
> computáveis) — distinção que continua sendo o problema central e serve de
> gancho para a discussão de validade.
> *Conferido em: CiNii Research e History of Information.*

**ATTALI, Y.; BURSTEIN, J.** Automated essay scoring with e-rater V.2.
*Journal of Technology, Learning, and Assessment*, v. 4, n. 3, 2006.
> Sistema da ETS, em uso operacional desde 1999. Referência para a geração
> baseada em extração de atributos e regressão, anterior aos modelos de
> linguagem.
> *Conferido em: ERIC (EJ843852), texto completo disponível.*

### Crítica e validade

**PERELMAN, L.** When "the state of the art" is counting words. *Assessing
Writing*, v. 21, p. 104–111, 2014.
> Argumenta que os sistemas medem *proxies* (extensão do texto, frequência de
> palavras raras) e não o construto "capacidade de escrever". É a crítica que o
> artigo precisa enfrentar de frente, não contornar.
> *Conferido em: lesperelman.com, PDF do artigo com volume e páginas na folha
> de rosto.*

### Corpus e estado da arte em português

**MARINHO, J. C.; ANCHIETA, R. T.; MOURA, R. S.** Essay-BR: a Brazilian Corpus
of Essays. arXiv:2105.09081, 2021.
> 4.570 redações de estudantes brasileiros do ensino médio, avaliadas por
> especialistas nas cinco competências do ENEM. Licença MIT, disponível em
> <https://github.com/rafaelanchieta/essay>. Divisão: 3.198 treino / 686
> validação / 686 teste.
> *Conferido em: arXiv (autores e ano) e repositório no GitHub (licença,
> tamanho e formato).*
> **Nota:** há também versão em periódico (*Journal of Information and Data
> Management*) e nos anais do *Dataset Showcase Workshop*. Definir qual citar.

**BARBOSA, A.; SILVEIRA, I. C.; MAUÁ, D. D.** An Empirical Analysis of Large
Language Models for Automated Cross-Prompt Essay Trait Scoring in Brazilian
Portuguese. *Journal of the Brazilian Computer Society*, v. 31, n. 1,
p. 857–870, 2025. DOI: 10.5753/jbcs.2025.5817.
> **A referência mais importante do artigo.** Estado da arte em português, com
> QWK entre 0,60 e 0,73 por competência no Essay-BR. Conclui que nenhuma
> arquitetura domina sempre e que modelos apenas-encoder equilibram bem custo e
> precisão. É a linha de base contra a qual o nosso experimento 2 se compara.
> *Conferido em: página do artigo no portal SBC, com volume, número, páginas e
> DOI.*

### Métrica

**COHEN, J.** Weighted kappa: nominal scale agreement with provision for scaled
disagreement or partial credit. *Psychological Bulletin*, v. 70, n. 4,
p. 213–220, 1968.
> Origem do kappa ponderado. O *quadratic weighted kappa* é a métrica padrão da
> área de correção automática porque penaliza o erro proporcionalmente à
> distância entre as notas, e não apenas ao desacordo.
> *Conferido em: Ovid (Psychological Bulletin, outubro de 1968) e verbete da
> Wikipédia com a citação completa.*

### Documento oficial do exame

**INSTITUTO NACIONAL DE ESTUDOS E PESQUISAS EDUCACIONAIS ANÍSIO TEIXEIRA
(INEP).** *A redação no Enem 2024: cartilha do participante.* Brasília: INEP,
2024.
> Fonte primária da matriz de cinco competências, da escala de 0 a 200 pontos
> por competência e das situações de anulação — inclusive a regra de cópia dos
> textos motivadores, que é o que o detector implementa.
> *Conferido em: PDF no domínio download.inep.gov.br.*
> **Nota:** existe a edição 2025, no mesmo domínio. Usar a mais recente na
> submissão.

---

## A verificar antes de citar

Estas aparecem na literatura mas ainda não tiveram os dados bibliográficos
conferidos na fonte. **Não usar no texto enquanto estiverem aqui.**

- **ZHENG, L. et al.** Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena.
  arXiv:2306.05685, 2023. — Referência canônica de "LLM como avaliador".
  Falta conferir a lista completa de autores e se cito a versão do NeurIPS.
- **NCTE.** Position Statement on Machine Scoring. — Posicionamento
  institucional de professores de escrita contra a correção por máquina. Falta
  o ano exato.
- Estudo de síntese sobre concordância entre LLMs e avaliadores humanos
  (QWK ~0,68 no melhor caso, 0,31–0,39 em modelos mais fracos). Vi o número em
  resultado de busca, **não no artigo**. Precisa ser lido antes de citar.
- Literatura sobre viés de posição e viés de verbosidade em LLM-como-juiz.
  Relevante para explicar por que a nota varia entre execuções idênticas.

---

## Lacunas do referencial

Para as 13 páginas mínimas da RECIMA21, o referencial ainda precisa cobrir:

1. **Correção de redação no Brasil como problema educacional** — razão
   aluno/corretor, acesso desigual a devolutiva. Buscar dados do INEP ou de
   pesquisa educacional brasileira.
2. **Trabalhos brasileiros de AES anteriores aos LLMs**, para situar a
   contribuição historicamente.
3. **Confiabilidade e validade em avaliação educacional** — a distinção
   conceitual que organiza o artigo inteiro. Precisa de fonte de teoria da
   medida, não só de PLN.
4. **Ética e uso de IA em avaliação educacional** — há documento da UNESCO
   sobre IA na educação que vale localizar.
