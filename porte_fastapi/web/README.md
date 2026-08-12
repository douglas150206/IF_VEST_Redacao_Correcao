# Corretor de Redação — componentes React

Porte da interface do sistema em Node (que era um `index.html` de ~1.100 linhas)
para componentes React. Copie a pasta `web/` para dentro do frontend do IFvest —
renomeie para o que fizer sentido lá (`src/corretor/`, por exemplo).

**Não desenha cabeçalho, logo nem navegação de propósito.** Quem monta o topo da
página é o layout de vocês; isto é só o miolo da tela.

## Montando

```tsx
import { CorretorDeRedacao } from "./corretor/CorretorDeRedacao";
import "./corretor/corretor.css";

<Route path="/redacao" element={<CorretorDeRedacao />} />
```

## Ligando na autenticação

Por padrão as requisições saem para `/api/redacao` com `credentials: "include"` —
se o IFvest usa **cookie de sessão**, já funciona sem configurar nada.

Se vocês usam **token no header**, chame uma vez no bootstrap do app:

```ts
import { configurarApi } from "./corretor/api";

configurarApi({
  aoMontarRequisicao: () => ({ Authorization: `Bearer ${pegarToken()}` }),
});
```

E se já existe um cliente HTTP com interceptors, é melhor entregar o `fetch` dele:

```ts
configurarApi({ fetch: meuFetchAutenticado, baseUrl: "/api/redacao" });
```

## Arquivos

| Arquivo | O que é |
|---|---|
| `CorretorDeRedacao.tsx` | a tela inteira — é o que vocês montam na rota |
| `useCorretor.ts` | estado: status de uso, temas, envio, erros, bloqueio |
| `api.ts` | cliente + tipos espelhando `corretor/esquemas.py` |
| `corretor.css` | estilos IFSP, escopados em `.corretor` |
| `componentes/CartaoPlano.tsx` | contador de 10 blocos e os quatro estados de uso |
| `componentes/SeletorDeTema.tsx` | tema do banco ou personalizado + textos de apoio |
| `componentes/ResultadoCorrecao.tsx` | nota final, as 5 competências, sugestões |
| `componentes/PainelPlagio.tsx` | painel de detecção de cópia |
| `componentes/ModalPlano.tsx` | explica o limite; abre sozinho ao entrar |
| `componentes/ModalChaveApi.tsx` | cadastro/remoção da chave própria |
| `componentes/ModalHistorico.tsx` | últimas correções do aluno |
| `componentes/ModalTemas.tsx` | CRUD de temas — só renderiza para professor |
| `componentes/Modal.tsx` · `Icone.tsx` | modal base (Esc, clique fora) e ícones em traço |

## Atenção ao mudar de API

O backend Python devolve **snake_case**, diferente do JS antigo:

| Antes (Node) | Agora (FastAPI) |
|---|---|
| `percentualCopiado` | `percentual_copiado` |
| `palavrasCopiadas` | `palavras_copiadas` |
| `trechosCopiados` | `trechos_copiados` |

Os tipos em `api.ts` já usam os nomes novos — se alguém copiar trecho do
`index.html` velho, o TypeScript acusa.

## Se o projeto não for TypeScript

Renomeie `.tsx` → `.jsx`, `.ts` → `.js` e apague as anotações de tipo (as
`interface`/`type` e os `: Tipo`). A lógica não muda.

## Se vocês usam CSS Modules

Renomeie para `corretor.module.css`, importe como objeto e troque
`className="plano-card"` por `className={estilos.planoCard}`. Como está, o CSS
é global mas todo aninhado sob `.corretor`, então não vaza nem colide.

## Verificação

`tsc --noEmit` limpo com `strict`, `noUnusedLocals` e `noUnusedParameters`,
contra `@types/react` **18 e 19** — o código evita `JSX.Element` justamente para
compilar nas duas versões.

O que **não** foi testado: renderização no navegador. Não tenho o projeto React
de vocês para montar os componentes de verdade. Vale um olhar na primeira
execução, principalmente no espaçamento do cartão de plano em telas estreitas.
