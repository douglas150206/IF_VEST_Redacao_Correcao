# Comparação Node × Python

Roteiro para provar, antes de desligar o Express, que o backend em FastAPI se
comporta igual.

## Rodando

Com os dois servidores no ar:

```bash
# Node (na pasta do projeto antigo)
npm start                       # http://localhost:3005

# Python (nesta pasta)
uvicorn exemplo_app:app --port 8000
```

```bash
python comparacao/comparar.py
```

Endereços diferentes: `--node http://...` e `--py http://...`.

## O que é comparado — e o que não é

**Comparado por igualdade** (determinístico, sem custo de API):

| Item | Como |
|---|---|
| Redação curta | os dois devolvem 400 |
| Tema inexistente | os dois devolvem 404 |
| Chave de API malformada | os dois devolvem 400 |
| Aluno tentando criar tema | os dois devolvem 403 |
| Status de uso | limite, usadas, restantes e flag de chave própria batem campo a campo |
| Antiplágio | percentual, palavras copiadas, total e a lista de trechos, idênticos |

**Não comparado por igualdade: a nota e o texto do feedback.** São saída de
modelo de linguagem — variam entre execuções mesmo no mesmo backend, então
exigir igualdade daria falso negativo sempre. Para esses campos o script:

- confere a **estrutura**: 5 competências, numeradas de 1 a 5, notas na escala
  `{0, 40, 80, 120, 160, 200}`, `nota_total` igual à soma, níveis válidos;
- **imprime as duas notas lado a lado** com a diferença, para você julgar se
  estão na mesma faixa;
- avisa quando a diferença passa de 200 pontos — pode ser só ruído, mas se
  repetir na mesma direção é viés sistemático e vale investigar o prompt.

O jeito honesto de avaliar a nota é rodar algumas vezes e olhar a tendência, não
uma execução única.

## Fase que gasta crédito

```bash
python comparacao/comparar.py --com-ia 1
```

Cada rodada corrige **duas** redações (uma limpa e uma copiada) em **cada**
backend — ou seja, `--com-ia 1` são 4 chamadas de API. Comece com 1.

Essa fase é a que vale a pena repetir algumas vezes antes de desligar o Node.

## Resultado de referência

Fase determinística, dois servidores locais:

```
comparações iguais: 9
nenhuma divergência nos itens determinísticos
```

Fase com IA, 3 rodadas (6 correções em cada backend). O antiplágio bateu campo a
campo em todas — inclusive a lista de trechos, caractere por caractere. As notas:

| Redação | Node (sonnet-4-5) | Python (opus-5) |
|---|---|---|
| Própria, rodada 1 | 200 | 640 |
| Própria, rodada 2 | 920 | 680 |
| Própria, rodada 3 | 200 | 640 |
| Copiada 74%, rodada 1 | 280 | 0 |
| Copiada 74%, rodada 2 | 280 | 160 |
| Copiada 74%, rodada 3 | 120 | 0 |

> ⚠️ **Correção.** Uma versão anterior deste arquivo concluía daqui que "o Node
> é instável e o Python é estável". **Essa conclusão não se sustentou.** Um
> experimento controlado — mesmo prompt, mesmo `max_tokens`, mesma entrada,
> variando só o modelo — mostrou o contrário no agregado. Ver
> `pesquisa/README.md`.
>
> O erro foi de método: aqui estão sendo comparados **dois backends**, que
> diferem em prompt e em `max_tokens` (1500 no Node, 8000 no Python), não dois
> modelos. A variação observada era da configuração, não do modelo. Esta tabela
> continua útil para conferir que os dois sistemas *funcionam*; ela não serve
> para comparar qualidade de correção.

O que dá para afirmar olhando só esta tabela: os dois backends produzem
correções bem formadas, na escala do ENEM, e o antiplágio é idêntico. As notas
diferem, e isolar a causa exige o experimento controlado.

## Um bug que esta comparação encontrou

Numa das rodadas o modelo devolveu `nota_total: 680` com competências somando
**640**. No ENEM a nota total é, por definição, a soma — o total solto era
simplesmente errado, e o backend Node nunca conferiu isso.

Corrigido no porte: `CorrecaoIA` recalcula `nota_total` a partir das
competências (`corretor/esquemas.py`), e o prompt passou a pedir que a cópia
zere *as cinco competências* em vez de zerar só o total, para a regra fluir pela
mesma conta. Há teste para os dois casos.

**Se vocês mantiverem o Node no ar por um tempo, ele ainda tem esse bug.**

## Uma diferença esperada, não é bug

O papel de professor: no Node vem de um código digitado pelo usuário
(`promover-professor`); no Python vem do perfil do IFvest. Os **403** batem — o
aluno é barrado nos dois. O caminho feliz não é comparável 1:1, e é justamente a
duplicação que a integração elimina.

## Limpeza

O script cria a conta `comparacao@local.test` no banco do Node (que tem cadastro
próprio). Para remover depois:

```bash
sqlite3 database.db "DELETE FROM correcoes WHERE usuario_id = (SELECT id FROM usuarios WHERE email='comparacao@local.test'); DELETE FROM usuarios WHERE email='comparacao@local.test';"
```

O lado Python usa o provedor falso do `exemplo_app.py` e não cria conta nenhuma.
