/* Daily 0.92.2 joins a shared audio room; private Vapi credentials are never in the browser. */
let room = null;
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
  room.sendAppMessage('playable');
}
async function joinRoom(url, name, startMuted = false) {
  if (room) throw Error('Already on a call');
  room = window.DailyIframe.createCallObject({videoSource: false});
  room.on('participant-joined', syncAudio);
  room.on('participant-updated', syncAudio);
  room.on('participant-left', syncAudio);
  room.on('track-started', syncAudio);
  room.on('left-meeting', () => { setStatus('Call ended.'); });
  room.on('error', () => setStatus('Room connection error. End the call and retry.'));
  try {
    await room.join({url, userName: name, startVideoOff: true, startAudioOff: startMuted});
    await room.setLocalVideo(false);
    syncAudio();
    setStatus('Connected to the audio room.');
  } catch (e) {
    await leaveRoom();
    throw e;
  }
}
async function leaveRoom() {
  if (!room) return;
  const old = room;
  room = null;
  try { await old.leave(); } finally { await old.destroy(); }
  for (const player of players.values()) player.remove();
  players.clear();
  document.getElementById('participants').textContent = '';
}
document.getElementById('sound').onclick = () => {
  for (const player of players.values()) player.play().catch(() => {});
};
async function api(path, payload) {
  const response = await fetch(path, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload || {})});
  if (response.status === 401) { location.href = '/login'; throw Error('Sign in first.'); }
  let result;
  try { result = await response.json(); } catch { throw Error('Service did not respond. Retry after it wakes up.'); }
  if (!response.ok) throw Error(result.detail || 'Request failed');
  return result;
}
