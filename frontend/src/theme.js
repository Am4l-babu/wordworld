import {useEffect, useState} from 'react';

// index.html applies the stored theme before first paint with the same key.
const KEY = 'wordworld-theme';
const darkQuery = () => window.matchMedia('(prefers-color-scheme: dark)');

function storedMode() {
  try {
    const value = localStorage.getItem(KEY);
    return value === 'light' || value === 'dark' ? value : 'system';
  } catch {
    return 'system';
  }
}

export function useTheme() {
  const [mode, setMode] = useState(storedMode);
  const [systemDark, setSystemDark] = useState(() => darkQuery().matches);
  useEffect(() => {
    const media = darkQuery(), update = () => setSystemDark(media.matches);
    media.addEventListener('change', update);
    return () => media.removeEventListener('change', update);
  }, []);
  const theme = mode === 'system' ? (systemDark ? 'dark' : 'light') : mode;
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    document.querySelector('meta[name=theme-color]')?.setAttribute('content', theme === 'dark' ? '#17151f' : '#f6f4ec');
  }, [theme]);
  useEffect(() => {
    try { mode === 'system' ? localStorage.removeItem(KEY) : localStorage.setItem(KEY, mode); } catch { /* not persisted */ }
  }, [mode]);
  // Toggling back to what the system prefers means "follow the system" again.
  function toggle() {
    const next = theme === 'dark' ? 'light' : 'dark';
    setMode(next === (systemDark ? 'dark' : 'light') ? 'system' : next);
  }
  return {theme, mode, toggle};
}
