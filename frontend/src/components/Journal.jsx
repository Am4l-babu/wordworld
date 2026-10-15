import React, {useEffect, useRef} from 'react';
import {Sparkles, WandSparkles, RotateCcw, Check, CornerDownLeft, ChevronRight} from 'lucide-react';
import {EXAMPLES} from '../world';

const EXAMPLE_ICONS = ['🏡', '🌲', '🏰', '🌉', '🌙', '🌷'];

function Avatar({kind}) {
  if (kind === 'system') return <div className="bot-avatar"><Sparkles size={16}/></div>;
  if (kind === 'welcome') return <div className="greeting-icon"><WandSparkles size={23} strokeWidth={2.5}/></div>;
  return <div className="user-avatar">YOU</div>;
}

export function Journal({messages, busy, onReset, onReuse}) {
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
          {m.text}
          {m.kind === 'system' && m.actionCount > 0 && <span className="applied"><Check size={12}/> Applied to world</span>}
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
