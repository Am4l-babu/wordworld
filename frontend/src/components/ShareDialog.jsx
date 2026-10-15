import React, {useEffect, useRef, useState} from 'react';
import {X, Copy, Link2} from 'lucide-react';
import Dialog from './Dialog';

export default function ShareDialog({url, count, onClose}) {
  const [status, setStatus] = useState('');
  const input = useRef(null);
  async function copy() {
    try {
      await navigator.clipboard.writeText(url);
      setStatus('Link copied to your clipboard.');
    } catch {
      input.current?.select();
      setStatus('Press Ctrl+C (⌘C on Mac) to copy the selected link.');
    }
  }
  // The menu click that opened this dialog still counts as a user gesture for the clipboard.
  useEffect(() => { copy(); }, []);
  return <Dialog labelledBy="share-title" onClose={onClose} className="help-modal share-modal">
    <button aria-label="Close share dialog" className="close-help" onClick={onClose}><X/></button>
    <div className="help-spark"><Link2 size={30}/></div>
    <h2 id="share-title">Share this island</h2>
    <p>The link holds the whole world ({count} object{count === 1 ? '' : 's'}, time of day and weather). Nothing is uploaded; opening it loads a copy in the other person's browser.</p>
    <div className="share-row">
      <label htmlFor="share-link" className="visually-hidden">Share link</label>
      <input id="share-link" ref={input} readOnly value={url} onFocus={e => e.target.select()} data-autofocus/>
      <button className="help-cta" onClick={copy}><Copy size={16}/> Copy link</button>
    </div>
    <p className="share-status" role="status">{status}</p>
    {url.length > 8000 && <p className="help-fine">This is a long link. Some chat apps shorten long links; download a JSON file instead if it doesn't open.</p>}
  </Dialog>;
}
