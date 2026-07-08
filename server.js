const express = require('express');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const Database = require('better-sqlite3');
const Anthropic = require('@anthropic-ai/sdk');
const path = require('path');
const { detectarCopia } = require('./plagio');
require('dotenv').config({ path: path.join(__dirname, '.env') });

const app = express();
const PORT = process.env.PORT || 3005;
const JWT_SECRET = process.env.JWT_SECRET || 'enem-correcao-secret-2025';
const LIMITE_MENSAL = 10;
// Código que promove um usuário a "professor" (quem gerencia o banco de temas).
const CODIGO_PROFESSOR = process.env.CODIGO_PROFESSOR || 'professor2025';

// ─── Banco de dados SQLite ───────────────────────────────────────────────────
const db = new Database(path.join(__dirname, 'database.db'));

db.exec(`
  CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    api_key TEXT DEFAULT NULL,
    criado_em TEXT DEFAULT (datetime('now'))
  );

  CREATE TABLE IF NOT EXISTS correcoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    tema TEXT,
    redacao TEXT NOT NULL,
    resultado TEXT NOT NULL,
    criado_em TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
  );

  CREATE TABLE IF NOT EXISTS temas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    textos_apoio TEXT NOT NULL,
    criado_em TEXT DEFAULT (datetime('now'))
  );
`);

// ─── Migração leve: adiciona colunas novas em bancos já existentes ────────────
function garantirColuna(tabela, coluna, definicao) {
  const cols = db.prepare(`PRAGMA table_info(${tabela})`).all();
  if (!cols.some((c) => c.name === coluna)) {
    db.exec(`ALTER TABLE ${tabela} ADD COLUMN ${coluna} ${definicao}`);
  }
}
garantirColuna('correcoes', 'tema_id', 'INTEGER');
garantirColuna('correcoes', 'plagio_percentual', 'INTEGER DEFAULT 0');
garantirColuna('usuarios', 'tipo', "TEXT DEFAULT 'aluno'"); // 'aluno' | 'professor'

// ─── Temas de exemplo (banco inicial no estilo ENEM) ──────────────────────────
// Os textos de apoio abaixo são resumos autorais no formato dos textos
// motivadores do ENEM; servem de base tanto para leitura quanto para a
// detecção de cópia.
const TEMAS_SEED = [
  {
    titulo: 'Os desafios da saúde mental na era digital',
    textos_apoio:
      'TEXTO I\nA Organização Mundial da Saúde aponta que os transtornos de ansiedade e a depressão figuram entre as principais causas de afastamento do trabalho no mundo. O ritmo acelerado da vida contemporânea e a hiperconexão contribuem para o adoecimento psíquico de milhões de pessoas.\n\n' +
      'TEXTO II\nPesquisas recentes indicam que o uso excessivo de redes sociais está associado ao aumento da ansiedade e da baixa autoestima, sobretudo entre adolescentes. A comparação constante com padrões idealizados de vida e de corpo intensifica sentimentos de inadequação.\n\n' +
      'TEXTO III\nApesar do avanço das discussões, o acesso a atendimento psicológico ainda é desigual no Brasil. A oferta de profissionais na rede pública é insuficiente, e o preconceito em torno das doenças mentais dificulta que muitas pessoas busquem ajuda.',
  },
  {
    titulo: 'Caminhos para combater a desinformação na internet',
    textos_apoio:
      'TEXTO I\nA circulação de notícias falsas cresceu de forma expressiva com a popularização das redes sociais e dos aplicativos de mensagem. Conteúdos enganosos se espalham mais rápido que checagens e correções, moldando opiniões e comportamentos.\n\n' +
      'TEXTO II\nEspecialistas defendem a educação midiática como ferramenta central de enfrentamento: ensinar o cidadão a verificar fontes, identificar vieses e desconfiar de manchetes sensacionalistas é tão importante quanto punir quem produz desinformação.\n\n' +
      'TEXTO III\nPlataformas digitais operam com algoritmos que priorizam o engajamento, o que muitas vezes favorece conteúdos polêmicos e imprecisos. O debate sobre a responsabilidade das empresas de tecnologia ganha força em diferentes países.',
  },
  {
    titulo: 'A valorização da leitura na formação do jovem brasileiro',
    textos_apoio:
      'TEXTO I\nDados de pesquisas nacionais mostram que o número de leitores no Brasil vem caindo, e que muitos jovens concluem a educação básica sem o hábito de ler por prazer. A leitura, no entanto, é essencial para o desenvolvimento do pensamento crítico.\n\n' +
      'TEXTO II\nBibliotecas públicas e escolares enfrentam falta de investimento e de acervo atualizado. Em muitas cidades, o acesso ao livro ainda é um privilégio, o que aprofunda desigualdades educacionais e culturais.\n\n' +
      'TEXTO III\nProjetos de incentivo à leitura, como clubes do livro e mediações em sala de aula, demonstram que o contato afetivo com a literatura desperta o interesse do estudante e amplia seu repertório sociocultural.',
  },
];

