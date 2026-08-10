#!/usr/bin/env python3
"""Snap the generated title illustration onto the game's pixel grid.

    python3 snap-poster.py attract-poster-raw.png

Writes `attract-poster.png` beside it, ready for the game to pick up.

Why this exists: an image generator asked for pixel art returns pixel-*looking* art. The
edges are anti-aliased, the "pixels" are not all the same size, and the palette runs to
thousands of colours. Dropped in as-is it is softer than everything the game draws itself,
which is the mixed-resolution look this project has spent a long time getting rid of.

So: resample to exactly the number of art pixels the screen has room for. The game draws it
across 1920x1080 with smoothing off and its block is 3px, so 640x360 puts every art pixel on
exactly one block. A square source is fitted by height, centred, and faded into black at the
edges so it becomes a full-screen scene rather than a picture with bars beside it.

    --size N     art pixels across (default 640 = 1920px at a 3px block; height follows 16:9)
    --colors N   quantise to N colours (default 0 = leave the colours alone;
                 an adaptive palette drops small bright accents like the scanner LED)
    --keep-alpha preserve transparency instead of flattening onto black
    --clear-left F  wipe the left F of the frame back to black, for a mockup that has its
                 lettering baked in - the game draws that text live instead
    --sharpen N  local contrast boost, percent (default 130, 0 = off). Pays back in advance
                 the blur the CRT pass will add when it bends and resamples the frame
    --align P    where a square source sits in the 16:9 frame: right (default), center, left.
                 The screen's own title and panel live down the left, so right is what fits
"""
import sys, os
from PIL import Image, ImageFilter

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    flags = [a for a in sys.argv[1:] if a.startswith('--')]
    if not args:
        print(__doc__); return 1
    src = args[0]
    if not os.path.exists(src):
        print('no such file:', src); return 1

    def opt(name, default):
        for i, f in enumerate(flags):
            if f == '--' + name and i + 1 < len(flags):
                return int(flags[i + 1])
        for f in flags:
            if f.startswith('--' + name + '='):
                return int(f.split('=', 1)[1])
        return default

    # the flag values may have landed in args if written with a space
    size = 640
    colors = 0
    rest = args[1:]
    for i, a in enumerate(sys.argv[1:]):
        if a == '--size' and i + 1 < len(sys.argv[1:]): size = int(sys.argv[1:][i + 1])
        if a == '--colors' and i + 1 < len(sys.argv[1:]): colors = int(sys.argv[1:][i + 1])
    size = opt('size', size); colors = opt('colors', colors)
    keep_alpha = '--keep-alpha' in flags
    clear_left = 0.0
    align = 'right'
    sharpen = 130
    for i, a2 in enumerate(sys.argv[1:]):
        if a2 == '--clear-left' and i + 1 < len(sys.argv[1:]):
            clear_left = float(sys.argv[1:][i + 1])
        if a2.startswith('--clear-left='):
            clear_left = float(a2.split('=', 1)[1])
        if a2 == '--align' and i + 1 < len(sys.argv[1:]):
            align = sys.argv[1:][i + 1]
        if a2.startswith('--align='):
            align = a2.split('=', 1)[1]
        if a2 == '--sharpen' and i + 1 < len(sys.argv[1:]):
            sharpen = int(sys.argv[1:][i + 1])
        if a2.startswith('--sharpen='):
            sharpen = int(a2.split('=', 1)[1])

    im = Image.open(src)
    print('%s  %dx%d  %s' % (src, im.width, im.height, im.mode))
    im = im.convert('RGB')

    """The plate is the whole screen now, so the output is 16:9 rather than square.

    640 x 360 is not arbitrary: the game draws it across 1920 x 1080 with smoothing off and its
    block is 3px, so every art pixel lands on exactly one block. It is also three times less
    reduction than the old 207 square, which is where most of the softness came from — a 1254px
    source squeezed to 207 throws away six pixels out of seven.

    A square illustration cannot fill 16:9 without losing the heads or the hands, so it is fitted
    by height and centred, and the left and right edges are faded into black. That is what lets it
    read as one continuous dark room rather than as a picture with two black bars beside it.
    """
    W, H = size, round(size * 9 / 16)

    if abs(im.width / im.height - 16 / 9) < 0.06:
        # already the screen shape: straight down to the grid, nothing to pad or feather
        canvas = im.resize((W, H), Image.BOX)
        print('16:9 source - resized straight to the grid')
    else:
        # a square source is fitted by height, centred, and faded into the black
        # A square source is fitted by height. Where it sits across the frame is the whole
        # composition: the screen carries its title, panel and invitation down the left, so the
        # art goes right and the left stays black. Only the inner edge is feathered - the outer
        # one is against the frame and has nothing to blend into.
        art = im.resize((H, H), Image.BOX)
        canvas = Image.new('RGB', (W, H), (0, 0, 0))
        ox = W - H if align == 'right' else (0 if align == 'left' else (W - H) // 2)
        canvas.paste(art, (ox, 0))
        px = canvas.load()
        fade = max(8, H // 5)
        inner = [ox + i for i in range(fade)] if align == 'right' else \
                ([ox + H - 1 - i for i in range(fade)] if align == 'left' else None)
        for y in range(H):
            for i in range(fade):
                f = i / fade
                xs = ([ox + i] if align == 'right'
                      else [ox + H - 1 - i] if align == 'left'
                      else [ox + i, ox + H - 1 - i])
                for x in xs:
                    if 0 <= x < W:
                        r, g, b = px[x, y]
                        px[x, y] = (int(r * f), int(g * f), int(b * f))
        print('placed %s in a 16:9 frame, inner edge faded over %d px' % (align, fade))

    # A mockup arrives with its lettering already in it, and baked lettering cannot blink, cannot
    # follow the panel own bindings, and cannot show a score table. So the text side is wiped back
    # to black and the game draws all of it live in the same place. The wipe is soft at its inner
    # edge so it meets the art rather than cutting it.
    if clear_left > 0:
        px = canvas.load()
        edge = int(W * clear_left)
        soft = max(4, W // 40)
        for y in range(H):
            for x in range(min(W, edge + soft)):
                if x < edge:
                    px[x, y] = (0, 0, 0)
                else:
                    f = (x - edge) / soft
                    r, g, b = px[x, y]
                    px[x, y] = (int(r * f), int(g * f), int(b * f))
        print('cleared the left %.0f%% to black, softened over %d px' % (clear_left * 100, soft))

    # Pre-compensation, and it is the answer to the art still looking soft while the game's own
    # HUD looks crisp. The tube bends the finished frame and samples it smoothly, so a block
    # lands on non-integer coordinates and its edges get blended with the block beside it. The
    # HUD does not care - its neighbours are the same flat colour, so the blend changes nothing.
    # In an illustration every neighbour is a different colour, so every edge softens.
    #
    # Raising local contrast before the reduction pays that blur back in advance: the blocks
    # leave here harder than they need to be, and arrive on screen about right. Turn it off with
    # --sharpen 0 if it starts to ring.
    if sharpen:
        canvas = canvas.filter(ImageFilter.UnsharpMask(radius=1, percent=sharpen, threshold=2))
        print('sharpened by %d%% to survive the tube' % sharpen)

    out = canvas
    if colors:
        out = out.convert('P', palette=Image.ADAPTIVE, colors=colors,
                          dither=Image.NONE).convert('RGB')

    used = len(set(out.getdata()))
    dst = os.path.join(os.path.dirname(os.path.abspath(src)), 'attract-poster.png')
    out.save(dst, optimize=True)
    print('wrote %s  %dx%d  %d colours  %.0f KB'
          % (dst, W, H, used, os.path.getsize(dst) / 1024))
    print('the game draws this across %dx%d — 3 screen pixels per art pixel'
          % (W * 3, H * 3))
    print('art occupies x %d..%d, faded %d px into the black each side' % (ox, ox + H, fade))
    return 0

if __name__ == '__main__':
    sys.exit(main())
