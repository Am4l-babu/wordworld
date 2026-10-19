export const TYPES = ['house','tree','lake','river','bridge','road','flower','mountain','tower','castle','rock'];
export const PALETTE={red:'#ed786f',blue:'#74a6ea',yellow:'#f5bc59',pink:'#eaa2bc',purple:'#a78bd8',green:'#80bea1',orange:'#f4a565',white:'#f7efe5'};
// Sprites whose fill reflects a color: house roofs, tree leaves and flower petals.
export const COLOR_PART={house:'Roof color',tree:'Leaf color',flower:'Petal color'};
export const MAX_ITEMS=120;
export const RELATION_LABEL={above:'behind',below:'in front of',left:'left of',right:'right of',near:'near',between:'between',inside:'inside',across:'across'};
export const TYPE_EMOJI = {house:'🏡',tree:'🌳',lake:'💧',river:'🌊',bridge:'🌉',road:'〰️',flower:'🌷',mountain:'🏔️',tower:'🗼',castle:'🏰',rock:'🪨'};
export const EXAMPLES = [
  'Build three little houses beside the lake',
  'Plant five trees near the road',
  'Add a castle behind the houses',
  'Put a bridge between two houses',
  'Make it night with rain',
  'Put two pink flowers near the castle',
  'Paint the houses blue and make them bigger',
  'Move the castle behind the lake',
];
let unique=0;
export const makeItem=(type,x,y,color,scale=1)=>({id:`w-${Date.now().toString(36)}-${(++unique).toString(36)}`,type,x,y,color:color||undefined,seed:unique*47,scale});
export const initialItems = () => [
  makeItem('road',477,402),
  makeItem('river',724,374),
  makeItem('lake',660,275),
  makeItem('bridge',751,376),
  makeItem('house',294,317,'red',1.08),
  makeItem('house',416,381,'yellow',.88),
  makeItem('tree',186,318,undefined,.95),
  makeItem('tree',230,246,undefined,.9),
  makeItem('tree',286,213,undefined,.75),
  makeItem('tree',455,208,undefined,.8),
  makeItem('tree',558,251,undefined,.76),
  makeItem('tree',822,268,undefined,.92),
  makeItem('tree',852,353,undefined,.65),
  makeItem('tree',195,438,undefined,.7),
  makeItem('tree',521,487,undefined,.75),
  makeItem('flower',374,290),makeItem('flower',358,329),makeItem('flower',517,311),
  makeItem('flower',596,456),makeItem('flower',555,457),makeItem('flower',762,493),
  makeItem('rock',831,433),
];
export const INITIAL_SETTINGS={time:'day',weather:'clear'};
const SETTING_VALUES={time:['day','night'],weather:['clear','rain','snow']};
export const snapshot = (items,settings)=>({items:items.map(x=>({...x})),settings:{...settings}});

