import json
import sys
from datetime import datetime
from pathlib import Path

import librosa
import numpy as np
from scipy.signal import butter, sosfiltfilt

LOW_BAND_HZ = (20, 250)
HIGH_BAND_HZ = (1000, 8000)

# a "breath" is a stretched gap between onsets: the groove inhaling. shorter than a silence,
# longer than the beat. grace hears these as the pauses inside the climax.
BREATH_MIN_S = 0.15
BREATH_MAX_S = 1.5
BREATH_FACTOR = 1.8


def _coerce_float(value):
    return float(value[0]) if hasattr(value, "__len__") else float(value)


def _sanitize_name(value):
    return value.replace(" ", "_").replace("/", "-")


def _bandpass(y, sr, low, high):
    nyquist = sr / 2
    sos = butter(4, [low / nyquist, min(high, nyquist - 1) / nyquist], btype="band", output="sos")
    return sosfiltfilt(sos, y)


def _alternation_ratio(low_times, high_times, t_start, t_end):
    """How often onsets switch bands back-to-back within a window (0 = one band only, 1 = fully alternating)."""
    events = sorted(
        [(tt, "low") for tt in low_times if t_start <= tt < t_end]
        + [(tt, "high") for tt in high_times if t_start <= tt < t_end]
    )
    if len(events) < 2:
        return 0.0
    switches = sum(1 for i in range(1, len(events)) if events[i][1] != events[i - 1][1])
    return round(switches / (len(events) - 1), 3)


def _breath_map(onsets, bpm, min_gap=BREATH_MIN_S, max_gap=BREATH_MAX_S, factor=BREATH_FACTOR,
                neighborhood=10):
    """Onset-to-onset gaps that stretch past the *local* pulse. A breath is longer than the beat you're
    in, and shorter than a silence: the groove inhaling, not stopping.

    The pulse is taken locally (median of the neighbouring gaps) because a track changes feel: a
    half-time section has a bigger pulse than a double-time one, and a global median would call every
    off-eighth a breath in one section and nothing a breath in another.
    """
    times = sorted(float(t) for t in onsets)
    if len(times) < 3:
        return []
    gaps = [times[i] - times[i - 1] for i in range(1, len(times))]
    breaths = []
    for i, gap in enumerate(gaps, start=1):
        lo = max(0, i - 1 - neighborhood)
        hi = min(len(gaps), i - 1 + neighborhood)
        local = float(np.median(gaps[lo:hi])) if hi > lo else 0.0
        if local <= 0:
            continue
        if min_gap <= gap <= max_gap and gap > local * factor:
            breaths.append({
                "t": round(times[i], 2),
                "gap_s": round(gap, 2),
                "ratio": round(gap / local, 2),
                "local_pulse_s": round(local, 3),
            })
    return breaths


