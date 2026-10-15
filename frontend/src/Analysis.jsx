import React, {useState} from 'react';

const labels={intent:'Instruction',object:'Object',quantity:'Quantity',color:'Color',spatial_relation:'Relation',landmark:'Landmark',setting:'Setting',protected:'Preserved',reference:'Reference'};
function HighlightedCommand({parsed}){
 const chars=Array.from(parsed.text||''),parts=[];let cursor=0;
 for(const span of parsed.highlights||[]){
  if(!Number.isInteger(span.start)||span.start<cursor)continue;
  parts.push(chars.slice(cursor,span.start).join(''));
  parts.push(<mark key={`${span.start}-${span.role}`} className={`span-${span.role}`} title={labels[span.role]||span.role}>{chars.slice(span.start,span.end).join('')}</mark>);
  cursor=span.end;
 }
 parts.push(chars.slice(cursor).join(''));
 return <p className="grounded-command" aria-label="Annotated command">{parts}</p>;
}
export default function Analysis({parsed}){
 const [active,setActive]=useState(0),token=parsed.tokens?.[active];
 return <>
  <div className="parsed-note"><span className="parse-engine">RULE-BASED ACTIONS</span><span>{parsed.model==='spacy'?'spaCy grammar annotations':parsed.model==='browser-preview'?'Limited browser preview':parsed.model==='spacy-tokenizer'?'spaCy tokenizer · grammar model unavailable':'Lexical tokenizer'} · {parsed.actions?.length||0} actions</span></div>
  <HighlightedCommand parsed={parsed}/>
  <div className="span-legend">{Object.entries(labels).map(([role,label])=><span key={role}><i className={`span-${role}`}/>{label}</span>)}</div>
  {parsed.resolutions?.length>0&&<p className="reference-resolutions">{parsed.resolutions.map((r,i)=><span key={i}>{r.text} → {r.objects.map(o=>`${o.count} ${o.type}${o.count>1?'s':''}`).join(' + ')}</span>)}</p>}
  <p className="analysis-caption">Select a word to inspect its grammar. Highlighted phrases show the grounding rules.</p>
  <div className="token-list">{parsed.tokens?.map((word,i)=><button key={i} type="button" aria-pressed={active===i} onClick={()=>setActive(i)} className={'token '+(word.pos==='NOUN'||word.pos==='PROPN'?'noun':word.pos==='VERB'?'verb':'')} title={word.dep?`${word.pos} · ${word.dep} → ${word.head}`:word.pos}>{word.text}<small>{word.pos==='TOKEN'?'':word.pos}</small></button>)}</div>
  {token&&<dl className="token-details"><div><dt>Word / lemma</dt><dd>{token.text} / {token.lemma}</dd></div><div><dt>Part of speech</dt><dd>{token.pos||'Unavailable'}</dd></div><div><dt>Dependency → head</dt><dd>{token.dep?`${token.dep} → ${token.head}`:'Requires spaCy English model'}</dd></div><div><dt>Character span</dt><dd>{token.start==null?'Unavailable':`${token.start}–${token.end}`}</dd></div></dl>}
  <div className="actions-chips">{parsed.actions?.map((a,i)=><span key={i}>{a.action==='add'?`+ ${a.count} ${a.type}${a.count>1?'s':''}`:a.action==='remove'?`− ${a.count} ${a.type}`:a.action==='setting'?`${a.key}: ${a.value}`:'Reset'}{a.target?` · ${a.relation} ${a.targets?a.targets.join(' & '):a.target}`:''}</span>)}</div>
  {parsed.warnings?.length>0&&<ul className="parse-warnings" aria-label="Parser notices">{parsed.warnings.map(w=><li key={w}>{w}</li>)}</ul>}
  <details className="action-json"><summary>Structured actions JSON</summary><pre>{JSON.stringify(parsed.actions,null,2)}</pre></details>
 </>;
}
