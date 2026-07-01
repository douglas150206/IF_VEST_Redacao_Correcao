# IF_VEST — Corretor de Redação ENEM

Sistema web que corrige redações no modelo ENEM usando inteligência artificial (API da Anthropic/Claude), avaliando as **5 competências** e a **nota final estimada (0–1000)**. Inclui banco de temas com textos de apoio e **detecção de cópia** dos textos de apoio.

## Funcionalidades

- **Autenticação** (cadastro/login com JWT) e limite mensal de correções gratuitas (ou chave de API própria para uso ilimitado).
- **Correção automática** nas 5 competências, com feedback e sugestões de melhoria.
- **Banco de temas com textos de apoio** (estilo ENEM): o aluno escolhe um tema e lê os textos, ou cola um tema personalizado.
- **Detecção de cópia dos textos de apoio** (antiplágio): identifica trechos copiados literalmente, mostra o percentual e destaca os trechos; a nota é penalizada seguindo a regra do ENEM (trechos copiados não contam como produção própria).
- **Perfil de professor**: gerencia o banco de temas (cadastrar/editar/excluir) por uma tela de administração restrita.
- **Histórico** de correções, com nota e percentual de cópia.

## Tecnologias

- **Backend:** Node.js, Express, better-sqlite3 (SQLite), JWT, bcryptjs, SDK `@anthropic-ai/sdk`.
- **Frontend:** HTML + CSS + JavaScript (página única `index.html`).
- **Detecção de cópia:** algoritmo de *shingles* (n-gramas de palavras) em `plagio.js`.

## Como executar

1. Instale as dependências:
   ```bash
   npm install
   ```
2. Crie o arquivo `.env` a partir do exemplo e preencha os valores:
   ```bash
   cp .env.example .env
   ```
   - `ANTHROPIC_API_KEY` — chave da API da Anthropic (https://console.anthropic.com/)
   - `JWT_SECRET` — um segredo longo e aleatório
   - `CODIGO_PROFESSOR` — código para cadastrar/promover um professor
3. Inicie o servidor:
   ```bash
   npm run dev     # ou: npm start
   ```
   O backend sobe em `http://localhost:3005`.
4. Abra o `index.html` no navegador (ou sirva em `http://localhost:3000`, que é a origem liberada no CORS por padrão).

## Perfil de professor

Para gerenciar os temas, cadastre-se informando o **código de professor** (definido em `CODIGO_PROFESSOR` no `.env`), ou, já logado, clique em **"Sou professor"** e informe o código. O professor vê o botão **"🛠️ Temas"** para administrar o banco.

## Estrutura

```
├── server.js         # API Express (auth, temas, correção, histórico)
├── plagio.js         # Detecção de cópia dos textos de apoio (shingles)
├── index.html        # Frontend (interface completa)
├── .env.example      # Modelo de variáveis de ambiente
└── package.json
```

> O banco `database.db` é criado automaticamente na primeira execução, com 3 temas de exemplo.
