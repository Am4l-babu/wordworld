// Property test: long random sequences of every action type keep the scene valid.
// Seeded, so a failure reproduces exactly.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {applyActions,initialItems,INITIAL_SETTINGS,TYPES,MAX_ITEMS,focusGroups} from '../src/world.js';

let seed=12345;const rnd=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296};
const pick=a=>a[Math.floor(rnd()*a.length)],int=(a,b)=>a+Math.floor(rnd()*(b-a+1));
const COLORS=['red','blue','yellow','pink','purple','green','orange','white'],REL=['left','right','above','below','near','inside','between','across'];
const FREL=['near','left','right','above','below','inside'];
function action(){
 const type=pick(TYPES),kind=pick(['add','add','add','remove','recolor','resize','move','move','setting','reset']);
 const count=rnd()<.3?'all':int(0,20);
 if(kind==='add'){const a={action:'add',type,count:int(0,20),color:rnd()<.4?pick(COLORS):null};if(rnd()<.6){const r=pick(REL);a.relation=r;a.target=pick(TYPES);if(r==='between')a.targets=[pick(TYPES),pick(TYPES)]}return a}
 if(kind==='remove'){const a={action:'remove',type,count};if(rnd()<.4){a.filter_relation=pick(FREL);a.filter_target=pick(TYPES)}return a}
 if(kind==='recolor'){const a={action:'recolor',type,count,color:pick(COLORS)};if(rnd()<.3)a.filter_color=pick(COLORS);if(rnd()<.4){a.filter_relation=pick(FREL);a.filter_target=pick(TYPES)}return a}
 if(kind==='resize'){const a={action:'resize',type,count,scale:pick([.67,.8,1.12,1.25,1.5])};if(rnd()<.4){a.filter_relation=pick(FREL);a.filter_target=pick(TYPES)}return a}
 if(kind==='move'){const a={action:'move',type,count};if(rnd()<.5){a.direction=pick(['left','right','up','down']);a.distance=pick(['small','medium','large'])}else{const r=pick(REL);a.relation=r;a.target=pick(TYPES);if(r==='between')a.targets=[pick(TYPES),pick(TYPES)]}if(rnd()<.3){a.filter_relation=pick(FREL);a.filter_target=pick(TYPES)}return a}
 if(kind==='setting')return {action:'setting',key:pick(['time','weather','bogus']),value:pick(['day','night','rain','snow','clear','x'])};
 return {action:'reset'};
}

test('random action sequences never break scene invariants',()=>{
const problems={};const bad=(k,d)=>{problems[k]??=d};
let steps=0;
for(let run=0;run<120;run++){
 let items=rnd()<.7?initialItems():[],settings={...INITIAL_SETTINGS},ctx=[];
 for(let step=0;step<20;step++){
  const n=int(1,4),actions=Array.from({length:n},action),bindings=[];
  actions.forEach((a,i)=>{if(rnd()<.3&&ctx.length)bindings.push({action_index:i,edit_from:[-int(1,ctx.length+1)],remove_from:[-int(1,ctx.length+1)],target_from:[-int(1,3),int(0,3)]});else if(i>0&&rnd()<.2)bindings.push({action_index:i,edit_from:[int(0,i)],remove_from:[int(0,i)],target_from:[int(0,i)]})});
  let out;
  try{out=applyActions(items,settings,actions,bindings,ctx)}catch(e){bad('exception: '+e.message,{actions,bindings});break}
  steps++;
  const ids=new Set(out.items.map(o=>o.id));
  if(out.items.length>MAX_ITEMS)bad('over cap',out.items.length);
  if(ids.size!==out.items.length)bad('duplicate ids',actions);
  for(const o of out.items){
   if(!TYPES.includes(o.type))bad('bad type',o);
   if(!Number.isFinite(o.x)||!Number.isFinite(o.y))bad('non-finite position',{o,actions});
   else if(o.x<77||o.x>925||o.y<110||o.y>525)bad('outside drag bounds',{o,actions});
   if(!Number.isFinite(o.scale)||o.scale<.3||o.scale>2)bad('bad scale',{o,actions});
   if(o.grounding&&!o.grounding.anchorIds.every(id=>ids.has(id)))bad('dangling guide anchor',{o:o.type,actions});
  }
  if(!['day','night'].includes(out.settings.time)||!['clear','rain','snow'].includes(out.settings.weather))bad('bad settings',out.settings);
  if(out.touched.some(id=>!ids.has(id)))bad('touched id missing',out.touched);
  items=out.items;settings=out.settings;ctx=out.touched.length?focusGroups(items,out.touched):ctx;
 }
}
assert.ok(steps>1500);
assert.deepEqual(problems,{});
});
