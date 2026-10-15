import {test} from 'node:test';
import assert from 'node:assert/strict';
import {makeItem,INITIAL_SETTINGS,MAX_ITEMS} from '../src/world.js';
import {encodeWorld,decodeWorld,MAX_SHARE_CODE} from '../src/share.js';
import {DEFAULT_VIEW,clampView,zoomAt,panBy,viewBox,isVisible} from '../src/view.js';
import {describeToken,headIndex,tokenRoles} from '../src/grammar.js';

test('share links round-trip objects, colors, settings and placement guides',()=>{
 const house=makeItem('house',300,320,'blue',1.08),tree=makeItem('tree',360,330,'purple',.9);
 tree.grounding={relation:'right',anchorIds:[house.id]};
 const world=decodeWorld(encodeWorld([house,tree],{time:'night',weather:'snow'}));
 assert.deepEqual(world.items.map(o=>[o.type,o.x,o.y,o.color,o.scale]),[['house',300,320,'blue',1.08],['tree',360,330,'purple',.9]]);
 assert.equal(world.items[1].seed,tree.seed);
 assert.deepEqual(world.items[1].grounding,{relation:'right',anchorIds:[world.items[0].id]});
 assert.deepEqual(world.settings,{time:'night',weather:'snow'});
});
test('a full island fits in a share link and hostile codes are rejected',()=>{
 const items=Array.from({length:MAX_ITEMS},(_,i)=>makeItem('flower',100+i*6,200+i,'pink',.95));
 const code=encodeWorld(items,INITIAL_SETTINGS);
 assert.ok(code.length<MAX_SHARE_CODE);
 assert.equal(decodeWorld(code).items.length,MAX_ITEMS);
 for(const bad of ['',null,'%%%','e30',btoa('[2,0,0,[]]'),btoa('[1,0,0,"x"]'),'a'.repeat(MAX_SHARE_CODE+1)])assert.equal(decodeWorld(bad),null);
 const odd=decodeWorld(btoa(JSON.stringify([1,0,0,[[99,1,1,0,100,0],[0,'x',1,0,100,0],[0,10,20,42,100,0,[0,7]]]])));
 assert.deepEqual(odd.items.map(o=>[o.type,o.color,o.grounding]),[['house',undefined,undefined]]);
});
test('the camera stays over the island while zooming and panning',()=>{
 assert.equal(viewBox(DEFAULT_VIEW),'0 0.5 1000 645');
 assert.deepEqual(clampView({zoom:5,x:-100,y:9999}),{zoom:2,x:250,y:645-161.25});
 assert.deepEqual(clampView({zoom:.5,x:10,y:10}),{zoom:.7,x:500,y:323});
 const zoomed=zoomAt(DEFAULT_VIEW,2,{x:300,y:200});
 assert.deepEqual([zoomed.x,zoomed.y],[400,261.5]);
 assert.deepEqual(panBy({zoom:2,x:500,y:323},1000,0),{zoom:2,x:750,y:323});
 assert.ok(isVisible(DEFAULT_VIEW,{x:500,y:300}));
 assert.ok(!isVisible({zoom:2,x:250,y:200},{x:900,y:500}));
});
test('grammar explanations name the head and grounding roles',()=>{
 const tokens=[
  {text:'Build',pos:'VERB',dep:'ROOT',start:0,end:5,head:'Build',head_start:0},
  {text:'two',pos:'NUM',dep:'nummod',start:6,end:9,head:'houses',head_start:10},
  {text:'houses',pos:'NOUN',dep:'dobj',start:10,end:16,head:'Build',head_start:0},
 ];
 assert.equal(headIndex(tokens,0),-1);
 assert.equal(headIndex(tokens,1),2);
 assert.equal(describeToken(tokens,2),'“houses” is a noun acting as the direct object of “Build”.');
 assert.match(describeToken(tokens,0),/root of the sentence/);
 assert.equal(describeToken([{text:'tree',pos:'WORD',dep:''}],0),'“tree” is a word token.');
 assert.deepEqual(tokenRoles(tokens[1],[{start:6,end:9,role:'quantity'},{start:10,end:16,role:'object'}]),['quantity']);
});
