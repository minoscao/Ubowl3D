import assert from 'node:assert/strict';
import { readFileSync,writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { shots,stateAt } from './dist/previs/timeline.js';

const script=JSON.parse(readFileSync(new URL('./dist/previs/script.json',import.meta.url),'utf8'));
assert.equal(shots.length,27);
assert.equal(script.scenes.length,8);
let cursor=0;
for(const shot of shots){
 assert.equal(shot.start,cursor,`Timeline gap/overlap before ${shot.id}`);
 assert(shot.end>shot.start);
 const scene=script.scenes[shot.scene-1];
 assert(shot.start>=scene.start&&shot.end<=scene.end,`Source scene boundary: ${shot.id}`);
 assert.equal(stateAt(shot.start).shot.id,shot.id);
 for(const pose of [shot.camera,shot.split].filter(Boolean)){
  assert(pose.pos.concat(pose.target).every(Number.isFinite));
  assert(pose.lens>0);
  assert(pose.pos.some((v,i)=>v!==pose.target[i]));
 }
 cursor=shot.end;
}
assert.equal(cursor,60);
assert.equal(stateAt(60).shot.id,'08B');
assert.equal(stateAt(-10).time,0);
assert.equal(stateAt(90).time,60);
for(const [t,expected] of [[36,'preparing'],[39.09,'preparing'],[39.1,'ready'],[42.49,'ready'],[42.5,'complete'],[60,'complete'],[36,'preparing']]){
 assert.equal(stateAt(t).order,expected,`Pickup state at ${t}s`);
}
assert.equal(stateAt(38.8).scanPulse,true);
assert.equal(stateAt(42.2).scanPulse,true);
assert.equal(stateAt(40).scanPulse,false);
for(const [t,expected] of [[19,'weight'],[21,'soup'],[22.8,'spice'],[24,'allergy'],[25,'dine'],[26,'pay'],[28,'receipt'],[31,'spice'],[35,'manual'],[46,'scan'],[48,'member']]){
 assert.equal(stateAt(t).screen,expected);
 const original=JSON.stringify(stateAt(t));stateAt(60);stateAt(0);
 assert.equal(JSON.stringify(stateAt(t)),original,'Scrubbing must not depend on previous playback state');
}
const glbHash=createHash('sha256').update(readFileSync(new URL('./dist/assets/UBowl_store.glb',import.meta.url))).digest('hex');
assert.equal(glbHash,'64b6f91245e1d210d8a69912d6ccd97c38f2ffc1afcdc7b57f96cc88abc24f43','Approved store model must remain unchanged');
writeFileSync(new URL('./dist/previs/shot-list.json',import.meta.url),JSON.stringify({
 title:'PiSell × U Bowl — shooting previs v1',
 source:script.source,duration:60,
 units:'metres; Y up; +Z towards customers; suggested full-frame lens in mm',
 scenes:script.scenes,shots,
},null,2));
console.log(JSON.stringify({passed:true,scenes:8,shots:27,duration:60,continuousTimeline:true,sourceSceneBoundaries:true,reverseScrubbing:true,twoScanTransitions:true,baseModelUnchanged:true,estimatedVoiceSeconds:script.scenes.reduce((sum,s)=>sum+s.readingSeconds,0)},null,2));
