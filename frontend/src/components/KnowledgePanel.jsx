import React from 'react';
import {TextCursorInput, ChevronRight} from 'lucide-react';
import Analysis from '../Analysis';

const STEPS = ['YOUR WORDS', 'ENTITY EXTRACTION', 'SPATIAL GROUNDING', 'YOUR WORLD ✨'];

export default function KnowledgePanel({parsed, open, onToggle}) {
  return <div className="knowledge-panel">
    <div className="knowledge-top">
      <div className="knowledge-icon"><TextCursorInput size={18}/></div>
      <div><strong>The language behind the magic</strong><p>Every creation begins with natural language understanding.</p></div>
      <button onClick={onToggle} className="knowledge-toggle" aria-expanded={open}>
        {open ? 'Hide details' : 'Show details'} <ChevronRight size={14} className={open ? 'turn' : ''}/>
      </button>
    </div>
    {open && <div className="knowledge-content">
      <div className="pipeline">
        {STEPS.map((step, i) => <React.Fragment key={step}>{i > 0 && <ChevronRight size={16}/>}<span>{step}</span></React.Fragment>)}
      </div>
      {parsed
        ? <Analysis key={parsed.text} parsed={parsed}/>
        : <p className="waiting-analysis">Give the world a new instruction to inspect its words, grammar tags, entities, and extracted scene actions.</p>}
    </div>}
  </div>;
}