if (db.prepare('SELECT COUNT(*) AS total FROM temas').get().total === 0) {
  const inserir = db.prepare('INSERT INTO temas (titulo, textos_apoio) VALUES (?, ?)');
  const inserirVarios = db.transaction((temas) => temas.forEach((t) => inserir.run(t.titulo, t.textos_apoio)));
  inserirVarios(TEMAS_SEED);
  console.log(`📚 ${TEMAS_SEED.length} temas de exemplo cadastrados.`);
}

// ─── Middlewares ─────────────────────────────────────────────────────────────
app.use(cors({ origin: process.env.FRONTEND_URL || '*' }));
app.use(express.json());

// Middleware de autenticação JWT
function autenticar(req, res, next) {
  const auth = req.headers.authorization;
  if (!auth || !auth.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Token não fornecido. Faça login.' });
  }
  try {
    const token = auth.split(' ')[1];
    req.usuario = jwt.verify(token, JWT_SECRET);
    next();
  } catch {
    return res.status(401).json({ error: 'Token inválido ou expirado. Faça login novamente.' });
  }
}

// Middleware que exige perfil de professor (use sempre depois de `autenticar`)
function apenasProfessor(req, res, next) {
  if (req.usuario?.tipo !== 'professor') {
    return res.status(403).json({ error: 'Ação restrita a professores.' });
  }
  next();
}

// ─── Prompt do corretor ENEM ─────────────────────────────────────────────────
const SYSTEM_PROMPT = `Você é um corretor especializado em redações do ENEM. Avalie a redação nas 5 competências do ENEM e retorne APENAS um JSON válido, sem markdown, sem explicações fora do JSON.

REGRA SOBRE OS TEXTOS DE APOIO (siga rigorosamente, como no ENEM real):
- Quando forem fornecidos os textos de apoio (motivadores) e/ou uma lista de "TRECHOS COPIADOS" detectados, trate cópia literal dos textos de apoio como algo que NÃO é produção do participante.
- Desconsidere os trechos copiados ao avaliar a argumentação: eles não somam repertório nem contam como desenvolvimento próprio.
- Quanto maior o percentual copiado, maior a penalização, principalmente nas Competências II (compreensão da proposta) e III (seleção e organização de argumentos).
- Se a redação for essencialmente cópia dos textos de apoio (percentual de cópia muito alto, sem elaboração própria relevante), atribua nota_total 0 e explique que se trata de cópia, no feedback das competências.
- Comente a ocorrência de cópia no feedback das competências afetadas e inclua uma sugestão de melhoria orientando o aluno a reescrever os trechos copiados com as próprias palavras.

Formato exato:
{
  "nota_total": <soma das 5 notas, máx 1000>,
  "competencias": [
    {
      "numero": 1,
      "titulo": "Domínio da norma culta da língua portuguesa",
      "nota": <0, 40, 80, 120, 160 ou 200>,
      "nivel": "alto" | "medio" | "baixo",
      "feedback": "<2-3 frases de feedback específico sobre a redação>"
    },
    {
      "numero": 2,
      "titulo": "Compreensão da proposta e aplicação de conceitos de diversas áreas",
      "nota": <0, 40, 80, 120, 160 ou 200>,
      "nivel": "alto" | "medio" | "baixo",
      "feedback": "<2-3 frases>"
    },
    {
      "numero": 3,
      "titulo": "Seleção, relação e organização de informações e argumentos",
      "nota": <0, 40, 80, 120, 160 ou 200>,
      "nivel": "alto" | "medio" | "baixo",
      "feedback": "<2-3 frases>"
    },
    {
      "numero": 4,
      "titulo": "Conhecimento dos mecanismos linguísticos de coesão textual",
      "nota": <0, 40, 80, 120, 160 ou 200>,
      "nivel": "alto" | "medio" | "baixo",
      "feedback": "<2-3 frases>"
    },
    {
      "numero": 5,
      "titulo": "Proposta de intervenção respeitando os direitos humanos",
      "nota": <0, 40, 80, 120, 160 ou 200>,
      "nivel": "alto" | "medio" | "baixo",
      "feedback": "<2-3 frases>"
    }
  ],
  "melhorias": [
    "<sugestão específica 1>",
    "<sugestão específica 2>",
    "<sugestão específica 3>",
    "<sugestão específica 4>"
  ]
}`;

