# CROWN RUNNER — Glidewell Dental Arcade

A cabinet title. Runs entirely in a browser, offline, with no build step and no
dependencies.

## Files

| File | Use |
|---|---|
| `crown-runner-standalone.html` | **Deploy this.** One self-contained file — the logo artwork is inlined, so it needs no asset folder, no server and no network. |
| `index.html` | Source. Loads the logo PNGs from this folder. Edit here. |
| `glidewell-mark.png` | The G tile, cropped from the official logo. |
| `glidewell-logo.png` | The full lockup, used on the attract screen. |
| `glidewell-wordmark.png` | Wordmark only. Spare — not referenced by the game. |

After editing `index.html`, rebuild the standalone file:

```bash
cd "07. Games/crown-runner" && python3 - <<'EOF'
import base64
src=open('index.html',encoding='utf-8').read()
u=lambda p:'data:image/png;base64,'+base64.b64encode(open(p,'rb').read()).decode()
src=src.replace("MARK.src='glidewell-mark.png';","MARK.src='%s';"%u('glidewell-mark.png'),1)
src=src.replace("LOGO.src='glidewell-logo.png';","LOGO.src='%s';"%u('glidewell-logo.png'),1)
open('crown-runner-standalone.html','w',encoding='utf-8').write(src)
print('rebuilt')
EOF
```

## Controls

| Key | Cabinet button | Action |
|---|---|---|
| `Enter` / `1` | Start | start a credit |
| `← →` | joystick | aim |
| `Z` / `LCtrl` | Button 1 | hold to scan *(stage 1)* · fire implant *(stage 2)* |
| `X` / `LAlt` | Button 2 | fire the crown *(both stages)* |
| `C` / `Space` *(hold)* | Button 3 | slow down · slows the marching ranks in stage 2 |
| `F` | — | fullscreen |
| `P` | — | frame-rate readout |
| `K` | — | CRT tube effect on / off |
| `Start` / `1` / `Enter` | Start | **pause** during a shift |
| `Esc` | — | end the round |

Key names follow MAME / RetroPie defaults, so a stock USB encoder works with no
remapping.

On screen the legend is drawn as the panel itself — a ball-top stick and lettered
arcade buttons (`icoJoystick`, `icoButton`, packed by `ctrlEntry`) — rather than as
lines of small grey type. The sign is always at least as large as the word beside it.

## Music

The game synthesises its own effects and a speed-linked drone; there is no music
track. Drop one in as a looping file if wanted — see the Suno prompts kept with the
project notes.

## Deploy to the cabinet

Copy `crown-runner-standalone.html` to the cabinet machine, then launch a browser
in kiosk mode.

**Raspberry Pi / Linux**

```bash
chromium-browser --kiosk --noerrdialogs --disable-infobars \
  --autoplay-policy=no-user-gesture-required \
  --check-for-update-interval=31536000 \
  file:///home/pi/crown-runner-standalone.html
```

**Windows**

```bash
"C:\Program Files\Google\Chrome\Application\chrome.exe" --kiosk --noerrdialogs --disable-infobars --autoplay-policy=no-user-gesture-required "file:///C:/arcade/crown-runner-standalone.html"
```

**macOS**

```bash
open -a "Google Chrome" --args --kiosk --autoplay-policy=no-user-gesture-required "file:///Users/Shared/crown-runner-standalone.html"
```

### Keep the screen awake

```bash
xset s off && xset -dpms && xset s noblank
```

### Start it on boot (Raspberry Pi OS desktop)

Add the kiosk command as the last line of
`~/.config/lxsession/LXDE-pi/autostart`, prefixed with `@`.

### Batocera / RetroPie

Drop a launcher script into the `ports` folder that runs the kiosk command above;
the game then appears in the menu alongside the other titles.

## Notes for the booth

- **Sound** needs one input event before the browser will play it. The first
  button press unlocks it, so the attract screen is silent until someone touches
  the panel — that is normal, not a fault.
- **High scores** live in the browser's local storage on that machine, so they
  survive restarts but do not travel with the file. Clearing browser data resets
  the table.
