import React from 'react';
import {headIndex, tokenRoles} from '../grammar';

const GAP = 12, BASE_ARC = 18, ARC_STEP = 19;
const tokenWidth = token => Math.max(token.text.length * 7.6, (token.pos || '').length * 6.4) + 16;

// displaCy-style arcs: each arrow runs from a head word to the word that depends on it.
// Mouse users can click words here; the token buttons below remain the keyboard path.
export default function DependencyArcs({tokens, highlights, active, onSelect}) {
  const xs = [];
  let cursor = 8;
  for (const token of tokens) {
    const width = tokenWidth(token);
    xs.push({left: cursor, width, center: cursor + width / 2});
    cursor += width + GAP;
  }
  const arcs = tokens.map((token, i) => ({i, head: headIndex(tokens, i), dep: token.dep}))
    .filter(arc => arc.head >= 0 && arc.head !== arc.i)
    .map(arc => ({...arc, from: Math.min(arc.i, arc.head), to: Math.max(arc.i, arc.head)}))
    .sort((a, b) => (a.to - a.from) - (b.to - b.from));
  // An arc sits one level above every arc nested inside it, so labels never share a height.
  for (const arc of arcs) {
    const inner = arcs.filter(o => o !== arc && o.level && o.from >= arc.from && o.to <= arc.to);
    arc.level = 1 + Math.max(0, ...inner.map(o => o.level));
    arc.height = BASE_ARC + ARC_STEP * (arc.level - 1);
  }
  const top = Math.max(BASE_ARC, ...arcs.map(a => a.height)) + 26;
  const width = cursor;
  return <div className="dep-scroll">
    <svg className="dep-arcs" width={width} height={top + 44} viewBox={`0 0 ${width} ${top + 44}`} aria-hidden="true">
      {arcs.map(({i, head, dep, height}) => {
        const x1 = xs[head].center, x2 = xs[i].center + (i > head ? -4 : 4), y = top, peak = y - height * 1.33;
        const linked = active === i || active === head;
        return <g key={i} className={'dep-arc' + (active == null ? '' : linked ? ' linked' : ' dim')}>
          <path d={`M${x1} ${y}C${x1} ${peak} ${x2} ${peak} ${x2} ${y}`} fill="none"/>
          <path d={`M${x2} ${y}l-4 -7h8z`} className="dep-head"/>
          <text x={(x1 + x2) / 2} y={y - height - 4} textAnchor="middle">{dep}</text>
        </g>;
      })}
      {tokens.map((token, i) => {
        const roles = tokenRoles(token, highlights);
        return <g key={i} className={'dep-token' + (active === i ? ' active' : '')} onClick={() => onSelect(i)}>
          <rect x={xs[i].left} y={top + 4} width={xs[i].width} height={36} rx="7"/>
          {roles[0] && <rect x={xs[i].left + 6} y={top + 36} width={xs[i].width - 12} height="3" rx="1.5" className={`span-${roles[0]}`}/>}
          <text x={xs[i].center} y={top + 20} textAnchor="middle" className="dep-word">{token.text}</text>
          <text x={xs[i].center} y={top + 32} textAnchor="middle" className="dep-pos">{token.pos}</text>
        </g>;
      })}
    </svg>
  </div>;
}
