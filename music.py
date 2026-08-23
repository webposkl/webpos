"""Synthesize an instrumental corporate-technology background track.
No vocals, no samples. Warm pad + gentle pluck arpeggio + soft bass + light
percussion over an uplifting I-V-vi-IV progression in A major. Continuous for
the whole length (no silent gaps). Written to music_raw.wav."""
import numpy as np, wave, struct

SR = 44100
DUR = 150.0                      # a little longer than the video; ffmpeg trims + fades
N = int(SR * DUR)
t = np.arange(N) / SR

def adsr(length, a, d, s, r, sus):
    n = length
    env = np.ones(n) * sus
    ai = int(a*SR); di = int(d*SR); ri = int(r*SR)
    ai = min(ai, n)
    env[:ai] = np.linspace(0, 1, ai)
    if di > 0 and ai+di <= n:
        env[ai:ai+di] = np.linspace(1, sus, di)
    if ri > 0:
        env[-ri:] = np.linspace(env[-ri] if n>ri else sus, 0, ri)
    return env

# I-V-vi-IV in A major, chord tones (Hz)
CHORDS = [
    [220.00, 277.18, 329.63, 440.00],   # A
    [164.81, 207.65, 246.94, 329.63],   # E
    [185.00, 220.00, 277.18, 369.99],   # F#m
    [146.83, 185.00, 220.00, 293.66],   # D
]
ROOTS = [110.00, 82.41, 92.50, 73.42]   # bass roots one octave down

CHORD_DUR = 4.0                          # seconds per chord
BEAT = 0.5                               # 120 BPM

left = np.zeros(N); right = np.zeros(N)

# ---- Pad (warm, slow) ----
pos = 0.0
ci = 0
while pos < DUR:
    ln = min(CHORD_DUR, DUR - pos)
    n = int(ln * SR); i0 = int(pos * SR)
    if n <= 0: break
    seg = np.zeros(n)
    env = adsr(n, a=0.8, d=0.4, s=0.0, r=0.9, sus=0.75)
    for f in CHORDS[ci % 4]:
        for det in (1.0, 1.004, 0.996):   # slight detune for warmth
            seg += np.sin(2*np.pi*f*det*(np.arange(n)/SR))
    seg *= env / (len(CHORDS[ci%4]) * 3)
    # gentle stereo width
    left[i0:i0+n]  += seg * 0.9
    right[i0:i0+n] += seg * 0.9 * 0.98
    pos += CHORD_DUR; ci += 1

# ---- Bass ----
pos = 0.0; ci = 0
while pos < DUR:
    ln = min(CHORD_DUR, DUR - pos); n = int(ln*SR); i0 = int(pos*SR)
    if n <= 0: break
    env = adsr(n, a=0.05, d=0.2, s=0.0, r=0.3, sus=0.7)
    f = ROOTS[ci % 4]
    seg = (np.sin(2*np.pi*f*(np.arange(n)/SR)) +
           0.25*np.sin(2*np.pi*2*f*(np.arange(n)/SR))) * env * 0.5
    left[i0:i0+n]  += seg
    right[i0:i0+n] += seg
    pos += CHORD_DUR; ci += 1

# ---- Pluck arpeggio (eighth notes) ----
step = BEAT/2
pos = 0.0; k = 0
while pos < DUR:
    ci = int(pos // CHORD_DUR) % 4
    tones = CHORDS[ci]
    pattern = [tones[0], tones[2], tones[1], tones[3], tones[2], tones[1]]
    f = pattern[k % len(pattern)] * 2       # up an octave
    n = int(step*SR); i0 = int(pos*SR)
    if i0 >= N: break
    n = min(n, N - i0)
    tt = np.arange(n)/SR
    env = np.exp(-tt*7.0)
    seg = (np.sin(2*np.pi*f*tt) + 0.3*np.sin(2*np.pi*2*f*tt)) * env * 0.16
    pan = 0.5 + 0.35*np.sin(k*0.6)          # gentle auto-pan
    left[i0:i0+n]  += seg*(1-pan)*1.4
    right[i0:i0+n] += seg*pan*1.4
    pos += step; k += 1

# ---- Soft percussion ----
def kick(i0):
    n = int(0.18*SR); n = min(n, N-i0)
    if n<=0: return
    tt = np.arange(n)/SR
    fsw = 120*np.exp(-tt*30)+45
    ph = 2*np.pi*np.cumsum(fsw)/SR
    seg = np.sin(ph)*np.exp(-tt*9)*0.6
    left[i0:i0+n]+=seg; right[i0:i0+n]+=seg
def hat(i0):
    n = int(0.05*SR); n = min(n, N-i0)
    if n<=0: return
    tt = np.arange(n)/SR
    seg = (np.random.rand(n)*2-1)*np.exp(-tt*60)*0.12
    left[i0:i0+n]+=seg*0.9; right[i0:i0+n]+=seg
beat = 0.0; b = 0
while beat < DUR:
    i0 = int(beat*SR)
    if b % 2 == 0: kick(i0)          # beats 1 & 3
    hat(int((beat+BEAT/2)*SR))       # offbeat hats
    beat += BEAT; b += 1

# ---- Mix / soft limit ----
mix = np.stack([left, right], axis=1)
peak = np.max(np.abs(mix))
mix = mix / peak * 0.9
mix = np.tanh(mix*1.1)/np.tanh(1.1)  # gentle saturation glue
mix = mix / np.max(np.abs(mix)) * 0.89

# write 16-bit PCM wav
data = (mix*32767).astype('<i2')
with wave.open('music_raw.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(data.tobytes())
print("music_raw.wav written", data.shape)