- **The panel is assumed 1920x1080.** The canvas is a fixed 16:9 and letterboxes
  on anything else, so no layout breaks on a different screen.
- **If it feels slow, press `P`.** The loop clamps its timestep, which means a
  performance problem shows up as slow motion rather than stutter — the readout
  is the only way to tell the two apart. Around 60 FPS means the renderer is fine
  and the pace is a design number (`CFG.speed.base`).

## The taught pre-level

There is one piece of onboarding, not two. The comic panels and the guided level
were teaching the same things twice, so the doctor and the intern moved into the
level itself: one guided tooth at 45% speed, no clock, nothing at stake, and the
cast standing in the empty top band explaining the element that is lit. He teaches,
she asks the question a first-timer actually has, and the text still types itself in
their two voices (`TYPE_CPS`, one square-wave blip per glyph, his pitched below hers). `TUTOR` is a list of beats; each names the element it is about
and a condition that fires it. When a beat fires the game freezes, the element is
ringed and glows **for one second alone**, and only then does a paper panel appear
with two or three lines and a dashed leader back to the thing it describes. The
first press finishes the line, the next lets the level run on — and `TUTOR_GAP`
seconds of play must pass before the following beat may fire, so the lesson never
arrives as a wall of text.

The beats are: the cracked tooth, the implant line, the closing scan ring, the mill
running on the wand, the crown in the magazine, the seated result, the **G mark**
(which upgrades the scanner) and the **debris** (which does not) — the last two bring
their own prop on with an `enter()` hook, and nothing in the pre-level can actually
cost you: a debris hit shakes and flashes but is not billed, and a tooth lost here
does not go on the surgery list.

**It cannot dead-end, twice over.** A beat that waits on a prop could hang the whole
lesson — collect the G mark or let the debris pass during the gap between beats and
the thing the line is about is gone, so the condition never comes true, and because
the pre-level is still running no teeth arrive either: you fly an empty bore forever.
A vanished prop is sent again, and any beat that still has not fired after nine
seconds is skipped rather than blocking the shift.

A missed shot used to end the lesson for good — the tooth was
gone, the pre-level sends no more, and the closing beat waits on a seated crown that
could never arrive. While the loop is unfinished another tooth is always sent, as
many as it takes to complete the cycle once. Add or
reword them in the `TUTOR` array — `tgt` picks the element (`tooth`, `line`, `mill`,
`mag`), `at` is the trigger.

## Two stages

**Stage 1 — Restoration.** Cracked teeth arrive, you crown them. Density ramps
continuously across the shift rather than in level steps — a gap of `spawn.gapStart`
at the first whistle down to `spawn.gapEnd` at the last, roughly four teeth per ten
seconds opening out to fourteen — and debris stays out of the first
`spawn.debrisAfter` seconds entirely, so the opening is quiet enough to learn in.

A tooth that crosses the implant line is not discarded: it is an extraction, and
extractions queue for surgery. The slip header counts them, `TO IMPLANT n/10`. At
`CFG.implantsToAdvance` the round hands over.

**Stage 2 — Implantation.** A different game: two ranks of sockets march across the
bore and step closer on every reversal. The near rank shields the far one, so it is
worked first. Two buttons, left to right in the order of the operation — `Z` fires a **Hahn
fixture**, `X` fires a **crown**. Fixtures are supplied by Glidewell and unlimited
(`CFG.surgery.unlimitedImplants`); only crowns are counted, and a plate announcing
the free fixtures shows before the hand-off — and each socket needs the fixture first, then the crown.
A wrong part is a miss that spends stock and breaks the combo. Run the stock out with
work left, or let a rank reach the wand, and it costs a remake. Clear both ranks and
the next wave arrives faster with one round less of each.

## The closing report

Nobody leaves a show floor having lost. The report leads with **teeth treated** and
turns that into the point the cabinet exists to make: a same-day case is one chair
visit, a case that leaves the building is two. Both plates are shown side by side
with the arithmetic's **basis printed underneath**, because it is a stated model and
not a borrowed statistic — change `VISITS_SAME` / `VISITS_LAB` in `drawOver` if the
assumption should differ.

