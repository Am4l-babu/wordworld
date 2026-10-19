import React, {useEffect, useRef, useState} from 'react';
import {Check, Sparkles} from 'lucide-react';
import Topbar from './components/Topbar';
import Composer from './components/Composer';
import {Journal, Inspiration} from './components/Journal';
import {WorldTitle, WorldStage} from './components/WorldStage';
import WorldControls from './components/WorldControls';
import KnowledgePanel from './components/KnowledgePanel';
import Explorer from './components/Explorer';
import HelpDialog from './components/HelpDialog';
import ShareDialog from './components/ShareDialog';
import TestLogDialog from './components/TestLogDialog';
import {fallbackParser} from './previewParser';
import {MAX_ITEMS, initialItems, INITIAL_SETTINGS, snapshot, makeItem, applyActions, cleanScene, focusGroups, describeFocus, pruneGuides} from './world';
import {KEYS, writeJSON, getSaved, getRecent, getSharedCommand, getTestLog} from './storage';
import {newEntry, addEntry, flagEntry, unflagEntry, acceptSuggestion, exportPayload, exportFilename} from './testlog';
import {downloadJSON} from './download';
import {readSharedWorld, clearSharedWorldParam, shareUrl} from './share';
import {DEFAULT_VIEW, clampView, zoomAt, isVisible} from './view';
import {useTheme} from './theme';

const intro = {text: 'Welcome to your little corner of imagination. Tell me what to create!', kind: 'welcome'};
const COMPACT_QUERY = '(max-width:735px), (max-width:950px) and (max-height:500px)';
const FULL_MESSAGE = `The island is full (${MAX_ITEMS} objects). Remove something first.`;
const article = word => /^[aeiou]/.test(word) ? 'an' : 'a';

// A ?world= link replaces the island, but the person's own saved island stays one undo away.
function boot() {
  const saved = getSaved(), shared = readSharedWorld();
  return shared ? {scene: shared, previous: saved} : {scene: saved, previous: null};
}

// FastAPI sends a string for errors we raise and a list of {msg} objects for request validation.
function apiErrorMessage(detail) {
  if (typeof detail === 'string') return detail;
  const first = Array.isArray(detail) ? detail[0]?.msg : null;
  return first ? `The API could not read that command (${first}). Please shorten or rephrase it.` : 'The API rejected this instruction. Please shorten or rephrase it.';
}

function useCompactLayout() {
  const [isCompact, setCompact] = useState(() => window.matchMedia(COMPACT_QUERY).matches);
  useEffect(() => {
    const media = window.matchMedia(COMPACT_QUERY), update = () => setCompact(media.matches);
    media.addEventListener('change', update);
    return () => media.removeEventListener('change', update);
  }, []);
  return isCompact;
}

