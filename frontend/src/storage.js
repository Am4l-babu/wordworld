import {initialItems, INITIAL_SETTINGS, cleanScene} from './world';
import {sanitizeLog} from './testlog';

export const KEYS = {scene: 'wordworld-scene-v1', recent: 'wordworld-recent-commands-v1', testlog: 'wordworld-testlog-v1'};

// Storage can be full, blocked or private; the app must keep working without it.
export function readJSON(key) {
  try { return JSON.parse(localStorage.getItem(key)); } catch { return null; }
}
export function writeJSON(key, value) {
  try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* not persisted */ }
}

export function getSaved() {
  return cleanScene(readJSON(KEYS.scene)) || {items: initialItems(), settings: {...INITIAL_SETTINGS}};
}

export function getRecent() {
  const list = readJSON(KEYS.recent);
  return Array.isArray(list) ? list.filter(x => typeof x === 'string').slice(-20) : [];
}

export function getTestLog() {
  return sanitizeLog(readJSON(KEYS.testlog));
}

export function getSharedCommand() {
  const command = new URLSearchParams(window.location.search).get('command') || '';
  return command.length <= 1400 ? command.trim() : '';
}
