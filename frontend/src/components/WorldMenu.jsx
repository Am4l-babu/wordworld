import React, {useEffect, useRef, useState} from 'react';
import {Share2, ChevronDown, Link2, Download, Upload, ClipboardList} from 'lucide-react';

const ITEMS = [
  ['share', Link2, 'Copy share link', 'Anyone with the link sees this island'],
  ['export', Download, 'Download JSON', 'Save a file you can import later'],
  ['import', Upload, 'Import JSON', 'Open a saved WordWorld file'],
  ['testlog', ClipboardList, 'Test log', 'Helping test? Review and download what you typed'],
];

export default function WorldMenu({onShare, onExport, onImport, onTestLog}) {
  const [open, setOpen] = useState(false);
  const root = useRef(null), trigger = useRef(null);
  const actions = {share: onShare, export: onExport, import: onImport, testlog: onTestLog};
  useEffect(() => {
    if (!open) return;
    root.current?.querySelector('[role=menuitem]')?.focus();
    const outside = e => { if (!root.current?.contains(e.target)) setOpen(false); };
    document.addEventListener('pointerdown', outside);
    return () => document.removeEventListener('pointerdown', outside);
  }, [open]);
  function choose(key) {
    setOpen(false);
    trigger.current?.focus();
    actions[key]();
  }
  function onKeyDown(e) {
    if (!open) return;
    const items = [...root.current.querySelectorAll('[role=menuitem]')];
    const at = items.indexOf(document.activeElement);
    if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); setOpen(false); trigger.current?.focus(); }
    else if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault();
      items[(at + (e.key === 'ArrowDown' ? 1 : -1) + items.length) % items.length]?.focus();
    }
    else if (e.key === 'Tab') setOpen(false);
  }
  return <div className="world-menu" ref={root} onKeyDown={onKeyDown}>
    <button ref={trigger} className="export-button" aria-haspopup="menu" aria-expanded={open} aria-label="Share or save world" onClick={() => setOpen(o => !o)}>
      <Share2 size={17}/> <span>Share &amp; save</span><ChevronDown size={15} className={'menu-caret' + (open ? ' turn' : '')}/>
    </button>
    {open && <div className="menu-popover" role="menu" aria-label="Share or save world">
      {ITEMS.map(([key, Icon, label, hint]) => <button key={key} role="menuitem" onClick={() => choose(key)}>
        <Icon size={17}/><span><b>{label}</b><small>{hint}</small></span>
      </button>)}
    </div>}
  </div>;
}
