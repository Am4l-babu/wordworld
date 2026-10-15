import React, {useEffect, useRef, useState} from 'react';
import {PALETTE as COLORS,RELATION_LABEL} from './world';
import {DEFAULT_VIEW,viewBox,panBy,zoomAt} from './view';
const hash=(n)=>((n*2654435761)>>>0)/4294967295;
const ground='url(#grass)';

function House({color='red'}) {let roof=COLORS[color]||COLORS.red;return <g>
  <ellipse cx="2" cy="4" rx="48" ry="15" fill="#294b3b" opacity=".13"/>
  <path d="M-40-22L0-47 42-22V12L0 33-40 12Z" fill="#ead8ad" stroke="#a19b7c" strokeWidth="1.5"/>
  <path d="M0-47L42-22V12L0 33Z" fill="#f5e6c1"/>
  <path d="M-48-22L-5-60 46-26 38-16 -6-46 -40-12Z" fill={roof} stroke="#955e68" strokeWidth="2" strokeLinejoin="round"/>
  <path d="M-5-60L43-39 51-21 45-25Z" fill="#dba18e"/>
  <path d="M15-47V-67h15v27" fill="#e4bc99" stroke="#b38678" strokeWidth="2"/>
  <path d="M-8 28V-5Q-8-17 2-18Q12-18 12-5V26L0 33Z" fill="#b97b66" stroke="#8c6465" strokeWidth="2"/>
  <circle cx="7" cy="7" r="2" fill="#fbe8a1"/>
  <path d="M-31-18h17v18h-17z" fill="#89cbd2" stroke="#fdf4dc" strokeWidth="3"/>
  <path d="M-22-18V0M-31-9h17" stroke="#fdf4dc" strokeWidth="2"/>
  <path d="M22-4h15v17H22z" fill="#80c3d6" stroke="#d3e0bd" strokeWidth="3"/>
  <path d="M29-4v17" stroke="#d3e0bd" strokeWidth="2"/>
  <path d="M-44 14q-11-9-14 2 M41 22q9-10 16 1" stroke="#4b966d" strokeWidth="4" fill="none"/>
  <circle cx="-54" cy="13" r="4" fill="#efb8b7"/><circle cx="51" cy="20" r="4" fill="#f7c773"/>
</g>}
function Tree({seed=4,color}){let s=hash(seed),leaf=COLORS[color];return <g>
  <ellipse cy="8" rx="34" ry="10" fill="#2e6c4c" opacity=".15"/>
  <path d="M-7-26L-5 12 6 12 8-29" fill="#9f7557" stroke="#83664e" strokeWidth="2"/>
  <path d="M-9-5L-25-24M7-12L27-31" stroke="#9f7557" strokeWidth="4"/>
  <circle cx="-21" cy="-38" r="25" fill={leaf||'#72b993'}/><circle cx="18" cy="-38" r="28" fill={leaf||'#5ea887'}/>
  <circle cx="0" cy="-57" r="29" fill={leaf||(s>.45?'#79c6a0':'#89cda1')}/>
  <path d="M-28-45q14-28 34-17" stroke="#b8e7bb" strokeWidth="4" fill="none" strokeLinecap="round" opacity=".6"/>
  <circle cx="-20" cy="-45" r="3" fill="#d9ecb7"/><circle cx="18" cy="-63" r="3" fill="#c8ebba"/>
</g>}
function Lake(){return <g>
  <ellipse cy="0" rx="97" ry="43" fill="#60a991" opacity=".6"/>
  <ellipse cx="0" cy="-5" rx="90" ry="37" fill="url(#water)" stroke="#b6e8ba" strokeWidth="6"/>
  <path d="M-62-8q38-15 70 0t59 1" stroke="#c7f8ef" opacity=".7" strokeWidth="3" fill="none" strokeLinecap="round"/>
  <path d="M-35 13q20-9 37-4t37 1" stroke="#bdf0e3" opacity=".8" strokeWidth="3" fill="none" strokeLinecap="round"/>
  <ellipse cx="48" cy="-12" rx="13" ry="6" fill="#a0d887"/><path d="M48-12l8-4" stroke="#5d9c71" strokeWidth="2"/>
  <circle cx="-75" cy="5" r="4" fill="#fff3d9"/><circle cx="-73" cy="4" r="2" fill="#f4cc70"/>
</g>}
function Road(){return <g>
  <path d="M-110 5 C-70-30-25 20 22-5 S83-12 119-1" stroke="#7e9673" strokeWidth="49" opacity=".33" fill="none" strokeLinecap="round"/>
  <path d="M-110 0 C-70-34-25 16 22-9 S83-16 119-5" stroke="#eadabb" strokeWidth="36" fill="none" strokeLinecap="round"/>
  <path d="M-110 0 C-70-34-25 16 22-9 S83-16 119-5" stroke="#fff5d6" strokeWidth="2.5" strokeDasharray="9 15" fill="none" strokeLinecap="round"/>
</g>}
function River(){return <g>
  <path d="M-116-50 C-40-99-45-8 15-26 S86 38 126 56" stroke="#9ad4b6" strokeWidth="51" fill="none" strokeLinecap="round"/>
  <path d="M-116-50 C-40-99-45-8 15-26 S86 38 126 56" stroke="url(#water)" strokeWidth="39" fill="none" strokeLinecap="round"/>
  <path d="M-114-49 C-40-98-45-7 15-25 S86 39 125 55" stroke="#e6fff5" opacity=".5" strokeWidth="2" strokeDasharray="11 18" fill="none"/>
</g>}
function Bridge(){return <g>
  <ellipse cy="5" rx="54" ry="13" fill="#4b695f" opacity=".14"/>
  <path d="M-55 4L-39-14 35-14 54 4 38 14-39 14Z" fill="#b78360" stroke="#93624e" strokeWidth="2"/>
  <path d="M-43-13v-24M40-13v-24" stroke="#996d4f" strokeWidth="6"/>
  <path d="M-43-35Q0-22 40-35" stroke="#996d4f" strokeWidth="5" fill="none"/>
  {[-29,-13,3,19,35].map(x=><path key={x} d={`M${x} -12 l 3 24`} stroke="#ecd1a3" strokeWidth="2"/>)}
</g>}
function Flower({seed=1,color}) {const c=COLORS[color]||['#ee9ab7','#fff4ae','#aebbe9','#fff9ed'][Math.floor(hash(seed)*4)];return <g>
  <path d="M0 5V-9" stroke="#49936e" strokeWidth="2"/><path d="M0-1l-7-4M0 0l7-6" stroke="#49936e" strokeWidth="2"/>
  {[0,72,144,216,288].map(a=><ellipse key={a} cx="0" cy="-15" rx="5" ry="8" transform={`rotate(${a} 0 -10)`} fill={c}/>)}
  <circle cy="-10" r="4" fill="#f8ca59"/>
</g>}
function Mountain(){return <g>
  <ellipse cy="5" rx="86" ry="17" fill="#325a56" opacity=".1"/>
  <path d="M-85 10L-21-98 25-25 53-71 93 10Z" fill="#8b9aab" stroke="#657f8e" strokeWidth="2"/>
  <path d="M-21-98L25-25 2-38-18-59-39-58Z" fill="#fcf9ed"/>
  <path d="M53-71L93 10 53-7 41-25 29-18Z" fill="#e5eef1"/>
  <path d="M-21-98L25-25 2-38-4-25Z" fill="#768b9b" opacity=".4"/>
</g>}
function Tower(){return <g>
 <ellipse cy="8" rx="42" ry="12" fill="#345848" opacity=".14"/>
 <path d="M-26 7L-20-91H21L30 7Z" fill="#f1dcc2" stroke="#a9a28a" strokeWidth="2"/>
 <path d="M-29-87L0-122 30-87Z" fill="#d08a85" stroke="#ac7773" strokeWidth="2"/>
 <path d="M-27-88H28v11h-55z" fill="#f9eccc"/>
 <path d="M-8 8V-13Q-8-24 1-24Q10-24 10-13V8Z" fill="#a17668"/>
 <path d="M-10-62h20v20h-20z" fill="#8fcee0" stroke="#fff7e5" strokeWidth="4"/>
 <path d="M0-62v20" stroke="#fff7e5" strokeWidth="2"/>
 <circle cx="0" cy="-103" r="3" fill="#fef5bc"/>
 </g>}
