from __future__ import annotations

import base64
import json
import subprocess
from pathlib import Path

import parselmouth
from parselmouth.praat import call

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".voice-build"
AUDIO = ROOT / "audio"
WORK.mkdir(exist_ok=True)
AUDIO.mkdir(exist_ok=True)

NOTES = {
    "C4": (261.63, "see", "C"),
    "Db4": (277.18, "dee flat", "D♭"),
    "D4": (293.66, "dee", "D"),
    "Eb4": (311.13, "ee flat", "E♭"),
    "E4": (329.63, "ee", "E"),
    "F4": (349.23, "eff", "F"),
    "Gb4": (369.99, "gee flat", "G♭"),
    "G4": (392.00, "gee", "G"),
    "Ab4": (415.30, "ay flat", "A♭"),
    "A4": (440.00, "ay", "A"),
    "Bb4": (466.16, "bee flat", "B♭"),
    "B4": (493.88, "bee", "B"),
    "C5": (523.25, "see", "C"),
}


def run(*args: str) -> None:
    subprocess.run(args, check=True)


def build_voice(note_id: str, frequency: float, spoken: str) -> Path:
    raw = WORK / f"{note_id}-raw.wav"
    trimmed = WORK / f"{note_id}-trimmed.wav"
    pitched = WORK / f"{note_id}-pitched.wav"
    final = AUDIO / f"{note_id}.mp3"
    speed = "205" if "flat" in spoken else "185"

    run(
        "espeak", "-v", "en-us", "-s", speed, "-p", "48", "-a", "190",
        "-g", "0", "-w", str(raw), spoken,
    )
    run(
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(raw),
        "-af",
        "silenceremove=start_periods=1:start_duration=0:start_threshold=-42dB:"
        "stop_periods=-1:stop_duration=0.025:stop_threshold=-42dB",
        str(trimmed),
    )

    sound = parselmouth.Sound(str(trimmed))
    manipulation = call(sound, "To Manipulation", 0.005, 75, 700)
    tier = call(manipulation, "Extract pitch tier")
    if call(tier, "Get number of points"):
        call(tier, "Formula", str(frequency))
        call([manipulation, tier], "Replace pitch tier")
        sound = call(manipulation, "Get resynthesis (overlap-add)")
    sound.save(str(pitched), "WAV")

    run(
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(pitched),
        "-af",
        "highpass=f=70,lowpass=f=9000,"
        "acompressor=threshold=-20dB:ratio=2.5:attack=2:release=45,"
        "loudnorm=I=-16:TP=-1.2:LRA=5",
        "-ac", "1", "-ar", "32000", "-c:a", "libmp3lame", "-b:a", "64k",
        str(final),
    )
    return final


