# Demonstração — rodando o corretor novo sem o IFvest

App mínimo em Vite + React só para **ver e testar** os componentes antes da
integração. Não vai para produção: no IFvest quem monta a página é o layout de
vocês.

## Subindo

Dois terminais.

**1. Backend** (na pasta `porte_fastapi`):

```bash
pip install -r requirements.txt
uvicorn exemplo_app:app --port 8000
```

**2. Frontend** (nesta pasta):

```bash
npm install
npm run dev
```

Abra **http://localhost:5173**.

## O que a barra preta do topo faz

Alterna entre **Aluno** e **Professor**. Ela manda o header `X-Papel`, que o
provedor **falso** do `exemplo_app.py` lê — serve para testar as duas visões sem
ter login de verdade. **Essa barra não existe em produção**: no IFvest o papel
vem do perfil do usuário.

Repare que aluno e professor são usuários diferentes (ids 1 e 2), com contadores
de uso independentes.

## Para as correções funcionarem

O backend precisa de uma chave da Anthropic. Duas formas:

- **Chave institucional:** defina `ANTHROPIC_API_KEY` no ambiente antes de subir
  o uvicorn — vale para todos os usuários, dentro da cota mensal.
- **Chave do aluno:** clique em "Cadastrar minha chave de API" na própria tela.
  Fica salva em `porte_fastapi/corretor.db` (ignorado pelo git).

Sem chave nenhuma, tudo funciona menos o botão de corrigir, que responde 503 com
a mensagem explicando o que falta.

## Roteiro de teste sugerido

1. **Limite** — como aluno, veja o cartão com os 10 blocos e o modal explicativo
   que abre sozinho. Cadastre uma chave e repare que o cartão vira "uso
   ilimitado"; remova a chave e o limite volta.
2. **Correção** — cole uma redação (mínimo 100 caracteres) e envie. Confira nota,
   as cinco competências e as sugestões.
3. **Antiplágio** — como professor, crie um tema com textos de apoio. Volte como
   aluno, selecione o tema e cole um trecho do apoio dentro da redação: o painel
   vermelho aparece com os trechos detectados.
4. **Histórico** — "Meu histórico" lista as correções daquele usuário. Troque de
   papel e veja que o histórico é outro.
5. **Permissão** — o botão "Gerenciar temas" só aparece para professor.

## Limpando os dados de teste

```bash
rm porte_fastapi/corretor.db
```

O banco é recriado vazio na próxima subida. Isso também apaga a chave de API
salva pela tela.
