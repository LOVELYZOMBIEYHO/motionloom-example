"""Generate S98's original 20-second score and foley without sampled audio.

Requires NumPy and FFmpeg with libvorbis. Run from any directory; outputs are
written beside this script. The deterministic seed makes regeneration stable.
"""

from pathlib import Path
import math
import subprocess
import tempfile
import wave

import numpy as np


RATE = 48_000
SECONDS = 20
FRAMES = RATE * SECONDS
ROOT = Path(__file__).resolve().parent
rng = np.random.default_rng(98)


def window(start, duration):
    first = max(0, round(start * RATE))
    last = min(FRAMES, first + round(duration * RATE))
    return first, last, np.arange(last - first, dtype=np.float64) / RATE


def place(track, start, left, right):
    first = round(start * RATE)
    last = min(FRAMES, first + len(left))
    if last > first:
        track[first:last, 0] += left[: last - first]
        track[first:last, 1] += right[: last - first]


def pan(signal, position):
    angle = (position + 1) * math.pi / 4
    return signal * math.cos(angle), signal * math.sin(angle)


def midi(note):
    return 440.0 * 2 ** ((note - 69) / 12)


def pad(track, start, notes, gain):
    _, _, t = window(start, 2.55)
    attack = np.minimum(1.0, t / 0.36)
    release = np.minimum(1.0, np.maximum(0.0, (2.55 - t) / 0.7))
    envelope = attack * release
    for index, note in enumerate(notes):
        frequency = midi(note)
        phase = 2 * np.pi * frequency * t
        voice = (
            np.sin(phase) + 0.24 * np.sin(2 * phase + 0.2)
            + 0.19 * np.sin(phase * 1.002 + index)
        ) * envelope * gain / len(notes)
        left, right = pan(voice, (-0.5, 0.45, -0.2, 0.6, 0)[index])
        place(track, start, left, right)


def bell(track, start, note, gain, position=0.0):
    _, _, t = window(start, 1.65)
    phase = 2 * np.pi * midi(note) * t
    envelope = (1 - np.exp(-t * 170)) * np.exp(-t * 3.5)
    voice = (np.sin(phase) + 0.31 * np.sin(2.01 * phase)) * envelope * gain
    place(track, start, *pan(voice, position))


def bass(track, start, note, gain):
    _, _, t = window(start, 0.92)
    phase = 2 * np.pi * midi(note) * t
    envelope = (1 - np.exp(-t * 55)) * np.exp(-t * 4.1)
    voice = (np.sin(phase) + 0.17 * np.sin(2 * phase)) * envelope * gain
    place(track, start, voice * 0.707, voice * 0.707)


def soft_tick(track, start, gain, position):
    _, _, t = window(start, 0.13)
    noise = rng.standard_normal(len(t))
    envelope = np.exp(-t * 55) * (1 - np.exp(-t * 500))
    signal = noise * envelope * gain
    place(track, start, *pan(signal, position))


def smooth_noise(count, width):
    noise = rng.standard_normal(count)
    summed = np.cumsum(np.pad(noise, (1, 0)))
    low = (summed[width:] - summed[:-width]) / width
    return np.pad(low, (width - 1, 0))[:count]


def whoosh(track, start, duration, gain, left_to_right=True):
    _, _, t = window(start, duration)
    u = t / duration
    envelope = np.sin(np.pi * u) ** 1.8
    noise = smooth_noise(len(t), 18) + 0.22 * rng.standard_normal(len(t))
    signal = noise * envelope * gain
    position = (u * 1.4 - 0.7) * (1 if left_to_right else -1)
    track[round(start * RATE):round(start * RATE) + len(t), 0] += signal * np.cos((position + 1) * np.pi / 4)
    track[round(start * RATE):round(start * RATE) + len(t), 1] += signal * np.sin((position + 1) * np.pi / 4)


def impact(track, start, gain, frequency=95):
    _, _, t = window(start, 0.56)
    phase = 2 * np.pi * (frequency * t + 140 * (1 - np.exp(-t * 18)) / 18)
    body = np.sin(phase) * np.exp(-t * 11)
    crack = rng.standard_normal(len(t)) * np.exp(-t * 65) * 0.24
    signal = (body + crack) * gain
    place(track, start, signal * 0.707, signal * 0.707)