const clamp=(v,min,max)=>Math.max(min,Math.min(max,v));
const random=(n)=>{let r=Math.sin(n*78.233+14.79)*43758.5453;return r-Math.floor(r)};
const sizes={house:84,tree:65,lake:155,road:180,river:160,bridge:86,flower:17,mountain:110,tower:80,castle:155,rock:53};
// Saved and imported scenes come from outside the app: keep only drawable objects,
// give them fresh unique ids and keep placement guides only when every landmark survives.
export function cleanScene(obj){
 if(!obj||typeof obj!=='object'||!Array.isArray(obj.items))return null;
 const ids=new Map();
 const entries=obj.items.filter(it=>it&&TYPES.includes(it.type)&&Number.isFinite(it.x)&&Number.isFinite(it.y)).slice(0,MAX_ITEMS).map(it=>{
  const spot=clampToCanvas(it),item=makeItem(it.type,spot.x,spot.y,PALETTE[it.color]?it.color:undefined,Number.isFinite(it.scale)?clamp(it.scale,.3,2):1);
  if(Number.isFinite(it.seed))item.seed=it.seed;
  if(typeof it.id==='string')ids.set(it.id,item.id);
  return {item,grounding:it.grounding};
 });
 for(const {item,grounding:g} of entries)if(g&&RELATION_LABEL[g.relation]&&Array.isArray(g.anchorIds)&&g.anchorIds.length&&g.anchorIds.every(id=>ids.has(id)))item.grounding={relation:g.relation,anchorIds:g.anchorIds.map(id=>ids.get(id))};
 const s=obj.settings&&typeof obj.settings==='object'?obj.settings:{};
 return {items:entries.map(e=>e.item),settings:{time:s.time==='night'?'night':'day',weather:['rain','snow'].includes(s.weather)?s.weather:'clear'}};
}
// Drop placement guides whose landmarks are gone (after a removal, reset or delete).
export function pruneGuides(items){
 const ids=new Set(items.map(o=>o.id));
 return items.map(o=>o.grounding&&!o.grounding.anchorIds.every(id=>ids.has(id))?{...o,grounding:undefined}:o);
}
// Objects stay inside the same bounds dragging uses.
const clampToCanvas=({x,y})=>({x:clamp(x,77,925),y:clamp(y,110,525)});
// Resolve once per action, so adding trees near trees cannot change its own anchor.
function resolveAnchors(items,act,allowedIds){
 const types=act.relation==='between'?act.targets||[act.target,act.target]:act.target?[act.target]:[];
 const used=new Set(),anchors=[];
 for(const type of types){
  const anchor=[...items].reverse().find(o=>o.type===type&&!used.has(o.id)&&(!allowedIds||allowedIds.has(o.id)));
  if(anchor){anchors.push(anchor);used.add(anchor.id)}
 }
 return anchors;
}
const onIsland=({x,y})=>((x-500)/390)**2+((y-350)/155)**2<=1;
// Footprints grow with each object's scale, so an enlarged castle keeps its distance.
function overlapScore(items,type,{x,y},scale=1){
 return items.reduce((score,it)=>{
  const min=(sizes[it.type]*(it.scale||1)+sizes[type]*scale)/2*.74;
  return score+Math.max(0,min-Math.hypot(it.x-x,(it.y-y)*1.15));
 },0);
}
function position(items,type,index,count,relation,anchors,scale=1){
 if(relation==='between'&&anchors.length===2){
  const [a,b]=anchors,t=(index+1)/(count+1);
  return {x:a.x+(b.x-a.x)*t,y:a.y+(b.y-a.y)*t};
 }
 const anchor=anchors[0];
 if(anchor&&(relation==='inside'||relation==='across')) return clampToCanvas({x:anchor.x+(index%2?1:-1)*Math.ceil(index/2)*12,y:anchor.y});
 const candidates=[];
 if(anchor){
  const base={left:Math.PI,right:0,above:-Math.PI/2,below:Math.PI/2}[relation];
  const distance=(sizes[type]*scale+sizes[anchor.type]*(anchor.scale||1))/2+18;
  for(const radius of [1,1.35,1.75,2.2]){
   for(let step=0;step<16;step++){
    const angle=base===undefined?.5+(step+index)*2.399:base+((step+index)%16/15-.5)*1.6;
    candidates.push({x:anchor.x+Math.cos(angle)*distance*radius,y:anchor.y+Math.sin(angle)*distance*radius*.67});
   }
  }
 }else{
  for(let step=0;step<100;step++){
   const angle=(step+items.length)*2.399,radius=step===0?0:Math.sqrt((step+.5)/100);
   candidates.push({x:500+Math.cos(angle)*radius*380,y:350+Math.sin(angle)*radius*150});
  }
 }
 const valid=candidates.filter(onIsland);
 if(!valid.length&&anchor)return {...position(items,type,index,count,null,[],scale),unresolved:true};
 // Dense scenes may still overlap; retain the relation and choose the least crowded spot.
 return valid.reduce((best,point)=>overlapScore(items,type,point,scale)<overlapScore(items,type,best,scale)?point:best,valid[0]||{x:500,y:350});
}
// The color a sprite actually shows: houses draw a red roof when no color is set.
export const shownColor=o=>o.color||(o.type==='house'?'red':undefined);
const plural=(type,n)=>`${n} ${type}${n===1?'':'s'}`;
const STEP={small:35,medium:75,large:150};
const DIRECTION={left:[-1,0],right:[1,0],up:[0,-1],down:[0,1]};
const DIRECTION_LABEL={left:'left',right:'right',up:'back',down:'forward'};
const VERB={recolor:'repaint',resize:'resize',move:'move'};
// "the trees near the lake": does `item` sit in the named relation to any landmark? The tests mirror
// where placement puts objects (the same cone and squash), so what you add "left of" a house is found
// by a later "left of the house" filter.
export function inPlace(item,anchors,relation){
 return anchors.some(anchor=>{
  if(anchor.id===item.id)return false;
  const dx=item.x-anchor.x,dy=item.y-anchor.y,distance=Math.hypot(dx,dy*1.15);
  const reach=(sizes[item.type]*(item.scale||1)+sizes[anchor.type]*(anchor.scale||1))/2;
  if(relation==='near')return distance<=reach+80;
  if(relation==='inside')return distance<=sizes[anchor.type]*(anchor.scale||1)/2;
  const base={left:Math.PI,right:0,above:-Math.PI/2,below:Math.PI/2}[relation];
  if(base===undefined)return false;
  let turn=Math.abs(Math.atan2(dy/.67,dx)-base);
  if(turn>Math.PI)turn=2*Math.PI-turn;
  return turn<=.9;  // anywhere on that side, within the same cone placement uses
 });
}
// Objects an action may touch: its type, any referenced ids, color and place filters. Edits and
// removals both act on the most recent matches.
function candidates(items,act,referenceIds){
 const anchors=act.filter_relation?items.filter(o=>o.type===act.filter_target):null;
 const matching=items.filter(o=>o.type===act.type&&(!referenceIds||referenceIds.has(o.id))&&(!act.filter_color||shownColor(o)===act.filter_color)
  &&(!anchors||inPlace(o,anchors,act.filter_relation)));
 return {matching,noAnchor:Boolean(anchors&&!anchors.length)};
}
const describeFilter=act=>act.filter_relation?` ${RELATION_LABEL[act.filter_relation]||act.filter_relation} the ${act.filter_target}`:'';
function editTargets(items,act,referenceIds){
 const {matching,noAnchor}=candidates(items,act,referenceIds);
 const n=act.count==='all'?matching.length:clamp(Math.floor(Number(act.count)||0),0,matching.length);
 return {matching,noAnchor,chosen:n?matching.slice(-n):[]};
}
// Walk back toward the start until the point is on the island again.
function stepOnIsland(item,dx,dy){
 for(let t=1;t>.1;t-=.1){const point={x:item.x+dx*t,y:item.y+dy*t};if(onIsland(point))return {...point,t}}
 return {x:item.x,y:item.y,t:0};
}
// `context` holds the objects the previous command touched ({type, ids}), oldest first.
// Bindings refer to them with negative indexes, so "make it blue" edits exactly those objects.
export function applyActions(items,settings,actions,bindings=[],context=[]){
 let nextItems=items.map(x=>({...x})),nextSettings={...settings};let descriptions=[];let missing=[];let notices=[];const touched=[];
 const introduced=new Map(context.map((group,k)=>[-(k+1),group.ids])),byAction=new Map(bindings.map(binding=>[binding.action_index,binding]));
 const boundIds=indices=>new Set(indices.flatMap(index=>introduced.get(index)||[]));
 const replace=updated=>{const byId=new Map(updated.map(o=>[o.id,o]));nextItems=nextItems.map(o=>byId.get(o.id)||o)};
 for(const [actionIndex,act] of actions.entries()){
  const binding=byAction.get(actionIndex);
  if(act.action==='reset') {nextItems=[];nextSettings={...INITIAL_SETTINGS};descriptions.push('Cleared the world');}
  else if(['recolor','resize','move'].includes(act.action)&&TYPES.includes(act.type)){
   const referenceIds=binding?.edit_from?boundIds(binding.edit_from):null;
   const {matching,noAnchor,chosen}=editTargets(nextItems,act,referenceIds);
   const label=`${act.filter_color?act.filter_color+' ':''}${act.type}s${describeFilter(act)}`;
   introduced.set(actionIndex,chosen.map(o=>o.id));
   if(noAnchor){notices.push(`There is no ${act.filter_target} to measure from, so no ${act.type}s were ${VERB[act.action]==='repaint'?'repainted':VERB[act.action]+'d'}.`);continue}
   if(!matching.length){notices.push(referenceIds?`The ${act.type} you referred to is no longer in the world.`:`There are no ${label} to ${VERB[act.action]}.`);continue}
   if(act.count!=='all'&&chosen.length<Number(act.count))notices.push(`Only ${plural(act.type,chosen.length)} could be found to ${VERB[act.action]}.`);
   if(act.action==='recolor'){
    replace(chosen.map(o=>({...o,color:act.color})));
    descriptions.push(`Painted ${plural(act.type,chosen.length)} ${act.color}`);
   }else if(act.action==='resize'){
    const resized=chosen.map(o=>({...o,scale:Math.round(clamp((o.scale||1)*act.scale,.45,1.9)*100)/100}));
    if(resized.every((o,i)=>o.scale===(chosen[i].scale||1)))notices.push(`The ${act.type} is already as ${act.scale>1?'big':'small'} as it can be.`);
    replace(resized);
    descriptions.push(`Made ${plural(act.type,chosen.length)} ${act.scale>1?'bigger':'smaller'}`);
   }else if(act.direction){
    const [ux,uy]=DIRECTION[act.direction]||[0,0],step=STEP[act.distance]||STEP.medium;
    const moved=chosen.map(o=>{const p=stepOnIsland(o,ux*step,uy*step*.6);if(p.t<1)notices.push(`The island edge stopped the ${act.type} early.`);return {...o,x:p.x,y:p.y,grounding:undefined}});
    replace(moved);
    descriptions.push(`Moved ${plural(act.type,chosen.length)} ${DIRECTION_LABEL[act.direction]}`);
   }else{
    // Landmarks come from everything except the objects being moved.
    const movingIds=new Set(chosen.map(o=>o.id)),others=nextItems.filter(o=>!movingIds.has(o.id));
    const anchors=resolveAnchors(others,act,binding?.target_from?boundIds(binding.target_from):null);
    const required=act.relation==='between'?2:1;
    if(anchors.length<required){notices.push(`Couldn't find ${act.relation==='between'?`two distinct landmarks (${(act.targets||[act.target,act.target]).join(' and ')})`:`a ${act.target}`} to move next to; nothing moved.`);continue}
    const placed=[...others],moved=[];
    chosen.forEach((o,i)=>{
     const {x,y,unresolved}=position(placed,act.type,i,chosen.length,act.relation,anchors,o.scale||1);
     if(unresolved){notices.push(`No space on the island ${RELATION_LABEL[act.relation]} the ${act.target}; the ${act.type} stayed put.`);moved.push(o);placed.push(o);return}
     const next={...o,x,y,grounding:{relation:act.relation,anchorIds:anchors.map(a=>a.id)}};
     moved.push(next);placed.push(next);
    });
    replace(moved);
    const count=moved.filter((o,i)=>o!==chosen[i]).length;
    if(count)descriptions.push(`Moved ${plural(act.type,count)} ${RELATION_LABEL[act.relation]||act.relation} ${(act.targets||[act.target]).join(' and ')}`);
   }
   touched.push(...chosen.map(o=>o.id));
  }
  else if(act.action==='setting') {if(SETTING_VALUES[act.key]?.includes(act.value)){nextSettings[act.key]=act.value;descriptions.push(`Changed ${act.key} to ${act.value}`)}}
  else if(act.action==='remove'){
   const referenceIds=binding?.remove_from?boundIds(binding.remove_from):null;
   const {matching,noAnchor}=candidates(nextItems,act,referenceIds);
   const n=act.count==='all'?matching.length:clamp(Math.floor(Number(act.count)||0),0,matching.length);
   const removed=new Set(n?matching.slice(-n).map(it=>it.id):[]);nextItems=nextItems.filter(it=>!removed.has(it.id));
   if(noAnchor)notices.push(`There is no ${act.filter_target} to measure from, so nothing was removed.`);
   else descriptions.push(`Removed ${n} ${act.type}${n===1?'':'s'}${describeFilter(act)}`);
   if(!matching.length&&!referenceIds&&!noAnchor)notices.push(act.filter_relation?`There are no ${act.type}s${describeFilter(act)} to remove.`:`There are no ${act.type}s in the world to remove.`);
   if(referenceIds&&n<Number(act.count))notices.push('Some referenced objects were not added or are no longer available; existing unrelated objects were preserved.');
  }else if(act.action==='add'&&TYPES.includes(act.type)){
   const n=clamp(Math.floor(Number(act.count)||0),0,Math.min(16,Math.max(0,MAX_ITEMS-nextItems.length)));
   if(n<Number(act.count))notices.push('Scene capacity limited the number of new objects.');
   const referenceIds=binding?.target_from?boundIds(binding.target_from):null;
   const anchors=resolveAnchors(nextItems,act,referenceIds);
   const required=act.relation==='between'?2:act.target?1:0;
   if(anchors.length<required)missing.push(act.relation==='between'?`two distinct landmarks (${(act.targets||[act.target,act.target]).join(' and ')})`:act.target);
   const grounded=anchors.length===required&&required>0;
   let allGrounded=grounded;const newIds=[];
   for(let i=0;i<n;i++){
    const {x,y,unresolved}=position(nextItems,act.type,i,n,grounded?act.relation:null,grounded?anchors:[]);
    const item=makeItem(act.type,x,y,act.color,act.type==='flower'?.85+random(i+items.length)*.25:.88+random(i+items.length)*.17);
    if(grounded&&!unresolved)item.grounding={relation:act.relation,anchorIds:anchors.map(a=>a.id)};
    if(unresolved){allGrounded=false;notices.push(`No space on the island for ${act.type} ${act.relation} ${act.target}; used available space.`)}
    nextItems.push(item);
    newIds.push(item.id);
   }
   introduced.set(actionIndex,newIds);
   touched.push(...newIds);
   descriptions.push(`Added ${n} ${act.type}${n===1?'':'s'}${allGrounded?` ${RELATION_LABEL[act.relation]||act.relation||'near'} ${act.targets?act.targets.join(' and '):act.target}`:''}`);
  }
 }
 nextItems=pruneGuides(nextItems);
 const remaining=new Set(nextItems.map(o=>o.id));
 return {items:nextItems,settings:nextSettings,descriptions,missing:[...new Set(missing)],notices:[...new Set(notices)],touched:[...new Set(touched)].filter(id=>remaining.has(id))};
}
// Group the focused objects by type, in order, for the parser's cross-request context.
export function focusGroups(items,ids){
 const byId=new Map(items.map(o=>[o.id,o])),groups=[];
 for(const id of ids){
  const item=byId.get(id);if(!item)continue;
  const last=groups.at(-1);
  if(last?.type===item.type)last.ids.push(id);else groups.push({type:item.type,ids:[id]});
 }
 return groups.slice(-12);
}
export const describeFocus=groups=>groups.map(g=>plural(g.type,g.ids.length)).join(' + ');
