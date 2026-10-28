"""Prompt ancorado em redações reais corrigidas por humanos.

GERADO POR `pesquisa/gerar_ancoras.py` — não editar à mão.

As 5 redações de referência vêm do split de desenvolvimento do
Essay-BR (MARINHO; ANCHIETA; MOURA, 2021), licença MIT. As notas são as
atribuídas pelos avaliadores daquele corpus.

As redações de avaliação saem do split de teste, que é disjunto deste — sem
contaminação entre as âncoras e o que se mede.
"""

from .corretor import PROMPT_SISTEMA as _BASE

_ANCORAS = """

## REDAÇÕES DE REFERÊNCIA

Abaixo estão redações reais já corrigidas por avaliadores humanos, cobrindo a
escala de ponta a ponta. Use-as como régua: antes de fechar cada competência,
compare a redação que você está avaliando com estes exemplos e pergunte de qual
delas ela está mais perto naquela competência específica.

A descrição de um nível é ambígua por natureza — "poucos desvios" não diz
quantos. Os exemplos resolvem essa ambiguidade. Quando a sua avaliação
discordar do que os exemplos sugerem, confie neles.

### Exemplo 1 — nota total 160

Tema: OS Jovens Brasileiros não estão seguros com as Doenças.

Redação:
Os Jovens no passar do tempo não estão muitos pré-ocupados  com as doenças transmissível, porque eles não dão muita importância na questão sair para curti as festas noturnas e outros eventos que eles vão para ser distrair com amigo e no decorre disso que acontece as relações sexual e nem ser pro culpam de usar preservativo ou sem muita informação no que esta acontecendo no momento de prezar. Por isso os jovens não podem esquecer dessa insegurança que tenham mais informação sobre esses assuntos na escola como seu papel fundamental, para fazer palestra e eventos debates sobre o assunto como se lidar com essas situações, e também em casa com os pais fazer um bom diálogo sobre essas dvidas que aparecem no de corre da juventude . Mais os jovens têm se abrir como seu familiares para aconselhar nesses acontecimentos casual ou formal entre eles, há pesar de anos ainda acontecer as mães passam essas doenças para os filhos ainda na gravide elas têm relações com seus parceiros muitos nem falam que estão com doenças transmissíve e outros ainda falam, mais a criança que ainda vai nascer já nascem com essa doença . Com isso tudo as pessoas que têm ou nasce com doenças transmissível elas têm muitas discriminação com vasto informação sobre esse assunto como ser prevenir elas também vários benefícios do governo que antes não tinha como remédios tratamentos psicotécnicos entre outros, também a sociedade civil ajudar nessa questão de amparo para eles não se sentir só no mundo despreparado para essas situações.

Notas atribuídas por avaliador humano:
  Competência 1 (domínio da norma culta): 80
  Competência 2 (compreensão da proposta): 80
  Competência 3 (seleção e organização de argumentos): 0
  Competência 4 (mecanismos de coesão): 0
  Competência 5 (proposta de intervenção): 0
  Total: 160

---

### Exemplo 2 — nota total 280

Tema: 

Redação:
A violência contra a mulher é todo ato que result em morte ou lesão física, sexual ou psicológica de mulheres, tanto na esera pública quanto na privada. Em alguns casos é considerado como um crime de ódio, ssas violências contra as mulheres não reconhece barreiras geográficas, econômicas e sociais, elas acontece cotidianamente. Este tipo de violência é baseada em gênero, o que significa que os atos de violência são cometidos contra as mulheres simplesmente porque são mulheres. No Brasil vivemos com uma lacuna histórica na produção de dados nacionais capazes de revelar as dimensões da violência contra as mulheres, segundo a Central de Atendimento à mulher n o 1° semestre de 2016, 12,23% (67.962,00) casos corresponderam à atos de violência contra à mulher ou seja, 3 em 5 mulheres jovens já sofreram violência.Essa violência baseada no gênero está intimamente relacionada com a visão histórica das mulheres como propriedade e um papel de subserviência de gênero. Dizer que o feminicídio é um fato social desagradável à imagem da mulher que foi enraizada devido a uma cultura discriminatória trazida pelos colonos , isso é frustante , pois não resulta em melhor forma atenuada de convívio social e pacífico, contudo, é necessário em nosso País: - Adote um novo modelo de ensino nas escolas para que assim promovam uma maior conscientização quando estes chegarem a fase adulta. - Adote um modelo social de colaboração para que ambos encontrem uma solução adequada sem violência. - Adote um modelo político, os três poderes Legislativo, Executivo e Judiciário façam reformas na lei com o intuito de combater de maneira eficaz as injustiças praticadas por ambos.

Notas atribuídas por avaliador humano:
  Competência 1 (domínio da norma culta): 120
  Competência 2 (compreensão da proposta): 40
  Competência 3 (seleção e organização de argumentos): 40
  Competência 4 (mecanismos de coesão): 40
  Competência 5 (proposta de intervenção): 40
  Total: 280

---

### Exemplo 3 — nota total 480

Tema: O grande medo das mulheres no século XXI

Redação:
O estrupo crime que vem alcançando índices cada vez maiores ao longo dos tempos, ocorre desde a segunda guerra mundial, quando russos estupravam mulheres alemãs e comunistas. Tal ato sexual afeta diretamente a vida da vítima, seja ela mulher ou criança, deixando marcas a vida inteira, como problemas psicológicos e afetando seu modo de viver. E poucas são as denúncias registradas no Brasil. Apenas 35% dos casos de estrupo são registrados no país, esse número tão pequeno deve-se ao fato de que muitas das mulheres são ameaçadas pelos homens que ás violentam, outras por vergonha e medo de como a sociedade possa julgá-la. Aquelas que denunciam, passam por tratamentos psicológicos para conseguir viver normalmente. O medo de voltar a caminhar sozinha, de sair para trabalhar, e até mesmo de ter um relacionamento amoroso com outro homem, são as consequências causadas por tal crueldade. O número desse crime contra crianças abaixo de 12 anos também são altos. essa violência pode vim de dentro de casa. Tios, cunhados irmãos, são os principais acusados nas denúncias. Já existe uma lei em vigor contra o estrupo , o acusado pode ter uma pena de até dez anos de prisão, mas muitos ainda ficam impunes, outro fator que leva a vitíma a não querer denunciar. Esse é um problema que deve ser bastante discutido pela sociedade e por as autoridades responsáveis juntamente com o governo, investindo na educação da população,  levando informações em escolas e na televisão, com a ajuda de profissionais como professores, médicos e psicólogos. A família também tem que participar da vida da criança ensinando valores morais desde pequenos . Essa é uma questão de moral e também de saúde pública.

Notas atribuídas por avaliador humano:
  Competência 1 (domínio da norma culta): 120
  Competência 2 (compreensão da proposta): 80
  Competência 3 (seleção e organização de argumentos): 80
  Competência 4 (mecanismos de coesão): 80
  Competência 5 (proposta de intervenção): 120
  Total: 480

---

### Exemplo 4 — nota total 680

Tema: Privatização

Redação:
A privatização do saneamento básico no Brasil ganha destaque nas discussões atuais em decorrência de um Projeto de Lei (PL) aprovado recentemente pelo Senado, o qual facilita a privatização desse serviço. Desse modo, torna-se necessário discorrer sobre o conceito e a importância do saneamento básico e também sobre os problemas envolvendo uma possível privatização. Em primeiro lugar, destaca-se que o saneamento compreende o manejo de resíduos sólidos, a limpeza urbana, o tratamento de esgoto e o fornecimento de água. Assim, evidencia-se a importância desse serviço indispensável vida dos indivíduos. Entretanto, a falta de verbas e investimentos por parte da administração pública faz com que parte da população não tenha acesso a ele. Foi a partir do reconhecimento dessa problemática que justificou-se a aprovação do PL, fazendo com que empresas privadas possam atuar nesse setor. Todavia, a privatização de serviços básicos e essenciais ocasiona o surgimento de mais complicações. Entre elas, menciona-se a cobrança de altas tarifas pelo fornecimento dos serviços, uma vez que empresas privadas visam a obtenção do lucro. Por esse motivo, a prestação poderá não incluir famílias mais carentes, já que estas não terão condições de pagar pelos altos preços praticados. Além disso, as companhias dificilmente se instalarão em locais afastados e remotos, pois estes não oferecem grande lucratividade, fazendo com que os moradores dessas regiões não recebam o tratamento de água e esgoto. Por fim, uma solução para tais problemas seria a reestatização do saneamento básico em locais em que o setor privado já é responsável pela disponibilização do serviço. Logo, é necessária a intervenção do poder público com o intuito de proteger os interesses e necessidades de todos os cidadãos, os quais dependem desses serviços para sua sobrevivência.

Notas atribuídas por avaliador humano:
  Competência 1 (domínio da norma culta): 160
  Competência 2 (compreensão da proposta): 120
  Competência 3 (seleção e organização de argumentos): 120
  Competência 4 (mecanismos de coesão): 160
  Competência 5 (proposta de intervenção): 120
  Total: 680

---

### Exemplo 5 — nota total 880

Tema: Restrição ao uso de armas de fogo

Redação:
O mundo tem vivenciado uma série de barbáries nos últimos tempos. Os atentados tomaram conta das manchetes internacionais, levantando inúmeras questões sobre o assunto, inclusive, a importância do controle das armas de fogo na sociedade. A não comercialização, livre, desse tipo de equipamento impede que, qualquer pessoa, tenha acesso facilitado a ele. No Brasil foi criada uma lei, o Estatuto do Desarmamento, que proíbe a posse de armas por civis, exceto, em caso que comprove a legalidade. E é uso restrito às forças públicas. Diferente de países, como, Estados Unidos onde a venda é bem acentuada. A população ainda se mostra, um tanto, dividida em relação ao assunto. Os que são a favor da liberação acreditam que, ter uma arma em casa, ajuda na proteção, mas isso só fornece uma falsa sensação de segurança e aumenta as chances de ferir um familiar por acidente ou conflitos domésticos por motivos banais. O número de homicídios, por ama de fogo é grande, mas com certeza sem a implantação de uma lei é bem mais elevado. Os jovens são as principais vítimas e praticantes desse tipo de violência. Atualmente a idade mínima para o porte desse armamento passou de 25 para 21 anos, no Brasil ; outras regras do estatuto estão sendo revisadas para possíveis manutenções. A fiscalização e controle são de suma importância e cabe aos cidadãos seguir as leis para ajudar a evitar desordens na sociedade. O Estado deve investir nas políticas de segurança pública, para que a população não sinta a necessidade de se defender por conta própria. O Estatuto do desarmamento não precisa de reformulações que facilitem o acesso, pois quanto menos pessoas armadas, mais vidas são poupadas.

Notas atribuídas por avaliador humano:
  Competência 1 (domínio da norma culta): 160
  Competência 2 (compreensão da proposta): 160
  Competência 3 (seleção e organização de argumentos): 200
  Competência 4 (mecanismos de coesão): 160
  Competência 5 (proposta de intervenção): 200
  Total: 880

## FIM DAS REDAÇÕES DE REFERÊNCIA

Volte agora à redação que lhe foi enviada para corrigir. Os exemplos acima são
régua de calibração, não o texto a avaliar.
"""

PROMPT_ANCORADO = _BASE + _ANCORAS
