# Artigo para a RECIMA21

Artigo científico derivado deste TCC, montado dentro do template oficial da
**RECIMA21 — Revista Científica Multidisciplinar** (ISSN 2675-6218).

| Arquivo | O que é |
|---|---|
| `ARTIGO_RECIMA21.docx` | **Versão cega — é esta que se submete agora.** Sem nomes. |
| `ARTIGO_RECIMA21_versao-final.docx` | Versão com os autores, para o *segundo* envio. |
| `template_recima21.docx` | Template oficial da revista, usado como base. |
| `conteudo.py` | Todo o texto do artigo (títulos, resumos, seções, tabelas, referências). |
| `montar.py` | Gera o `.docx` injetando o conteúdo no template. |

## Como editar

Edite o texto em `conteudo.py` e regenere:

```bash
python3 montar.py            # versão cega (submissão inicial)
python3 montar.py --final    # versão com os autores (versão final)
```

O script reextrai o template a cada execução e substitui apenas o corpo do
documento, de modo que **cabeçalho, rodapé, margens, estilos e a logomarca da
revista são sempre preservados**. Marcação inline disponível: `_texto_` vira
itálico (exigido pela revista para palavras estrangeiras).

Para conferir o resultado visualmente:

```bash
soffice --headless --convert-to pdf ARTIGO_RECIMA21.docx
```

## Conformidade com as normas da revista

- A4, margens do template (não alteradas), Arial 10, espaço 1,5 no corpo.
- Título em português, inglês e espanhol — maiúsculas, negrito, centralizado.
- Resumo / *Abstract* / *Resumen* em espaço simples, todos **abaixo de 250
  palavras** (243, 243 e 249), cada um com 5 descritores.
- Seções na ordem exigida: Introdução (com objetivo geral e específicos,
  justificativa e problema), 1 Referencial Teórico, 2 Metodologia,
  3 Resultados e Discussão, 4 Considerações Finais, Referências.
- 2 quadros e 3 tabelas, numerados em sequência, com título e fonte, todos
  mencionados e discutidos no texto.
- 22 referências em ABNT, em ordem alfabética, **todas citadas no corpo**.
- 19 páginas (o limite recomendado é 20).

## Antes de submeter

1. **Submeta a versão cega.** A revista exige avaliação cega no primeiro
   envio: o campo de autores fica em branco e a submissão é vinculada ao login
   de quem envia. Os nomes entram só no segundo envio, após a avaliação.
2. **Anonimato.** Pelo mesmo motivo, o texto não cita o nome do sistema, a
   instituição nem o repositório. Vale incluir na versão final.
3. **Cadastro dos autores.** Todos os autores precisam estar cadastrados na
   plataforma da revista *no momento da submissão* — inclusive a orientadora.
   Incluir nome depois da editoração implica taxa adicional, segundo o
   template.
4. **Referências.** Conferir páginas e volumes na fonte original antes do
   envio.
5. **Formato.** A revista só aceita `.docx` — não envie PDF nem `.doc`.

## Origem dos dados

Os números das tabelas vêm de `../pesquisa/` — experimento de confiabilidade
teste-reteste com 120 correções (6 redações × 2 modelos × 10 repetições).
Para reproduzi-los:

```bash
cd ../pesquisa && python3 analisar.py
```
