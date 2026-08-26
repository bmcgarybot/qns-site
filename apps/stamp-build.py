#!/usr/bin/env python3
"""Stamp every board with the moment it was built.

  python3 stamp-build.py

Run this immediately before committing. Without it there is no way to tell a
current build from a cached one: both look identical on screen, which is how a
stale staging page cost us a review round.

The stamp is a UTC timestamp rather than a commit sha, because the sha of the
commit you are about to make does not exist yet and stamping the previous one
is worse than useless.
"""
import re, os, glob
from datetime import datetime, timezone

os.chdir(os.path.dirname(os.path.abspath(__file__)))
stamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

pages = sorted(glob.glob('my-buddy-demo*.html') + glob.glob('my-buddy-test*.html'))
for p in pages:
    t = open(p, encoding='utf-8').read()
    if 'const BUILD=' not in t:
        print('  %-26s no BUILD marker, skipped' % p)
        continue
    t = re.sub(r'const BUILD="[^"]*"', 'const BUILD="%s"' % stamp, t, count=1)
    open(p, 'w', encoding='utf-8').write(t)
    print('  %-26s %s' % (p, stamp))

print('\nStamped %d page(s). Now bump VERSION in sw.js and commit.' % len(pages))
