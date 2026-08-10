# The title illustration — what to generate and how it gets in

The game loads `attract-poster.png` from this folder if it is there, and ignores it if it is
not. Drop the file in and the attract screen rearranges itself around it; nothing else to do.

## Read this before generating

**Ask for pixel art, not a painting.** Everything on screen is now on a 3px grid with a
hand-built bitmap face. A rendered movie poster beside it will read as a picture pasted in
from somewhere else — which is the exact thing you caught me on before, with the vector game
and the pixel cast. The good news is that the reference you want *is* a pixel-art tradition:
late-80s and early-90s arcade title screens drew heroic character art in pixels, with hard edges
and a small palette.

Three references settle the register, and between them they answer the one open question:

- **NES Contra** — two figures back to back, cropped at the waist, lit from the sides.
- **Battletoads / Double Dragon** — flat, hard-edged, sixteen colours, heavy outlines.
- **Bare Knuckle / Streets of Rage** — and this one settles the background: the figures stand
  against a real scene, a night skyline, not a void.

So: **a dark scene, not plain black.** The chair goes behind them the way the city goes behind
the Streets of Rage three. It is drawn as a square plate on the screen with the bore behind it,
which makes it a framed poster — and a square holding a scene needs a thin edge or it reads as
torn, so the game draws one. Naming all three games in the prompt is worth more to a generator
than any amount of adjectives.

**Three frames in one image will not work.** A generator cannot hold two figures identical
across three panels — faces, colours and line weight all drift, and a loop built from drifting
art reads as a fault rather than as motion. Generate **one** poster. The movement is already
done in code: the plate reveals in four steps (dark, a third, two thirds, up), then breathes by
one block and a pale sweep crosses it on a slow cycle. That is how an arcade attract screen did
it and it costs nothing.

If you still want a hand-made loop, the loader supports it: send a **3:1 strip** — three square
panels side by side in one PNG, same size — and it cycles them at six frames a second instead of
running the code loop. Worth trying only if you cut the frames yourself from one generated
poster, moving a single element.

## The size to ask for — this one matters most

**Give me one of these, exactly:**

| Deliver | Why |
|---|---|
| **640 × 360** | best. No resampling at all — it goes straight in |
| **1280 × 720** | exactly 2× — a clean halving, every output pixel is four input pixels and nothing straddles |
| **1920 × 1080** | exactly 3× — same, and the highest quality most generators will give |
| 2560 × 1440 | exactly 4× — also fine |

**Avoid anything else.** The square 1254 × 1254 was doubly wrong: it had to be padded into 16:9,
and 1254 → 640 is a reduction of 1.959, which is not a whole number. When the ratio is not whole,
every output pixel samples a window that does not line up with the input grid, so neighbouring
output pixels share input pixels and come out correlated — which is exactly what "the picture
smears" means. At 2× or 3× the reduction partitions the input cleanly and nothing is shared.

That is the whole reason I was reducing it: the file did not match the screen. Given a file that
does, I do nothing to it, and there is nothing left to soften.

## Prompt

**16:9 landscape.** Ask for 1920 x 1080, or any multiple of it. The game reduces it to 640 x 360
art pixels — that is 1920/3, so every art pixel lands on exactly one 3px block of the grid the
rest of the screen uses. Square was my mistake in the brief, and it is what produced the hard cut
down the side: the figures ended, and the picture ended with them.

The composition matters as much as the style. The screen carries a title block in the **upper
left**, so that corner has to be dark room and nothing else. Ask for the figures in the right two
thirds.

```
Pixel art title screen art in the style of the NES Contra, Battletoads Double Dragon and Sega
Bare Knuckle / Streets of Rage title screens. Wide 16:9 landscape composition, the scene fills
the whole frame edge to edge with nothing cut off abruptly. Two dental clinicians standing back
to back in a heroic action pose, placed in the right two thirds of the frame, three-quarter view,
from the thighs up. The upper left third is empty dark surgery — a window with closed blinds, deep
shadow, no detail — kept clear for a title. On the left of the pair a senior dentist in a white
coat with a crimson tie, grey hair, surgical loupes on the forehead, holding an intraoral scanner
wand raised like a weapon with a pale blue glow at its tip. On the right a younger clinician in
blue scrubs, holding a single white dental crown in fine tweezers up to the light. The dim surgery
continues past them to both edges: a treatment chair in dark silhouette, an overhead operating
lamp throwing a hard cone of light, a milling unit glowing faintly, instrument trays, deep shadow
in all four corners so the image falls away into black at the edges rather than stopping. Strong
rim light on both figures. The bottom fifth of the frame is dark and almost empty. Hard-edged
pixels, no anti-aliasing, no gradients, no blur, limited palette of flat colours: crimson, dark
magenta, near-black, deep teal, bone white, cream, pale blue, mid grey, amber. Strong dark
outlines, clean readable silhouettes.
```

**Exclude / negative:**

```
photorealistic, 3d render, painted, airbrushed, soft focus, blurry, anti-aliased, gradient mesh,
watermark, text, logo, lettering, signature, borders, frame, letterboxing, black bars, vignette
ring, cropped heads, extra limbs, extra fingers, horror, gore, deformed faces, modern flat vector
illustration, chibi
```

Three things in there are load-bearing:

- **"continues past them to both edges"**, with objects named left and right — so the scene does not
  end where the figures do. That is exactly what makes the seam visible now.
- **"deep shadow in all four corners"** — the falling away into black is done by the picture, not by
  a filter afterwards. Mine was fading content that had already been cut, which is why it read as
  an edge rather than as darkness.
- **"upper left third is empty dark surgery"** and **"bottom fifth is dark"** — those are where the
  title and the invitation go. The screen darkens both bands itself as insurance, but art that
  arrives already dark there needs less of it and looks better for it.

## Notes that will save a re-roll

- **No lettering.** The screen already sets the title, the pipeline line and PRESS START in the
  game's own face. Text inside the illustration will collide with it and will be misspelled.
- **A dim room, not a bright one.** The plate sits on a dark screen with the bore behind it, so a
  brightly lit background will punch a hole in the composition. Ask for night, deep shadow and one
  hard light source — which is what the Streets of Rage skyline does: dark field, a few lit
  windows.
- **Keep the edges quiet.** The plate is drawn at 620 x 620; anything important in the outer 6%
  ends up against the screen's own furniture.
- **The scanner beam should be pale blue** (`#7FD4F0`) — the same blue the scan uses in play, so
  the poster and the game agree about what the instrument does.
- Faces at this size are a few pixels wide. Ask for readable silhouettes rather than detail; a
  generator asked for detailed faces at pixel scale returns mush.

## When you have it

Save as `attract-poster.png` next to `index.html`. If it comes back as a painting rather than
pixel art and you like it anyway, send it over — I can snap it onto the grid: resample to the
plate's size taking the dominant colour per cell, quantise to the palette above, drop partial
alpha. It will not invent detail that is not in it, but it will stop being a foreign object on
the screen.

**Size matters for the shareable link.** The single-file build inlines every asset as base64, so
a 1.5 MB PNG adds about 2 MB to it. Save the poster as an 8-bit palette PNG — at sixteen colours
it should come out under 200 KB, and pixel art loses nothing by it.
