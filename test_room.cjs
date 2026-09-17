const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

function scenario(denied) {
  const nodes = new Map();
  const node = id => { if (!nodes.has(id)) nodes.set(id,{disabled:false,textContent:'',onclick:null}); return nodes.get(id); };
  const events = new Map();
  const calls = [];
  const roomEvents = new Map();
  let participants = {};
  const remoteTrack = {kind:'audio'};
  const assistant = {local:false,session_id:'assistant',user_name:'Vapi Speaker',tracks:{audio:{persistentTrack:remoteTrack}}};
  const track = {stop(){calls.push('stop-microphone')}};
  const stream = {getAudioTracks(){return [track]},getTracks(){return [track]}};
  const fakeRoom = {
    on(name,fn){roomEvents.set(name,fn)},async startLocalAudioLevelObserver(){},async join(options){assert.equal(options.subscribeToTracksAutomatically,false);assert.ok(!('userName' in options));calls.push('join-room');participants={assistant};roomEvents.get('participant-joined')({participant:assistant})}, async setLocalVideo(){},async setLocalAudio(){},
    participants(){return participants},updateParticipant(id,options){assert.equal(id,'assistant');assert.equal(options.setSubscribedTracks.audio,true);calls.push('subscribe-assistant')},sendAppMessage(message){calls.push(message)},async leave(){calls.push('leave-room')},async destroy(){calls.push('destroy-room')}
  };
  const context = vm.createContext({
    Map,Set,Error,JSON,MediaStream: class {constructor(tracks){this.tracks=tracks}getAudioTracks(){return this.tracks}},Event: class {constructor(type){this.type=type}},
    navigator:{mediaDevices:{async getUserMedia(){calls.push('microphone-permission');if(denied)throw {name:'NotAllowedError'};return stream}}},
    document:{getElementById:node,addEventListener(n,fn){events.set(n,fn)},dispatchEvent(e){events.get(e.type)?.()},createElement(){return {setAttribute(){},async play(){calls.push('play-audio')},remove(){}}},body:{append(){}}},
    window:{DailyIframe:{createCallObject(options){assert.equal(options.audioSource,track);calls.push('create-room');return fakeRoom}}},
    location:{href:''},
    async fetch(){calls.push('create-call');return {status:200,ok:true,async json(){return {call_id:'test',room_url:'https://vapi.daily.co/test'}}}},
  });
  vm.runInContext(fs.readFileSync('assets/room.js','utf8'),context);
  const html=fs.readFileSync('voice.html','utf8');
  const inline=html.split('<script>').pop().split('</script>')[0];
  vm.runInContext(inline,context);
  return {node,calls,roomEvents,assistant,remoteTrack};
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
  assert.ok(s.calls.includes('subscribe-assistant'));
  await s.roomEvents.get('track-started')({participant:s.assistant,track:s.remoteTrack});
  assert.ok(s.calls.indexOf('playable') > s.calls.indexOf('play-audio'));
  s.roomEvents.get('local-audio-level')({audioLevel:0.05});
  assert.match(s.node('mic-level').textContent,/sound detected/);
  await s.node('end').onclick();
  assert.ok(s.calls.includes('stop-microphone'));
  assert.equal(s.node('start').disabled,false);
  console.log('PASS: denied microphone creates no provider call');
  console.log('PASS: permission precedes creation; source track supplied; end releases microphone');
  console.log('PASS: assistant audio subscribed; playback signals readiness; microphone activity shown');
})().catch(e=>{console.error(e);process.exitCode=1});
