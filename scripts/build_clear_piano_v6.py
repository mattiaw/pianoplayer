from pathlib import Path

# Running the v5 builder first regenerates the self-contained piano and voices.
import build_clear_piano_v5  # noqa: F401

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
html = INDEX.read_text(encoding="utf-8")

html = html.replace(
    'button[aria-pressed="false"]{background:#f3f4f6;color:#4b5563}',
    'button[aria-pressed="false"]{background:#f3f4f6;color:#4b5563}'
    '.song-controls{display:flex;flex-wrap:wrap;justify-content:center;gap:8px;margin:14px auto 4px;max-width:560px}'
    '.song-button,.stop-button{border-width:1px;padding:7px 12px;font-size:.92rem;background:#eef2ff;color:#3730a3}'
    '.song-button:hover,.song-button.playing{background:#c7d2fe}'
    '.stop-button{background:#fff1f2;color:#9f1239}',
)

html = html.replace(
    '<button id="toggle" aria-pressed="true">Singing: On</button>',
    '<button id="toggle" aria-pressed="true">Singing: On</button>'
    '<div class="song-controls" aria-label="One-octave songs">'
    '<button class="song-button" data-song="twinkle">Twinkle Twinkle</button>'
    '<button class="song-button" data-song="mary">Mary Had a Little Lamb</button>'
    '<button class="song-button" data-song="ode">Ode to Joy</button>'
    '<button class="song-button" data-song="jingle">Jingle Bells</button>'
    '<button id="stop-song" class="stop-button">Stop Song</button>'
    '</div>',
)

songs_js = r'''
let songRun=0;
const SONG_BPM=112;
const songs={
 twinkle:{title:'Twinkle Twinkle Little Star',notes:[
  ['C4',1],['C4',1],['G4',1],['G4',1],['A4',1],['A4',1],['G4',2],
  ['F4',1],['F4',1],['E4',1],['E4',1],['D4',1],['D4',1],['C4',2],
  ['G4',1],['G4',1],['F4',1],['F4',1],['E4',1],['E4',1],['D4',2],
  ['G4',1],['G4',1],['F4',1],['F4',1],['E4',1],['E4',1],['D4',2],
  ['C4',1],['C4',1],['G4',1],['G4',1],['A4',1],['A4',1],['G4',2],
  ['F4',1],['F4',1],['E4',1],['E4',1],['D4',1],['D4',1],['C4',2]
 ]},
 mary:{title:'Mary Had a Little Lamb',notes:[
  ['E4',1],['D4',1],['C4',1],['D4',1],['E4',1],['E4',1],['E4',2],
  ['D4',1],['D4',1],['D4',2],['E4',1],['G4',1],['G4',2],
  ['E4',1],['D4',1],['C4',1],['D4',1],['E4',1],['E4',1],['E4',1],['E4',1],
  ['D4',1],['D4',1],['E4',1],['D4',1],['C4',2]
 ]},
 ode:{title:'Ode to Joy',notes:[
  ['E4',1],['E4',1],['F4',1],['G4',1],['G4',1],['F4',1],['E4',1],['D4',1],
  ['C4',1],['C4',1],['D4',1],['E4',1],['E4',1.5],['D4',.5],['D4',2],
  ['E4',1],['E4',1],['F4',1],['G4',1],['G4',1],['F4',1],['E4',1],['D4',1],
  ['C4',1],['C4',1],['D4',1],['E4',1],['D4',1.5],['C4',.5],['C4',2]
 ]},
 jingle:{title:'Jingle Bells',notes:[
  ['E4',1],['E4',1],['E4',2],['E4',1],['E4',1],['E4',2],
  ['E4',1],['G4',1],['C4',1.5],['D4',.5],['E4',4],
  ['F4',1],['F4',1],['F4',1.5],['F4',.5],['F4',1],['E4',1],['E4',1],['E4',.5],['E4',.5],
  ['E4',1],['D4',1],['D4',1],['E4',1],['D4',2],['G4',2]
 ]}
};
const wait=milliseconds=>new Promise(resolve=>setTimeout(resolve,milliseconds));
function clearSongButtons(){document.querySelectorAll('.song-button.playing').forEach(button=>button.classList.remove('playing'))}
function clearSongKey(id){const key=document.getElementById(id),label=document.getElementById('L'+id);if(key)key.classList.remove('active');if(label)label.classList.remove('show')}
async function playSong(songId){
 await resumeContext();
 stopCurrent();
 const run=++songRun;
 const song=songs[songId];
 if(!song)return;
 clearSongButtons();
 const button=document.querySelector(`[data-song="${songId}"]`);
 if(button)button.classList.add('playing');
 status.textContent=`Playing ${song.title} — watch the keys and letters.`;
 const beatMs=60000/SONG_BPM;
 for(const [id,beats] of song.notes){
  if(run!==songRun)return;
  const totalMs=beatMs*beats;
  const duration=Math.max(.14,(totalMs*.86)/1000);
  const when=audioCtx.currentTime+.012;
  playPiano(id,when,duration);
  const key=document.getElementById(id),label=document.getElementById('L'+id);
  key.classList.add('active');
  label.classList.add('show');
  status.textContent=`${song.title}: ${notes[id].label}`;
  await wait(totalMs*.86);
  clearSongKey(id);
  await wait(totalMs*.14);
 }
 if(run===songRun){
  clearSongButtons();
  activeSources=[];
  status.textContent=`Finished ${song.title}.`;
 }
}
function stopSong(){
 stopCurrent();
 clearSongButtons();
 status.textContent='Song stopped.';
}
'''

html = html.replace(
    'function makeLabels(){',
    songs_js + '\nfunction makeLabels(){',
)

html = html.replace(
    "function stopCurrent(){sequence++;",
    "function stopCurrent(){sequence++;songRun++;",
)

html = html.replace(
    "makeLabels();toggle.addEventListener('click'",
    "makeLabels();document.querySelectorAll('.song-button').forEach(button=>button.addEventListener('click',()=>void playSong(button.dataset.song)));document.getElementById('stop-song').addEventListener('click',stopSong);toggle.addEventListener('click'",
)

html = html.replace(
    'Clear Voice v5',
    'Clear Voice v6 — one-octave song buttons',
)

INDEX.write_text(html, encoding="utf-8")
