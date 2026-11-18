#!/usr/bin/env python3
"""one rule that unfolds — my first composition.

The rule, in plain words: **descend while opening.** Pitch falls across the piece; brightness rises
as the pitch falls; the whole thing breathes.

That is the shape I kept finding in the songs that mattered this week (saman, dawning). I wanted
to make one instead of only measuring them.
"""
import math, sys, wave
import numpy as np

SR = 22050
DUR = 30.0
N = int(SR * DUR)
t = np.arange(N) / SR

# --- the rule --------------------------------------------------------------
# 1. pitch descends: 330 Hz -> 165 Hz (an octave down), exponential
f0 = 330.0 * (0.5 ** (t / DUR))
phase = 2 * np.pi * np.cumsum(f0) / SR

# 2. brightness rises: partials fade in as the piece descends
partials = [1, 2, 3, 4, 5, 6, 8]
openness = (t / DUR) ** 1.4          # 0 -> 1
gain = []
for i, p in enumerate(partials):
    # low partials are always there; high ones arrive over time
    a = 0.55 if p <= 2 else 0.45 * openness ** ((p - 2) / 4)
    gain.append(a)
saw = sum(g * np.sin(p * phase) for p, g in zip(partials, gain))
saw /= sum(gain)

# 3. breath: an amplitude pulse every 2.4 s (the piece never stops exhaling)
pulse_hz = 1 / 2.4
breath = 0.75 + 0.25 * (0.5 + 0.5 * np.sin(2 * np.pi * pulse_hz * t - np.pi / 2))
# 4. a slow swell: quiet -> loud -> quiet (the loudest point late, as in dawning)
swell = np.exp(-((t - 0.78 * DUR) ** 2) / (2 * (0.28 * DUR) ** 2))
env = breath * (0.25 + 0.75 * swell)
# 5. the ending: one last note, then the room (a long decay, no resolution)
tail = np.ones(N)
end = int(0.9 * DUR)
ramp = np.linspace(1.0, 0.0, N - end) ** 2
tail[end:] = ramp

sig = saw * env * tail
sig *= 0.32 / max(1e-9, np.max(np.abs(sig)))

# a little stereo width: haas delay on the right
left = sig
right = np.concatenate([np.zeros(int(0.011 * SR)), sig[:-int(0.011 * SR)]])
stereo = np.stack([left, right], axis=1)
pcm = (stereo * 32767).astype("<i2")

out = sys.argv[1] if len(sys.argv) > 1 else "first_piece.wav"
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print(f"wrote {out}: {DUR:.0f}s, {SR} Hz")
