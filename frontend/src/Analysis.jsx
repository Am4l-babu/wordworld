import React, {useState} from 'react';
import {RELATION_LABEL} from './world';
import {describeToken, tokenRoles, headIndex} from './grammar';
import DependencyArcs from './components/DependencyArcs';
import ExtractorComparison from './components/ExtractorComparison';

const plural = (type, count) => count === 1 ? type : `${type}s`;
const labels = {intent: 'Instruction', object: 'Object', quantity: 'Quantity', color: 'Color', change: 'Change', spatial_relation: 'Relation', landmark: 'Landmark', setting: 'Setting', protected: 'Preserved', reference: 'Reference'};
const MODEL_NOTE = {
  spacy: 'spaCy grammar annotations',
  'browser-preview': 'Limited browser preview',
  'spacy-tokenizer': 'spaCy tokenizer · grammar model unavailable',
};

// Clicking a highlighted phrase selects its first word, linking grounding spans to grammar.
function HighlightedCommand({parsed, onPickSpan}) {
  const chars = Array.from(parsed.text || ''), parts = [];
  let cursor = 0;
  for (const span of parsed.highlights || []) {
    if (!Number.isInteger(span.start) || span.start < cursor) continue;
    parts.push(chars.slice(cursor, span.start).join(''));
    parts.push(<mark key={`${span.start}-${span.role}`} className={`span-${span.role}`} title={labels[span.role] || span.role} onClick={() => onPickSpan(span)}>
      {chars.slice(span.start, span.end).join('')}
    </mark>);
    cursor = span.end;
  }
  parts.push(chars.slice(cursor).join(''));
  return <p className="grounded-command" aria-label="Annotated command">{parts}</p>;
}

const DIRECTION_LABEL = {left: 'left', right: 'right', up: 'back', down: 'forward'};

function actionLabel(a) {
  const place = a.filter_relation ? ` ${RELATION_LABEL[a.filter_relation] || a.filter_relation} ${a.filter_target}` : '';
  const who = `${a.count === 'all' ? 'all' : a.count} ${a.filter_color ? a.filter_color + ' ' : ''}${plural(a.type, a.count)}${place}`;
  const main = a.action === 'add' ? `+ ${a.count} ${a.color ? a.color + ' ' : ''}${plural(a.type, a.count)}`
    : a.action === 'remove' ? `− ${who}`
    : a.action === 'recolor' ? `🎨 ${who} → ${a.color}`
    : a.action === 'resize' ? `⤢ ${who} ${a.scale > 1 ? 'bigger' : 'smaller'}`
    : a.action === 'move' ? `↔ move ${who}${a.direction ? ` ${DIRECTION_LABEL[a.direction]}` : ''}`
    : a.action === 'setting' ? `${a.key}: ${a.value}` : 'Reset world';
  return main + (a.relation ? ` · ${RELATION_LABEL[a.relation] || a.relation} ${(a.targets || [a.target]).join(' & ')}` : '');
}

export default function Analysis({parsed}) {
  const tokens = parsed.tokens || [];
  const [active, setActive] = useState(0), token = tokens[active];
  const hasDependencies = tokens.some(t => t.dep);
  const roles = token ? tokenRoles(token, parsed.highlights) : [];
  const head = token ? tokens[headIndex(tokens, active)] : null;
  function pickSpan(span) {
    const i = tokens.findIndex(t => t.start < span.end && t.end > span.start);
    if (i >= 0) setActive(i);
  }
  return <>
    <div className="parsed-note">
      <span className="parse-engine">RULE-BASED ACTIONS</span>
      <span>{MODEL_NOTE[parsed.model] || 'Lexical tokenizer'} · {parsed.actions?.length || 0} actions</span>
    </div>
    <HighlightedCommand parsed={parsed} onPickSpan={pickSpan}/>
    <div className="span-legend">{Object.entries(labels).map(([role, label]) => <span key={role}><i className={`span-${role}`}/>{label}</span>)}</div>
    {parsed.resolutions?.length > 0 && <p className="reference-resolutions">
      {parsed.resolutions.map((r, i) => <span key={i}>{r.text} → {r.objects.map(o => `${o.count} ${o.type}${o.count > 1 ? 's' : ''}`).join(' + ')}{r.earlier ? ' (from before)' : ''}</span>)}
    </p>}
    {hasDependencies && <div className="dep-section">
      <div className="dep-heading"><b>Sentence structure</b><span>spaCy dependency parse · annotation only, the actions above come from the grounding rules</span></div>
      <DependencyArcs tokens={tokens} highlights={parsed.highlights} active={active} onSelect={setActive}/>
    </div>}
    <p className="analysis-caption">Select a word to inspect its grammar. Highlighted phrases show the grounding rules.</p>
    <div className="token-list">
      {tokens.map((word, i) => <button key={i} type="button" aria-pressed={active === i} onClick={() => setActive(i)}
        className={'token ' + (word.pos === 'NOUN' || word.pos === 'PROPN' ? 'noun' : word.pos === 'VERB' ? 'verb' : '')}
        title={word.dep ? `${word.pos} · ${word.dep} → ${word.head}` : word.pos}>
        {word.text}<small>{word.pos === 'TOKEN' ? '' : word.pos}</small>
      </button>)}
    </div>
    {token && <>
      <p className="token-meaning" aria-live="polite">{describeToken(tokens, active)}</p>
      <dl className="token-details">
        <div><dt>Word / lemma</dt><dd>{token.text} / {token.lemma}</dd></div>
        <div><dt>Part of speech</dt><dd>{token.pos || 'Unavailable'}</dd></div>
        <div><dt>Dependency → head</dt><dd>{token.dep ? `${token.dep} → ${token.head}` : 'Requires spaCy English model'}</dd></div>
        <div><dt>Character span</dt><dd>{token.start == null ? 'Unavailable' : `${token.start}–${token.end}`}</dd></div>
        <div><dt>Grounding role</dt><dd>{roles.length ? roles.map(r => labels[r] || r).join(', ') : 'Not used by the rules'}</dd></div>
        <div><dt>Head word</dt><dd>{head ? <button type="button" className="link-button" onClick={() => setActive(tokens.indexOf(head))}>{head.text}</button> : token.dep === 'ROOT' ? 'Itself (root)' : '—'}</dd></div>
      </dl>
    </>}
    <div className="actions-chips">{parsed.actions?.map((a, i) => <span key={i}>{actionLabel(a)}</span>)}</div>
    <ExtractorComparison parsed={parsed} label={actionLabel}/>
    {parsed.warnings?.length > 0 && <ul className="parse-warnings" aria-label="Parser notices">{parsed.warnings.map(w => <li key={w}>{w}</li>)}</ul>}
    <details className="action-json"><summary>Structured actions JSON</summary><pre>{JSON.stringify(parsed.actions, null, 2)}</pre></details>
  </>;
}
