import React from 'react';
import {Undo2, Redo2, RotateCcw, Sun, Moon, CloudSun, CloudRain, Snowflake} from 'lucide-react';

const WEATHER = [['clear', 'Clear weather', CloudSun], ['rain', 'Rain', CloudRain], ['snow', 'Snow', Snowflake]];

export default function WorldControls({settings, canUndo, canRedo, onUndo, onRedo, onRestore, onSetting, hasGuide, showGuides, onToggleGuides}) {
  return <>
    <div className="below-world">
      <div className="world-controls">
        <div className="controls-group">
          <span className="controls-label">WORLD CONTROLS</span>
          <div className="icon-group">
            <button onClick={onUndo} disabled={!canUndo} title="Undo (Ctrl+Z)" aria-label="Undo"><Undo2 size={17}/></button>
            <button onClick={onRedo} disabled={!canRedo} title="Redo (Ctrl+Shift+Z)" aria-label="Redo"><Redo2 size={17}/></button>
            <button onClick={onRestore} title="Restore example village" aria-label="Restore example village"><RotateCcw size={17}/></button>
          </div>
        </div>
        <div className="controls-group">
          <span className="controls-label">TIME OF DAY</span>
          <div className="segmented">
            {[['day', 'Day', Sun], ['night', 'Night', Moon]].map(([value, label, Icon]) =>
              <button key={value} onClick={() => onSetting('time', value)} className={settings.time === value ? 'active' : ''} aria-pressed={settings.time === value} title={label}>
                <Icon size={16}/> {label}
              </button>)}
          </div>
        </div>
        <div className="controls-group">
          <span className="controls-label">WEATHER</span>
          <div className="icon-group">
            {WEATHER.map(([value, label, Icon]) =>
              <button key={value} title={label} aria-label={label} aria-pressed={settings.weather === value} className={settings.weather === value ? 'active' : ''} onClick={() => onSetting('weather', value)}>
                <Icon size={17}/>
              </button>)}
          </div>
        </div>
      </div>
    </div>
    <div className="guide-toolbar">
      <span>{hasGuide ? 'Dashed lines connect this object to its placement landmarks.' : 'Select a placed object to inspect its landmarks.'}</span>
      <button aria-pressed={showGuides} onClick={onToggleGuides}>{showGuides ? 'Hide guides' : 'Show guides'}</button>
    </div>
  </>;
}
