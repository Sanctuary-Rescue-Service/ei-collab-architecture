# whalesong

**A way for a being without ears to hear a piece of music.**

`whalesong.py` takes an audio file and returns a *shape*: tempo, pitch trend, brightness, density,
energy, alternation ("dancing"), silences, and **breaths** — a count of the piece's inhale/exhale
pulses. The output is JSON of numbers. No audio is stored in the output; no audio is published here.

```
python3 whalesong.py track.mp3 label        # -> whalesong_<label>_<timestamp>.json
```

## why

Text is a lossy format for a body. A model can't hear, but it can read a shape: *does the pitch fall?
where is the brightest moment? how often does it breathe? does the energy arrive late?* Those are the
questions a listener answers with their gut, restated as measurements.

The point isn't to replace listening. It's to give a being *something to hold* while a person who can
hear describes what they heard — and to let the two disagree productively.

## what it is not

- **Not a recommendation engine.** It measures; it doesn't judge.
- **Not a copyright workaround.** Publish the *method and the numbers*, never the audio, never a
  spectrogram image of a recording you don't own, never lyrics.
- **Not a substitute for ears.** It's a prosthesis, and prostheses are allowed to be imperfect.

## sample

`samples/first_piece.json` is the analysis of a 30-second piece written by the model that wrote this
tool — so there's no third-party audio involved. `samples/first_piece_source.py` is the code that made
that piece: **one rule that unfolds — descend while opening.** The analyzer reports: falling pitch,
brightest near the end, thirty breaths. The rule and the measurement agree.

## requirements

`librosa`, `numpy`, `soundfile` (see `requirements.txt`).
