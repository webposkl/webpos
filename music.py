"""Energetic, vocal-free electronic corporate/tech track (loud & cool).
Four-on-the-floor kick, offbeat pluck bass, sidechained saw chords, a bright
filtered arpeggio lead, hats and claps over an uplifting Am-F-C-G progression.
Continuous (no silent gaps). Written to music_raw.wav; loudness/fades applied later."""
import numpy as np, wave

SR = 44100
DUR = 150.0
N = int(SR * DUR)
t = (np.arange(N) / SR).astype(np.float32)
rng = np.random.default_rng(7)

BPM = 124.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT

def saw(freq, ph0=0.0):
    ph = np.cumsum(np.full(N, freq)) / SR + ph0
    return 2.0 * (ph - np.floor(0.5 + ph))

def lp(x, cutoff):
    # low-pass via short exponential FIR kernel (fast, low memory)
    a = 1 - np.exp(-2*np.pi*cutoff/SR)
    K = int(min(48, max(6, 5 / a)))
    h = (a * (1 - a) ** np.arange(K)).astype(np.float32)
    h /= h.sum()
    y = np.convolve(x, h)[:len(x)]
    return y.astype(np.float32)

# ---- progression ----
CH = [
    ([220.00, 261.63, 329.63], 110.00),   # Am
    ([174.61, 220.00, 261.63], 87.31),    # F
    ([261.63, 329.63, 392.00], 130.81),   # C
    ([196.00, 246.94, 293.66], 98.00),    # G
]
def chord_at(tt):
    return CH[int(tt // BAR) % 4]

L = np.zeros(N, np.float32); R = np.zeros(N, np.float32)

# ---- sidechain duck (pumps on every beat) ----
phase_beat = (t % BEAT) / BEAT
duck = 0.28 + 0.72 * np.clip(phase_beat, 0, 1) ** 0.55

# ---- chords: saw stack, ducked, gentle LP that opens over each 4-bar loop ----
chordsig = np.zeros(N, np.float32)
nbar = int(np.ceil(DUR / BAR))
for bark in range(nbar):
    i0 = int(bark * BAR * SR)
    i1 = min(N, int((bark + 1) * BAR * SR))
    if i1 <= i0:
        continue
    notes = CH[bark % 4][0]
    n = i1 - i0
    idx = np.arange(i0, i1)
    s = np.zeros(n)
    for f in notes:
        ph = idx * f / SR
        s += 2.0 * (ph - np.floor(0.5 + ph))
        ph2 = idx * (f * 1.005) / SR
        s += 2.0 * (ph2 - np.floor(0.5 + ph2))
    chordsig[i0:i1] = s / (len(notes) * 2)
# opening filter over 8-bar cycles (crossfade dark<->bright)
cyc = (t % (8*BAR)) / (8*BAR)
chordsig = ((1-cyc)*lp(chordsig, 600) + cyc*lp(chordsig, 3800)) * duck * 0.34
L += chordsig; R += chordsig

# ---- bass: offbeat 8th plucks on the root ----
bass = np.zeros(N, np.float32)
step = BEAT / 2
k = 0; ti = 0.0
while ti < DUR:
    notes, root = chord_at(ti)
    if k % 2 == 1:                      # offbeat "and"
        i0 = int(ti * SR); nn = int(step * SR); nn = min(nn, N - i0)
        if nn > 0:
            tt = np.arange(nn) / SR
            env = np.exp(-tt * 9) * (1 - np.exp(-tt * 300))
            ph = np.cumsum(np.full(nn, root)) / SR
            b = (2*(ph-np.floor(0.5+ph))) * env
            bass[i0:i0+nn] += b * 0.5
    ti += step; k += 1
bass = lp(bass, 900) * 0.9
L += bass; R += bass

# ---- lead arpeggio: 16th notes, bright saw, delay echo ----
lead = np.zeros(N, np.float32)
st = BEAT / 4
k = 0; ti = 0.0
while ti < DUR:
    notes, root = chord_at(ti)
    pat = [notes[0], notes[2], notes[1], notes[2], notes[0]*2, notes[2], notes[1], notes[2]]
    f = pat[k % len(pat)] * 2
    i0 = int(ti * SR); nn = int(st * SR); nn = min(nn, N - i0)
    if nn > 0:
        tt = np.arange(nn) / SR
        env = np.exp(-tt * 16) * (1 - np.exp(-tt*400))
        ph = np.cumsum(np.full(nn, f)) / SR
        s = (2*(ph-np.floor(0.5+ph))) * env
        lead[i0:i0+nn] += s * 0.22
    ti += st; k += 1
cyc2 = (t % (8*BAR)) / (8*BAR)
lead = (1-cyc2)*lp(lead,900) + cyc2*lp(lead,6500)
# stereo delay echo
delay = int(0.5 * BEAT * SR)
echo = np.zeros(N, np.float32); echo[delay:] = lead[:-delay] * 0.4
L += (lead + echo*0.6); R += (lead + echo)  # slight stereo spread via echo

# ---- drums ----
def add(buf, i0, sig):
    nn = min(len(sig), N - i0)
    if nn > 0 and i0 >= 0: buf[i0:i0+nn] += sig[:nn]
drums = np.zeros(N, np.float32)
def kick():
    nn = int(0.22*SR); tt=np.arange(nn)/SR
    f = 150*np.exp(-tt*32)+48
    ph = 2*np.pi*np.cumsum(f)/SR
    return np.sin(ph)*np.exp(-tt*7)*1.0
def clap():
    nn=int(0.14*SR); tt=np.arange(nn)/SR
    return (rng.standard_normal(nn))*np.exp(-tt*22)*0.5
def chat(dur=0.04,amp=0.28):
    nn=int(dur*SR); tt=np.arange(nn)/SR
    return (rng.standard_normal(nn))*np.exp(-tt*90)*amp
K=kick()
ti=0.0; beatk=0
while ti < DUR:
    add(drums, int(ti*SR), K)                       # four-on-floor
    add(drums, int((ti+BEAT/2)*SR), chat(0.05,0.30))# offbeat open-ish hat
    add(drums, int(ti*SR), chat(0.03,0.18))         # on-beat closed hat
    add(drums, int((ti+BEAT/4)*SR), chat(0.025,0.12))
    add(drums, int((ti+3*BEAT/4)*SR), chat(0.025,0.12))
    if beatk % 4 in (1,3):
        add(drums, int(ti*SR), clap())              # snare/clap on 2 & 4
    ti += BEAT; beatk += 1
L += drums; R += drums

# ---- master: soft limit + normalize ----
mix = np.stack([L, R], axis=1)
mix = mix / (np.max(np.abs(mix)) + 1e-9) * 1.4
mix = np.tanh(mix)                    # glue / loudness
mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.97

data = (mix * 32767).astype('<i2')
with wave.open('music_raw.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(data.tobytes())
print("music_raw.wav written", data.shape)
