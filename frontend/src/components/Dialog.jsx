import React, {useEffect, useRef} from 'react';

const FOCUSABLE = 'button,input,textarea,select,[href],[tabindex]:not([tabindex="-1"])';

// Modal shell: moves focus inside, keeps Tab within the dialog, closes on Escape or
// backdrop click, and returns focus to whatever opened it.
export default function Dialog({labelledBy, onClose, className, children}) {
  const ref = useRef(null);
  useEffect(() => {
    const opener = document.activeElement;
    const node = ref.current;
    (node.querySelector('[data-autofocus]') || node.querySelector(FOCUSABLE))?.focus();
    return () => opener?.focus?.();
  }, []);
  function onKeyDown(e) {
    if (e.key === 'Escape') {
      e.stopPropagation();
      onClose();
      return;
    }
    if (e.key !== 'Tab') return;
    const focusable = [...ref.current.querySelectorAll(FOCUSABLE)].filter(el => !el.disabled);
    const first = focusable[0], last = focusable.at(-1);
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  }
  return <div className="overlay" onClick={onClose}>
    <div ref={ref} className={className} role="dialog" aria-modal="true" aria-labelledby={labelledBy}
      onClick={e => e.stopPropagation()} onKeyDown={onKeyDown}>
      {children}
    </div>
  </div>;
}