The headline is always `SHIFT COMPLETE`; how the round ended is a factual sub-line
rather than a verdict. The five-star clinic rating that used to sit here, and on the
slip, is gone: on a stand a low score reads as a judgement on the visitor. The
rating is still tracked internally (`CFG.rating`, `rate()`) if it is ever wanted
back, but nothing displays it.

The clock and the bore pause for the hand-off while the doctor says his line; any
button cuts it short. Everything routes through one `stock()` switch and one
`partPath()`, so the pipeline itself is unchanged between stages.

## Pixel art, one asset at a time

Downsampling the whole frame (`PIXEL=2`) did unify the styles, but it dirtied
everything — the type furred up and the slip's hairlines turned to mush — so it was
reverted to `PIXEL=1`. The game renders crisp and assets are converted to sprites by
hand instead.

**Done: the type.** A 5x7 bitmap face is authored in code (`FONT5x7`, `pixText`) and
every `txt()` call now renders through it. A webfont was never possible — the cabinet
is offline and the published page blocks external hosts — and a hand-built face lands
on the same grid the sprites use, which a hinted outline never would. Digits are four
columns wide so long numbers stay compact. Block size is derived from the px size that
call sites already passed, so nothing else had to change, but the advance is a little
wider than the old face: two rows on the case slip needed reflowing.

**Done: hit bursts.** Eight spikes of blocks that shoot out and snap off in a third of
a second (`pixBurst`), fired on a seated crown, a placed fixture, a contamination hit
and a scanner upgrade. The soft square particles stay for dust and powder, where a
scatter is right.

**Done: the scanner.** Four tones and a hard dark keyline, laid into every empty cell
that touches the silhouette — without that keyline a sprite has nothing holding it off
the background and reads as a blocky gradient rather than pixel art. Its silhouette comes from a per-row width profile so the shape
is authored but still lands square on the grid, and the block size follows the
projection, so it pixellates consistently at any distance. It deliberately does not
rotate — rotating a pixel sprite destroys the grid, so banking is a one-block shift.

Sprite units must be even (`u=8`) or the characters land off-grid and go soft.

## The CRT tube

The frame is rendered into a fixed 1920x1080 buffer and then put through a WebGL
fragment shader: curved-glass barrel distortion, per-channel radial offset,
shadow-mask lines and corner falloff. It costs a texture upload per frame,
roughly 2 ms, rather than the several full-frame passes the same look would need
in Canvas 2D.

It **fails soft**. If WebGL is unavailable, the shader fails to compile, or the
pass throws, the buffer is blitted straight through and the game keeps running
without the effect. Press `K` to compare.

Strength lives in `CFG.crt`. It is deliberately restrained: at full strength the
fringing doubled the type and cost real legibility, which matters more than the
effect on a show floor. Scanline pitch is derived from the live backing height,
so it does not moire on a panel that is not 1080p.

## The implant line

The crimson ring in the bore is the clinical boundary, not an abstract deadline:
outside it a cracked tooth can still be crowned, inside it there is no runway left
to cut a crown and fire it home, so the case becomes an extraction and an implant.
The scanner refuses to lock anything past it and the tooth collapses on it, labelled
`IMPLANT CASE`. The collapse is a process of about `CRUMBLE_SECS` — the silhouette
breaks into bands that slide and sink while shedding powder — rather than an instant
burst of fragments.

## If the screen is black

Any startup failure now paints a readable report over the page — the message, the
file and line, the viewport and canvas geometry, and the browser. Send that text
on and it can be diagnosed.

The one cause already fixed: an embed that reports a zero viewport at load used to
scale the canvas to 0x0 css pixels, leaving a black page with no way back. `fit()`
now falls back to the document box and never scales below 0.05, and the layout is
re-checked by `ResizeObserver` as well as by resize events.

## Tuning

Everything worth adjusting is in the `CFG` block at the top of `index.html`:
round length, number of remakes, magazine size, scan and mill times per scanner
generation, speeds, and scoring.