function Castle(){return <g>
 <ellipse cy="12" rx="80" ry="18" fill="#234c4d" opacity=".12"/>
 <path d="M-67 3V-56H63V3Z" fill="#e1d5c4" stroke="#ada9a5" strokeWidth="2"/>
 <path d="M-80-12V-96h37v84M41-12V-96h36v84" fill="#c9d1cc" stroke="#abb0b2" strokeWidth="2"/>
 {[-81,-68,-55,-43,40,53,66].map((x,i)=><rect key={i} x={x} y={i<4?-105:-105} width="12" height="15" fill="#d9d9ce"/>)}
 <path d="M-20 5V-37Q0-60 22-37V5" fill="#aa8c82" stroke="#8f8078" strokeWidth="3"/>
 <path d="M-8-66h20v17H-8z" fill="#91c7d1" stroke="#f7ede2" strokeWidth="3"/>
 <path d="M-63-84h13v24h-13zM51-84h12v24H51z" fill="#91c7d1"/>
 <path d="M-3-105v-35" stroke="#86765f" strokeWidth="3"/><path d="M-2-140l33 10-33 9Z" fill="#e38e84"/>
 </g>}
function Rock(){return <g><ellipse cy="5" rx="34" ry="10" fill="#385c4e" opacity=".14"/><path d="M-34 1L-19-22 12-28 33-5 24 10-26 10Z" fill="#c3c4b8" stroke="#9faea4" strokeWidth="2"/><path d="M12-28L33-5 24 10 3-2Z" fill="#a3b3b0"/><path d="M-19-22L3-2-26 10-34 1Z" fill="#d5d6c8"/></g>}
const SPRITES={house:House,tree:Tree,lake:Lake,road:Road,river:River,bridge:Bridge,flower:Flower,mountain:Mountain,tower:Tower,castle:Castle,rock:Rock};
const sizes={house:1,tree:.82,lake:1,road:1,river:1,bridge:.9,flower:.82,mountain:.94,tower:.95,castle:1,rock:.8};
const backLayers=['road','river','lake'];
function SceneObject({item,selected,onSelect,onStartDrag,onKeyMove}){const Component=SPRITES[item.type]||Rock;return <g transform={`translate(${item.x} ${item.y}) scale(${(sizes[item.type]||1)*(item.scale||1)})`} className={'scene-object '+(selected?'selected':'')} onPointerDown={e=>{e.stopPropagation();onStartDrag(e,item.id)}} onClick={e=>{e.stopPropagation();onSelect(item.id)}} onKeyDown={e=>{if(['Enter',' '].includes(e.key)){e.preventDefault();onSelect(item.id)}else if(e.key==='Escape'){onSelect(null)}else if(e.key.startsWith('Arrow')){e.preventDefault();onKeyMove(item,e.key,e.shiftKey?20:8)}}} role="button" tabIndex="0" aria-pressed={selected} aria-label={`Select ${item.type}`}>
  {selected&&<ellipse cx="0" cy="10" rx={item.type==='lake'?108:58} ry="29" fill="none" stroke="#8a61ed" strokeWidth="3" strokeDasharray="8 5" className="selection-ring"/>}
  <Component color={item.color} seed={item.seed||2}/>
  {selected&&<g><rect x="-43" y="-140" width="86" height="25" rx="12" fill="#fffdf4" stroke="#d7d1ef"/><text x="0" y="-123" fill="#62527e" textAnchor="middle" fontSize="12" fontWeight="700" fontFamily="Fredoka">{item.type}</text></g>}
 </g>}
