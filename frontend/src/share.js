import {TYPES, PALETTE, RELATION_LABEL, cleanScene} from './world.js';

// A share link carries the whole island in the URL: nothing is uploaded or stored.
// Rows are compact and versioned so a full 120-object island stays a few kilobytes.
const VERSION = 1;
const COLORS = Object.keys(PALETTE);
const RELATIONS = Object.keys(RELATION_LABEL);
const WEATHER = ['clear', 'rain', 'snow'];
export const MAX_SHARE_CODE = 20000;

const toBase64Url = text => btoa(text).replaceAll('+', '-').replaceAll('/', '_').replace(/=+$/, '');
const fromBase64Url = text => atob(text.replaceAll('-', '+').replaceAll('_', '/'));

export function encodeWorld(items, settings) {
  const index = new Map(items.map((item, i) => [item.id, i]));
  const rows = items.map(item => {
    const row = [TYPES.indexOf(item.type), Math.round(item.x), Math.round(item.y),
      item.color ? COLORS.indexOf(item.color) : -1, Math.round((item.scale || 1) * 100), item.seed || 0];
    const guide = item.grounding;
    if (guide && guide.anchorIds.every(id => index.has(id))) {
      row.push([RELATIONS.indexOf(guide.relation), ...guide.anchorIds.map(id => index.get(id))]);
    }
    return row;
  });
  const payload = [VERSION, settings.time === 'night' ? 1 : 0, WEATHER.indexOf(settings.weather), rows];
  return toBase64Url(JSON.stringify(payload));
}

// Links come from anyone, so decoding reuses the same validation as file import.
export function decodeWorld(code) {
  try {
    if (typeof code !== 'string' || !code || code.length > MAX_SHARE_CODE) return null;
    const [version, night, weather, rows] = JSON.parse(fromBase64Url(code));
    if (version !== VERSION || !Array.isArray(rows)) return null;
    const items = rows.filter(Array.isArray).map((row, i) => {
      const [type, x, y, color, scale, seed, guide] = row;
      return {
        id: `s${i}`, type: TYPES[type], x, y, color: COLORS[color], scale: scale / 100, seed,
        grounding: Array.isArray(guide) ? {relation: RELATIONS[guide[0]], anchorIds: guide.slice(1).map(j => `s${j}`)} : undefined,
      };
    });
    return cleanScene({items, settings: {time: night === 1 ? 'night' : 'day', weather: WEATHER[weather]}});
  } catch {
    return null;
  }
}

export function shareUrl(items, settings, location = window.location) {
  return `${location.origin}${location.pathname}?world=${encodeWorld(items, settings)}`;
}

export function readSharedWorld() {
  const code = new URLSearchParams(window.location.search).get('world');
  return code ? decodeWorld(code) : null;
}

// Once opened, the island belongs to this browser; reloading must not reopen the link.
export function clearSharedWorldParam() {
  const url = new URL(window.location.href);
  if (!url.searchParams.has('world')) return;
  url.searchParams.delete('world');
  window.history.replaceState(null, '', url);
}
