import React, {useEffect, useRef, useState} from 'react';
import {Sparkles, WandSparkles, RotateCcw, Check, CornerDownLeft, ChevronRight, Lightbulb, Undo2, Flag} from 'lucide-react';
import {EXAMPLES} from '../world';

const EXAMPLE_ICONS = ['🏡', '🌲', '🏰', '🌉', '🌙', '🌷', '🎨', '↔️'];

function Avatar({kind}) {
  if (kind === 'system') return <div className="bot-avatar"><Sparkles size={16}/></div>;
  if (kind === 'welcome') return <div className="greeting-icon"><WandSparkles size={23} strokeWidth={2.5}/></div>;
  return <div className="user-avatar">YOU</div>;
}

// "Not what I meant": marks a reply in the local test log, with an optional note about what was expected.
function FlagControl({entry, onFlag, onUnflag}) {
  const [editing, setEditing] = useState(false), [note, setNote] = useState('');
  const form = useRef(null);
  // The journal scrolls (smoothly), and the input's autofocus would cancel a smooth scroll half-way, so jump
  // instantly to bring the whole form, Save button included, into view once it has opened.
  useEffect(() => { if (editing) form.current?.scrollIntoView({block: 'nearest', behavior: 'instant'}); }, [editing]);
  if (!entry) return null;
  if (entry.flagged && !editing) return <p className="flagged"><Check size={12}/> Saved to your test log{entry.note ? `: “${entry.note}”` : ''}. <button type="button" className="link-button" onClick={() => onUnflag(entry.id)}>Undo</button></p>;
  if (!editing) return <button type="button" className="flag-button" onClick={() => setEditing(true)}><Flag size={12}/> Not what I meant</button>;
  return <form className="flag-form" ref={form} onSubmit={e => { e.preventDefault(); onFlag(entry.id, note); setEditing(false); setNote(''); }}>
    <label htmlFor={`flag-${entry.id}`}>What did you expect? (optional)</label>
    <input id={`flag-${entry.id}`} value={note} maxLength={500} autoFocus onChange={e => setNote(e.target.value)} placeholder="e.g. two red houses next to the lake"/>
    <div><button type="submit">Save</button><button type="button" onClick={() => { setEditing(false); setNote(''); }}>Cancel</button></div>
  </form>;
}

export function Journal({messages, busy, onReset, onReuse, onUndo, canUndo, entries = {}, onFlag, onUnflag, onAccept}) {
  const log = useRef(null);
  useEffect(() => {
    if (log.current) log.current.scrollTop = log.current.scrollHeight;
  }, [messages, busy]);
  return <>
    <div className="chat-heading">
      <div><span className="small-dot purple"/> Creation journal</div>
      <button title="Clear the world (you can undo)" aria-label="Clear the world" onClick={onReset}><RotateCcw size={16}/></button>
    </div>
    <div className="chat-history" ref={log} role="log" aria-live="polite" aria-label="Creation journal">
      {messages.map((m, i) => <div className={'chat-row ' + m.kind} key={i}>
        <Avatar kind={m.kind}/>
        <div className="chat-bubble">
          <span className="bubble-text">{m.text}</span>
          {m.kind === 'system' && m.actionCount > 0 && <span className="applied"><Check size={12}/> Applied to world</span>}
          {m.suggestion && <div className="suggestion">
            {m.suggestion.replaces && <p className="suggestion-note">Part of that wasn’t understood, so the result may be incomplete.</p>}
            <button className="did-you-mean" onClick={() => { onAccept?.(m.logId); onReuse(m.suggestion.text); }} title="Put the corrected sentence in the editor; nothing changes until you press Create">
              <Lightbulb size={13}/> <span>Did you mean <b>{m.suggestion.text}</b>?</span>
            </button>
            {m.suggestion.replaces && i === messages.length - 1 && canUndo && <button className="did-you-mean secondary" onClick={onUndo} title="Undo that step first, so the corrected sentence does not build things twice">
              <Undo2 size={13}/> <span>Undo that step</span>
            </button>}
          </div>}
          {m.kind === 'system' && m.logId && <FlagControl entry={entries[m.logId]} onFlag={onFlag} onUnflag={onUnflag}/>}
          {m.kind === 'user' && <button className="reuse" onClick={() => onReuse(m.text)} aria-label={`Edit again: ${m.text}`} title="Put this command back in the editor">
            <CornerDownLeft size={12}/> Edit again
          </button>}
        </div>
      </div>)}
      {busy && <div className="thinking"><span/><span/><span/> Thinking in pictures...</div>}
    </div>
  </>;
}

export function Inspiration({onPick}) {
  return <div className="suggestions">
    <span>NEED INSPIRATION?</span>
    <div className="example-list">
      {EXAMPLES.map((example, i) => <button key={example} onClick={() => onPick(example)}>
        <span>{EXAMPLE_ICONS[i]}</span>{example}<ChevronRight size={15}/>
      </button>)}
    </div>
  </div>;
}
