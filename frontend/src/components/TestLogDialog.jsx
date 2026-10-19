import React from 'react';
import {X, Download, Trash2, ClipboardList} from 'lucide-react';
import Dialog from './Dialog';
import {summarize} from '../testlog';

export default function TestLogDialog({entries, onDownload, onClear, onClose}) {
  const s = summarize(entries);
  return <Dialog labelledBy="testlog-title" onClose={onClose} className="help-modal testlog-modal">
    <button aria-label="Close test log" className="close-help" onClick={onClose}><X/></button>
    <div className="help-spark"><ClipboardList size={30}/></div>
    <h2 id="testlog-title">Test log</h2>
    <p>Helping test WordWorld? While you play, this browser keeps a private list of what you typed and what the language engine did with it, plus any
      replies you mark <b>Not what I meant</b>. <b>Nothing is sent anywhere</b>: it stays on this device until you download it and send the file to whoever asked.
      It never includes your island, only the sentences.</p>
    <dl className="testlog-stats">
      <div><dt>Commands</dt><dd>{s.commands}</dd></div>
      <div><dt>Changed the world</dt><dd>{s.applied}</dd></div>
      <div><dt>Understood as nothing</dt><dd>{s.nothing + s.rejected}</dd></div>
      <div><dt>Marked “not what I meant”</dt><dd>{s.flagged}</dd></div>
      <div><dt>“Did you mean” shown / used</dt><dd>{s.suggestionsShown} / {s.suggestionsAccepted}</dd></div>
    </dl>
    {s.preview > 0 && <p className="help-fine">{s.preview} command{s.preview === 1 ? ' was' : 's were'} answered by the offline preview, not the full language engine.</p>}
    <div className="testlog-actions">
      <button className="help-cta" onClick={onDownload} disabled={!s.commands} data-autofocus><Download size={16}/> Download my test log</button>
      <button className="testlog-clear" onClick={onClear} disabled={!s.commands}><Trash2 size={15}/> Clear it</button>
    </div>
  </Dialog>;
}
