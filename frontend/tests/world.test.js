import {test} from 'node:test';
import assert from 'node:assert/strict';
import {applyActions,makeItem,INITIAL_SETTINGS} from '../src/world.js';
import {fallbackParser} from '../src/previewParser.js';

test('reference removal preserves preexisting objects of the same type',()=>{
 const old=makeItem('house',300,350);
 const result=applyActions([old],INITIAL_SETTINGS,[{action:'add',type:'house',count:1},{action:'remove',type:'house',count:1}],[{action_index:1,remove_from:[0]}]);
 assert.deepEqual(result.items.map(o=>o.id),[old.id]);
});

test('reference to a capacity-blocked creation never removes an older object',()=>{
 const old=Array.from({length:120},()=>makeItem('house',500,350));
 const result=applyActions(old,INITIAL_SETTINGS,[{action:'add',type:'house',count:1},{action:'remove',type:'house',count:1}],[{action_index:1,remove_from:[0]}]);
 assert.deepEqual(result.items.map(o=>o.id),old.map(o=>o.id));
 assert.ok(result.notices.some(n=>n.includes('unrelated objects were preserved')));
});

test('bound spatial references cannot substitute an unrelated existing landmark',()=>{
 const old=[makeItem('house',300,350)];
 const result=applyActions(old,INITIAL_SETTINGS,[{action:'add',type:'tree',count:1,relation:'near',target:'house'}],[{action_index:0,target_from:[99]}]);
 assert.equal(result.items.at(-1).grounding,undefined);
 assert.equal(result.missing.length,1);
});

const apply=(items,actions)=>applyActions(items,INITIAL_SETTINGS,actions);
test('between uses two distinct, existing houses and places exactly at midpoint',()=>{
 const houses=[makeItem('house',250,300),makeItem('house',550,400)];
 const result=apply(houses,[{action:'add',type:'bridge',count:1,relation:'between',target:'house',targets:['house','house']}]);
 assert.equal(result.items.length,3);
 const bridge=result.items.at(-1);
 assert.deepEqual([bridge.x,bridge.y],[400,350]);
 assert.equal(new Set(bridge.grounding.anchorIds).size,2);
});
test('between different types and multiple additions stay on the segment',()=>{
 const items=[makeItem('house',200,300),makeItem('lake',800,400)];
 const result=apply(items,[{action:'add',type:'flower',count:3,relation:'between',targets:['house','lake']}]);
 assert.deepEqual(result.items.slice(2).map(o=>[o.x,o.y]),[[350,325],[500,350],[650,375]]);
});
test('one house is not used twice and missing relations are reported',()=>{
 const result=apply([makeItem('house',400,320)],[{action:'add',type:'bridge',count:1,relation:'between',target:'house',targets:['house','house']}]);
 assert.equal(result.missing.length,1);
 assert.equal(result.items.at(-1).grounding,undefined);
});
test('same-type additions keep the original landmark instead of chaining',()=>{
 const anchor=makeItem('tree',500,350);
 const result=apply([anchor],[{action:'add',type:'tree',count:3,relation:'near',target:'tree'}]);
 for(const item of result.items.slice(1))assert.deepEqual(item.grounding.anchorIds,[anchor.id]);
});
for(const relation of ['left','right','above','below'])test(`${relation} remains true for a group of 16`,()=>{
 const anchor=makeItem('house',500,350);
 const result=apply([anchor],[{action:'add',type:'tree',count:16,relation,target:'house'}]);
 for(const point of result.items.slice(1)){
  assert.ok(relation==='left'?point.x<anchor.x:relation==='right'?point.x>anchor.x:relation==='above'?point.y<anchor.y:point.y>anchor.y);
  assert.ok(((point.x-500)/390)**2+((point.y-350)/155)**2<=1.00001);
 }
});
test('free placement avoids overlapping a small group',()=>{
 const result=apply([],[{action:'add',type:'house',count:5}]);
 for(let i=0;i<result.items.length;i++)for(let j=0;j<i;j++){
  const a=result.items[i],b=result.items[j];
  assert.ok(Math.hypot(a.x-b.x,(a.y-b.y)*1.15)>=84*.74);
 }
});
test('across a river is grounded at its position',()=>{
 const river=makeItem('river',650,350);
 const bridge=apply([river],[{action:'add',type:'bridge',count:1,relation:'across',target:'river'}]).items.at(-1);
 assert.deepEqual([bridge.x,bridge.y],[river.x,river.y]);
});
test('an impossible direction reports fallback instead of claiming grounding',()=>{
 const result=apply([makeItem('house',77,350)],[{action:'add',type:'tree',count:1,relation:'left',target:'house'}]);
 assert.equal(result.items.at(-1).grounding,undefined);
 assert.equal(result.notices.length,1);
 assert.equal(result.descriptions[0],'Added 1 tree');
});
test('zero removal preserves existing objects and capacity does not discard them',()=>{
 const original=Array.from({length:120},()=>makeItem('tree',500,350));
 assert.equal(apply(original,[{action:'remove',type:'tree',count:0}]).items.length,120);
 const result=apply(original,[{action:'add',type:'house',count:1}]);
 assert.deepEqual(result.items.map(o=>o.id),original.map(o=>o.id));
 assert.equal(result.notices.length,1);
});
test('offline preview never guesses negation, spatial commands, or removal',()=>{
 for(const text of ["Don't add trees",'Put a bridge between two houses','Remove trees','Add a tree and a lake'])assert.deepEqual(fallbackParser(text).actions,[]);
 assert.equal(fallbackParser('Add two red houses').actions[0].count,2);
 assert.equal(fallbackParser('No rain').actions[0].value,'clear');
});
