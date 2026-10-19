import {test} from 'node:test';
import assert from 'node:assert/strict';
import {classify, newEntry, addEntry, flagEntry, unflagEntry, acceptSuggestion, sanitizeLog, summarize, exportPayload, exportFilename, MAX_ENTRIES, MAX_NOTE} from '../src/testlog.js';

const when = new Date('2026-10-19T10:00:00Z');
const applied = {actions: [{action: 'add', type: 'tree', count: 1}], warnings: [], model: 'spacy'};

test('outcomes distinguish applied, nothing, rejected and the offline preview', () => {
  assert.equal(classify(applied), 'applied');
  assert.equal(classify({actions: [], warnings: ['x'], model: 'spacy'}), 'nothing');
  assert.equal(classify({actions: [], rejected: true, model: 'spacy'}), 'rejected');
  assert.equal(classify({actions: [{action: 'add'}], model: 'browser-preview'}), 'preview');
});

test('an entry keeps what was typed and what the parser did, never the scene', () => {
  const entry = newEntry({text: 'Paint the tres blue', context: [{type: 'tree', count: 2}], device: 'phone', now: when, id: 'a',
    result: {actions: [], warnings: ['No supported object'], model: 'spacy', message: 'No scene changes were applied.', suggestions: [{text: 'Paint the trees blue', replaces: false}]}});
  assert.deepEqual(entry, {id: 'a', at: '2026-10-19T10:00:00.000Z', text: 'Paint the tres blue', outcome: 'nothing', device: 'phone',
    context: [{type: 'tree', count: 2}], actions: [], warnings: ['No supported object'], message: 'No scene changes were applied.', model: 'spacy',
    suggestion: 'Paint the trees blue', replaces: false, suggestionAccepted: false, flagged: false, note: ''});
  assert.ok(!('items' in entry) && !('tokens' in entry));
});

test('flagging, notes and accepted suggestions update one entry and cap sizes', () => {
  let log = [newEntry({text: 'a', result: applied, id: 'a'}), newEntry({text: 'b', result: applied, id: 'b'})];
  log = flagEntry(log, 'b', '  I wanted two houses  ');
  assert.deepEqual(log.map(e => [e.flagged, e.note]), [[false, ''], [true, 'I wanted two houses']]);
  log = acceptSuggestion(log, 'a');
  assert.equal(log[0].suggestionAccepted, true);
  log = unflagEntry(log, 'b');
  assert.deepEqual([log[1].flagged, log[1].note], [false, '']);
  assert.equal(flagEntry(log, 'a', 'x'.repeat(5000))[0].note.length, MAX_NOTE);
});

test('the log keeps only the most recent entries', () => {
  let log = [];
  for (let i = 0; i < MAX_ENTRIES + 25; i++) log = addEntry(log, newEntry({text: `c${i}`, result: applied, id: `i${i}`}));
  assert.equal(log.length, MAX_ENTRIES);
  assert.equal(log[0].text, 'c25');
});

test('adding the same entry twice, as a double-invoked updater would, logs it once', () => {
  const entry = newEntry({text: 'a', result: applied, id: 'same'});
  assert.deepEqual(addEntry(addEntry([], entry), entry).map(e => e.id), ['same']);
});

test('damaged saved data is repaired or dropped, never trusted', () => {
  assert.deepEqual(sanitizeLog('nope'), []);
  assert.deepEqual(sanitizeLog(null), []);
  const repaired = sanitizeLog([null, 5, {id: 1, text: 'x', outcome: 'applied'}, {id: 'ok', text: 'hi', outcome: 'bogus'},
    {id: 'good', text: 'Add a tree', outcome: 'applied', device: 'tablet', context: 'x', actions: [null, {action: 'add'}], warnings: [1, 'w'], flagged: 'yes', note: 7, suggestion: 5}]);
  assert.equal(repaired.length, 1);
  assert.deepEqual([repaired[0].device, repaired[0].context, repaired[0].actions, repaired[0].warnings, repaired[0].flagged, repaired[0].note, repaired[0].suggestion],
    ['desktop', [], [{action: 'add'}], ['w'], false, '7', null]);
});

test('the export carries a summary and a dated filename', () => {
  const log = [newEntry({text: 'a', result: applied, id: 'a'}), flagEntry([newEntry({text: 'b', result: {actions: [], model: 'spacy'}, id: 'b'})], 'b', 'n')[0]];
  const payload = exportPayload(log, when);
  assert.deepEqual(payload.summary, {commands: 2, applied: 1, nothing: 1, rejected: 0, preview: 0, flagged: 1, suggestionsShown: 0, suggestionsAccepted: 0});
  assert.deepEqual([payload.schema, payload.app, payload.exportedAt], [1, 'wordworld-testlog', '2026-10-19T10:00:00.000Z']);
  assert.equal(exportFilename(when), 'wordworld-testlog-2026-10-19.json');
  assert.deepEqual(summarize([]), {commands: 0, applied: 0, nothing: 0, rejected: 0, preview: 0, flagged: 0, suggestionsShown: 0, suggestionsAccepted: 0});
});
