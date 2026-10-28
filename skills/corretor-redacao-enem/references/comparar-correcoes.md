# Comparar duas correções

Use este guia quando a tarefa for confrontar a correção automática com a de um
corretor humano, ou duas correções humanas entre si.

## As margens aceitas na prática

Informadas pela Profa. Daniela Matos, a partir da prática de banca:

| Comparação | Margem aceitável |
|---|---|
| Entre dois corretores, por competência | até **40 pontos** |
| Entre competências | até **80 pontos** |
| Na nota final | até **100 pontos** |

Uma ressalva importante dela: a régua do INEP é larga por causa do **volume** de
correções. Em contexto controlado de preparação, onde a banca é pequena e o
objetivo é formativo, não se aceita margem tão grande. Então trate esses valores
como teto absoluto, não como meta.

## O erro de leitura que inverte a conclusão

É tentador olhar uma diferença média de 60 pontos e concluir "está dentro dos
100 da nota final, então está bom". **Essa conclusão é errada**, e vale entender
por quê.

As margens acima descrevem **discordância aleatória** entre dois avaliadores. Um
corretor que ora dá 40 a mais, ora 40 a menos, tem média correta: o erro se
compensa e o conjunto dos alunos é avaliado com justiça. A margem existe porque
julgamento humano sobre texto tem variação irredutível.

Um desvio **sempre na mesma direção** é outra coisa. Não se compensa nunca,
desloca a nota de todos os alunos no mesmo sentido, e é erro de calibração do
instrumento, não variação de julgamento. Cem pontos de viés sistemático é um
problema grave; cem pontos de dispersão aleatória é ruído tolerável.

Por isso, ao comparar, **reporte duas métricas separadas**:

- **Erro médio com sinal** — a média das diferenças preservando o sinal
  (automática menos oficial). Mede **viés**. Deve tender a zero. Se der +60,
  o sistema é sistematicamente generoso, e nenhuma margem de tolerância
  justifica isso.
- **Erro absoluto médio** — a média dos módulos das diferenças. Mede
  **acurácia**. É este que se compara com os 40 pontos.

Os dois juntos contam a história inteira. Erro médio perto de zero com erro
absoluto alto significa um corretor errático mas não enviesado. Erro médio alto
com erro absoluto igual a ele significa um corretor consistente que está
consistentemente errado — que é mais fácil de consertar, porque basta
recalibrar.

## O que mais olhar

**Onde o erro se concentra.** Média esconde distribuição. Separe por faixa de
nota oficial: um sistema que acerta redações boas e erra feio nas fracas tem um
problema diferente de um que erra parelho. Nos testes do projeto, o erro foi
muito maior nas redações fracas — notas oficiais de 320 receberam de 520 a 600,
bem fora de qualquer margem.

**Qual competência puxa.** O erro total é a soma de cinco erros. Quase sempre
uma ou duas competências respondem pela maior parte. Competência II e III são
as candidatas naturais, porque dependem de julgamento sobre repertório e
projeto de texto, onde a grade dá mais margem de interpretação.

**Quantos casos estouram a margem.** Além das médias, conte a proporção de
redações fora dos 100 pontos na nota final. Uma média boa com 20% de casos
muito fora é pior, para o aluno, do que uma média um pouco pior e distribuição
apertada.

**Se a divergência tem explicação na grade.** Antes de concluir que a IA errou,
verifique se algum teto obrigatório deveria ter sido aplicado e não foi. Muitas
divergências em Competência II vêm de cópia não penalizada; em Competência IV,
de monobloco não detectado. Esses casos não são erro de julgamento, são regra
não aplicada — e têm conserto determinístico.

## Formato do relato

Apresente nesta ordem:

1. **Erro médio com sinal** e **erro absoluto médio**, no total e por
   competência.
2. **Erro por faixa de nota oficial** — pelo menos separando fracas, médias e
   boas.
3. **Proporção de casos fora da margem** de 100 pontos na nota final.
4. **Os casos mais discrepantes**, com o texto e as duas notas, para leitura
   humana.
5. **Divergências que a grade explica** — teto não aplicado, cópia não
   detectada — separadas das que são julgamento genuinamente diferente.

Essa última separação é a mais útil, porque divide o problema em duas partes com
soluções diferentes: regra não aplicada se conserta em código, julgamento
divergente se conserta calibrando o prompt.