// ─── Rotas de autenticação ───────────────────────────────────────────────────

// POST /api/auth/cadastro
app.post('/api/auth/cadastro', async (req, res) => {
  const { nome, email, senha, codigo_professor } = req.body;

  if (!nome || !email || !senha) {
    return res.status(400).json({ error: 'Nome, e-mail e senha são obrigatórios.' });
  }
  if (senha.length < 6) {
    return res.status(400).json({ error: 'A senha deve ter pelo menos 6 caracteres.' });
  }
  // Código de professor opcional: se enviado, precisa estar correto.
  if (codigo_professor && codigo_professor.trim() !== CODIGO_PROFESSOR) {
    return res.status(400).json({ error: 'Código de professor inválido.' });
  }
  const tipo = codigo_professor && codigo_professor.trim() === CODIGO_PROFESSOR ? 'professor' : 'aluno';

  try {
    const hash = await bcrypt.hash(senha, 10);
    const stmt = db.prepare('INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)');
    const result = stmt.run(nome, email.toLowerCase().trim(), hash, tipo);

    const token = jwt.sign({ id: result.lastInsertRowid, nome, email, tipo }, JWT_SECRET, { expiresIn: '7d' });
    return res.status(201).json({ token, usuario: { id: result.lastInsertRowid, nome, email, tipo } });
  } catch (err) {
    if (err.message.includes('UNIQUE')) {
      return res.status(409).json({ error: 'E-mail já cadastrado.' });
    }
    return res.status(500).json({ error: 'Erro ao criar conta.' });
  }
});

// POST /api/auth/login
app.post('/api/auth/login', async (req, res) => {
  const { email, senha } = req.body;

  if (!email || !senha) {
    return res.status(400).json({ error: 'E-mail e senha são obrigatórios.' });
  }

  const usuario = db.prepare('SELECT * FROM usuarios WHERE email = ?').get(email.toLowerCase().trim());
  if (!usuario) {
    return res.status(401).json({ error: 'E-mail ou senha incorretos.' });
  }

  const senhaOk = await bcrypt.compare(senha, usuario.senha);
  if (!senhaOk) {
    return res.status(401).json({ error: 'E-mail ou senha incorretos.' });
  }

  const tipo = usuario.tipo || 'aluno';
  const token = jwt.sign({ id: usuario.id, nome: usuario.nome, email: usuario.email, tipo }, JWT_SECRET, { expiresIn: '7d' });
  return res.json({ token, usuario: { id: usuario.id, nome: usuario.nome, email: usuario.email, tipo } });
});

// POST /api/usuario/promover-professor — promove o usuário logado usando o código
app.post('/api/usuario/promover-professor', autenticar, (req, res) => {
  const { codigo } = req.body;
  if (!codigo || codigo.trim() !== CODIGO_PROFESSOR) {
    return res.status(403).json({ error: 'Código de professor inválido.' });
  }
  db.prepare("UPDATE usuarios SET tipo = 'professor' WHERE id = ?").run(req.usuario.id);
  const u = db.prepare('SELECT id, nome, email FROM usuarios WHERE id = ?').get(req.usuario.id);
  const token = jwt.sign({ id: u.id, nome: u.nome, email: u.email, tipo: 'professor' }, JWT_SECRET, { expiresIn: '7d' });
  return res.json({ message: 'Você agora é professor e pode gerenciar os temas.', token, tipo: 'professor' });
});

// ─── Rota para salvar chave de API própria ───────────────────────────────────

// POST /api/usuario/api-key
app.post('/api/usuario/api-key', autenticar, (req, res) => {
  const { api_key } = req.body;

  if (!api_key || !api_key.startsWith('sk-ant-')) {
    return res.status(400).json({ error: 'Chave inválida. Deve começar com sk-ant-' });
  }

  db.prepare('UPDATE usuarios SET api_key = ? WHERE id = ?').run(api_key.trim(), req.usuario.id);
  return res.json({ message: 'Chave de API salva com sucesso! Agora você tem uso ilimitado.' });
});

// DELETE /api/usuario/api-key
app.delete('/api/usuario/api-key', autenticar, (req, res) => {
  db.prepare('UPDATE usuarios SET api_key = NULL WHERE id = ?').run(req.usuario.id);
  return res.json({ message: 'Chave removida. Limite mensal de 10 redações restaurado.' });
});

