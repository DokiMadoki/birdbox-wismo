/* Daily 0.92.2 joins a shared audio room; private Vapi credentials are never in the browser. */
let room = null;
let microphoneStream = null;
const players = new Map();
const statusNode = () => document.getElementById('room-status');
function setStatus(text) { statusNode().textContent = text; }
function syncAudio() {
  if (!room) return;
  const participants = room.participants();
  const keep = new Set();
  for (const participant of Object.values(participants)) {
    if (participant.local) continue;
    keep.add(participant.session_id);
    const track = participant.tracks?.audio?.persistentTrack || participant.audioTrack;
    if (!track) continue;
    let player = players.get(participant.session_id);
    if (!player) {
      player = document.createElement('audio');
      player.autoplay = true;
      player.setAttribute('playsinline', '');
      document.body.append(player);
      players.set(participant.session_id, player);
    }
    if (player.srcObject?.getAudioTracks()[0] !== track) {
      player.srcObject = new MediaStream([track]);
      player.play().catch(() => setStatus('Tap Enable sound to allow call audio.'));
    }
  }
  for (const [id, player] of players) {
    if (!keep.has(id)) { player.remove(); players.delete(id); }
  }
  const count = Object.values(participants).filter(p => !p.local).length;
  document.getElementById('participants').textContent = count + ' other room participants';
}
async function prepareMicrophone() {
  if (microphoneStream) return microphoneStream;
  if (!navigator.mediaDevices?.getUserMedia) throw Error('Microphone access is unavailable in this browser. Open this HTTPS page in Chrome or Edge.');
  try {
    microphoneStream = await navigator.mediaDevices.getUserMedia({audio: {echoCancellation: true, noiseSuppression: true}, video: false});
    return microphoneStream;
  } catch (e) {
    if (e.name === 'NotAllowedError') throw Error('Microphone permission was denied. Allow the microphone for this site, then retry.');
    if (e.name === 'NotFoundError') throw Error('No microphone was found. Connect one, then retry.');
    if (e.name === 'NotReadableError') throw Error('The microphone is unavailable or in use. Close other calling apps, then retry.');
    throw Error('Microphone setup failed: ' + e.name);
  }
}
function releaseMicrophone() {
  microphoneStream?.getTracks().forEach(track => track.stop());
  microphoneStream = null;
}
async function joinRoom(url, name, startMuted = false) {
  if (room) throw Error('Already on a call');
  const media = await prepareMicrophone();
  room = window.DailyIframe.createCallObject({audioSource: media.getAudioTracks()[0], videoSource: false});
  room.on('participant-joined', syncAudio);
  room.on('participant-updated', syncAudio);
  room.on('participant-left', syncAudio);
  room.on('track-started', async e => {
    syncAudio();
    if (!e.participant?.local && e.track?.kind === 'audio' && e.participant?.user_name === 'Vapi Speaker') {
      let player = players.get(e.participant.session_id);
      if (!player) {
        player = document.createElement('audio'); player.autoplay = true; document.body.append(player); players.set(e.participant.session_id, player);
      }
      player.srcObject = new MediaStream([e.track]);
      try { await player.play(); room?.sendAppMessage('playable'); } catch { setStatus('Tap Enable sound to allow call audio.'); }
    }
  });
  room.on('app-message', e => {
    if (e.data === 'listening') setStatus('Robin is connected. You can speak now.');
    else try {
      const message = typeof e.data === 'string' ? JSON.parse(e.data) : e.data;
      if (message?.type === 'status-update' && message.status === 'ended') setStatus('Call ended: ' + (message.endedReason || 'disconnected'));
    } catch {}
  });
  room.on('left-meeting', () => {
    setStatus('The call disconnected. You can start a new call.');
    document.dispatchEvent(new Event('birdbox-call-ended'));
  });
  room.on('error', e => setStatus('Room connection error: ' + (e.errorMsg || e.error?.msg || 'connection lost')));
  try {
    await room.join({url, userName: name, startVideoOff: true, startAudioOff: startMuted});
    await room.setLocalVideo(false);
    await room.setLocalAudio(!startMuted);
    syncAudio();
    setStatus('Audio room joined. Waiting for Robin…');
  } catch (e) {
    await leaveRoom();
    throw e;
  }
}
async function leaveRoom() {
  if (!room) { releaseMicrophone(); return; }
  const old = room;
  room = null;
  try { await old.leave(); } finally { await old.destroy(); releaseMicrophone(); }
  for (const player of players.values()) player.remove();
  players.clear();
  document.getElementById('participants').textContent = '';
}
document.getElementById('sound').onclick = () => {
  for (const player of players.values()) player.play().then(() => room?.sendAppMessage('playable')).catch(() => {});
};
async function api(path, payload) {
  const response = await fetch(path, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload || {})});
  if (response.status === 401) { location.href = '/login'; throw Error('Sign in first.'); }
  let result;
  try { result = await response.json(); } catch { throw Error('Service did not respond. Retry after it wakes up.'); }
  if (!response.ok) throw Error(result.detail || 'Request failed');
  return result;
}
