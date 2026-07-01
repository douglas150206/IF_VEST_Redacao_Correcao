// ─── Detecção de cópia dos textos de apoio ───────────────────────────────────
// Compara a redação do aluno com os textos de apoio do tema e identifica
// trechos copiados literalmente, no espírito da regra do ENEM: trechos copiados
// dos textos motivadores não contam como produção do participante.
//
// Técnica: "shingles" (n-gramas de palavras). Constrói-se o conjunto de todas as
// sequências de N palavras dos textos de apoio; depois percorre-se a redação e,
// sempre que uma sequência de N palavras da redação já existe nesse conjunto,
// aquelas palavras são marcadas como copiadas. Sequências marcadas e contíguas
// são agrupadas em "trechos copiados".

/**
 * Normaliza uma palavra: minúsculas, sem acentos e sem pontuação.
 * Assim "Educação," e "educacao" passam a ser comparáveis.
 */
function normalizarPalavra(palavra) {
  return palavra
    .toLowerCase()
    .normalize('NFD')            // decompõe letras acentuadas: "ç" -> "c" + cedilha
    .replace(/[^a-z0-9]/g, '');  // remove acentos (agora soltos), pontuação e símbolos
}

/**
 * Quebra o texto em tokens, guardando a palavra original (para exibir os trechos
 * ao usuário) e a forma normalizada (para comparar). Tokens vazios são descartados.
 */
function tokenizar(texto) {
  return (texto || '')
    .split(/\s+/)
    .map((original) => ({ original, norm: normalizarPalavra(original) }))
    .filter((t) => t.norm.length > 0);
}

/**
 * Detecta cópia da redação em relação aos textos de apoio.
 *
 * @param {string} redacao        Texto da redação do aluno.
 * @param {string} textosApoio    Textos de apoio/motivadores do tema (concatenados).
 * @param {object} [opcoes]
 * @param {number} [opcoes.tamanhoShingle=7]  Nº de palavras da sequência mínima considerada cópia.
 * @returns {{
 *   percentualCopiado: number,   // 0–100
 *   palavrasCopiadas: number,
 *   totalPalavras: number,
 *   trechosCopiados: {texto: string, palavras: number}[]
 * }}
 */
function detectarCopia(redacao, textosApoio, opcoes = {}) {
  const tamanhoShingle = opcoes.tamanhoShingle || 7;

  const apoioTokens = tokenizar(textosApoio);
  const redacaoTokens = tokenizar(redacao);

  const vazio = {
    percentualCopiado: 0,
    palavrasCopiadas: 0,
    totalPalavras: redacaoTokens.length,
    trechosCopiados: [],
  };

  // Sem texto de apoio ou textos curtos demais → não há como comparar.
  if (apoioTokens.length < tamanhoShingle || redacaoTokens.length < tamanhoShingle) {
    return vazio;
  }

  // 1) Conjunto de todas as sequências de N palavras dos textos de apoio.
  const shinglesApoio = new Set();
  for (let i = 0; i + tamanhoShingle <= apoioTokens.length; i++) {
    const gram = apoioTokens.slice(i, i + tamanhoShingle).map((t) => t.norm).join(' ');
    shinglesApoio.add(gram);
  }

  // 2) Marca na redação toda palavra que faz parte de uma sequência copiada.
  const copiado = new Array(redacaoTokens.length).fill(false);
  for (let i = 0; i + tamanhoShingle <= redacaoTokens.length; i++) {
    const gram = redacaoTokens.slice(i, i + tamanhoShingle).map((t) => t.norm).join(' ');
    if (shinglesApoio.has(gram)) {
      for (let j = i; j < i + tamanhoShingle; j++) copiado[j] = true;
    }
  }

  // 3) Agrupa palavras copiadas contíguas em trechos legíveis (palavras originais).
  const trechosCopiados = [];
  let inicio = -1;
  for (let i = 0; i <= redacaoTokens.length; i++) {
    const marcada = i < redacaoTokens.length && copiado[i];
    if (marcada && inicio === -1) {
      inicio = i;
    } else if (!marcada && inicio !== -1) {
      const texto = redacaoTokens.slice(inicio, i).map((t) => t.original).join(' ');
      trechosCopiados.push({ texto, palavras: i - inicio });
      inicio = -1;
    }
  }

  const palavrasCopiadas = copiado.filter(Boolean).length;
  const totalPalavras = redacaoTokens.length;
  const percentualCopiado = Math.round((palavrasCopiadas / totalPalavras) * 100);

  // Trechos maiores primeiro (mais relevantes para exibir).
  trechosCopiados.sort((a, b) => b.palavras - a.palavras);

  return { percentualCopiado, palavrasCopiadas, totalPalavras, trechosCopiados };
}

module.exports = { detectarCopia, tokenizar, normalizarPalavra };