function toSvgPoint(svg,clientX,clientY){const pt=svg.createSVGPoint();pt.x=clientX;pt.y=clientY;return pt.matrixTransform(svg.getScreenCTM().inverse())}
export default function Scene({items,settings,selected,onSelect,onMove,onDragBegin,view=DEFAULT_VIEW,onView,showGuides=true}){
 const svgRef=useRef(null), dragging=useRef(null), lastKeyMove=useRef({id:null,at:0}), panning=useRef(null), suppressClick=useRef(false);
 const [isPanning,setPanning]=useState(false);
 // Two-finger pinch zooms around the midpoint; it works over objects too and cancels their drag.
 const touches=useRef(new Map()),pinch=useRef(null);
 function touchDown(e){
  if(e.pointerType!=='touch')return;
  touches.current.set(e.pointerId,{x:e.clientX,y:e.clientY});
  if(touches.current.size!==2||!onView)return;
  const [a,b]=[...touches.current.values()],svg=svgRef.current,matrix=svg.getScreenCTM().inverse(),pt=svg.createSVGPoint();
  pt.x=(a.x+b.x)/2;pt.y=(a.y+b.y)/2;
  pinch.current={distance:Math.hypot(a.x-b.x,a.y-b.y)||1,view,mid:pt.matrixTransform(matrix)};
  dragging.current=null;panning.current=null;suppressClick.current=true;
 }
 function touchMove(e){
  if(!touches.current.has(e.pointerId))return false;
  touches.current.set(e.pointerId,{x:e.clientX,y:e.clientY});
  if(!pinch.current||touches.current.size<2)return false;
  const [a,b]=[...touches.current.values()],start=pinch.current;
  onView(zoomAt(start.view,start.view.zoom*Math.hypot(a.x-b.x,a.y-b.y)/start.distance,start.mid));
  return true;
 }
 function touchUp(e){touches.current.delete(e.pointerId);if(touches.current.size<2)pinch.current=null}
 const latest=useRef({view,onView});latest.current={view,onView};
 // Ctrl/⌘ + wheel zooms around the cursor; a plain wheel keeps scrolling the page.
 useEffect(()=>{const svg=svgRef.current;function wheel(e){if(!(e.ctrlKey||e.metaKey)||!latest.current.onView)return;e.preventDefault();const {view,onView}=latest.current;onView(zoomAt(view,view.zoom+(e.deltaY<0?.1:-.1),toSvgPoint(svg,e.clientX,e.clientY)))}svg.addEventListener('wheel',wheel,{passive:false});return()=>svg.removeEventListener('wheel',wheel)},[]);
 const ordered=[...items].sort((a,b)=>(backLayers.includes(a.type)?-1000+a.y:a.y)-(backLayers.includes(b.type)?-1000+b.y:b.y));
 const isNight=settings.time==='night';
 const chosen=items.find(item=>item.id===selected);
 const anchors=chosen?.grounding?.anchorIds.map(id=>items.find(item=>item.id===id)).filter(Boolean)||[];
 const showPlacement=showGuides&&chosen?.grounding&&anchors.length===chosen.grounding.anchorIds.length;
 // A burst of arrow presses on one object is a single undo step.
 function keyMove(item,key,step){onSelect(item.id);const now=Date.now(),last=lastKeyMove.current;if(last.id!==item.id||now-last.at>800)onDragBegin?.();lastKeyMove.current={id:item.id,at:now};onMove(item.id,Math.max(77,Math.min(925,item.x+(key==='ArrowRight'?step:key==='ArrowLeft'?-step:0))),Math.max(110,Math.min(525,item.y+(key==='ArrowDown'?step:key==='ArrowUp'?-step:0))))}
 function startDrag(e,id){let obj=items.find(i=>i.id===id);if(!obj)return;const pt=toSvgPoint(svgRef.current,e.clientX,e.clientY);dragging.current={id,dx:obj.x-pt.x,dy:obj.y-pt.y,started:false,startX:pt.x,startY:pt.y};e.currentTarget.setPointerCapture(e.pointerId);onSelect(id)}
 // Dragging empty space pans when zoomed in. The matrix is frozen at the start so the
 // moving viewBox does not feed back into the pointer math.
 function startPan(e){if(view.zoom<=1||!onView||e.button>0)return;const svg=svgRef.current,matrix=svg.getScreenCTM().inverse(),toWorld=(x,y)=>{const pt=svg.createSVGPoint();pt.x=x;pt.y=y;return pt.matrixTransform(matrix)};panning.current={toWorld,origin:toWorld(e.clientX,e.clientY),view,client:[e.clientX,e.clientY]};e.currentTarget.setPointerCapture(e.pointerId);setPanning(true)}
 function move(e){if(touchMove(e))return;if(panning.current){const pan=panning.current,pt=pan.toWorld(e.clientX,e.clientY);if(Math.hypot(e.clientX-pan.client[0],e.clientY-pan.client[1])>3)suppressClick.current=true;onView(panBy(pan.view,pan.origin.x-pt.x,pan.origin.y-pt.y));return}if(!dragging.current)return;let pt=toSvgPoint(svgRef.current,e.clientX,e.clientY);if(!dragging.current.started){if(Math.hypot(pt.x-dragging.current.startX,pt.y-dragging.current.startY)<3)return;dragging.current.started=true;onDragBegin?.();}onMove(dragging.current.id,Math.max(77,Math.min(925,pt.x+dragging.current.dx)),Math.max(110,Math.min(525,pt.y+dragging.current.dy)))}
 function stop(){dragging.current=null;panning.current=null;setPanning(false)}
 return <svg ref={svgRef} className={'world-svg'+(isNight?' night':'')+(view.zoom>1?' pannable':'')+(isPanning?' panning':'')} viewBox={viewBox(view)} preserveAspectRatio="xMidYMid meet" onPointerDownCapture={touchDown} onPointerDown={startPan} onPointerMove={move} onPointerUp={stop} onPointerCancel={stop} onPointerUpCapture={touchUp} onPointerCancelCapture={touchUp} onClick={()=>{if(suppressClick.current){suppressClick.current=false;return}onSelect(null)}} role="group" aria-label="Interactive illustrated world. Select objects with Enter; move with arrow keys or drag.">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop stopColor={isNight?'#28305f':'#e3f8ff'}/><stop offset="1" stopColor={isNight?'#7371ad':'#f5fae9'}/></linearGradient>
    <linearGradient id="grass" x1="0" y1="0" x2="0" y2="1"><stop stopColor="#cfeb9c"/><stop offset="1" stopColor="#8fce83"/></linearGradient>
    <linearGradient id="islandEdge" x1="0" y1="0" x2="0" y2="1"><stop stopColor="#a1c68b"/><stop offset="1" stopColor="#6eab85"/></linearGradient>
    <linearGradient id="water" x1="0" y1="0" x2="1" y2="1"><stop stopColor="#a6e4ed"/><stop offset="1" stopColor="#6eb9d4"/></linearGradient>
    <radialGradient id="islandHalo"><stop stopColor="#c0efdc" stopOpacity=".65"/><stop offset="1" stopColor="#c0efdc" stopOpacity="0"/></radialGradient>
    <filter id="landShadow"><feGaussianBlur stdDeviation="20"/></filter>
  </defs>
  <rect width="1000" height="645" fill="url(#sky)"/>
  {isNight ? <g fill="#fff4d4">{Array.from({length:38},(_,i)=><circle key={i} cx={25+hash(i+66)*930} cy={20+hash(i+213)*330} r={1+hash(i+50)*1.5} opacity={.4+hash(i+77)*.6}/>)}<circle cx="835" cy="80" r="34" fill="#fff5c3"/><circle cx="852" cy="69" r="29" fill="#394170"/></g>
  : <g><circle cx="855" cy="91" r="45" fill="#ffe89c" opacity=".72"/>
  {[{x:127,y:118,s:1},{x:744,y:155,s:.83},{x:277,y:63,s:.6}].map((c,i)=><g key={i} transform={`translate(${c.x},${c.y}) scale(${c.s})`} fill="#fff" opacity=".9"><ellipse rx="55" ry="22"/><circle cx="-25" cy="-13" r="23"/><circle cx="10" cy="-24" r="32"/><circle cx="37" cy="-9" r="24"/></g>)}</g>}
  <ellipse cx="500" cy="495" rx="464" ry="120" fill="#517fb8" opacity=".12" filter="url(#landShadow)"/>
  <ellipse cx="500" cy="371" rx="465" ry="252" fill="url(#islandHalo)"/>
  <path d="M65 363 C79 240 250 160 489 159 C756 143 912 237 935 349L936 388 C921 515 755 573 510 576 C276 584 73 499 65 396Z" fill="url(#islandEdge)" stroke="#82ad79" strokeWidth="3"/>
  <ellipse cx="500" cy="349" rx="435" ry="218" fill="url(#grass)" stroke="#e2f1ac" strokeWidth="5"/>
  <ellipse cx="500" cy="348" rx="411" ry="196" fill="none" stroke="#f0f9ba" opacity=".35" strokeWidth="3" strokeDasharray="4 13"/>
  {Array.from({length:65},(_,i)=>{let x=130+hash(i+2)*734,y=199+hash(i+84)*301;let nx=(x-500)/410,ny=(y-348)/195;if(nx*nx+ny*ny>.85)return null;return <g key={i} transform={`translate(${x},${y}) rotate(${hash(i+90)*45-20})`} opacity=".48"><path d="M0 5l-3-8M0 5l5-10" stroke="#75ad6d" strokeWidth="2" strokeLinecap="round"/>{i%6===0&&<circle cx="0" cy="-7" r="3" fill="#fff5cb"/>}</g>})}
  {ordered.map(item=><SceneObject key={item.id} item={item} selected={selected===item.id} onSelect={onSelect} onStartDrag={startDrag} onKeyMove={keyMove}/>)}
  {showPlacement&&<g className="placement-guide" pointerEvents="none" role="group" aria-label={`Placement guide: ${chosen.grounding.relation}`}>
   {anchors.map(anchor=><g key={anchor.id}><line x1={anchor.x} y1={anchor.y} x2={chosen.x} y2={chosen.y} stroke="#7551ba" strokeWidth="2.5" strokeDasharray="6 5"/><circle cx={anchor.x} cy={anchor.y} r="8" fill="#fffdf4" stroke="#7551ba" strokeWidth="2.5"/></g>)}
   <g transform={`translate(${chosen.x},${chosen.y+36})`}><rect x="-52" y="-13" width="104" height="23" rx="10" fill="#fffdf4" stroke="#d7d1ef"/><text textAnchor="middle" y="3" fill="#62527e" fontSize="12" fontWeight="700">{RELATION_LABEL[chosen.grounding.relation]||chosen.grounding.relation}</text></g>
  </g>}
  {settings.weather==='rain'&&<g className="rain" pointerEvents="none" stroke="#82addc" strokeWidth="3" strokeLinecap="round" opacity=".75">{Array.from({length:70},(_,i)=><path key={i} d={`M${hash(i+5)*950+20} ${hash(i+555)*575} l-8 23`} style={{animationDelay:`-${hash(i+20)*1.6}s`}}/>)}</g>}
  {settings.weather==='snow'&&<g fill="#fff" pointerEvents="none">{Array.from({length:80},(_,i)=><circle key={i} cx={hash(i+5)*950+20} cy={hash(i+555)*590} r={2+hash(i+456)*3} className="snowflake" style={{animationDelay:`-${hash(i+200)*5}s`}}/>)}</g>}
  {isNight&&<rect width="1000" height="645" fill="#373878" opacity=".14" pointerEvents="none"/>}
 </svg>
}
