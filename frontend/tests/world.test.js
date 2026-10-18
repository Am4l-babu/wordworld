import {test} from 'node:test';
import assert from 'node:assert/strict';
import {applyActions,makeItem,cleanScene,focusGroups,inPlace,INITIAL_SETTINGS,MAX_ITEMS} from '../src/world.js';
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

test('imported scenes keep only drawable objects with fresh ids and remapped guides',()=>{
 const scene=cleanScene({items:[
  {id:'a',type:'house',x:300,y:320,color:'blue'},
  {id:'b',type:'tree',x:360,y:330,color:'chartreuse',grounding:{relation:'near',anchorIds:['a']}},
  {id:'c',type:'dragon',x:1,y:1},{id:'d',type:'rock',x:'oops',y:2},
  {id:'e',type:'flower',x:9999,y:-50,grounding:{relation:'near',anchorIds:['missing']}},
 ],settings:{time:'night',weather:'hail'}});
 assert.deepEqual(scene.items.map(o=>o.type),['house','tree','flower']);
 assert.equal(scene.items[0].color,'blue');
 assert.equal(scene.items[1].color,undefined);
 assert.deepEqual(scene.items[1].grounding,{relation:'near',anchorIds:[scene.items[0].id]});
 assert.equal(scene.items[2].grounding,undefined);
 assert.deepEqual([scene.items[2].x,scene.items[2].y],[1000,0]);
 assert.notEqual(scene.items[0].id,'a');
 assert.deepEqual(scene.settings,{time:'night',weather:'clear'});
});
test('non-scene files are rejected and oversized scenes are capped',()=>{
 for(const bad of [null,42,'x',{},{items:'nope'}])assert.equal(cleanScene(bad),null);
 const many=cleanScene({items:Array.from({length:200},(_,i)=>({type:'rock',x:i,y:i}))});
 assert.equal(many.items.length,MAX_ITEMS);
 assert.equal(new Set(many.items.map(o=>o.id)).size,MAX_ITEMS);
});
test('removing a type that is absent explains why nothing changed',()=>{
 const result=apply([makeItem('house',300,350)],[{action:'remove',type:'castle',count:1}]);
 assert.equal(result.items.length,1);
 assert.deepEqual(result.notices,['There are no castles in the world to remove.']);
});

