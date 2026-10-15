import React from 'react';
import {WandSparkles} from 'lucide-react';

export default function Composer({inputRef, value, onChange, onKeyDown, onSubmit, busy, isCompact, canRecall, focusLabel}) {
  return <div className="composer">
    <label htmlFor="world-command" className="composer-label"><WandSparkles size={15}/> Describe your imagination</label>
    <textarea id="world-command" ref={inputRef} rows={3} maxLength={1400} value={value}
      onChange={e => onChange(e.target.value)} onKeyDown={onKeyDown}
      placeholder="A cozy village with three houses and a little lake..." aria-describedby="composer-hint"/>
    {focusLabel && <div className="focus-chip" title="Say 'it' or 'them' to refer to these, e.g. “make it blue”">
      <span>it / them</span> → {focusLabel}
    </div>}
    <div className="composer-footer">
      <span id="composer-hint">{isCompact ? 'Tap Create to update your island' : <>↵ create · ⇧↵ new line{canRecall && ' · ↑ previous'}</>}</span>
      {value.length > 1200 && <span className="char-count">{value.length}/1400</span>}
      <button onClick={onSubmit} disabled={!value.trim() || busy} aria-label="Generate objects" title="Generate objects">
        <WandSparkles size={17} className={busy ? 'spin' : ''}/>
        <span className="create-label">{busy ? 'Creating…' : 'Create'}</span>
      </button>
    </div>
  </div>;
}