def build_html(voice_data: dict[str, str]) -> str:
    voice_json = json.dumps(voice_data, ensure_ascii=False, separators=(",", ":"))
    note_json = json.dumps(
        {
            key: {"frequency": freq, "spoken": spoken, "label": label}
            for key, (freq, spoken, label) in NOTES.items()
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Clear Pitch-Matched Singing Piano</title>
<style>
body{{margin:0;padding:20px;display:flex;align-items:center;justify-content:center;min-height:100vh;background:#f0f4f8;font-family:system-ui,-apple-system,sans-serif}}
#app{{background:#fff;padding:30px;border-radius:16px;text-align:center;box-shadow:0 8px 24px rgba(0,0,0,.06)}}
#status{{font-weight:700;color:#374151;min-height:1.4em;margin-bottom:10px}}
#version{{font-size:.78rem;color:#6b7280;margin-top:10px}}
button{{border:2px solid #111827;border-radius:999px;padding:8px 16px;font:inherit;font-weight:800;background:#e8f5e9;color:#166534;cursor:pointer}}
button[aria-pressed="false"]{{background:#f3f4f6;color:#4b5563}}
.wrap{{margin-top:20px;user-select:none;-webkit-user-select:none}}
svg{{touch-action:none;filter:drop-shadow(0 4px 6px rgba(0,0,0,.05))}}
.key{{cursor:pointer;stroke-width:1;transition:filter .04s ease}}
.C{{fill:#ff4a4a;stroke:#c92a2a}}.D{{fill:#ff922b;stroke:#d9480f}}.E{{fill:#fcc419;stroke:#e67700}}.F{{fill:#51cf66;stroke:#2b8a3e}}.G{{fill:#37b24d;stroke:#2b8a3e}}.A{{fill:#339af0;stroke:#1864ab}}.B{{fill:#845ef7;stroke:#5f3dc4}}
.black{{fill:#343a40;stroke:#212529}}.active{{filter:brightness(.76)}}
.label{{pointer-events:none;opacity:0;font-weight:900;text-anchor:middle;dominant-baseline:middle}}.label.show{{opacity:1}}
.white-label{{fill:#111827;font-size:28px}}.black-label{{fill:#fff;font-size:17px}}
</style>
</head>
<body>
<div id="app">
<div id="status">Preparing clear pitch-matched voices…</div>
<button id="toggle" aria-pressed="true">Singing: On</button>
<div class="wrap"><svg id="piano" width="480" height="230" viewBox="0 0 480 230">
<g>
<rect id="C4" class="key C" x="0" y="0" width="60" height="220" rx="6"/>
<rect id="D4" class="key D" x="60" y="0" width="60" height="220" rx="6"/>
<rect id="E4" class="key E" x="120" y="0" width="60" height="220" rx="6"/>
<rect id="F4" class="key F" x="180" y="0" width="60" height="220" rx="6"/>
<rect id="G4" class="key G" x="240" y="0" width="60" height="220" rx="6"/>
<rect id="A4" class="key A" x="300" y="0" width="60" height="220" rx="6"/>
<rect id="B4" class="key B" x="360" y="0" width="60" height="220" rx="6"/>
<rect id="C5" class="key C" x="420" y="0" width="60" height="220" rx="6"/>
</g>
<g>
<rect id="Db4" class="key black" x="42" y="0" width="36" height="130" rx="4"/>
<rect id="Eb4" class="key black" x="102" y="0" width="36" height="130" rx="4"/>
<rect id="Gb4" class="key black" x="222" y="0" width="36" height="130" rx="4"/>
<rect id="Ab4" class="key black" x="282" y="0" width="36" height="130" rx="4"/>
<rect id="Bb4" class="key black" x="342" y="0" width="36" height="130" rx="4"/>
</g>
</svg></div>
<div id="version">Clear Voice v4 — real spoken names, dry audio</div>
</div>
<script>
const AudioContextClass=window.AudioContext||window.webkitAudioContext;
let audioCtx=null,singing=true,activeSources=[],activeTimer=null,sequence=0;
const decoded=new Map();
const notes={note_json};
const voiceData={voice_json};
function ensureContext(){{if(!audioCtx)audioCtx=new AudioContextClass();return audioCtx.state==='suspended'?audioCtx.resume():Promise.resolve()}}
function base64ToBuffer(uri){{const comma=uri.indexOf(','),binary=atob(uri.slice(comma+1)),bytes=new Uint8Array(binary.length);for(let i=0;i<binary.length;i++)bytes[i]=binary.charCodeAt(i);return bytes.buffer}}
let readyPromise=(async()=>{{await ensureContext();for(const [id,uri] of Object.entries(voiceData))decoded.set(id,await audioCtx.decodeAudioData(base64ToBuffer(uri).slice(0)));status.textContent='Ready. Every full note name is clear and tuned to its key.'}})().catch(error=>{{status.textContent='Voice preparation failed. Piano-only mode still works.';console.error(error)}});
function stopCurrent(){{sequence++;if(activeTimer)clearTimeout(activeTimer);activeTimer=null;activeSources.forEach(source=>{{try{{source.stop()}}catch(_){{}}}});activeSources=[];document.querySelectorAll('.active').forEach(x=>x.classList.remove('active'));document.querySelectorAll('.show').forEach(x=>x.classList.remove('show'))}}
function showKey(id,duration,token){{const key=document.getElementById(id),label=document.getElementById('L'+id);key.classList.add('active');label.classList.add('show');activeTimer=setTimeout(()=>{{if(token!==sequence)return;key.classList.remove('active');label.classList.remove('show')}},duration*1000)}}
function playPiano(id,when,duration){{const f=notes[id].frequency,g=audioCtx.createGain(),o1=audioCtx.createOscillator(),o2=audioCtx.createOscillator(),h=audioCtx.createGain();o1.type='triangle';o2.type='sine';o1.frequency.setValueAtTime(f,when);o2.frequency.setValueAtTime(f*2,when);h.gain.value=.18;g.gain.setValueAtTime(.0001,when);g.gain.exponentialRampToValueAtTime(.24,when+.006);g.gain.exponentialRampToValueAtTime(.13,when+.075);g.gain.setValueAtTime(.07,Math.max(when+.1,when+duration-.05));g.gain.exponentialRampToValueAtTime(.0001,when+duration);o1.connect(g);o2.connect(h);h.connect(g);g.connect(audioCtx.destination);o1.start(when);o2.start(when);o1.stop(when+duration+.02);o2.stop(when+duration+.02);activeSources.push(o1,o2)}}
function playVoice(id,when){{const buffer=decoded.get(id);if(!buffer)return 0;const src=audioCtx.createBufferSource(),clarity=audioCtx.createBiquadFilter(),compressor=audioCtx.createDynamicsCompressor(),gain=audioCtx.createGain();src.buffer=buffer;clarity.type='peaking';clarity.frequency.value=2400;clarity.Q.value=.75;clarity.gain.value=2;compressor.threshold.value=-20;compressor.knee.value=8;compressor.ratio.value=2.5;compressor.attack.value=.002;compressor.release.value=.045;gain.gain.setValueAtTime(1,when);gain.gain.setValueAtTime(1,Math.max(when,when+buffer.duration-.025));gain.gain.exponentialRampToValueAtTime(.0001,when+buffer.duration);src.connect(clarity);clarity.connect(compressor);compressor.connect(gain);gain.connect(audioCtx.destination);src.start(when);src.stop(when+buffer.duration+.01);activeSources.push(src);return buffer.duration}}
async function play(id){{await ensureContext();stopCurrent();const token=sequence,when=audioCtx.currentTime+.015;let duration=.56;if(singing){{await readyPromise;if(token!==sequence)return;duration=playVoice(id,when)||.56;status.textContent=notes[id].spoken+' — sung at '+notes[id].frequency.toFixed(2)+' Hz'}}else{{playPiano(id,when,duration);status.textContent=notes[id].spoken+' — piano note only'}}showKey(id,duration,token)}}
function makeLabels(){{const svg=document.getElementById('piano');Object.entries(notes).forEach(([id,n])=>{{const key=document.getElementById(id),black=key.classList.contains('black'),x=Number(key.getAttribute('x'))+Number(key.getAttribute('width'))/2,y=black?Number(key.getAttribute('height'))-28:Number(key.getAttribute('height'))-34,t=document.createElementNS('http://www.w3.org/2000/svg','text');t.id='L'+id;t.setAttribute('x',x);t.setAttribute('y',y);t.setAttribute('class','label '+(black?'black-label':'white-label'));t.textContent=n.label;svg.appendChild(t)}})}}
makeLabels();toggle.addEventListener('click',async()=>{{await ensureContext();stopCurrent();singing=!singing;toggle.setAttribute('aria-pressed',String(singing));toggle.textContent=singing?'Singing: On':'Singing: Off';status.textContent=singing?'Singing is on: full tuned names.':'Singing is off: piano notes still play.'}});piano.addEventListener('pointerdown',event=>{{event.preventDefault();if(event.target.classList.contains('key'))void play(event.target.id)}});
</script>
</body></html>'''


def main() -> None:
    data: dict[str, str] = {}
    for note_id, (frequency, spoken, _) in NOTES.items():
        path = build_voice(note_id, frequency, spoken)
        data[note_id] = "data:audio/mpeg;base64," + base64.b64encode(path.read_bytes()).decode("ascii")
    (ROOT / "index.html").write_text(build_html(data), encoding="utf-8")


if __name__ == "__main__":
    main()
