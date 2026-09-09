#!/usr/bin/env python3
"""Regenerate sw.js from everything any installable board references.

Run this after ANY change to the board, then bump VERSION in the output by
passing --version N. If the precache list goes stale, a child ends up offline
with missing symbols, which is worse than being online with all of them.

  python3 build-sw.py --version 28
"""
import re, os, sys, json

ver = sys.argv[sys.argv.index('--version') + 1] if '--version' in sys.argv else '1'
here = os.path.dirname(os.path.abspath(__file__))
os.chdir(here)
pages = ['my-buddy-demo.html', 'my-buddy-demo-es.html',
         'my-buddy-test.html', 'my-buddy-test-es.html']
source = '\n'.join(open(page, encoding='utf-8').read() for page in pages)
paths = set(re.findall(r"symbols/[A-Za-z0-9_,.\-/]+\.svg", source))
fallbacks = {'symbols/mybuddy/%s.svg' % m for m in re.findall(r'svgName:"([^"]+)"', source)}
paths |= {p for p in fallbacks if os.path.exists(p)}

missing = sorted(p for p in paths if not os.path.exists(p))
if missing:
    print('WARNING: %d referenced symbols do not exist and cannot be cached:' % len(missing))
    for m in missing[:10]:
        print('   ' + m)

shell = ['./' + page for page in pages]
shell += ['./my-buddy.webmanifest', './my-buddy-es.webmanifest',
          './my-buddy-test.webmanifest', './my-buddy-test-es.webmanifest',
          './my-buddy-privacy.html', './my-buddy-terms.html',
          './my-buddy-licenses.html', './icons/mybuddy-192.png',
          './icons/mybuddy-512.png', './icons/mybuddy-180.png']
assets = shell + ['./' + p for p in sorted(p for p in paths if os.path.exists(p))]

sw = open('sw.js', encoding='utf-8').read()
sw = re.sub(r"const VERSION = 'mybuddy-v[^']*';",
            "const VERSION = 'mybuddy-v%s';" % ver, sw, count=1)
sw = re.sub(r"const ASSETS = \[.*?\];",
            'const ASSETS = %s;' % json.dumps(assets, indent=0).replace('\n', ''),
            sw, count=1, flags=re.S)
open('sw.js', 'w', encoding='utf-8').write(sw)

size = sum(os.path.getsize(a[2:]) for a in assets if os.path.exists(a[2:]))
print('sw.js: version %s, %d assets, %.2f MB' % (ver, len(assets), size / 1048576))
