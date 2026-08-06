# Arquivos públicos

Tudo que estiver nesta pasta é servido pelo backend na raiz do site.
Exemplo: `publico/logo-ifsp.svg` fica disponível em `http://localhost:3005/logo-ifsp.svg`.

## Logotipo institucional

Baixe o arquivo oficial em https://spo.ifsp.edu.br/identidade-visual e salve
aqui com um destes nomes (o sistema tenta nesta ordem):

- `logo-ifsp.svg` (preferível — não perde qualidade em nenhum tamanho)
- `logo-ifsp.png`
- `logo-ifsp.jpg`

O IFSP distribui os arquivos em JPG e PDF. O JPG serve direto; se quiser
qualidade melhor, abra o PDF no Inkscape ou no Illustrator e exporte como SVG.

**Atenção:** o arquivo precisa conter **uma única assinatura**, não a prancha do
manual com as três versões lado a lado. O sistema usa a *versão simplificada
horizontal (uso prioritário)* — símbolo à esquerda, "INSTITUTO FEDERAL" e
"São Paulo" à direita. O arquivo atual já está recortado assim (496x153).

O cabeçalho e a tela de acesso passam a exibir o arquivo assim que ele existir.
Enquanto não houver logotipo, o sistema mostra apenas o texto
"INSTITUTO FEDERAL / São Paulo" em Open Sans — nada quebra.

Se o arquivo contiver **somente o símbolo** (sem as palavras "Instituto Federal
São Paulo"), abra o `index.html` e troque `LOGO_INCLUI_TEXTO` para `false`:
assim o texto continua aparecendo ao lado do símbolo.

**Não coloque aqui** nada que não deva ser público — esta pasta fica acessível
a qualquer pessoa que abrir o sistema.
