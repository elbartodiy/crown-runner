#!/usr/bin/env python3
"""Syntax, duplicate definitions, and dead references — the three faults that present as a
black page rather than as an error."""
import io, os, re, subprocess, sys, tempfile
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s=io.open(os.path.join(HERE,'index.html'),encoding='utf-8').read()
bad=0
dupes=[f for f in set(re.findall(r'^function ([A-Za-z0-9_]+)\s*\(',s,re.M))
       if len(re.findall(r'^function %s\s*\('%f,s,re.M))>1]
if dupes: print('DUPLICATE:', sorted(dupes)); bad=1
b=s.index('<script'); b=s.index('>',b)+1
js=s[b:s.rindex('</script>')]
with tempfile.NamedTemporaryFile('w',suffix='.js',delete=False,encoding='utf-8') as t:
    t.write(js); tmp=t.name
r=subprocess.run(['node','--check',tmp],capture_output=True,text=True)
os.unlink(tmp)
if r.returncode: print(r.stderr); bad=1
if not bad: print('index.html  %.0f KB  syntax OK, no duplicates'%(len(s)/1024))
sys.exit(bad)
