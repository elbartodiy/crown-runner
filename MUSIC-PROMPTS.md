# Crown Runner — music prompts for Suno

Three loops, and the game now wires all three. Paste the **Style** text into Suno's
style box, tick **Instrumental**, and leave the lyrics box empty.

## What plays where

| File | Plays on |
|---|---|
| `music-calm.mp3` | attract screen, the taught pre-level, the closing report |
| `music-stage1.mp3` | stage 1 — restoration |
| `music-stage2.mp3` | stage 2 — implantation |

Stage 1 and stage 2 are the two tracks already in the cabinet. **The calm one is the
new one** — prompt 3 below. Drop the file in beside `index.html` under that exact
name and it starts working; a missing file fails soft and the game just runs silent.

Two notes before you generate:

- Ask for a **loop**, not a song. Suno tends to write an intro and an ending; say
  "loopable, no fade, no intro" and cut the top and tail yourself.
- The game synthesises all its effects plus a speed-linked drone, and the 8-bit speech
  blips in the lesson sit around 150–260 Hz. Keep the bass out of a mud fight with
  that: ask for a **tight triangle bass, not a sub**.

---

## 3 · Calm loop — the lesson, and the cabinet at rest  ← the new one

This one has two jobs at once, and they pull the same way. Under the lesson it has to
leave the doctor's voice and the typing on top of it, so it must be sparse and stay out
of the mid-range. On the attract screen it plays for eight hours next to people who are
working, so it has to be something a stand can live with — inviting, not calling.

### Why the first attempt opened with a long intro

Because it was asked for a piece of music, and a piece of music begins. Suno builds a
song shape by default — an opening, a body, an ending — and "no intro" placed at the end
of the style box is a footnote it weighs against everything before it.

The fix is to stop describing a song. Describe **a fragment of something already
playing**: an eight-bar loop, caught mid-phrase, that repeats. Suno has no reason to
write an opening for a thing that is defined as having no beginning. Three levers, in
order of how much they actually move it:

1. **Frame it as an excerpt, not a piece** — "mid-song excerpt", "cold open", "the
   melody is already running when the clip starts".
2. **Front-load it.** The style box is weighted towards its opening words. The
   anti-intro clause goes first, not last.
3. **Use the negative field.** If your Suno has *Exclude styles*, put the list there —
   it is a harder constraint than anything in the positive prompt.

**Style** — paste this whole thing:

```
Cold open: an eight-bar 8-bit chiptune loop caught mid-phrase, already running at full
arrangement from the very first beat, repeating verbatim with no development and no
ending. Not a song, a looping fragment. NES 2A03 palette, calm and patient, 110 BPM,
natural minor, unhurried and warm rather than heroic. One soft pulse lead on a 25% duty
cycle carrying a simple four-note motif, answered by the same motif a fifth up. Sparse
triangle bass on the root, two notes to the bar. A single quiet noise-channel tick on
the half bar and nothing else. Long rests between phrases, plenty of air, nothing in
the middle register. The sound of a good machine idling correctly. Dry, no reverb.
```

**Exclude styles** (or append to the style box if your version has no such field):

```
intro, outro, ambient intro, fade in, fade out, build-up, riser, swell, drum fill,
count-in, silence at the start, sparse opening, atmospheric opening, song structure,
verse, chorus, bridge, breakdown, key change, ritardando, vocals
```

**Lyrics box:** leave it completely empty and tick **Instrumental**. Do not put
`[Intro]`, `[Verse]` or any other tag in it — a structure tag is an invitation to build
a structure, and `[Intro: none]` reads to it as the word "intro".

### If the take is still wrong

- *Still opens quietly for a few bars* — put `first beat is the loudest beat` at the very
  front, and add `the clip starts on a downbeat, not on an upbeat`.
- *Too sleepy, no melody* — Suno reads "calm" as "ambient" more often than not. Add
  `clear singable melody, one note per beat in the lead, no pads, no drones`.
- *Too busy under the speech* — add `no arpeggios, no sixteenth notes, lead only in the
  upper octave` and drop the percussion clause entirely.

Generate two or three and pick by playing them against the lesson with the game running.
The one to keep is the one you stop noticing.

---

## 1 · Stage 1 loop — the shift, driving

**Style**

```
8-bit chiptune run-and-gun action theme in the spirit of late-80s NES side-scroller
soundtracks — heroic minor-key melody over a galloping sixteenth-note triangle bass,
duty-cycle pulse lead, snappy noise percussion with a marching backbeat. 158 BPM,
harmonic minor, relentless forward motion, no breakdown. Melody built from short
four-bar answering phrases. Bright and metallic, dry mix, tight low end.
Loopable, no intro, no fade, instrumental.
```

## 2 · Stage 2 loop — implant surgery, the formation closing in

**Style**

```
8-bit chiptune boss-approach theme. Same NES palette as before but tenser: chromatic
descending bass line, off-beat pulse stabs, tremolo lead held over the bar, noise
channel used as a mechanical tick rather than a backbeat. 168 BPM, minor with a
flattened fifth, mounting pressure, no resolution. Sparse in the first half, dense in
the second so it can sit under a screen that is filling up. Dry, no reverb.
Loopable, no intro, no fade, instrumental.
```

---

## Optional short cues

Worth generating as separate 4–8 second clips rather than trimming from a loop:

| Cue | Style |
|---|---|
| Stage hand-off | `8-bit chiptune fanfare, four bars, rising major arpeggio, triumphant, NES pulse and triangle, dry, no fade` |
| Shift complete | `8-bit chiptune outro, six bars, warm major cadence, slowing, NES palette, ends on a held chord` |
| Line stopped | `8-bit chiptune failure sting, three bars, descending chromatic, minor, abrupt end` |

## How the tracks are wired

Nothing to edit — the loops are read by name. `MUSIC` at the top of the script maps the
three slots, `musTick()` picks one per frame from the game's state, and the volume ramps
over `MUS_FADE` seconds rather than cutting. The lesson ducks whatever is playing to
`MUS_DUCK` while a panel is up. `M` mutes.

Keep the files as `.mp3` or `.m4a`. The cabinet build loads them from the folder at full
quality; the shareable single-file build inlines mono 40 kbps copies, which is why
`crown-runner-standalone.html` is a couple of megabytes rather than nine. The rebuild
step makes those copies:

```bash
cd "07. Games/crown-runner" && for f in calm stage1 stage2; do afconvert -f m4af -d "aac@32000" -b 40000 -c 1 "music-$f.mp3" "music-$f.m4a"; done
```
