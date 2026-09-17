const handoffPanel = document.createElement('section');
handoffPanel.className = 'panel';
handoffPanel.style.marginTop = '22px';
const heading = document.createElement('h2');
heading.textContent = 'Human support handoffs';
const links = document.createElement('p');
const voiceLink = document.createElement('a'); voiceLink.href='/voice'; voiceLink.textContent='Start a customer browser call';
const deskLink = document.createElement('a'); deskLink.href='/support'; deskLink.textContent='Open support desk';
links.append(voiceLink,document.createTextNode(' · '),deskLink);
const handoffContent = document.createElement('div');
handoffPanel.append(heading,links,handoffContent);
document.querySelector('main').insertBefore(handoffPanel,document.querySelector('footer'));
async function loadHandoffs(){
  try{
    const r=await fetch('/support/queue'); if(!r.ok)return;
    const data=await r.json();handoffContent.replaceChildren();
    const joined=data.handoffs.filter(h=>h.joined_at!=null).length;
    const note=document.createElement('p');note.className='muted';
    note.textContent=data.handoffs.length+' recorded requests · '+joined+' reported rep joins · '+(data.rep_available?'Rep available':'No rep currently available')+'. A reported join means browser room join and accepted AI mute; two-way audio must be checked in the demo.';
    handoffContent.append(note);
    for(const h of data.handoffs.slice(0,10)){
      const p=document.createElement('p');p.className='muted';p.textContent=h.state+' · '+h.reason.replaceAll('_',' ')+' · '+h.summary;handoffContent.append(p);
    }
  }catch{}
}
document.getElementById('refresh').addEventListener('click',loadHandoffs);loadHandoffs();