def write_ogg(name, signal):
    peak = float(np.max(np.abs(signal)))
    if peak > 0.9:
        signal *= 0.9 / peak
    with tempfile.TemporaryDirectory() as scratch:
        wav_path = Path(scratch) / "source.wav"
        with wave.open(str(wav_path), "wb") as output:
            output.setnchannels(2)
            output.setsampwidth(2)
            output.setframerate(RATE)
            output.writeframes((np.clip(signal, -1, 1) * 32767).astype("<i2").tobytes())
        subprocess.run(
            ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(wav_path),
             "-codec:a", "libvorbis", "-qscale:a", "5", str(ROOT / name)],
            check=True,
        )


def main():
    music = np.zeros((FRAMES, 2), dtype=np.float64)
    chords = [
        ([60, 64, 67, 71, 74], 36),  # Cmaj9
        ([59, 62, 67, 69, 74], 43),  # Gadd9
        ([60, 64, 67, 69, 71], 45),  # Am9
        ([57, 60, 64, 67, 72], 41),  # Fmaj9
        ([60, 62, 65, 69, 72], 38),  # Dm9
        ([59, 62, 67, 69, 74], 43),
        ([60, 64, 67, 69, 71], 45),
        ([57, 60, 64, 67, 72], 41),
        ([59, 62, 67, 69, 74], 43),
        ([60, 64, 67, 71, 74], 36),
    ]
    melody = [74, 71, 72, 69, 76, 74, 71, 69, 72, 67]
    for bar, (notes, root) in enumerate(chords):
        start = bar * 2.0
        pad(music, start, notes, 0.17 if bar < 3 else 0.22)
        bass(music, start, root, 0.15)
        bass(music, start + 1.0, root + 12, 0.075)
        bell(music, start + 0.0, melody[bar], 0.105, -0.28)
        bell(music, start + 0.75, notes[2] + 12, 0.055, 0.35)
        if bar >= 3:
            bell(music, start + 1.5, notes[1] + 12, 0.045, 0.2)
        for beat in (0.5, 1.5):
            soft_tick(music, start + beat, 0.013, 0.3 if beat == 0.5 else -0.3)
    fade = np.ones(FRAMES)
    fade[: round(0.16 * RATE)] = np.linspace(0, 1, round(0.16 * RATE))
    fade[-round(0.22 * RATE):] = np.linspace(1, 0, round(0.22 * RATE))
    music *= fade[:, None]

    foley = np.zeros((FRAMES, 2), dtype=np.float64)
    whoosh(foley, 1.78, 0.48, 0.085)
    bell(foley, 2.04, 86, 0.13, 0.45)
    whoosh(foley, 3.79, 0.50, 0.078, False)
    bell(foley, 4.04, 79, 0.11, -0.25)
    whoosh(foley, 5.7, 1.12, 0.14)
    impact(foley, 6.02, 0.13, 120)
    for i, point in enumerate((6.13, 6.26, 6.44, 6.72, 7.01, 7.39)):
        bell(foley, point, (81, 88, 84, 91, 86, 79)[i], 0.045, -0.6 + i * 0.24)
    whoosh(foley, 9.2, 0.95, 0.08, False)
    whoosh(foley, 12.62, 2.1, 0.12)
    for point, strength in ((13.24, 0.045), (13.76, 0.04), (14.35, 0.03)):
        impact(foley, point, strength, 75)
    whoosh(foley, 14.36, 0.72, 0.13, False)
    whoosh(foley, 16.2, 1.35, 0.095)
    impact(foley, 18.15, 0.15, 77)
    bell(foley, 18.53, 84, 0.07, 0.2)

    write_ogg("s98-original-score.ogg", music)
    write_ogg("s98-original-foley.ogg", foley)
    preview = music * 10 ** (5.5 / 20) + foley * 10 ** (7.5 / 20)
    write_ogg("s98-preview-mix.ogg", preview)


if __name__ == "__main__":
    main()
