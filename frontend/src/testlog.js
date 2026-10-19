// Local test log for user testing. Everything stays in this browser until the person downloads it:
// nothing is sent to a server. Entries hold what was typed and what the parser did, never the scene.
export const SCHEMA = 1;
export const MAX_ENTRIES = 300;
export const MAX_TEXT = 1400;
export const MAX_NOTE = 500;
const OUTCOMES = ['applied', 'nothing', 'rejected', 'preview'];

const clip = (value, max) => String(value ?? '').slice(0, max);
const randomId = () => `t-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;

// applied: the world changed · nothing: understood as nothing · rejected: the API refused it ·
// preview: the offline browser preview answered, so the Python parser was not involved
export function classify(result) {
  if (result.rejected) return 'rejected';
  if (result.model === 'browser-preview') return 'preview';
  return result.actions?.length ? 'applied' : 'nothing';
}

export function newEntry({text, result, context = [], device = 'desktop', now = new Date(), id = randomId()}) {
  const suggestion = result.suggestions?.[0];
  return {
    id, at: now.toISOString(), text: clip(text, MAX_TEXT), outcome: classify(result), device,
    context: context.slice(0, 12).map(g => ({type: String(g.type), count: Number(g.count) || 0})),
    actions: (result.actions || []).slice(0, 20),
    warnings: (result.warnings || []).slice(0, 10).map(w => clip(w, 300)),
    message: clip(result.message, 300), model: clip(result.model, 30),
    suggestion: suggestion ? clip(suggestion.text, MAX_TEXT) : null, replaces: Boolean(suggestion?.replaces), suggestionAccepted: false,
    flagged: false, note: '',
  };
}

// Idempotent by id: React may run a state updater twice, and one command must never be logged twice.
export const addEntry = (entries, entry) => [...entries.filter(e => e.id !== entry.id), entry].slice(-MAX_ENTRIES);
const update = (entries, id, change) => entries.map(e => e.id === id ? {...e, ...change} : e);
export const flagEntry = (entries, id, note = '') => update(entries, id, {flagged: true, note: clip(note, MAX_NOTE).trim()});
export const unflagEntry = (entries, id) => update(entries, id, {flagged: false, note: ''});
export const acceptSuggestion = (entries, id) => update(entries, id, {suggestionAccepted: true});

// Saved data can be damaged or edited, so keep only well-formed entries.
export function sanitizeLog(value) {
  if (!Array.isArray(value)) return [];
  return value.filter(e => e && typeof e.id === 'string' && typeof e.text === 'string' && OUTCOMES.includes(e.outcome)).slice(-MAX_ENTRIES).map(e => ({
    id: clip(e.id, 60), at: clip(e.at, 40), text: clip(e.text, MAX_TEXT), outcome: e.outcome, device: e.device === 'phone' ? 'phone' : 'desktop',
    context: Array.isArray(e.context) ? e.context.filter(g => g && typeof g.type === 'string').slice(0, 12).map(g => ({type: clip(g.type, 20), count: Number(g.count) || 0})) : [],
    actions: Array.isArray(e.actions) ? e.actions.filter(a => a && typeof a === 'object').slice(0, 20) : [],
    warnings: Array.isArray(e.warnings) ? e.warnings.filter(w => typeof w === 'string').slice(0, 10).map(w => clip(w, 300)) : [],
    message: clip(e.message, 300), model: clip(e.model, 30),
    suggestion: typeof e.suggestion === 'string' ? clip(e.suggestion, MAX_TEXT) : null, replaces: e.replaces === true, suggestionAccepted: e.suggestionAccepted === true,
    flagged: e.flagged === true, note: clip(e.note, MAX_NOTE),
  }));
}

export function summarize(entries) {
  const count = outcome => entries.filter(e => e.outcome === outcome).length;
  return {
    commands: entries.length, applied: count('applied'), nothing: count('nothing'), rejected: count('rejected'), preview: count('preview'),
    flagged: entries.filter(e => e.flagged).length,
    suggestionsShown: entries.filter(e => e.suggestion).length, suggestionsAccepted: entries.filter(e => e.suggestionAccepted).length,
  };
}

export function exportPayload(entries, now = new Date()) {
  return {schema: SCHEMA, app: 'wordworld-testlog', exportedAt: now.toISOString(), summary: summarize(entries), entries};
}

export const exportFilename = (now = new Date()) => `wordworld-testlog-${now.toISOString().slice(0, 10)}.json`;