function App() {
  const [start] = useState(boot);
  const isCompact = useCompactLayout();
  const {theme, toggle: toggleTheme} = useTheme();
  const [items, setItems] = useState(start.scene.items), [settings, setSettings] = useState(start.scene.settings);
  // `focus` is what 'it'/'them' mean in the next command: the objects the last command or click touched.
  const [focus, setFocus] = useState([]);
  const [selected, setSelected] = useState(null), [view, setView] = useState(DEFAULT_VIEW), [showGuides, setShowGuides] = useState(true);
  const [prompt, setPrompt] = useState(getSharedCommand), [busy, setBusy] = useState(false);
  const [messages, setMessages] = useState([intro]), [parsed, setParsed] = useState(null), [recent, setRecent] = useState(getRecent);
  const [history, setHistory] = useState(() => start.previous ? [snapshot(start.previous.items, start.previous.settings)] : []);
  const [future, setFuture] = useState([]);
  const [analysisOpen, setAnalysisOpen] = useState(true), [apiState, setApiState] = useState('checking');
  const [dialog, setDialog] = useState(null), [toast, setToast] = useState(null);
  // Everything typed and what the parser did, kept only in this browser until it is downloaded (see testlog.js).
  const [testLog, setTestLog] = useState(getTestLog);
  const inputRef = useRef(null), toastTimer = useRef(null), fileRef = useRef(null);
  // Handlers that run after an await must read the latest scene, not the one captured at call time.
  const live = useRef({items, settings});
  live.current = {items, settings};
  const busyRef = useRef(false), recall = useRef(null);

  useEffect(() => writeJSON(KEYS.scene, {items, settings}), [items, settings]);
  useEffect(() => writeJSON(KEYS.recent, recent), [recent]);
  useEffect(() => writeJSON(KEYS.testlog, testLog), [testLog]);
  useEffect(checkHealth, []);
  useEffect(() => {
    if (!start.previous) return;
    clearSharedWorldParam();
    notify('Opened a shared island. Your own island is one undo away.', true);
  }, []);

  function checkHealth() {
    setApiState('checking');
    fetch('/api/health')
      .then(r => { if (!r.ok) throw Error(); return r.json(); })
      .then(x => setApiState(x.parser))
      .catch(() => setApiState('offline'));
  }
  function notify(text, undoable = false) {
    setToast({text, undoable});
    clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(null), undoable ? 6000 : 3300);
  }

  // History
  function remember() {
    const {items, settings} = live.current;
    setHistory(h => [...h.slice(-29), snapshot(items, settings)]);
    setFuture([]);
  }
  function restore(state) {
    setItems(state.items);
    setSettings(state.settings);
    setSelected(null);
  }
  function undo() {
    if (!history.length) return;
    const {items, settings} = live.current;
    setFuture(x => [...x, snapshot(items, settings)]);
    setHistory(h => h.slice(0, -1));
    restore(history.at(-1));
  }
  function redo() {
    if (!future.length) return;
    const {items, settings} = live.current;
    setHistory(x => [...x, snapshot(items, settings)]);
    setFuture(x => x.slice(0, -1));
    restore(future.at(-1));
  }

  // Language commands
  async function submit(text = prompt) {
    const cmd = text.trim();
    if (!cmd || busyRef.current) return;
    const context = focusGroups(live.current.items, focus);
    busyRef.current = true;
    setBusy(true);
    setPrompt('');
    recall.current = null;
    setRecent(r => [...r.filter(x => x !== cmd), cmd].slice(-20));
    setMessages(v => [...v.slice(-59), {text: cmd, kind: 'user'}]);
    let result;
    try {
      const response = await fetch('/api/parse', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({text: cmd, context: context.map(g => ({type: g.type, count: g.ids.length}))}), signal: AbortSignal.timeout?.(10000)});
      const data = await response.json();
      result = response.ok ? data : {text: cmd, actions: [], tokens: [], highlights: [], warnings: [], model: apiState, rejected: true,
        message: apiErrorMessage(data.detail)};
      if (response.ok) setApiState(result.model);
    } catch {
      result = fallbackParser(cmd);
      setApiState('offline');
    }
    // The person may have dragged, deleted or added objects while the request was pending.
    const {items: current, settings: currentSettings} = live.current;
    setParsed(result);
    if (result.actions?.length) {
      remember();
      const output = applyActions(current, currentSettings, result.actions, result.bindings, context);
      setItems(output.items);
      setSettings(output.settings);
      setSelected(output.touched.at(-1) ?? null);
      if (output.touched.length) setFocus(output.touched);
      const notices = [...(result.warnings || []), ...output.notices,
        ...(output.missing.length ? [`Couldn't find ${output.missing.join(', ')}; used available space instead.`] : [])];
      setParsed({...result, warnings: notices});
      const actionText = output.descriptions.join(' · ') + (notices.length ? `. ${notices.join(' ')}` : '');
      // Log first: a state updater may run twice, and must stay free of side effects.
      const logId = record(cmd, {...result, message: actionText}, context);
      setMessages(v => [...v, {text: actionText, kind: 'system', actionCount: result.actions.length, suggestion: result.suggestions?.[0], logId}]);
    } else {
      const text = [result.message || 'Try a different world-building command.', ...(result.warnings || [])].join(' ');
      const logId = record(cmd, {...result, message: text}, context);
      setMessages(v => [...v, {text, kind: 'system', actionCount: 0, suggestion: result.suggestions?.[0], logId}]);
    }
    busyRef.current = false;
    setBusy(false);
  }
  function record(text, result, context) {
    const entry = newEntry({text, result, context: context.map(g => ({type: g.type, count: g.ids.length})), device: isCompact ? 'phone' : 'desktop'});
    setTestLog(log => addEntry(log, entry));
    return entry.id;
  }
  function downloadTestLog() {
    downloadJSON(exportFilename(), exportPayload(testLog));
    notify('Test log downloaded');
  }
  function reuse(text) {
    setPrompt(text);
    recall.current = null;
    inputRef.current?.focus();
  }
  function composerKey(e) {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey || !e.shiftKey && !isCompact)) {
      e.preventDefault();
      submit();
      return;
    }
    const el = e.currentTarget, collapsed = el.selectionStart === el.selectionEnd;
    // Shell-style recall: ↑ on an empty box (or while browsing) walks back through sent commands.
    if (e.key === 'ArrowUp' && recent.length && collapsed && (!prompt || recall.current !== null) && !el.value.slice(0, el.selectionStart).includes('\n')) {
      e.preventDefault();
      const i = recall.current === null ? recent.length - 1 : Math.max(0, recall.current - 1);
      recall.current = i;
      setPrompt(recent[i]);
    } else if (e.key === 'ArrowDown' && recall.current !== null && collapsed && !el.value.slice(el.selectionEnd).includes('\n')) {
      e.preventDefault();
      const i = recall.current + 1;
      recall.current = i >= recent.length ? null : i;
      setPrompt(i >= recent.length ? '' : recent[i]);
    }
  }

  // Direct manipulation
  function addDirect(type) {
    const {items, settings} = live.current;
    if (items.length >= MAX_ITEMS) return notify(FULL_MESSAGE);
    remember();
    const result = applyActions(items, settings, [{action: 'add', type, count: 1}]);
    setItems(result.items);
    select(result.items.at(-1)?.id);
    notify(`Added ${article(type)} ${type}`);
  }
  function deleteSelected() {
    if (!selected) return;
    remember();
    setItems(v => pruneGuides(v.filter(it => it.id !== selected)));
    setSelected(null);
    notify('Object removed', true);
  }
  function duplicateSelected() {
    const obj = items.find(it => it.id === selected);
    if (!obj) return;
    if (items.length >= MAX_ITEMS) return notify(FULL_MESSAGE);
    remember();
    const copy = makeItem(obj.type, Math.min(obj.x + 48, 880), Math.min(obj.y + 34, 500), obj.color, obj.scale);
    setItems(v => [...v, copy]);
    select(copy.id);
    notify('Object duplicated');
  }
  // Clicking an object makes it what 'it' refers to next.
  function select(id) {
    setSelected(id);
    if (id) setFocus([id]);
  }
  function recolor(color) {
    remember();
    setItems(v => v.map(o => o.id === selected ? {...o, color} : o));
  }
  // Same limits as the language edit "make it bigger/smaller".
  function resize(factor) {
    remember();
    setItems(v => v.map(o => o.id === selected ? {...o, scale: Math.round(Math.min(1.9, Math.max(0.45, (o.scale || 1) * factor)) * 100) / 100} : o));
  }
  function moveItem(id, x, y) {
    setItems(v => v.map(it => it.id === id ? {...it, x, y, grounding: undefined} : it));
  }
  function setSetting(key, value) {
    if (settings[key] === value) return;
    remember();
    setSettings(s => ({...s, [key]: value}));
  }
  function reset() {
    if (!items.length && settings.time === INITIAL_SETTINGS.time && settings.weather === INITIAL_SETTINGS.weather) return;
    remember();
    restore({items: [], settings: {...INITIAL_SETTINGS}});
    notify('World cleared', true);
  }
  function loadExample() {
    remember();
    restore({items: initialItems(), settings: {...INITIAL_SETTINGS}});
    notify('Starter village restored', true);
  }
  // Each click on a type selects its next object, panning to it when zoomed in.
  function selectType(type) {
    const list = items.filter(i => i.type === type);
    if (!list.length) return;
    const next = list[(list.findIndex(i => i.id === selected) + 1) % list.length];
    select(next.id);
    if (!isVisible(view, next)) setView(v => clampView({...v, x: next.x, y: next.y}));
  }

  // Files and links
  function exportJSON() {
    downloadJSON(`wordworld-${new Date().toISOString().slice(0, 10)}.json`, {name: 'My WordWorld', items, settings, exportedAt: new Date().toISOString()});
    notify('Scene exported as JSON');
  }
  async function importJSON(e) {
    const file = e.target.files?.[0];
    e.target.value = '';
    if (!file) return;
    try {
      if (file.size > 2_000_000) throw Error('too large');
      const scene = cleanScene(JSON.parse(await file.text()));
      if (!scene) throw Error('not a scene');
      remember();
      restore(scene);
      notify(`Imported ${scene.items.length} object${scene.items.length === 1 ? '' : 's'}`, true);
    } catch {
      notify('That file is not a WordWorld scene export.');
    }
  }

  // Global shortcuts; re-subscribed every render so they always see the current scene and history.
  useEffect(() => {
    function onKey(e) {
      if (dialog) return;
      const target = e.target, mod = e.ctrlKey || e.metaKey, key = e.key.toLowerCase();
      if (target.tagName === 'TEXTAREA' || target.tagName === 'INPUT' || target.isContentEditable) return;
      if (mod && key === 'z') { e.preventDefault(); e.shiftKey ? redo() : undo(); }
      else if (mod && key === 'y') { e.preventDefault(); redo(); }
      else if ((e.key === 'Delete' || e.key === 'Backspace') && selected && (target === document.body || target.closest?.('.world-svg'))) { e.preventDefault(); deleteSelected(); }
      else if (e.key === 'Escape' && selected) setSelected(null);
      else if (e.key === '/' && !mod) { e.preventDefault(); inputRef.current?.focus(); }
    }
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  });

  const chosen = items.find(o => o.id === selected);
  const focusLabel = describeFocus(focusGroups(items, focus));
  const composer = <Composer inputRef={inputRef} value={prompt} busy={busy} isCompact={isCompact} canRecall={recent.length > 0} focusLabel={focusLabel}
    onChange={value => { recall.current = null; setPrompt(value); }} onKeyDown={composerKey} onSubmit={() => submit()}/>;

  return <div className="app-shell">
    <Topbar theme={theme} onToggleTheme={toggleTheme} onHelp={() => setDialog('help')}
      onShare={() => setDialog('share')} onExport={exportJSON} onImport={() => fileRef.current?.click()} onTestLog={() => setDialog('testlog')}/>
    <input ref={fileRef} type="file" accept="application/json,.json" hidden onChange={importJSON}/>
    <div className="workspace">
      <aside className="left-panel">
        <section className="intro-section">
          <div className="eyebrow"><Sparkles size={14}/> WELCOME TO YOUR CANVAS</div>
          <h1>Dream it.<br/><span>Build it.</span></h1>
          <p>Turn simple sentences into a little world that's entirely yours.</p>
        </section>
        <Journal messages={messages} busy={busy} onReset={reset} onReuse={reuse} onUndo={undo} canUndo={history.length > 0}
          entries={Object.fromEntries(testLog.map(e => [e.id, e]))} onFlag={(id, note) => setTestLog(l => flagEntry(l, id, note))} onUnflag={id => setTestLog(l => unflagEntry(l, id))}
          onAccept={id => setTestLog(l => acceptSuggestion(l, id))}/>
        {!isCompact && composer}
        <Inspiration onPick={reuse}/>
      </aside>
      <main className="main-panel">
        <WorldTitle count={items.length}/>
        {isCompact && composer}
        <WorldStage items={items} settings={settings} selected={selected} onSelect={select} onMove={moveItem} onDragBegin={remember}
          view={view} onView={setView} onZoom={step => setView(v => zoomAt(v, v.zoom + step))} onResetView={() => setView(DEFAULT_VIEW)}
          showGuides={showGuides} onTrySentence={() => reuse('Build three houses and plant five trees')} onRestore={loadExample}/>
        <WorldControls settings={settings} canUndo={history.length > 0} canRedo={future.length > 0} onUndo={undo} onRedo={redo}
          onRestore={loadExample} onSetting={setSetting} hasGuide={Boolean(chosen?.grounding)} showGuides={showGuides} onToggleGuides={() => setShowGuides(v => !v)}/>
        <KnowledgePanel parsed={parsed} open={analysisOpen} onToggle={() => setAnalysisOpen(v => !v)}/>
      </main>
      <Explorer items={items} selected={selected} apiState={apiState} onRetryApi={checkHealth} onSelectType={selectType} onAdd={addDirect}
        onDuplicate={duplicateSelected} onDelete={deleteSelected} onRecolor={recolor} onResize={resize}/>
    </div>
    <div className="toast-region" aria-live="polite">
      {toast && <div className="toast" role="status">
        <Check size={17}/>{toast.text}
        {toast.undoable && <button className="toast-undo" onClick={() => { undo(); setToast(null); }} aria-label="Undo last change">Undo</button>}
      </div>}
    </div>
    {dialog === 'help' && <HelpDialog onClose={() => setDialog(null)}/>}
    {dialog === 'testlog' && <TestLogDialog entries={testLog} onDownload={downloadTestLog} onClear={() => { setTestLog([]); notify('Test log cleared'); }} onClose={() => setDialog(null)}/>}
    {dialog === 'share' && <ShareDialog url={shareUrl(items, settings)} count={items.length} onClose={() => setDialog(null)}/>}
  </div>;
}

export default App;
