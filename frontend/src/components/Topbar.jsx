import React from 'react';
import {Layers3, Check, CircleHelp, Sun, Moon} from 'lucide-react';
import WorldMenu from './WorldMenu';

export default function Topbar({theme, onToggleTheme, onHelp, onShare, onExport, onImport, onTestLog}) {
  const next = theme === 'dark' ? 'light' : 'dark';
  return <header className="topbar">
    <div className="brand">
      <div className="brand-icon"><Layers3 size={24} fill="rgba(255,255,255,.15)"/></div>
      <div className="brand-name">word<span>world</span><i>.</i></div>
      <div className="brand-tag">beta</div>
    </div>
    <div className="top-center"><span className="status-dot"/> Your imagination, visualized <span className="top-starfish">✳</span></div>
    <div className="top-actions">
      <div className="autosaved"><Check size={13}/> Auto-saved</div>
      <button className="top-help theme-toggle" onClick={onToggleTheme} aria-label={`Switch to ${next} theme`} title={`Switch to ${next} theme`}>
        {theme === 'dark' ? <Sun size={17}/> : <Moon size={17}/>}
      </button>
      <button aria-label="How it works" className="top-help" onClick={onHelp}><CircleHelp size={17}/> <span>How it works</span></button>
      <WorldMenu onShare={onShare} onExport={onExport} onImport={onImport} onTestLog={onTestLog}/>
    </div>
  </header>;
}
