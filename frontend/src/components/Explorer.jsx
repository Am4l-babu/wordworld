import React, {useState} from 'react';
import {Layers3, Plus, Minus, Copy, Trash2, MousePointer2, RefreshCw} from 'lucide-react';
import {TYPES, TYPE_EMOJI, PALETTE, COLOR_PART, MAX_ITEMS, RELATION_LABEL} from '../world';

const typeLabel = type => type.replaceAll('_', ' ');

function ObjectList({items, selected, onSelectType}) {
  const groups = TYPES.map(type => ({type, list: items.filter(i => i.type === type)})).filter(g => g.list.length);
  return <div className="object-list">
    <div className="objects-summary"><span>OBJECT COLLECTION</span><span>{items.length} total</span></div>
    {groups.map(({type, list}) => {
      const at = list.findIndex(i => i.id === selected), count = list.length;
      return <div key={type} className="object-group">
        <button className={at >= 0 ? 'current' : ''} onClick={() => onSelectType(type)} title={count > 1 ? `Select the next ${type}` : `Select the ${type}`}>
          <span className="object-emoji">{TYPE_EMOJI[type]}</span>
          <span className="object-name">{typeLabel(type)}<small>{at >= 0 && count > 1 ? `${at + 1} of ${count} · click for next` : `${count} on canvas`}</small></span>
          <span className="group-count">{count}</span>
        </button>
      </div>;
    })}
    {groups.length === 0 && <p className="no-objects">This world is empty. Add your first object!</p>}
  </div>;
}

function QuickAdd({full, onAdd}) {
  return <div className="object-list">
    <div className="objects-summary"><span>QUICK ADD</span><span>{full ? 'ISLAND IS FULL' : 'CLICK TO CREATE'}</span></div>
    {TYPES.map(type => <div key={type} className="object-group">
      <button onClick={() => onAdd(type)} disabled={full}>
        <span className="object-emoji">{TYPE_EMOJI[type]}</span><span className="object-name">{typeLabel(type)}</span><Plus size={16}/>
      </button>
    </div>)}
  </div>;
}

function SelectionPanel({items, chosen, full, onDuplicate, onDelete, onRecolor, onResize}) {
  if (!chosen) return <div className="selection-panel">
    <div className="selection-label">SELECTED OBJECT</div>
    <div className="nothing-selected"><MousePointer2 size={21}/><span>Select any object on the canvas to inspect, recolor, move, or delete it.</span></div>
  </div>;
  const anchors = chosen.grounding?.anchorIds.map(id => items.find(o => o.id === id)?.type).filter(Boolean) || [];
  // Houses always draw a roof color (red by default); trees and flowers have a natural default.
  const current = chosen.color || (chosen.type === 'house' ? 'red' : undefined);
  return <div className="selection-panel">
    <div className="selection-label">SELECTED OBJECT</div>
    <div className="selected-details">
      <div className="selected-emoji">{TYPE_EMOJI[chosen.type]}</div>
      <div>
        <b>{chosen.color && COLOR_PART[chosen.type] ? `${chosen.color} ` : ''}{chosen.type}</b>
        <small>Position {Math.round(chosen.x)}, {Math.round(chosen.y)}</small>
        {anchors.length > 0 && <small>Placed {RELATION_LABEL[chosen.grounding.relation] || chosen.grounding.relation} {anchors.join(' & ')}</small>}
      </div>
    </div>
    <div className="selection-actions">
      <button onClick={onDuplicate} disabled={full}><Copy size={15}/> Duplicate</button>
      <button className="delete" onClick={onDelete} title="Delete (Del)"><Trash2 size={15}/> Delete</button>
    </div>
    <div className="size-control">
      <small>SIZE</small>
      <button onClick={() => onResize(0.8)} disabled={(chosen.scale || 1) <= 0.45} aria-label="Make smaller" title="Smaller (or say “make it smaller”)"><Minus size={15}/></button>
      <span>{Math.round((chosen.scale || 1) * 100)}%</span>
      <button onClick={() => onResize(1.25)} disabled={(chosen.scale || 1) >= 1.9} aria-label="Make bigger" title="Bigger (or say “make it bigger”)"><Plus size={15}/></button>
    </div>
    {COLOR_PART[chosen.type] && <div className="color-options">
      <small>{COLOR_PART[chosen.type].toUpperCase()}</small>
      <div>
        {chosen.type !== 'house' && <button title="default" aria-label="default" aria-pressed={!current} className={'default-swatch' + (!current ? ' picked' : '')} onClick={() => onRecolor(undefined)}/>}
        {Object.entries(PALETTE).map(([color, hex]) => <button key={color} title={color} aria-label={color} aria-pressed={current === color}
          style={{background: hex}} className={current === color ? 'picked' : ''} onClick={() => onRecolor(color)}/>)}
      </div>
    </div>}
  </div>;
}

function ApiStatus({state, onRetry}) {
  const text = {
    spacy: ['spaCy NLP connected', 'Tokenization · POS · Dependencies'],
    offline: ['Browser preview mode', 'Start the Python API for POS / dependency tags'],
    checking: ['Connecting to language engine…', 'Checking the Python API'],
  }[state] || ['Language engine ready', 'World commands · Spatial parsing'];
  return <div className="api-indicator">
    <span className={'api-dot ' + (state === 'offline' || state === 'checking' ? state : '')}/>
    <div><strong>{text[0]}</strong><small>{text[1]}</small></div>
    {state === 'offline' && <button className="api-retry" onClick={onRetry} aria-label="Retry connecting to the language engine" title="Retry"><RefreshCw size={14}/></button>}
  </div>;
}

export default function Explorer({items, selected, apiState, onRetryApi, onSelectType, onAdd, onDuplicate, onDelete, onRecolor, onResize}) {
  const [tab, setTab] = useState('objects');
  const full = items.length >= MAX_ITEMS;
  const chosen = items.find(o => o.id === selected);
  return <aside className="right-panel">
    <div className="right-header">
      <div className="right-heading"><Layers3 size={19}/><h3>World explorer</h3></div>
      <p>All the little things in your world.</p>
    </div>
    <div className="right-tabs" role="tablist">
      <button role="tab" aria-selected={tab === 'objects'} className={tab === 'objects' ? 'active' : ''} onClick={() => setTab('objects')}><Layers3 size={15}/> Objects</button>
      <button role="tab" aria-selected={tab === 'add'} className={tab === 'add' ? 'active' : ''} onClick={() => setTab('add')}><Plus size={15}/> Add new</button>
    </div>
    {tab === 'objects'
      ? <ObjectList items={items} selected={selected} onSelectType={onSelectType}/>
      : <QuickAdd full={full} onAdd={onAdd}/>}
    <SelectionPanel items={items} chosen={chosen} full={full} onDuplicate={onDuplicate} onDelete={onDelete} onRecolor={onRecolor} onResize={onResize}/>
    <div className="tip-card"><span className="tip-icon">💡</span><strong>Little tip!</strong><p>Try describing where things should go: <em>“Add a tree to the left of the house.”</em> Then change it: <em>“make it purple.”</em></p></div>
    <ApiStatus state={apiState} onRetry={onRetryApi}/>
  </aside>;
}
