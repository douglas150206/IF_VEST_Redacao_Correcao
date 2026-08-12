# Corretor de Redação ENEM — módulo FastAPI para o IFvest

Porte do backend do [IF_VEST_Redacao_Correcao](https://github.com/douglas150206/IF_VEST_Redacao_Correcao)
(Node/Express) para FastAPI, pronto para ser montado dentro do sistema geral.

Copie a pasta `corretor/` para dentro do repositório do IFvest e monte o router.
Nada aqui depende de estar nesta pasta.

## Como plugar (3 passos)

```python
from fastapi import FastAPI
from corretor import UsuarioAtual, criar_tabelas, router, usar_provedor_de_usuario

app = FastAPI()

# 1. cria as tabelas do corretor (idempotente)
criar_tabelas()

# 2. diz ao corretor como descobrir quem está logado
async def provedor(request):
    u = await get_current_user(request)          # a função de vocês
    return UsuarioAtual(id=u.id, nome=u.nome, email=u.email,
                        professor=u.papel == "professor")

usar_provedor_de_usuario(provedor)

# 3. monta as rotas
app.include_router(router)
```

Se preferirem manter o `Depends` de vocês, dá para ignorar o passo 2 e
sobrescrever a dependência direto no FastAPI:

```python
app.dependency_overrides[corretor.usuario_atual] = a_dependencia_de_voces
```

Para ver funcionando antes de integrar: `uvicorn exemplo_app:app --reload` e
abra `/docs`. O exemplo usa um usuário falso (mande o header `X-Papel: professor`
para testar as rotas de professor).

## Variáveis de ambiente

| Variável | Padrão | O que é |
|---|---|---|
| `CORRETOR_BANCO` | `corretor.db` | Arquivo SQLite. Pode ser o mesmo do IFvest — as tabelas têm prefixo `corretor_` e não colidem. |
| `ANTHROPIC_API_KEY` | — | Chave institucional, usada por quem não cadastrou chave própria. |
| `CORRETOR_LIMITE_MENSAL` | `10` | Correções gratuitas por mês. **`0` desliga o limite** (se a instituição bancar tudo). |
| `CORRETOR_MODELO` | `claude-opus-5` | Modelo usado na correção. |
| `CORRETOR_MAX_TOKENS` | `8000` | Teto de tokens da resposta (raciocínio + texto). |
| `CORRETOR_ESFORCO` | `medium` | `low`, `medium`, `high`, `xhigh` ou `max`. Mais esforço = correção mais criteriosa, mais lenta e mais cara. |

## Rotas

Todas sob o prefixo `/api/redacao` (mude em `corretor/rotas.py` se quiser outro).

| Método | Rota | Quem pode |
|---|---|---|
| GET | `/status` | logado |
| GET | `/temas` | logado |
| POST · PUT · DELETE | `/temas` · `/temas/{id}` | professor |
| POST | `/corrigir` | logado |
| GET | `/historico` | logado |
| POST · DELETE | `/chave` | logado |

## O que mudou em relação à versão Node

**Saiu:** cadastro, login, JWT, bcrypt, a tabela `usuarios` e a rota de promoção
a professor. Identidade e papel vêm do IFvest — era essa a duplicação que
atrapalhava a integração.

**Entrou:**

- **Structured outputs.** O modelo é obrigado a devolver o formato de
  `CorrecaoIA`, então sumiu o `text.replace(/```json/…)` seguido de `JSON.parse`
  e o risco de resposta malformada.
- **`claude-opus-5`** no lugar de `claude-sonnet-4-5`, com `max_tokens` de 1500 →
  8000. Os 1500 antigos truncavam feedback longo, e no Opus 5 o raciocínio conta
  dentro do mesmo teto. Se o custo pesar, `CORRETOR_MODELO=claude-sonnet-5` é a
  troca natural — mais barato, ainda muito bom nesta tarefa.
- **Erros tratados por tipo** (`AuthenticationError`, `RateLimitError`,
  `APIStatusError`, `APIConnectionError`), cada um com uma mensagem e um HTTP
  status próprios, em vez de um 500 genérico.
- **Tabelas com prefixo `corretor_`** e índice em `(usuario_id, criado_em)`.

**Igual, de propósito:** o algoritmo do antiplágio. `corretor/plagio.py` é porte
fiel de `plagio.js` — mesmos shingles de 7 palavras, mesma normalização, mesmo
arredondamento (`Math.round` do JS arredonda 0,5 para cima; o `round()` do Python
não, então o porte usa `floor(x + 0.5)`).

## Testes

```bash
pip install -r requirements.txt pytest httpx
pytest testes/
```

20 testes, nenhum consome API (a chamada à IA é substituída). Cobrem os estados
do antiplágio com valores conferidos contra a saída do `plagio.js` original, o
CRUD de temas com e sem permissão, o limite mensal, a chave própria e o
isolamento do histórico entre usuários.

## Frontend

Os componentes React estão em [`web/`](web/README.md) — a tela inteira portada
do `index.html`, incluindo histórico e gestão de temas. Montagem:

```tsx
import { CorretorDeRedacao } from "./corretor/CorretorDeRedacao";
import "./corretor/corretor.css";

<Route path="/redacao" element={<CorretorDeRedacao />} />
```

Veja o `web/README.md` para ligar na autenticação de vocês (cookie de sessão
funciona sem configurar nada) e para as diferenças de nome de campo — o backend
Python devolve `percentual_copiado` onde o Node devolvia `percentualCopiado`.

Sugestão de ordem: suba este módulo com o Node ainda rodando ao lado, compare as
respostas das duas APIs, depois troque a interface e desligue o Node.

## Comparando com o backend antigo

[`comparacao/comparar.py`](comparacao/README.md) roda os dois backends lado a
lado e confere validações, permissões, status de uso e o bloco de antiplágio.

```bash
python comparacao/comparar.py            # sem custo de API
python comparacao/comparar.py --com-ia 1 # inclui correções reais
```

## Decisão pendente do grupo

O modelo de custo. Hoje é "10 grátis, depois o aluno compra créditos e cola a
própria chave" — herdado do sistema avulso. Num sistema institucional o normal
seria **uma chave da instituição com cota por aluno**, que é o que
`CORRETOR_LIMITE_MENSAL` + `ANTHROPIC_API_KEY` já fazem: basta não expor a tela
de chave própria e ajustar a cota. As rotas `/chave` continuam existindo caso
vocês queiram manter as duas opções.
