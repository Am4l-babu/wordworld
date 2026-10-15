import React from 'react';
import {X, ArrowUpRight} from 'lucide-react';
import Dialog from './Dialog';

const SHORTCUTS = [
  [['/'], 'Focus the command box'],
  [['↑', '↓'], 'Recall earlier commands (empty box)'],
  [['Ctrl', 'Z'], <>Undo · add <kbd>Shift</kbd> to redo</>],
  [['Del'], 'Delete the selected object'],
  [['Arrows'], <>Move the selected object (<kbd>Shift</kbd> = faster)</>],
  [['Ctrl', 'Scroll'], 'Zoom the island; drag empty space to pan'],
  [['Esc'], 'Deselect or close this dialog'],
];

export default function HelpDialog({onClose}) {
  return <Dialog labelledBy="help-title" onClose={onClose} className="help-modal">
    <button aria-label="Close help" className="close-help" onClick={onClose} data-autofocus><X/></button>
    <div className="help-spark">✨</div>
    <h2 id="help-title">How WordWorld works</h2>
    <p>Describe a place in everyday English. Our NLP parser identifies objects, quantity, color, and spatial relationships before rendering the scene.</p>
    <div className="help-steps">
      <div><b>01 · Dream</b><span>“Place two red cottages next to the lake.”</span></div>
      <div><b>02 · Understand</b><span>Entity: house · Count: 2 · Color: red · Relation: near lake</span></div>
      <div><b>03 · Explore</b><span>Click and drag to move objects. Use the explorer to modify or delete them.</span></div>
    </div>
    <div className="shortcuts">
      <b>Keyboard shortcuts</b>
      <dl>
        {SHORTCUTS.map(([keys, text]) => <div key={keys.join('+')}>
          <dt>{keys.map((key, i) => <React.Fragment key={key}>{i > 0 && (keys[0] === 'Ctrl' ? '+' : ' ')}<kbd>{key}</kbd></React.Fragment>)}</dt>
          <dd>{text}</dd>
        </div>)}
      </dl>
    </div>
    <p className="help-fine">Supported objects: houses, trees, lakes, rivers, bridges, roads, flowers, mountains, towers, castles, rocks. Colors: red, blue, yellow, pink, purple, green, orange, white. Set day, night, rain, or snow. This MVP uses explicit language patterns for spatial grounding and spaCy for linguistic annotation; it does not understand arbitrary free-form descriptions.</p>
    <button className="help-cta" onClick={onClose}>Let's create something <ArrowUpRight size={16}/></button>
  </Dialog>;
}
