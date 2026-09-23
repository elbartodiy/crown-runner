#!/usr/bin/env python3
"""Apply an ordered list of exact-match replacements to index.html.

Every edit must match exactly once. A patch that matches twice is ambiguous and a patch that
matches nothing has already been applied or was written against the wrong text — both are
mistakes worth stopping for rather than silently doing nothing.
"""
import io, os, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC  = os.path.join(HERE, 'index.html')

def apply(edits, path=SRC):
    s = io.open(path, encoding='utf-8').read()
    for i, (old, new) in enumerate(edits, 1):
        n = s.count(old)
        if n != 1:
            head = old.strip().splitlines()[0][:90]
            sys.exit('edit %d matched %d times (want 1): %s' % (i, n, head))
        s = s.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8').write(s)
    print('applied %d edits  -> %s (%.0f KB)' % (len(edits), os.path.basename(path),
                                                 os.path.getsize(path)/1024))
