export const TYPES = ['house','tree','lake','river','bridge','road','flower','mountain','tower','castle','rock'];
export const TYPE_EMOJI = {house:'🏡',tree:'🌳',lake:'💧',river:'🌊',bridge:'🌉',road:'〰️',flower:'🌷',mountain:'🏔️',tower:'🗼',castle:'🏰',rock:'🪨'};
export const EXAMPLES = [
  'Build three little houses beside the lake',
  'Plant five trees near the road',
  'Add a castle behind the houses',
  'Put a bridge between two houses',
  'Make it night with rain',
  'Put two pink flowers near the castle',
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
export const snapshot = (items,settings)=>({items:items.map(x=>({...x})),settings:{...settings}});

const clamp=(v,min,max)=>Math.max(min,Math.min(max,v));
const random=(n)=>{let r=Math.sin(n*78.233+14.79)*43758.5453;return r-Math.floor(r)};
const sizes={house:84,tree:65,lake:155,road:180,river:160,bridge:86,flower:17,mountain:110,tower:80,castle:155,rock:53};
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
function overlapScore(items,type,{x,y}){
 return items.reduce((score,it)=>{
  const min=(sizes[it.type]+sizes[type])/2*.74;
  return score+Math.max(0,min-Math.hypot(it.x-x,(it.y-y)*1.15));
 },0);
}
function position(items,type,index,count,relation,anchors){
 if(relation==='between'&&anchors.length===2){
  const [a,b]=anchors,t=(index+1)/(count+1);
  return {x:a.x+(b.x-a.x)*t,y:a.y+(b.y-a.y)*t};
 }
 const anchor=anchors[0];
 if(anchor&&(relation==='inside'||relation==='across')) return {x:anchor.x+index*12,y:anchor.y};
 const candidates=[];
 if(anchor){
  const base={left:Math.PI,right:0,above:-Math.PI/2,below:Math.PI/2}[relation];
  const distance=(sizes[type]+sizes[anchor.type])/2+18;
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
 if(!valid.length&&anchor)return {...position(items,type,index,count,null,[]),unresolved:true};
 // Dense scenes may still overlap; retain the relation and choose the least crowded spot.
 return valid.reduce((best,point)=>overlapScore(items,type,point)<overlapScore(items,type,best)?point:best,valid[0]||{x:500,y:350});
}
export function applyActions(items,settings,actions,bindings=[]){
 let nextItems=items.map(x=>({...x})),nextSettings={...settings};let descriptions=[];let missing=[];let notices=[];
 const introduced=new Map(),byAction=new Map(bindings.map(binding=>[binding.action_index,binding]));
 const boundIds=indices=>new Set(indices.flatMap(index=>introduced.get(index)||[]));
 for(const [actionIndex,act] of actions.entries()){
  const binding=byAction.get(actionIndex);
  if(act.action==='reset') {nextItems=[];nextSettings={...INITIAL_SETTINGS};descriptions.push('Cleared the world');}
  else if(act.action==='setting') {if(['time','weather'].includes(act.key)){nextSettings[act.key]=act.value;descriptions.push(`Changed ${act.key} to ${act.value}`)}}
  else if(act.action==='remove'){
   const referenceIds=binding?.remove_from?boundIds(binding.remove_from):null;
   const matching=nextItems.filter(o=>o.type===act.type&&(!referenceIds||referenceIds.has(o.id)));
   const n=act.count==='all'?matching.length:clamp(Math.floor(Number(act.count)||0),0,matching.length);
   const removed=new Set(n?matching.slice(-n).map(it=>it.id):[]);nextItems=nextItems.filter(it=>!removed.has(it.id));descriptions.push(`Removed ${n} ${act.type}${n===1?'':'s'}`);
   if(referenceIds&&n<Number(act.count))notices.push('Some referenced objects were not added or are no longer available; existing unrelated objects were preserved.');
  }else if(act.action==='add'&&TYPES.includes(act.type)){
   const n=clamp(Math.floor(Number(act.count)||0),0,Math.min(16,Math.max(0,120-nextItems.length)));
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
   descriptions.push(`Added ${n} ${act.type}${n===1?'':'s'}${allGrounded?` ${act.relation||'near'} ${act.targets?act.targets.join(' and '):act.target}`:''}`);
  }
 }
 return {items:nextItems,settings:nextSettings,descriptions,missing:[...new Set(missing)],notices:[...new Set(notices)]};
}
