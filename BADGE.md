# The badge, and the name in the game

A visitor scans their badge before playing, and the game knows who they are: it greets them on
the title screen, prints them on the case slip as the dentist the case came from, Jim addresses
them during the shift, the closing patient writes them a thank-you note **by name**, and the
score goes on the board under their name instead of three initials.

## On the cabinet, the shell already does the scanning

`~/Work/07. Games/arcade-cabinet` is what is installed on the machine. **Nothing in it needs
changing** — it was read only to find out what it already does, which is all of it:

- it shows a "Сканируй бейдж" gate before each of the four games;
- it drives the reader itself (over a serial port in host mode, so the aimer only lights while
  a badge is being asked for — or as a plain keyboard if the port was not granted);
- it parses the card;
- and it hands the result to the game:

```js
iframe.contentWindow.postMessage({game:'crown-runner', cmd:'player', name: displayName}, '*');
```

That message has always been accepted here; until now it only put the name on the high-score
table. Everything else in this document is what it does now.

Three facts about that shell, all of them handled:

- **`displayName` is `"First Last"` with the title stripped off** — the badge's `Dr.` lives in
  a separate field the shell does not send. That is why the game's own default is to address
  everyone as doctor; on a dental stand that is right, and CALL THEM DOCTOR turns it off. If a
  future shell does send `prefix` / `firstName` / `lastName`, the game uses them.
- **It re-sends the message every 400 ms** until the game reports `event:'start'`. Taking a
  badge is therefore idempotent — the same person arriving again is not a new scan. Without
  that guard the accept sound fired two and a half times a second on the title screen.
- **It does not send `config {outro:false}`**, so the game's own ending still plays — which is
  where the personalised note lives.

Verified against the shell's exact handshake (`cmd:'player'` followed by the synthetic Enter it
uses to press START): the game greets `DR HOWARD`, the slip carries `DR HOWARD`, the board gets
`HOWARD FARRAN`, and six repeats of the message make one sound, not six.

## What the badge can contain

This show's cards are **vCards** — scanning the QR yields a contact record — and a staff card is
six bare digits. Both are read the same way the shell reads them, so the two always agree. The
game additionally copes with delimited records and JSON, for the case where it is run outside
the shell with a reader of its own.

| on the badge | the game says | on the board |
|---|---|---|
| `BEGIN:VCARD … FN:Dr. Howard Farran … N:Farran;Howard;;Dr.` | DR HOWARD | HOWARD FARRAN |
| `Howard Farran` (what the shell sends) | DR HOWARD | HOWARD FARRAN |
| `123456` (staff card) | DOCTOR | EMP-123456 |
| `Eldar Asanov\|Glidewell\|DDS\|884213` | DR ELDAR | ELDAR ASANOV |

**The face in this build is hand-drawn** — twenty-six letters, ten digits and a few marks. A
name carrying anything else would draw as a row of question marks and then sit on the score
table looking like that for the rest of the show, so names are folded down to what can actually
be drawn. The show is American and the badges are Latin, so in practice that means one thing:
accents lose their marks and the letter stays — `José Müller-Ávila` → `JOSE MULLER-AVILA`.

## Fixing it on the stand, without a developer

Service screen (hold SCAN for three seconds on the title) → right-hand column, **BADGE READER**.
It prints the last scan: the raw text, the name taken out of it, what the game will call them,
and how many fields it found. Point the reader at a real badge and read it off.

Two rows in the list control the parse:

- **BADGE NAME FIELD** — `FIND IT` (default), or `FIELD 1…6` if the name is not where the
  guesser looks.
- **CALL THEM DOCTOR** — `ALWAYS` (default), `FROM THE BADGE`, or `NEVER`.

## The reader inside the game

Only used when the game runs **outside** the shell — off the standalone file, at a desk. A
barcode reader in keyboard mode types what it read very fast and then presses Enter, and that is
what is detected: characters a few milliseconds apart, and every printable key held for 75 ms
before the game may see it, so the first characters of a badge cannot leak through as button
presses. (A badge containing a `1` would otherwise press START mid-scan.) Nothing the panel
sends is held — a stick and eight buttons are not keys, so the cabinet pays nothing for this.

At a desk, with no reader at all: `?badge=Dr.%20Howard%20Farran%7CDDS` or `?player=HOWARD FARRAN`.

## With no badge

Exactly as before: impersonal patient quotes, three initials for the board, and the title screen
quietly inviting a scan.
