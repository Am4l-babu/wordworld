import React,{useEffect,useState,useRef} from 'react';
import {WandSparkles, Sparkles, Layers3, BookOpen, Download, Undo2, Redo2, Send, SlidersHorizontal, Plus, Minus, Sun, Moon, CloudRain, Snowflake, Trash2, Copy, MousePointer2, Map, ChevronRight, CircleHelp, RotateCcw, Code2, Check, X, ArrowUpRight, CloudSun, Github, Play, Bot, TextCursorInput} from 'lucide-react';
import Scene from './Scene';
import Analysis from './Analysis';
import {fallbackParser} from './previewParser';
import {TYPES,TYPE_EMOJI,EXAMPLES,initialItems,INITIAL_SETTINGS,snapshot,makeItem,applyActions} from './world';

const STORAGE='wordworld-scene-v1';
const intro={text:'Welcome to your little corner of imagination. Tell me what to create!',kind:'welcome'};
function getSaved(){try{let obj=JSON.parse(localStorage.getItem(STORAGE));if(Array.isArray(obj.items)&&obj.settings)return obj}catch{}return {items:initialItems(),settings:{...INITIAL_SETTINGS}}}
const typeLabel=(t)=>t.replaceAll('_',' ');
const verbs=['Build','Place','Add','Create','Plant','Remove','Draw','Make'];
function IntroIllustration(){return <div className="greeting-icon"><WandSparkles size={23} strokeWidth={2.5}/></div>}
function App(){
 const [saved] = useState(getSaved);
 const [items,setItems]=useState(saved.items),[settings,setSettings]=useState(saved.settings);
 const [selected,setSelected]=useState(null),[zoom,setZoom]=useState(1),[showGuides,setShowGuides]=useState(true);
 const [prompt,setPrompt]=useState(''),[busy,setBusy]=useState(false);
 const [messages,setMessages]=useState([intro]),[parsed,setParsed]=useState(null);
 const [history,setHistory]=useState([]),[future,setFuture]=useState([]);
 const [activeTab,setActiveTab]=useState('objects'),[analysisOpen,setAnalysisOpen]=useState(true);
 const [apiState,setApiState]=useState('checking'),[showHelp,setShowHelp]=useState(false),[toast,setToast]=useState('');
 const inputRef=useRef(null),toastTimer=useRef(null);
 useEffect(()=>{localStorage.setItem(STORAGE,JSON.stringify({items,settings}))},[items,settings]);
 useEffect(()=>{fetch('/api/health').then(r=>{if(!r.ok)throw Error();return r.json()}).then(x=>setApiState(x.parser)).catch(()=>setApiState('offline'))},[]);
 function notify(m){setToast(m);clearTimeout(toastTimer.current);toastTimer.current=setTimeout(()=>setToast(''),3300)}
 function remember(){setHistory(h=>[...h.slice(-29),snapshot(items,settings)]);setFuture([])}
 function undo(){if(!history.length)return;setFuture(x=>[...x,snapshot(items,settings)]);const previous=history.at(-1);setHistory(h=>h.slice(0,-1));setItems(previous.items);setSettings(previous.settings);setSelected(null)}
 function redo(){if(!future.length)return;setHistory(x=>[...x,snapshot(items,settings)]);const next=future.at(-1);setFuture(x=>x.slice(0,-1));setItems(next.items);setSettings(next.settings);setSelected(null)}
 async function submit(text=prompt){const cmd=text.trim();if(!cmd||busy)return;setBusy(true);setPrompt('');setMessages(v=>[...v,{text:cmd,kind:'user'}]);
  let result;
  try{
   const response=await fetch('/api/parse',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:cmd}),signal:AbortSignal.timeout(10000)});
   const data=await response.json();
   result=response.ok?data:{text:cmd,actions:[],tokens:[],highlights:[],warnings:[],message:typeof data.detail==='string'?data.detail:'The API rejected this instruction. Please shorten or rephrase it.',model:apiState};
   if(response.ok)setApiState(result.model);
  }catch{result=fallbackParser(cmd);setApiState('offline')}
  setParsed(result);
  if(result.actions?.length){remember();const output=applyActions(items,settings,result.actions,result.bindings);setItems(output.items);setSettings(output.settings);setSelected(result.actions.some(a=>a.action==='add')?output.items.at(-1)?.id:null);
    const notices=[...(result.warnings||[]),...output.notices,...(output.missing.length?[`Couldn't find ${output.missing.join(', ')}; used available space instead.`]:[])];
    setParsed({...result,warnings:notices});
    const actionText=output.descriptions.join(' · ')+(notices.length?`. ${notices.join(' ')}`:'');
    setMessages(v=>[...v,{text:actionText,kind:'system',actionCount:result.actions.length}]);
  }else setMessages(v=>[...v,{text:[result.message||'Try a different world-building command.',...(result.warnings||[])].join(' '),kind:'system',actionCount:0}]);
  setBusy(false);
 }
 function addDirect(type){remember();let action={action:'add',type,count:1};let result=applyActions(items,settings,[action]);setItems(result.items);setSelected(result.items.at(-1)?.id);notify(`Added a ${type}`)}
 function deleteSelected(){if(!selected)return;remember();setItems(v=>v.filter(it=>it.id!==selected));setSelected(null);notify('Object removed')}
 function duplicateSelected(){let obj=items.find(it=>it.id===selected);if(!obj)return;remember();let newObj=makeItem(obj.type,Math.min(obj.x+48,880),Math.min(obj.y+34,500),obj.color,obj.scale);setItems(v=>[...v,newObj]);setSelected(newObj.id);notify('Object duplicated')}
 function setSetting(key,value){remember();setSettings(s=>({...s,[key]:value}))}
 function reset(){remember();setItems([]);setSettings({...INITIAL_SETTINGS});setSelected(null);notify('Ready for a fresh new world')}
 function loadExample(){remember();setItems(initialItems());setSettings({...INITIAL_SETTINGS});setSelected(null);notify('Starter village restored')}
 function exportJSON(){let blob=new Blob([JSON.stringify({name:'My WordWorld',items,settings,exportedAt:new Date().toISOString()},null,2)],{type:'application/json'});let url=URL.createObjectURL(blob);let a=document.createElement('a');a.href=url;a.download='wordworld-scene.json';a.click();URL.revokeObjectURL(url);notify('Scene exported as JSON')}
 const chosen=items.find(o=>o.id===selected);
 const counts=TYPES.map(type=>({type,count:items.filter(i=>i.type===type).length})).filter(c=>c.count);
 return <div className="app-shell">
 <header className="topbar">
  <div className="brand"><div className="brand-icon"><Layers3 size={24} fill="rgba(255,255,255,.15)"/></div><div className="brand-name">word<span>world</span><i>.</i></div><div className="brand-tag">beta</div></div>
  <div className="top-center"><span className="status-dot"/> Your imagination, visualized <span className="top-starfish">✳</span></div>
  <div className="top-actions"><div className="autosaved"><Check size={13}/> Auto-saved</div><button className="top-help" onClick={()=>setShowHelp(true)}><CircleHelp size={17}/> <span>How it works</span></button><button className="export-button" onClick={exportJSON}><Download size={17}/> <span>Export world</span></button></div>
 </header>
 <div className="workspace">
 <aside className="left-panel">
  <section className="intro-section"><div className="eyebrow"><Sparkles size={14}/> WELCOME TO YOUR CANVAS</div><h1>Dream it.<br/><span>Build it.</span></h1><p>Turn simple sentences into a little world that's entirely yours.</p></section>
  <div className="chat-heading"><div><span className="small-dot purple"/> Creation journal</div><button title="Start a fresh world" onClick={reset}><RotateCcw size={16}/></button></div>
  <div className="chat-history">
    {messages.map((m,i)=><div className={'chat-row '+m.kind} key={i}>{m.kind==='system'?<div className="bot-avatar"><Sparkles size={16}/></div>:m.kind==='welcome'?<IntroIllustration/>:<div className="user-avatar">YOU</div>}<div className="chat-bubble">{m.text}{m.kind==='system'&&m.actionCount>0&&<span className="applied"><Check size={12}/> Applied to world</span>}</div></div>)}
    {busy&&<div className="thinking"><span/><span/><span/> Thinking in pictures...</div>}
  </div>
  <div className="composer"><label htmlFor="world-command" className="composer-label"><WandSparkles size={15}/> Describe your imagination</label><textarea id="world-command" ref={inputRef} rows={3} maxLength={1400} value={prompt} onChange={e=>setPrompt(e.target.value)} onKeyDown={e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();submit()}}} placeholder="A cozy village with three houses and a little lake..."/><div className="composer-footer"><span>↵ to create · ⇧↵ for a new line</span><button onClick={()=>submit()} disabled={!prompt.trim()||busy} title="Generate objects"><WandSparkles size={17}/></button></div></div>
  <div className="suggestions"><span>NEED INSPIRATION?</span><div className="example-list">{EXAMPLES.map((example,i)=><button key={i} onClick={()=>{setPrompt(example);inputRef.current?.focus()}}><span>{['🏡','🌲','🏰','🌉','🌙','🌷'][i]}</span>{example}<ChevronRight size={15}/></button>)}</div></div>
 </aside>
 <main className="main-panel">
  <div className="world-title"><div><div className="section-overline">YOUR LITTLE UNIVERSE <span className="overline-sparkle">✦</span></div><div className="title-line"><h2>The Dreamscape</h2><span className="live-pill"><span/> LIVE WORLD</span></div><p>A tiny world with endless possibilities. Every word changes something.</p></div><div className="world-count"><span className="count-value">{items.length}</span><span className="count-label">objects created</span></div></div>
  <div className="world-frame">
    <div className="world-badge"><span>✦</span> ISLAND NO. 001 <span className="separator">/</span> {settings.time==='night'?'MOONLIT':'DAYLIGHT'} DREAM</div>
    <Scene items={items} settings={settings} selected={selected} onSelect={setSelected} onMove={(id,x,y)=>setItems(v=>v.map(it=>it.id===id?{...it,x,y,grounding:undefined}:it))} onDragBegin={remember} zoom={zoom} showGuides={showGuides}/>
    <div className="world-hint"><MousePointer2 size={14}/> Select · Drag or use arrow keys</div>
    <div className="zoom-controls"><button title="Zoom out" onClick={()=>setZoom(z=>Math.max(.7,Math.round((z-.1)*10)/10))}><Minus size={17}/></button><span>{Math.round(zoom*100)}%</span><button title="Zoom in" onClick={()=>setZoom(z=>Math.min(1.5,Math.round((z+.1)*10)/10))}><Plus size={17}/></button></div>
    {items.length===0&&<div className="empty-world"><div>✨</div><strong>Your story starts here</strong><span>Try “Build a village next to a lake”</span></div>}
  </div>
  <div className="below-world"><div className="world-controls"><div className="controls-group"><span className="controls-label">WORLD CONTROLS</span><div className="icon-group"><button onClick={undo} disabled={!history.length} title="Undo"><Undo2 size={17}/></button><button onClick={redo} disabled={!future.length} title="Redo"><Redo2 size={17}/></button><button onClick={loadExample} title="Restore example village"><RotateCcw size={17}/></button></div></div><div className="controls-group"><span className="controls-label">TIME OF DAY</span><div className="segmented"><button onClick={()=>setSetting('time','day')} className={settings.time==='day'?'active':''} title="Day"><Sun size={16}/> Day</button><button onClick={()=>setSetting('time','night')} className={settings.time==='night'?'active':''} title="Night"><Moon size={16}/> Night</button></div></div><div className="controls-group"><span className="controls-label">WEATHER</span><div className="icon-group"><button title="Clear weather" className={settings.weather==='clear'?'active':''} onClick={()=>setSetting('weather','clear')}><CloudSun size={17}/></button><button title="Rain" className={settings.weather==='rain'?'active':''} onClick={()=>setSetting('weather','rain')}><CloudRain size={17}/></button><button title="Snow" className={settings.weather==='snow'?'active':''} onClick={()=>setSetting('weather','snow')}><Snowflake size={17}/></button></div></div></div></div>
  <div className="guide-toolbar"><span>{chosen?.grounding?'Dashed lines connect this object to its placement landmarks.':'Select a placed object to inspect its landmarks.'}</span><button aria-pressed={showGuides} onClick={()=>setShowGuides(v=>!v)}>{showGuides?'Hide guides':'Show guides'}</button></div>
  <div className="knowledge-panel"><div className="knowledge-top"><div className="knowledge-icon"><TextCursorInput size={18}/></div><div><strong>The language behind the magic</strong><p>Every creation begins with natural language understanding.</p></div><button onClick={()=>setAnalysisOpen(v=>!v)} className="knowledge-toggle">{analysisOpen?'Hide details':'Show details'} <ChevronRight size={14} className={analysisOpen?'turn':''}/></button></div>{analysisOpen&&<div className="knowledge-content"><div className="pipeline"><span>YOUR WORDS</span><ChevronRight size={16}/><span>ENTITY EXTRACTION</span><ChevronRight size={16}/><span>SPATIAL GROUNDING</span><ChevronRight size={16}/><span>YOUR WORLD ✨</span></div>{parsed?<Analysis key={parsed.text} parsed={parsed}/>:<p className="waiting-analysis">Give the world a new instruction to inspect its words, grammar tags, entities, and extracted scene actions.</p>}</div>}</div>
 </main>
 <aside className="right-panel"><div className="right-header"><div className="right-heading"><Layers3 size={19}/><h3>World explorer</h3></div><p>All the little things in your world.</p></div>
   <div className="right-tabs"><button className={activeTab==='objects'?'active':''} onClick={()=>setActiveTab('objects')}><Layers3 size={15}/> Objects</button><button className={activeTab==='add'?'active':''} onClick={()=>setActiveTab('add')}><Plus size={15}/> Add new</button></div>
   {activeTab==='objects'?<div className="object-list"><div className="objects-summary"><span>OBJECT COLLECTION</span><span>{items.length} total</span></div>{counts.map(({type,count})=><div key={type} className="object-group"><button onClick={()=>{let object=items.find(i=>i.type===type);setSelected(object?.id)}}><span className="object-emoji">{TYPE_EMOJI[type]}</span><span className="object-name">{typeLabel(type)}<small>{count} on canvas</small></span><span className="group-count">{count}</span></button></div>)}{counts.length===0&&<p className="no-objects">This world is empty. Add your first object!</p>}</div>:<div className="object-list"><div className="objects-summary"><span>QUICK ADD</span><span>CLICK TO CREATE</span></div>{TYPES.map(type=><div key={type} className="object-group"><button onClick={()=>addDirect(type)}><span className="object-emoji">{TYPE_EMOJI[type]}</span><span className="object-name">{typeLabel(type)}</span><Plus size={16}/></button></div>)}</div>}
   <div className="selection-panel"><div className="selection-label">SELECTED OBJECT</div>{chosen?<><div className="selected-details"><div className="selected-emoji">{TYPE_EMOJI[chosen.type]}</div><div><b>{chosen.type}</b><small>Position {Math.round(chosen.x)}, {Math.round(chosen.y)}</small></div></div><div className="selection-actions"><button onClick={duplicateSelected}><Copy size={15}/> Duplicate</button><button className="delete" onClick={deleteSelected}><Trash2 size={15}/> Delete</button></div>{chosen.type==='house'&&<div className="color-options"><small>ROOF COLOR</small><div>{['red','yellow','blue','pink','purple','green'].map(color=><button key={color} title={color} style={{background:({red:'#ed7866',yellow:'#f5bc59',blue:'#74a6ea',pink:'#eaa2bc',purple:'#a78bd8',green:'#80bea1'})[color]}} className={chosen.color===color?'picked':''} onClick={()=>{remember();setItems(v=>v.map(o=>o.id===chosen.id?{...o,color}:o))}}/>)}</div></div>}</>:<div className="nothing-selected"><MousePointer2 size={21}/><span>Select any object on the canvas to inspect, recolor, move, or delete it.</span></div>}</div>
   <div className="tip-card"><span className="tip-icon">💡</span><strong>Little tip!</strong><p>Try describing where things should go: <em>“Add a tree to the left of the house.”</em></p></div>
   <div className="api-indicator"><span className={apiState==='offline'?'api-dot offline':'api-dot'}/><div><strong>{apiState==='spacy'?'spaCy NLP connected':apiState==='offline'?'Browser preview mode':'Language engine ready'}</strong><small>{apiState==='offline'?'Start the Python API for POS / dependency tags':apiState==='spacy'?'Tokenization · POS · Dependencies':'World commands · Spatial parsing'}</small></div></div>
 </aside>
 </div>
 {toast&&<div className="toast"><Check size={17}/>{toast}</div>}
 {showHelp&&<div className="overlay" onClick={()=>setShowHelp(false)}><div className="help-modal" onClick={e=>e.stopPropagation()}><button className="close-help" onClick={()=>setShowHelp(false)}><X/></button><div className="help-spark">✨</div><h2>How WordWorld works</h2><p>Describe a place in everyday English. Our NLP parser identifies objects, quantity, color, and spatial relationships before rendering the scene.</p><div className="help-steps"><div><b>01 · Dream</b><span>“Place two red cottages next to the lake.”</span></div><div><b>02 · Understand</b><span>Entity: house · Count: 2 · Color: red · Relation: near lake</span></div><div><b>03 · Explore</b><span>Click and drag to move objects. Use the explorer to modify or delete them.</span></div></div><p className="help-fine">Supported objects: houses, trees, lakes, rivers, bridges, roads, flowers, mountains, towers, castles, rocks. Set day, night, rain, or snow. This MVP uses explicit language patterns for spatial grounding and spaCy for linguistic annotation; it does not understand arbitrary free-form descriptions.</p><button className="help-cta" onClick={()=>setShowHelp(false)}>Let's create something <ArrowUpRight size={16}/></button></div></div>}
 </div>
}
export default App;