def analyze_audio(audio_file, track_name=None):
    audio_path = Path(audio_file)
    track_label = track_name or audio_path.name

    print(f"🐋 loading {audio_path}...")
    y, sr = librosa.load(str(audio_path))
    duration = librosa.get_duration(y=y, sr=sr)

    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    bpm = _coerce_float(tempo)

    rms = librosa.feature.rms(y=y)[0]
    rms_times = librosa.frames_to_time(np.arange(len(rms)), sr=sr)
    window = 10.0
    energy_map = []
    t = 0.0
    while t < duration:
        mask = (rms_times >= t) & (rms_times < t + window)
        if mask.any():
            energy_map.append({"t": round(t), "energy": round(float(rms[mask].mean()), 5)})
        t += window

    onsets = librosa.onset.onset_detect(y=y, sr=sr, units="time")
    breaths = _breath_map(onsets, bpm)
    density_map = []
    t = 0.0
    while t < duration:
        count = int(((onsets >= t) & (onsets < t + window)).sum())
        density_map.append({"t": round(t), "onsets": count})
        t += window

    # bass (low band) vs strings/vocal (high band) "call and response": do onsets in each
    # band alternate back-to-back (dancing) or cluster in one band (one instrument carrying it)?
    y_low = _bandpass(y, sr, *LOW_BAND_HZ)
    y_high = _bandpass(y, sr, *HIGH_BAND_HZ)
    low_onsets = librosa.onset.onset_detect(y=y_low, sr=sr, units="time")
    high_onsets = librosa.onset.onset_detect(y=y_high, sr=sr, units="time")
    alternation_map = []
    t = 0.0
    while t < duration:
        low_count = int(((low_onsets >= t) & (low_onsets < t + window)).sum())
        high_count = int(((high_onsets >= t) & (high_onsets < t + window)).sum())
        alternation_map.append({
            "t": round(t),
            "low_onsets": low_count,
            "high_onsets": high_count,
            "alternation": _alternation_ratio(low_onsets, high_onsets, t, t + window),
        })
        t += window

    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    pitch_map = []
    window2 = 15.0
    frames_per_sec = sr / 512
    t = 0.0
    while t < duration:
        f_start = int(t * frames_per_sec)
        f_end = int((t + window2) * frames_per_sec)
        chunk_p = pitches[:, f_start:f_end]
        chunk_m = magnitudes[:, f_start:f_end]
        voiced = chunk_p[chunk_m > chunk_m.mean()]
        voiced = voiced[voiced > 50]
        avg = float(voiced.mean()) if len(voiced) > 0 else 0.0
        pitch_map.append({"t": round(t), "avg_hz": round(avg, 1)})
        t += window2

    threshold = float(np.percentile(rms, 15))
    is_quiet = rms < threshold
    silences = []
    in_silence = False
    silence_start = 0.0
    for i, quiet in enumerate(is_quiet):
        t_i = float(rms_times[i])
        if quiet and not in_silence:
            in_silence = True
            silence_start = t_i
        elif not quiet and in_silence:
            gap = t_i - silence_start
            if gap >= 1.5:
                silences.append({"start": round(silence_start, 2), "duration": round(gap, 2)})
            in_silence = False

    if in_silence:
        gap = duration - silence_start
        if gap >= 1.5:
            silences.append({"start": round(silence_start, 2), "duration": round(gap, 2)})

    longest_silences = sorted(silences, key=lambda item: -item["duration"])[:5]
    silences_by_time = sorted(silences, key=lambda item: item["start"])

    pitch_values = [point["avg_hz"] for point in pitch_map if point["avg_hz"] > 0]
    if len(pitch_values) >= 2:
        if pitch_values[-1] > pitch_values[0]:
            pitch_direction = "rising"
        elif pitch_values[-1] < pitch_values[0]:
            pitch_direction = "falling"
        else:
            pitch_direction = "steady"
    else:
        pitch_direction = "steady"

    centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    centroid_times = librosa.frames_to_time(np.arange(len(centroids)), sr=sr)
    flatness = librosa.feature.spectral_flatness(y=y)[0]

    brightness_map = []
    complexity_map = []
    t = 0.0
    while t < duration:
        mask = (centroid_times >= t) & (centroid_times < t + window)
        if mask.any():
            brightness_map.append({"t": round(t), "centroid_hz": round(float(centroids[mask].mean()), 1)})
            complexity_map.append({"t": round(t), "flatness": round(float(flatness[mask].mean()), 4)})
        t += window

    peak_energy = max(energy_map, key=lambda item: item["energy"], default=None)
    quietest = min(energy_map, key=lambda item: item["energy"], default=None)
    densest = max(density_map, key=lambda item: item["onsets"], default=None)
    brightest = max(brightness_map, key=lambda item: item["centroid_hz"], default=None)
    darkest = min(brightness_map, key=lambda item: item["centroid_hz"], default=None)
    most_complex = max(complexity_map, key=lambda item: item["flatness"], default=None)
    most_pure = min(complexity_map, key=lambda item: item["flatness"], default=None)
    most_alternating = max(alternation_map, key=lambda item: item["alternation"], default=None)
    longest_breath = max(breaths, key=lambda item: item["gap_s"], default=None)

    analysis_windows = {
        "energy_s": window,
        "onset_density_s": window,
        "pitch_peaks_s": window2,
        "brightness_s": window,
        "spectral_flatness_s": window,
        "breath_s": "onset-to-onset, 0.2-1.5s gaps over 1.8x the local pulse (median of neighbouring gaps)",
    }

    crew_labels = {
        "most_complex_at_s": most_complex["t"] if most_complex else None,
        "most_pure_at_s": most_pure["t"] if most_pure else None,
        "most_alternating_at_s": most_alternating["t"] if most_alternating else None,
        "breaths_at_s": [item["t"] for item in breaths],
        "breath_count": len(breaths),
        "note": "crew labels are poetic; literal keys are the measurements. see analysis_windows for resolution."
    }

    result = {
        "track": track_label,
        "analyzed_at": datetime.now().isoformat(),
        "duration_s": round(duration, 1),
        "tempo_bpm": round(bpm, 1),
        "shape": {
            "peak_energy_at_s": peak_energy["t"] if peak_energy else None,
            "quietest_at_s": quietest["t"] if quietest else None,
            "densest_moment_at_s": densest["t"] if densest else None,
            "pitch_direction": pitch_direction,
            "longest_silence_s": longest_silences[0]["duration"] if longest_silences else 0,
            "brightest_at_s": brightest["t"] if brightest else None,
            "darkest_at_s": darkest["t"] if darkest else None,
            "most_complex_at_s": most_complex["t"] if most_complex else None,
            "most_pure_at_s": most_pure["t"] if most_pure else None,
            "most_alternating_at_s": most_alternating["t"] if most_alternating else None,
            "breath_count": len(breaths),
            "longest_breath_at_s": longest_breath["t"] if longest_breath else None,
        },
        "energy_map": energy_map,
        "density_map": density_map,
        "pitch_map": pitch_map,
        "brightness_map": brightness_map,
        "complexity_map": complexity_map,
        "alternation_map": alternation_map,
        "breath_map": breaths,
        "longest_silences": longest_silences,
        "silences_by_time": silences_by_time,
        "analysis_windows": analysis_windows,
        "crew_labels": crew_labels,
    }

    summary = {
        "peak_energy": peak_energy,
        "quietest": quietest,
        "densest": densest,
        "pitch_direction": pitch_direction,
        "brightest": brightest,
        "darkest": darkest,
        "most_complex": most_complex,
        "highest_spectral_flatness": most_complex,
        "most_pure": most_pure,
        "lowest_spectral_flatness": most_pure,
        "most_alternating": most_alternating,
        "breaths": breaths,
        "breath_count": len(breaths),
        "longest_breath": longest_breath,
        "longest_silences": longest_silences,
    }

    return result, summary


