const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

function scenario(denied) {
  const nodes = new Map();
  const node = id => { if (!nodes.has(id)) nodes.set(id,{disabled:false,textContent:'',onclick:null}); return nodes.get(id); };
  const events = new Map();
  const calls = [];
  const track = {stop(){calls.push('stop-microphone')}};
  const stream = {getAudioTracks(){return [track]},getTracks(){return [track]}};
  const fakeRoom = {
    on(){},async join(){calls.push('join-room')}, async setLocalVideo(){},async setLocalAudio(){},
    participants(){return {}},sendAppMessage(){},async leave(){calls.push('leave-room')},async destroy(){calls.push('destroy-room')}
  };
  const context = vm.createContext({
    Map,Set,Error,JSON,Event: class {constructor(type){this.type=type}},
    navigator:{mediaDevices:{async getUserMedia(){calls.push('microphone-permission');if(denied)throw {name:'NotAllowedError'};return stream}}},
    document:{getElementById:node,addEventListener(n,fn){events.set(n,fn)},dispatchEvent(e){events.get(e.type)?.()},createElement(){return {}},body:{append(){}}},
    window:{DailyIframe:{createCallObject(options){assert.equal(options.audioSource,track);calls.push('create-room');return fakeRoom}}},
    location:{href:''},
    async fetch(){calls.push('create-call');return {status:200,ok:true,async json(){return {call_id:'test',room_url:'https://vapi.daily.co/test'}}}},
  });
  vm.runInContext(fs.readFileSync('assets/room.js','utf8'),context);
  const html=fs.readFileSync('voice.html','utf8');
  const inline=html.split('<script>').pop().split('</script>')[0];
  vm.runInContext(inline,context);
  return {node,calls};
}
(async()=>{
  let s=scenario(true);
  await s.node('start').onclick();
  assert.deepEqual(s.calls,['microphone-permission']);
  assert.match(s.node('error').textContent,/permission was denied/);
  assert.equal(s.node('start').disabled,false);
  s=scenario(false);
  await s.node('start').onclick();
  assert.deepEqual(s.calls.slice(0,4),['microphone-permission','create-call','create-room','join-room']);
  assert.equal(s.node('end').disabled,false);
  await s.node('end').onclick();
  assert.ok(s.calls.includes('stop-microphone'));
  assert.equal(s.node('start').disabled,false);
  console.log('PASS: denied microphone creates no provider call');
  console.log('PASS: permission precedes creation; source track supplied; end releases microphone');
})().catch(e=>{console.error(e);process.exitCode=1});
