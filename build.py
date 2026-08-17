#!/usr/bin/env python3
"""Build crown-runner-standalone.html from index.html.

The cabinet runs offline and the published artifact is served under a strict CSP,
so the shipped file may not reference a single external asset. This inlines every
image and track as a data URI and then *checks* that nothing was missed — a bare
'foo.png' surviving into the build is a black rectangle on the stand, discovered
by a visitor rather than by us.

The build used to be an ad-hoc snippet retyped each time. It is a file now because
two of its checks exist only because the corresponding mistake shipped once.
"""
import base64, mimetypes, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(HERE, 'index.html')
OUT  = os.path.join(HERE, 'crown-runner-standalone.html')

IMAGES = ['glidewell-mark.png', 'glidewell-logo.png', 'attract-poster.png',
          'cast-jim.png', 'cast-intern.png'] + \
         ['patient-%02d.png' % i for i in range(1, 11)]
# Slot -> file. A slot whose file is absent is dropped from the map entirely and
# picked up at runtime by MUS_FALLBACK, which hops calm -> stage1. It must NOT be
# emitted as a second copy of another track: two <audio> elements on one source
# cross-fade against each other and you hear the same music twice, seconds apart.
TRACKS = {'calm': 'music-calm.mp3', 'stage1': 'music-stage1.mp3', 'stage2': 'music-stage2.mp3'}

# The tracks are ~180 kbps stereo MP3, three and a half megabytes each. Base64 inflates by a
# third, so shipping them untouched put the build at 9.9 MB — three times its usual size, for
# background loops nobody listens to closely. Transcoded to AAC they come back to ~40 kbps,
# which is what the file that has been on the stand all along actually contains.
AAC_BITRATE = 48000
CACHE = os.path.join(HERE, '.build-cache')


def transcode(src):
    """MP3 -> AAC/m4a via afconvert (macOS built-in). Cached on mtime."""
    os.makedirs(CACHE, exist_ok=True)
    dst = os.path.join(CACHE, os.path.splitext(os.path.basename(src))[0] + '.m4a')
    if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
        return dst
    subprocess.run(['afconvert', '-f', 'm4af', '-d', 'aac', '-b', str(AAC_BITRATE), src, dst],
                   check=True)
    return dst


def data_uri(path):
    mime = mimetypes.guess_type(path)[0] or 'application/octet-stream'
    with open(path, 'rb') as f:
        return 'data:%s;base64,%s' % (mime, base64.b64encode(f.read()).decode('ascii'))


def main():
    s = open(SRC, encoding='utf-8').read()

    for name in IMAGES:
        path = os.path.join(HERE, name)
        if not os.path.exists(path):
            sys.exit('MISSING ASSET: %s' % name)
        if ("'%s'" % name) not in s:
            sys.exit('asset %s is never referenced in index.html — stale IMAGES list?' % name)
        s = s.replace("'%s'" % name, "'%s'" % data_uri(path))

    have = {slot: f for slot, f in TRACKS.items() if os.path.exists(os.path.join(HERE, f))}
    if 'stage1' not in have:
        sys.exit('MISSING ASSET: music-stage1.mp3 is the fallback for every other slot')
    dropped = sorted(set(TRACKS) - set(have))
    body = ', '.join("%s:'%s'" % (slot, data_uri(transcode(os.path.join(HERE, f))))
                     for slot, f in sorted(have.items()))
    s, n = re.subn(r'const MUSIC=\{[^}]*\};', 'const MUSIC={%s};' % body, s, count=1)
    if n != 1:
        sys.exit('could not find the MUSIC map to rewrite')

    # ---- checks -----------------------------------------------------------
    left = re.findall(r"'[A-Za-z0-9_-]+\.(?:png|jpg|mp3|wav|ogg)'", s)
    if left:
        sys.exit('unresolved asset references left in the build: %s' % sorted(set(left)))

    dupes = [f for f in set(re.findall(r'function ([A-Za-z0-9_]+)\s*\(', s))
             if len(re.findall(r'function %s\s*\(' % f, s)) > 1]
    if dupes:
        sys.exit('function defined more than once (later wins in JS): %s' % sorted(dupes))

    open(OUT, 'w', encoding='utf-8').write(s)

    b = s.index('<script'); b = s.index('>', b) + 1
    js = s[b:s.rindex('</script>')]
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as t:
        t.write(js); tmp = t.name
    try:
        subprocess.run(['node', '--check', tmp], check=True)
    finally:
        os.unlink(tmp)

    print('built %s  (%.2f MB)' % (os.path.basename(OUT), os.path.getsize(OUT) / 1048576))
    print('inlined: %d images, %d tracks' % (len(IMAGES), len(have)))
    if dropped:
        print('slots aliased at runtime (file absent): %s' % ', '.join(dropped))


if __name__ == '__main__':
    main()
