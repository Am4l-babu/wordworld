// Scene camera. The island is drawn in a fixed 1000×645 space; zooming in narrows
// the visible window and panning moves it, always clamped to stay over the world.
export const WORLD = {width: 1000, height: 645};
export const DEFAULT_VIEW = {zoom: 1, x: 500, y: 323};
export const ZOOM_MIN = 0.7;
export const ZOOM_MAX = 2;

const clamp = (value, min, max) => Math.max(min, Math.min(max, value));

export function clampView({zoom, x, y}) {
  const z = clamp(Math.round(zoom * 10) / 10, ZOOM_MIN, ZOOM_MAX);
  const w = WORLD.width / z, h = WORLD.height / z;
  return {
    zoom: z,
    x: w < WORLD.width ? clamp(x, w / 2, WORLD.width - w / 2) : DEFAULT_VIEW.x,
    y: h < WORLD.height ? clamp(y, h / 2, WORLD.height - h / 2) : DEFAULT_VIEW.y,
  };
}

export function viewBox({zoom, x, y}) {
  const w = WORLD.width / zoom, h = WORLD.height / zoom;
  return `${x - w / 2} ${y - h / 2} ${w} ${h}`;
}

// Change zoom while keeping `point` (a world coordinate, e.g. under the cursor) fixed on screen.
export function zoomAt(view, zoom, point) {
  const next = clampView({...view, zoom});
  if (!point) return clampView({...view, zoom: next.zoom});
  const k = view.zoom / next.zoom;
  return clampView({zoom: next.zoom, x: point.x + (view.x - point.x) * k, y: point.y + (view.y - point.y) * k});
}

export const panBy = (view, dx, dy) => clampView({...view, x: view.x + dx, y: view.y + dy});

export function isVisible(view, {x, y}, margin = 40) {
  const w = WORLD.width / view.zoom, h = WORLD.height / view.zoom;
  return Math.abs(x - view.x) <= w / 2 - margin && Math.abs(y - view.y) <= h / 2 - margin;
}