// ─── Rota de status do usuário ───────────────────────────────────────────────

// GET /api/usuario/status
app.get('/api/usuario/status', autenticar, (req, res) => {
  const usuario = db.prepare('SELECT nome, email, api_key, tipo FROM usuarios WHERE id = ?').get(req.usuario.id);

  const mesAtual = new Date().toISOString().slice(0, 7); // "2025-05"
  const usadoMes = db.prepare(
    "SELECT COUNT(*) as total FROM correcoes WHERE usuario_id = ? AND strftime('%Y-%m', criado_em) = ?"
  ).get(req.usuario.id, mesAtual).total;

  const temChavesPropria = !!usuario.api_key;

  return res.json({
    nome: usuario.nome,
    email: usuario.email,
    tipo: usuario.tipo || 'aluno',
    tem_chave_propria: temChavesPropria,
    redacoes_usadas: usadoMes,
    redacoes_limite: temChavesPropria ? null : LIMITE_MENSAL,
    redacoes_restantes: temChavesPropria ? null : Math.max(0, LIMITE_MENSAL - usadoMes),
  });
});

// ─── Rotas de temas (banco de temas + textos de apoio) ───────────────────────

// GET /api/temas — lista os temas cadastrados com seus textos de apoio
app.get('/api/temas', autenticar, (req, res) => {
  const temas = db.prepare('SELECT id, titulo, textos_apoio FROM temas ORDER BY titulo').all();
  return res.json(temas);
});

// POST /api/temas — cadastra um novo tema no banco (somente professor)
app.post('/api/temas', autenticar, apenasProfessor, (req, res) => {
  const { titulo, textos_apoio } = req.body;

  if (!titulo || !titulo.trim()) {
    return res.status(400).json({ error: 'O título do tema é obrigatório.' });
  }
  if (!textos_apoio || textos_apoio.trim().length < 50) {
    return res.status(400).json({ error: 'Inclua os textos de apoio (mínimo de 50 caracteres).' });
  }

  const result = db
    .prepare('INSERT INTO temas (titulo, textos_apoio) VALUES (?, ?)')
    .run(titulo.trim(), textos_apoio.trim());

  return res.status(201).json({ id: result.lastInsertRowid, titulo: titulo.trim(), textos_apoio: textos_apoio.trim() });
});

// PUT /api/temas/:id — edita um tema existente (somente professor)
app.put('/api/temas/:id', autenticar, apenasProfessor, (req, res) => {
  const { titulo, textos_apoio } = req.body;

  if (!titulo || !titulo.trim()) {
    return res.status(400).json({ error: 'O título do tema é obrigatório.' });
  }
  if (!textos_apoio || textos_apoio.trim().length < 50) {
    return res.status(400).json({ error: 'Inclua os textos de apoio (mínimo de 50 caracteres).' });
  }

  const info = db
    .prepare('UPDATE temas SET titulo = ?, textos_apoio = ? WHERE id = ?')
    .run(titulo.trim(), textos_apoio.trim(), req.params.id);

  if (info.changes === 0) return res.status(404).json({ error: 'Tema não encontrado.' });
  return res.json({ id: Number(req.params.id), titulo: titulo.trim(), textos_apoio: textos_apoio.trim() });
});

// DELETE /api/temas/:id — remove um tema (somente professor)
app.delete('/api/temas/:id', autenticar, apenasProfessor, (req, res) => {
  const info = db.prepare('DELETE FROM temas WHERE id = ?').run(req.params.id);
  if (info.changes === 0) return res.status(404).json({ error: 'Tema não encontrado.' });
  return res.json({ message: 'Tema removido.' });
});

// ─── Rota principal de correção ──────────────────────────────────────────────

