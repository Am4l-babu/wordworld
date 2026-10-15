import React, {useEffect, useState} from 'react';

let scoresRequest = null;
function useCorpusScores() {
  const [scores, setScores] = useState(null);
  useEffect(() => {
    scoresRequest ??= fetch('/api/extractors').then(r => r.ok ? r.json() : null).catch(() => null);
    scoresRequest.then(result => {
      if (!result) scoresRequest = null;  // retry on the next analysis instead of caching a failure
      setScores(result);
    });
  }, []);
  return scores;
}

const pct = metric => `${Math.round(metric.accuracy * 100)}%`;

// Same sentence, two extractors: the grounding rules (which drive the world) and a
// dependency-parse baseline (comparison only). Shown only when the full spaCy model ran.
export default function ExtractorComparison({parsed, label}) {
  const scores = useCorpusScores();
  if (!Array.isArray(parsed.baseline)) return null;
  const same = JSON.stringify(parsed.actions || []) === JSON.stringify(parsed.baseline);
  const column = (title, note, actions) => <div className="compare-column">
    <b>{title}</b><small>{note}</small>
    <div className="actions-chips">{actions.length ? actions.map((a, i) => <span key={i}>{label(a)}</span>) : <em>No actions</em>}</div>
  </div>;
  return <div className="compare-section" aria-label="Extractor comparison">
    <div className="dep-heading">
      <b>Rules vs dependency baseline</b>
      <span className={'compare-badge ' + (same ? 'same' : 'different')}>{same ? 'Same actions' : 'Different actions'}</span>
    </div>
    <div className="compare-columns">
      {column('Grounding rules', 'drives the world', parsed.actions || [])}
      {column('Dependency baseline', 'spaCy arcs only · comparison', parsed.baseline)}
    </div>
    {scores && <p className="compare-corpus">
      Across {scores.commands} labelled commands, the rules match every field of the expected actions {pct(scores.rules.exact_match)} of the time
      ({Math.round(scores.rules_first_run_exact.correct / scores.rules_first_run_exact.total * 100)}% on first sight of each new set);
      the dependency baseline manages {pct(scores.baseline.exact_match)}.
    </p>}
  </div>;
}
