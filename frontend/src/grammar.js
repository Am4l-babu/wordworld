// Plain-English names for spaCy's Universal POS tags and English dependency labels.
export const POS_NAMES = {
  NOUN: 'noun', PROPN: 'proper noun', VERB: 'verb', AUX: 'auxiliary verb', ADJ: 'adjective', ADV: 'adverb',
  NUM: 'number', DET: 'determiner', ADP: 'preposition', PRON: 'pronoun', CCONJ: 'conjunction',
  SCONJ: 'subordinating conjunction', PART: 'particle', PUNCT: 'punctuation', INTJ: 'interjection',
  SYM: 'symbol', X: 'word', SPACE: 'space',
};

export const DEP_NAMES = {
  ROOT: 'main verb of the sentence', nsubj: 'subject', nsubjpass: 'passive subject', dobj: 'direct object',
  iobj: 'indirect object', dative: 'recipient', attr: 'attribute', oprd: 'object predicate', amod: 'adjective modifier',
  nummod: 'number modifier', quantmod: 'quantity modifier', det: 'determiner', predet: 'pre-determiner',
  compound: 'compound part', prep: 'preposition', pobj: 'object of a preposition', pcomp: 'preposition complement',
  advmod: 'adverb modifier', npadvmod: 'noun used as an adverb', conj: 'coordinated item', cc: 'coordinating conjunction',
  punct: 'punctuation', aux: 'auxiliary', auxpass: 'passive auxiliary', neg: 'negation', prt: 'verb particle',
  acl: 'clause modifying a noun', relcl: 'relative clause', advcl: 'adverbial clause', ccomp: 'clausal complement',
  xcomp: 'open clausal complement', appos: 'apposition', poss: 'possessive', case: 'possessive marker',
  mark: 'clause marker', expl: 'expletive', agent: 'agent', nmod: 'noun modifier', intj: 'interjection',
  meta: 'meta word', parataxis: 'loosely joined clause', dep: 'unclassified dependent', acomp: 'adjective complement',
  csubj: 'clausal subject', preconj: 'pre-conjunction',
};

// Grounding roles whose highlight span overlaps a token, so grammar and grounding read together.
export function tokenRoles(token, highlights = []) {
  return [...new Set(highlights.filter(h => h.start < token.end && h.end > token.start).map(h => h.role))];
}

export function headIndex(tokens, i) {
  const token = tokens[i];
  if (!token?.dep || token.head_start == null || token.dep === 'ROOT') return -1;
  return tokens.findIndex(t => t.start === token.head_start);
}

export function describeToken(tokens, i) {
  const token = tokens[i];
  if (!token) return '';
  const pos = POS_NAMES[token.pos];
  if (!token.dep) return pos ? `“${token.text}” is a ${pos}.` : `“${token.text}” is a word token.`;
  if (token.dep === 'ROOT') return `“${token.text}” is the ${pos || 'word'} at the root of the sentence; other words hang off it.`;
  const head = tokens[headIndex(tokens, i)];
  const relation = DEP_NAMES[token.dep] || token.dep;
  return `“${token.text}” is a ${pos || 'word'} acting as the ${relation} of “${head?.text ?? token.head}”.`;
}
