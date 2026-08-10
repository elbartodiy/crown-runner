#!/usr/bin/env python3
"""Trim a music file to a loop, using only macOS built-ins and the standard library.

Suno almost always writes an intro and an ending even when told not to. Rather than
re-rolling the generation until it behaves, cut the file:

    python3 trim-loop.py music-calm.mp3 12.5            # drop the first 12.5s
    python3 trim-loop.py music-calm.mp3 12.5 76.0       # and everything after 76.0s
    python3 trim-loop.py music-calm.mp3 --where         # just report where sound starts

It writes two files beside the input:
    <name>.m4a        full quality, for the cabinet
    <name>.small.m4a  mono 40 kbps, for inlining into the single-file build

There is no ffmpeg on a stock Mac, so this goes via afconvert to WAV, slices the raw
PCM with the `wave` module, and encodes back with afconvert.
"""
import os, subprocess, sys, tempfile, wave, audioop

def run(*a):
    subprocess.run(a, check=True, capture_output=True)

def main():
    args = [a for a in sys.argv[1:]]
    if not args:
        print(__doc__); return 1
    src = args[0]
    if not os.path.exists(src):
        print('no such file:', src); return 1
    where = '--where' in args
    times = [float(a) for a in args[1:] if not a.startswith('--')]
    start = times[0] if len(times) > 0 else 0.0
    end   = times[1] if len(times) > 1 else None

    stem = os.path.splitext(src)[0]
    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, 'a.wav')
        run('afconvert', '-f', 'WAVE', '-d', 'LEI16', src, wav)
        with wave.open(wav, 'rb') as w:
            ch, sw, sr, n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
            frames = w.readframes(n)
        dur = n / sr
        print('%s  %.1fs  %dch  %dHz' % (src, dur, ch, sr))

        if where:
            # first frame whose 40ms window rises above -42 dBFS, i.e. where sound starts
            win = int(sr * 0.04) * ch * sw
            for i in range(0, len(frames) - win, win):
                if audioop.rms(frames[i:i+win], sw) > 260:
                    print('sound starts at %.2fs' % (i / (ch * sw) / sr))
                    return 0
            print('no sound found above the floor'); return 0

        a = int(start * sr) * ch * sw
        b = int(end * sr) * ch * sw if end else len(frames)
        cut = frames[a:b]
        print('keeping %.2fs .. %.2fs  (%.1fs)' % (start, (b/(ch*sw))/sr, len(cut)/(ch*sw)/sr))

        out_wav = os.path.join(tmp, 'b.wav')
        with wave.open(out_wav, 'wb') as w:
            w.setnchannels(ch); w.setsampwidth(sw); w.setframerate(sr)
            w.writeframes(cut)

        full = stem + '.m4a'
        small = stem + '.small.m4a'
        run('afconvert', '-f', 'm4af', '-d', 'aac', '-b', '128000', out_wav, full)
        run('afconvert', '-f', 'm4af', '-d', 'aac@32000', '-b', '40000', '-c', '1',
            out_wav, small)
        for f in (full, small):
            print('wrote %-28s %.2f MB' % (f, os.path.getsize(f) / 1048576))
    return 0

if __name__ == '__main__':
    sys.exit(main())
