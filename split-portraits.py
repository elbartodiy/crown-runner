#!/usr/bin/env python3
"""Split a two-portrait image into the two files the game loads.

    python3 split-portraits.py portraits-raw.png

Writes cast-jim.png (left half) and cast-intern.png (right half), each 120 x 180 art pixels —
the size the game draws at 3x, so every art pixel lands on one 3px block of the shared grid.

A source that is a whole multiple of 240 x 180 reduces exactly and loses nothing. Anything else
has to be resampled between grid positions and softens; the script says so rather than hiding it.
"""
import os, sys
from PIL import Image

TARGET_W, TARGET_H = 120, 180

def main():
    if len(sys.argv) < 2:
        print(__doc__); return 1
    src = sys.argv[1]
    if not os.path.exists(src):
        print('no such file:', src); return 1

    im = Image.open(src).convert('RGB')
    print('%s  %dx%d' % (src, im.width, im.height))

    ratio = im.width / (TARGET_W * 2)
    if abs(ratio - round(ratio)) < 1e-9 and abs(im.height / TARGET_H - ratio) < 1e-9:
        print('exact %dx reduction - nothing is lost' % round(ratio))
    else:
        # A generator asked for 1440x1080 hands back 1448x1086 and calls it 4:3. Rather than
        # resample between grid positions - which is what softens an image - trim the few pixels
        # of overshoot off the edges and then reduce by a whole number. Eight pixels of margin
        # cost nothing; a fractional reduction costs the crispness of every pixel in the frame.
        k = round(ratio)
        want_w, want_h = TARGET_W * 2 * k, TARGET_H * k
        if k >= 1 and abs(im.width - want_w) <= max(12, want_w * 0.01) \
                  and abs(im.height - want_h) <= max(12, want_h * 0.01):
            dx, dy = (im.width - want_w) // 2, (im.height - want_h) // 2
            im = im.crop((dx, dy, dx + want_w, dy + want_h))
            print('trimmed %dx%d to %dx%d from the centre, then an exact %dx reduction'
                  % (im.width + (0), im.height + (0), want_w, want_h, k))
            print('   (overshoot was %d x %d px)' % (dx * 2, dy * 2))
        else:
            print('WARNING: %dx%d is not a whole multiple of %dx%d (ratio %.3f).'
                  % (im.width, im.height, TARGET_W * 2, TARGET_H, ratio))
            print('         It will be resampled between grid positions and will look softer than')
            print('         the rest of the screen. Regenerate at 240x180, 480x360, 720x540,')
            print('         960x720 or 1440x1080.')

    half = im.width // 2
    out = [('cast-jim.png', im.crop((0, 0, half, im.height))),
           ('cast-intern.png', im.crop((half, 0, im.width, im.height)))]
    here = os.path.dirname(os.path.abspath(src))
    for name, part in out:
        if part.size != (TARGET_W, TARGET_H):
            part = part.resize((TARGET_W, TARGET_H), Image.BOX)
        dst = os.path.join(here, name)
        part.save(dst, optimize=True)
        print('wrote %-18s %dx%d art px  ->  %dx%d on screen  %.0f KB'
              % (name, TARGET_W, TARGET_H, TARGET_W * 3, TARGET_H * 3,
                 os.path.getsize(dst) / 1024))
    return 0

if __name__ == '__main__':
    sys.exit(main())
