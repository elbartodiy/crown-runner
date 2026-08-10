# Sprite spec — what to hand me

Yes, this is the right way round. Everything I have been fighting comes from generating
art with code: one pixel size per element instead of one for the whole screen. Drawn
sprites fix that at the source.

Read the two hard rules first — they matter more than the sizes.

## Rule 1 · No anti-aliasing

Every pixel fully opaque or fully transparent. No soft edges, no 50% grey fringe, no
drop shadows, no gradients. A single row of half-transparent pixels around a sprite is
exactly what has been reading as "dirty" on the cabinet, and the CRT pass magnifies it.

## Rule 2 · One art pixel

Author at **1 art pixel = 1 image pixel** and send it at that size — small files, e.g.
the wand is a 45 × 73 PNG, not 135 × 219. I scale ×3 with nearest-neighbour at draw
time. If a sprite arrives pre-scaled, every element has to be pre-scaled by the *same*
factor or the screen goes back to mixed resolutions.

## Sizes

| Element | Art px | Notes |
|---|---:|---|
| Scanner wand | 45 × 73 | glossy white, brushed collar, dark optics slot, one blue button, a hatch mid-body |
| Cracked tooth | 44 × 44 | molar, dull and stained, a visible fissure |
| Prepped tooth | 44 × 44 | same molar, bright bone, a clean margin line |
| Crown | 26 × 22 | cap only, no roots |
| Hahn fixture | 20 × 34 | tapered implant screw, platform on top, thread ridges |
| Extraction socket | 30 × 30 | bone plate with an open bore through it |
| Moisture drop | 24 × 30 | teardrop, pale blue, one specular block |
| Glidewell G pickup | 26 × 26 | the logo tile, hard square corners |
| Doctor | 30 × 56 | white coat, red tie, grey hair, glasses |
| Intern | 30 × 56 | blue scrubs |
| Debris chunk | 20 × 20 | 3 frames of break-up if easy |

Four frames of the tooth breaking apart would be a real gain — the collapse is animated
in code right now and it is the weakest thing on screen.

## Palette

Please stay on these. They are sampled from the official logo and the product line, and
the game's colour logic depends on them.

```
crimson    #EB0045      grey        #808285
bone       #F2ECDF      score amber #FFCC33
graphite   #1E2025      keyline     #0A0C10
blue       #0E86D4      pale blue   #7FD4F0
BruxZir    #F2E8D5      Obsidian    #57B89A      Hahn #F0536B
paper      #F4F1E8      ink         #1E1E1E
```

Max **four tones per material plus the keyline**. Every sprite gets a 1px `#0A0C10`
outline — that keyline is what holds a sprite off the background; without it the art
reads as a blocky gradient no matter how good the shading is.

## Format

Separate PNGs with alpha, one per element, named as in the table. Easier and far less
error-prone for me than slicing a sheet. If you would rather send one sheet, use
uniform cells and tell me the cell size.

## The honest caveat

**Image generators do not produce clean pixel art.** They produce pixel-*looking* art:
anti-aliased edges, pixels that drift off the grid, and different pixel sizes within one
image. If you generate the sheet, expect it to break both rules above.

Two ways round it, and the second is the one I would take:

1. Draw them in a real pixel editor — Aseprite, or Piskel and Lospec free in a browser.
   Set the canvas to the exact art-px size from the table and the rules hold by
   construction.
2. **Send me whatever you generate anyway.** I can snap it to the grid: resample down to
   the art-px size taking the dominant colour per cell, quantise to the palette above,
   drop partial alpha, and add the keyline. That turns a fuzzy generated sprite into
   clean pixel art. It will not invent detail that is not there, but it will be honest
   pixel art on one grid.

Either way, send them over and I will wire them in — loading real sprites will also let
me delete a good deal of drawing code.
