#!/usr/bin/env python3
"""Check that staging is a trustworthy gate for the live boards.

  python3 check-staging.py

Staging only means something if two things hold:

  1. Staging never links to a live page. When the English staging board linked
     to the live Spanish demo, tapping Espanol silently left staging, so the
     Spanish board was never actually tested before it shipped.

  2. Staging and live differ only in ways we intend. If they differ anywhere
     else, approving staging tells you nothing about what will go live.

  3. Installable staging is cached with its own shell so it can be tested in
     airplane mode without silently falling back to the live board.

Exits non-zero on any failure.
"""
import re, sys, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

PAIRS = [('my-buddy-test.html', 'my-buddy-demo.html'),
         ('my-buddy-test-es.html', 'my-buddy-demo-es.html')]
fails = []


def links(path):
    t = open(path, encoding='utf-8').read()
    m = re.search(r'<div id="langPick">.*?</div>', t, re.S)
    return re.findall(r'href="([^"]+)"', m.group(0)) if m else []


def normalise(t, stg_names, live_names):
    """Collapse the differences that are supposed to exist."""
    for s, l in zip(stg_names, live_names):
        t = t.replace(s, '@PAGE@').replace(l, '@PAGE@')
    # Staging must remain visibly distinct when opened or installed as a PWA.
    t = t.replace('My Buddy Español TEST', 'My Buddy')
    t = t.replace('My Buddy TEST', 'My Buddy')
    t = t.replace('<meta name="robots" content="noindex,nofollow">\n', '')
    t = re.sub(r'href="my-buddy(-test)?(-es)?\.webmanifest"', 'href="@MANIFEST@"', t)
    return t


print('1. staging never links to live')
for stg, live in PAIRS:
    out = [h for h in links(stg) if 'demo' in h]
    ok = not out
    print('   %-24s %s' % (stg, 'ok' if ok else 'LEAKS TO ' + ', '.join(out)))
    if not ok:
        fails.append('%s links to live: %s' % (stg, out))

AHEAD_OK = os.path.exists('.staging-ahead')
print('\n2. staging matches live apart from the intended differences')
if AHEAD_OK:
    print('   .staging-ahead present: staging is expected to be ahead of live,')
    print('   so divergence is reported but not treated as a failure. Delete')
    print('   that file once staging has been promoted.')
stg_names = ['my-buddy-test-es.html', 'my-buddy-test.html']
live_names = ['my-buddy-demo-es.html', 'my-buddy-demo.html']
for stg, live in PAIRS:
    if not (os.path.exists(stg) and os.path.exists(live)):
        fails.append('missing %s or %s' % (stg, live))
        continue
    a = normalise(open(stg, encoding='utf-8').read(), stg_names, live_names)
    b = normalise(open(live, encoding='utf-8').read(), stg_names, live_names)
    import difflib
    d = [l for l in difflib.unified_diff(a.split('\n'), b.split('\n'), lineterm='', n=0)
         if l.startswith(('+', '-')) and not l.startswith(('---', '+++'))]
    print('   %-24s %s' % (stg, 'identical to live' if not d else '%d DIFFERING LINES' % len(d)))
    for l in d[:6]:
        print('      ' + l[:110])
    if d and not AHEAD_OK:
        fails.append('%s and %s have diverged (%d lines)' % (stg, live, len(d)))

print('\n3. installable staging works offline as staging')
sw = open('sw.js', encoding='utf-8').read()
import json
assets = json.loads(re.search(r"const ASSETS = (\[.*?\]);", sw, re.S).group(1))
cached = [a for a in assets if 'my-buddy-test' in a]
expected = {'./my-buddy-test.html', './my-buddy-test-es.html',
            './my-buddy-test.webmanifest', './my-buddy-test-es.webmanifest'}
missing = sorted(expected.difference(assets))
print('   staging entries in precache: %d' % len(cached))
print('   staging shell complete: %s' % ('yes' if not missing else 'NO'))
if missing:
    fails.append('service worker misses staging shell: %s' % missing)
if "req.url.indexOf('my-buddy-test')" in sw:
    fails.append('service worker still bypasses staging cache')
fallback = "'./my-buddy-test.html'" in sw and "'./my-buddy-test-es.html'" in sw
print('   staging navigation fallback: %s' % ('yes' if fallback else 'NO'))
if not fallback:
    fails.append('service worker has no staging navigation fallback')

print()
if fails:
    print('FAILED')
    for f in fails:
        print('  - ' + f)
    sys.exit(1)
print('STAGING IS A VALID GATE')
