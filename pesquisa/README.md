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
| 74% | R4 | 0,0% | 0,0% | 10/10 |

A dispersão é máxima na faixa de **cópia parcial** e desaparece nos extremos. O
sistema é decidido justamente onde a decisão é fácil, e vacila onde um corretor
humano também deliberaria — só que sem sinalizar essa incerteza ao aluno.

### Resultado 3 — a regra de cópia é degrau, não rampa

| Cópia medida | Zerou (opus-5) | Zerou (sonnet-4-5) | Nota média (opus) |
|---|---|---|---|
| 0% | 0/10 | 0/10 | 376–960 |
| 29% | 0/10 | 0/10 | 556 |
| 45% | 0/10 | 0/10 | 380 |
| 74% | **10/10** | **10/10** | 0 |

O prompt pede penalização proporcional ao percentual copiado e zeramento quando a
redação é "essencialmente cópia". O modelo implementa isso como função degrau: nada
zera até 45%, tudo zera em 74%. Há penalização gradual na nota (380 contra 960),
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

## Experimento 2 — concordância com nota oficial (pendente)

Precisa de corpus real com notas por competência. O *Essay-BR* é o mais citado na
literatura em português; **verificar disponibilidade e licença antes de depender
dele**. Métrica padrão da área: *quadratic weighted kappa*.

## Experimento 3 — detecção de cópia (pendente)

Precisão e recall do algoritmo de shingles com cópia injetada de forma controlada.
O gradiente do corpus atual (0 / 29 / 45 / 74%) é o começo disso.
