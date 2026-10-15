import React from 'react';
import {MousePointer2, Minus, Plus} from 'lucide-react';
import Scene from '../Scene';
import {MAX_ITEMS} from '../world';
import {ZOOM_MIN, ZOOM_MAX} from '../view';

export function WorldTitle({count}) {
  const full = count >= MAX_ITEMS;
  return <div className="world-title">
    <div>
      <div className="section-overline">YOUR LITTLE UNIVERSE <span className="overline-sparkle">✦</span></div>
      <div className="title-line"><h2>The Dreamscape</h2><span className="live-pill"><span/> LIVE WORLD</span></div>
      <p>A tiny world with endless possibilities. Every word changes something.</p>
    </div>
    <div className={'world-count' + (full ? ' full' : '')} title={`Up to ${MAX_ITEMS} objects`}>
      <span className="count-value">{count}</span>
      <span className="count-label">{full ? 'island is full' : 'objects created'}</span>
    </div>
  </div>;
}

export function WorldStage({items, settings, selected, onSelect, onMove, onDragBegin, view, onView, onZoom, onResetView, showGuides, onTrySentence, onRestore}) {
  const percent = Math.round(view.zoom * 100);
  return <div className="world-frame">
    <div className="world-badge">
      <span>✦</span> ISLAND NO. 001 <span className="separator">/</span> {settings.time === 'night' ? 'MOONLIT' : 'DAYLIGHT'} DREAM
      {settings.weather !== 'clear' && <> <span className="separator">/</span> {settings.weather === 'rain' ? 'RAINY' : 'SNOWY'}</>}
    </div>
    <Scene items={items} settings={settings} selected={selected} onSelect={onSelect} onMove={onMove} onDragBegin={onDragBegin}
      view={view} onView={onView} showGuides={showGuides}/>
    <div className="world-hint">
      <MousePointer2 size={14}/> {view.zoom > 1 ? 'Drag empty space to pan · Ctrl+scroll to zoom' : 'Select · Drag or use arrow keys · Del removes'}
    </div>
    <div className="zoom-controls">
      <button title="Zoom out" aria-label="Zoom out" disabled={view.zoom <= ZOOM_MIN} onClick={() => onZoom(-0.1)}><Minus size={17}/></button>
      <button className="zoom-reset" title="Reset zoom and position" aria-label={`Zoom ${percent}%, reset view`} onClick={onResetView}>{percent}%</button>
      <button title="Zoom in" aria-label="Zoom in" disabled={view.zoom >= ZOOM_MAX} onClick={() => onZoom(0.1)}><Plus size={17}/></button>
    </div>
    {items.length === 0 && <div className="empty-world">
      <div>✨</div>
      <strong>Your story starts here</strong>
      <span>Describe a scene, or start from something.</span>
      <div className="empty-actions">
        <button onClick={onTrySentence}>Try a sentence</button>
        <button onClick={onRestore}>Restore starter village</button>
      </div>
    </div>}
  </div>;
}