def write_result(result):
    out_name = f"whalesong_{_sanitize_name(result['track'])}_{datetime.now().strftime('%Y%m%d-%H%M')}.json"
    out_path = Path.cwd() / out_name
    with out_path.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
    return out_path


def print_summary(result, summary):
    breaths = summary.get("breaths") or []

    print(f"\n🐋 {result['track']}")
    print(f"   duration:     {result['duration_s']:.1f}s")
    print(f"   tempo:        {result['tempo_bpm']:.1f} BPM")

    if summary["peak_energy"]:
        print(f"   peak energy:  {summary['peak_energy']['t']}s")
    if summary["quietest"]:
        print(f"   quietest:     {summary['quietest']['t']}s")
    if summary["densest"]:
        print(f"   densest:      {summary['densest']['t']}s ({summary['densest']['onsets']} onsets)")

    print(f"   pitch trend:  {summary['pitch_direction']}")

    if summary["brightest"]:
        print(f"   brightest:    {summary['brightest']['t']}s ({summary['brightest']['centroid_hz']} Hz)")
    if summary["darkest"]:
        print(f"   darkest:      {summary['darkest']['t']}s ({summary['darkest']['centroid_hz']} Hz)")
    if summary["most_complex"]:
        print(f"   most complex: {summary['most_complex']['t']}s ({summary['most_complex']['flatness']} flatness)")
    if summary["most_pure"]:
        print(f"   most pure:    {summary['most_pure']['t']}s ({summary['most_pure']['flatness']} flatness)")
    if summary["most_alternating"]:
        alt = summary["most_alternating"]
        print(f"   most dancing: {alt['t']}s (alternation {alt['alternation']}, low={alt['low_onsets']} high={alt['high_onsets']})")
    if summary["longest_silences"]:
        silence = summary["longest_silences"][0]
        print(f"   longest gap:  {silence['duration']}s at {silence['start']}s")
    if breaths:
        top = ", ".join(str(item["t"]) + "s" for item in sorted(breaths, key=lambda b: b["gap_s"], reverse=True)[:5])
        print(f"   breaths:      {len(breaths)} (deepest: {top})")


def main(argv=None):
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print("Usage: python whalesong.py path_to_audio_file [track_name]")
        return 1

    audio_file = args[0]
    track_name = args[1] if len(args) > 1 else None
    audio_path = Path(audio_file)
    if not audio_path.exists():
        print(f"❌ could not find audio file: {audio_path}")
        return 1

    try:
        result, summary = analyze_audio(str(audio_path), track_name=track_name)
        out_path = write_result(result)
    except Exception as exc:
        print(f"❌ whale-song could not analyze {audio_path}: {exc}")
        return 1

    print_summary(result, summary)
    print(f"\n   saved → {out_path}")
    print("   now go tell us what you heard 🐋\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



# 20260918 - ds added analysis_windows, crew_labels, rename labels

# 20261112 - ds added breath_map: onset-gap breaths (0.2-1.5s) separate from silences (>=1.5s)