test('edits repaint, resize and move only the most recent matching objects',()=>{
 const red=makeItem('house',300,320,'red'),plain=makeItem('house',400,330),lake=makeItem('lake',650,300);
 let r=apply([red,plain,lake],[{action:'recolor',type:'house',count:1,color:'blue'}]);
 assert.deepEqual(r.items.map(o=>o.color),['red','blue',undefined]);
 assert.deepEqual(r.touched,[plain.id]);
 r=apply([red,plain,lake],[{action:'recolor',type:'house',count:'all',color:'pink',filter_color:'red'}]);
 assert.deepEqual(r.items.map(o=>o.color),['pink','pink',undefined]);
 r=apply([red,plain],[{action:'resize',type:'house',count:'all',scale:1.25}]);
 assert.deepEqual(r.items.map(o=>o.scale),[1.25,1.25]);
 r=apply([makeItem('house',300,320,null,1.85)],[{action:'resize',type:'house',count:1,scale:1.25}]);
 assert.equal(r.items[0].scale,1.9);
 assert.deepEqual(r.notices,[]);
 r=apply(r.items,[{action:'resize',type:'house',count:1,scale:1.25}]);
 assert.deepEqual(r.notices,['The house is already as big as it can be.']);
 r=apply([red,lake],[{action:'move',type:'house',count:1,relation:'left',target:'lake'}]);
 const moved=r.items[0];
 assert.ok(moved.x<lake.x);
 assert.deepEqual(moved.grounding,{relation:'left',anchorIds:[lake.id]});
 r=apply([red],[{action:'move',type:'house',count:1,direction:'right',distance:'medium'}]);
 assert.deepEqual([r.items[0].x,r.items[0].y],[375,320]);
});
test('edits explain missing objects and never move without a landmark',()=>{
 let r=apply([makeItem('tree',300,320)],[{action:'recolor',type:'house',count:1,color:'blue'}]);
 assert.deepEqual(r.notices,['There are no houses to repaint.']);
 const house=makeItem('house',300,320);
 r=apply([house],[{action:'move',type:'house',count:1,relation:'near',target:'lake'}]);
 assert.deepEqual([r.items[0].x,r.items[0].y],[300,320]);
 assert.match(r.notices[0],/Couldn't find a lake/);
 r=apply([makeItem('house',880,350)],[{action:'move',type:'house',count:1,direction:'right',distance:'large'}]);
 assert.ok(r.items[0].x>=880&&((r.items[0].x-500)/390)**2+((r.items[0].y-350)/155)**2<=1);
});
test('context bindings let "it" edit exactly the objects the last command touched',()=>{
 const older=makeItem('castle',300,320),newer=makeItem('house',400,320),target=makeItem('house',500,320);
 const r=applyActions([older,newer,target],INITIAL_SETTINGS,[{action:'recolor',type:'house',count:1,color:'blue'}],[{action_index:0,edit_from:[-1]}],[{type:'house',ids:[newer.id]}]);
 assert.deepEqual(r.items.map(o=>o.color),[undefined,'blue',undefined]);
 const gone=applyActions([older],INITIAL_SETTINGS,[{action:'recolor',type:'house',count:1,color:'blue'}],[{action_index:0,edit_from:[-1]}],[{type:'house',ids:['deleted']}]);
 assert.match(gone.notices[0],/no longer in the world/);
 assert.deepEqual(focusGroups([older,newer,target],[newer.id,target.id,older.id,'missing']),[{type:'house',ids:[newer.id,target.id]},{type:'castle',ids:[older.id]}]);
});
test('a move with no room reports that the object stayed put without claiming it moved',()=>{
 const lake=makeItem('lake',500,197),castle=makeItem('castle',500,450);
 const r=apply([lake,castle],[{action:'move',type:'castle',count:1,relation:'above',target:'lake'}]);
 assert.deepEqual([r.items[1].x,r.items[1].y],[500,450]);
 assert.deepEqual(r.descriptions,[]);
 assert.match(r.notices[0],/stayed put/);
});

test('edits and removals filtered by place touch only objects in that place',()=>{
 const lake=makeItem('lake',700,300),nearTree=makeItem('tree',640,330),farTree=makeItem('tree',200,300);
 let r=apply([lake,nearTree,farTree],[{action:'recolor',type:'tree',count:'all',color:'red',filter_relation:'near',filter_target:'lake'}]);
 assert.deepEqual(r.items.map(o=>o.color),[undefined,'red',undefined]);
 assert.deepEqual(r.descriptions,['Painted 1 tree red']);
 r=apply([lake,nearTree,farTree],[{action:'remove',type:'tree',count:'all',filter_relation:'near',filter_target:'lake'}]);
 assert.deepEqual(r.items.map(o=>o.id),[lake.id,farTree.id]);
 assert.deepEqual(r.descriptions,['Removed 1 tree near the lake']);
 r=apply([lake,nearTree,farTree],[{action:'resize',type:'tree',count:'all',scale:1.25,filter_relation:'left',filter_target:'lake'}]);
 assert.deepEqual(r.items.map(o=>o.scale),[1,1.25,1.25]);
});
test('a place filter without its landmark explains itself and changes nothing',()=>{
 const tree=makeItem('tree',300,300);
 let r=apply([tree],[{action:'remove',type:'tree',count:'all',filter_relation:'near',filter_target:'lake'}]);
 assert.equal(r.items.length,1);
 assert.deepEqual(r.notices,['There is no lake to measure from, so nothing was removed.']);
 r=apply([tree],[{action:'recolor',type:'tree',count:'all',color:'red',filter_relation:'near',filter_target:'lake'}]);
 assert.equal(r.items[0].color,undefined);
 assert.match(r.notices[0],/no lake to measure from/);
 const lake=makeItem('lake',700,300);
 r=apply([tree,lake],[{action:'remove',type:'tree',count:'all',filter_relation:'near',filter_target:'lake'}]);
 assert.deepEqual(r.notices,['There are no trees near the lake to remove.']);
});
for(const relation of ['left','right','above','below','near'])test(`objects placed ${relation} of a house are found by a ${relation} filter and not by its opposite`,()=>{
 const house=makeItem('house',500,350);
 const placed=apply([house],[{action:'add',type:'tree',count:6,relation,target:'house'}]).items.slice(1);
 assert.equal(placed.length,6);
 for(const tree of placed)assert.ok(inPlace(tree,[house],relation),`${relation}: ${tree.x},${tree.y}`);
 const opposite={left:'right',right:'left',above:'below',below:'above'}[relation];
 if(opposite)for(const tree of placed)assert.ok(!inPlace(tree,[house],opposite));
});
test('"inside" needs the object centre within the landmark and a lake is not inside itself',()=>{
 const lake=makeItem('lake',500,300);
 assert.ok(inPlace(makeItem('rock',520,305),[lake],'inside'));
 assert.ok(!inPlace(makeItem('rock',700,300),[lake],'inside'));
 assert.ok(!inPlace(lake,[lake],'near'));
});