// POST /api/corrigir
app.post('/api/corrigir', autenticar, async (req, res) => {
  const { redacao, tema, tema_id, textos_apoio } = req.body;

  if (!redacao || redacao.trim().length < 100) {
    return res.status(400).json({ error: 'Redação muito curta. Mínimo de 100 caracteres.' });
  }

  // Resolve o tema e os textos de apoio: podem vir do banco (tema_id) ou personalizados.
  let tituloTema = tema && tema.trim() ? tema.trim() : null;
  let textosApoio = textos_apoio && textos_apoio.trim() ? textos_apoio.trim() : null;
  let temaId = null;
  if (tema_id) {
    const temaBanco = db.prepare('SELECT id, titulo, textos_apoio FROM temas WHERE id = ?').get(tema_id);
    if (!temaBanco) return res.status(404).json({ error: 'Tema não encontrado.' });
    temaId = temaBanco.id;
    tituloTema = temaBanco.titulo;
    textosApoio = temaBanco.textos_apoio;
  }

  // Detecta cópia dos textos de apoio (só quando há textos de apoio informados).
  const plagio = textosApoio
    ? detectarCopia(redacao, textosApoio)
    : { percentualCopiado: 0, palavrasCopiadas: 0, totalPalavras: 0, trechosCopiados: [] };

  // Busca dados do usuário
  const usuario = db.prepare('SELECT api_key FROM usuarios WHERE id = ?').get(req.usuario.id);

  // Verifica limite se não tem chave própria
  if (!usuario.api_key) {
    const mesAtual = new Date().toISOString().slice(0, 7);
    const usadoMes = db.prepare(
      "SELECT COUNT(*) as total FROM correcoes WHERE usuario_id = ? AND strftime('%Y-%m', criado_em) = ?"
    ).get(req.usuario.id, mesAtual).total;

    if (usadoMes >= LIMITE_MENSAL) {
      return res.status(429).json({
        error: `Limite de ${LIMITE_MENSAL} redações por mês atingido.`,
        limite_atingido: true,
        dica: 'Cadastre sua própria chave de API da Anthropic para uso ilimitado.'
      });
    }
  }

  // Usa chave própria do usuário ou chave do sistema
  const apiKey = usuario.api_key || process.env.ANTHROPIC_API_KEY;
  const client = new Anthropic({ apiKey });

  // Monta o prompt com tema, textos de apoio e os trechos copiados detectados.
  const partes = [];
  if (tituloTema) partes.push(`Tema: ${tituloTema}`);
  if (textosApoio) partes.push(`Textos de apoio:\n${textosApoio}`);
  if (plagio.trechosCopiados.length > 0) {
    const lista = plagio.trechosCopiados
      .slice(0, 10)
      .map((t, i) => `${i + 1}. "${t.texto}"`)
      .join('\n');
    partes.push(
      `TRECHOS COPIADOS dos textos de apoio (detecção automática — ${plagio.percentualCopiado}% da redação é cópia literal). ` +
      `Desconsidere-os como produção do participante e penalize conforme a regra do ENEM:\n${lista}`
    );
  }
  partes.push(`Redação:\n${redacao.trim()}`);
  const userPrompt = partes.join('\n\n');

  try {
    const message = await client.messages.create({
      model: 'claude-sonnet-4-5',
      max_tokens: 1500,
      system: SYSTEM_PROMPT,
      messages: [{ role: 'user', content: userPrompt }],
    });

    const text = message.content.map(b => b.text || '').join('');
    const clean = text.replace(/```json|```/g, '').trim();
    const result = JSON.parse(clean);

    // Anexa o resultado da detecção de cópia à resposta.
    result.plagio = plagio;

    // Salva correção no banco
    db.prepare(
      'INSERT INTO correcoes (usuario_id, tema, tema_id, redacao, resultado, plagio_percentual) VALUES (?, ?, ?, ?, ?, ?)'
    ).run(req.usuario.id, tituloTema || null, temaId, redacao.trim(), JSON.stringify(result), plagio.percentualCopiado);

    return res.json(result);
  } catch (err) {
    console.error('Erro ao chamar a API Anthropic:', err.message);
    if (err.status === 401) return res.status(500).json({ error: 'Chave de API inválida.' });
    if (err instanceof SyntaxError) return res.status(500).json({ error: 'Erro ao interpretar resposta da IA.' });
    return res.status(500).json({ error: 'Erro interno ao processar a redação.' });
  }
});

// GET /api/usuario/historico
app.get('/api/usuario/historico', autenticar, (req, res) => {
  const correcoes = db.prepare(
    `SELECT id, tema, criado_em, plagio_percentual, json_extract(resultado, '$.nota_total') AS nota_total FROM correcoes WHERE usuario_id = ? ORDER BY criado_em DESC LIMIT 20`
  ).all(req.usuario.id);
  return res.json(correcoes);
});

// GET /api/health
app.get('/api/health', (req, res) => res.json({ status: 'ok' }));

// Serve o frontend: assim tudo roda em http://localhost:3005 (sem CORS nem 2º servidor)
app.get('/', (req, res) => res.sendFile(path.join(__dirname, 'index.html')));

app.listen(PORT, () => {
  console.log(`✅ Servidor rodando em http://localhost:${PORT}`);
  console.log(`   Abra o sistema em: http://localhost:${PORT}`);
});
