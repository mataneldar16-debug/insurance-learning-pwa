#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
navfix.py — תיקון פס ניווט
Fix all navigation bar bugs in insurance-pwa/index.html

BUGS FOUND & FIXED:
  1. (CRITICAL) #app-main extends to bottom:0 — physically overlaps the nav bar.
     On iOS, -webkit-overflow-scrolling:touch creates a native scroll layer that
     intercepts touches *before* z-index is evaluated. The scroll momentum area
     bleeds into the nav zone and swallows taps meant for the nav buttons.
     FIX: bottom:calc(var(--nav-h) + var(--safe-bottom)) — scroll area stops exactly
          at the top of the nav. Also add explicit z-index:1 to make stacking clear.

  2. (RELATED) #app-main bottom padding double-counted the nav height.
     Old: padding: 16px 13px calc(var(--nav-h) + var(--safe-bottom) + 18px)
     After fix-1 the scroll area no longer extends under the nav, so bottom
     padding only needs visual breathing room.
     FIX: padding: 16px 13px 18px

  3. (RELATED) @media(max-width:480px) had the same nav-height double-count.
     FIX: padding: 12px 10px 12px

  4. (iOS RENDERING) .bottom-nav missing GPU compositing hint.
     Without will-change, iOS can render the nav in the same layer as scrolling
     content, causing flicker/disappearance during fast scroll momentum.
     FIX: will-change:transform on .bottom-nav forces a dedicated compositor layer.

  5. (NICE-TO-HAVE) Nav element had no id="app-nav", making it harder to query.
     FIX: add id="app-nav" to <nav class="bottom-nav">
"""

import sys

FILE = r'C:\Users\Eldar\AppData\Local\Temp\insurance-pwa\index.html'

print('=== navfix.py — תיקון פס ניווט ===\n')

# Read file
with open(FILE, 'r', encoding='utf-8') as f:
    html = f.read()

original_len = len(html)
bugs_fixed = []
bugs_failed = []

# ─────────────────────────────────────────────────────────────────────────────
# FIX 1 (CRITICAL): #app-main bottom:0 → calc(nav-h + safe-bottom)
#   Also: simplify bottom padding (no longer needs nav height)
#   Also: add z-index:1 (explicit stacking, below nav z-index:200)
# ─────────────────────────────────────────────────────────────────────────────
OLD1 = (
    '#app-main{position:fixed;top:var(--header-h);left:0;right:0;bottom:0;'
    'overflow-y:scroll;-webkit-overflow-scrolling:touch;'
    'padding:16px 13px calc(var(--nav-h) + var(--safe-bottom) + 18px)}'
)
NEW1 = (
    '#app-main{position:fixed;top:var(--header-h);left:0;right:0;'
    'bottom:calc(var(--nav-h) + var(--safe-bottom));z-index:1;'
    'overflow-y:scroll;-webkit-overflow-scrolling:touch;'
    'padding:16px 13px 18px}'
)
if OLD1 in html:
    html = html.replace(OLD1, NEW1, 1)
    bugs_fixed.append('FIX 1 ✅ #app-main: bottom:0 → calc(nav+safe), z-index:1 added, padding simplified')
else:
    bugs_failed.append('FIX 1 ❌ #app-main CSS string not found — check for whitespace changes')

# ─────────────────────────────────────────────────────────────────────────────
# FIX 2: @media(max-width:480px) — same nav-height double-count in padding
# ─────────────────────────────────────────────────────────────────────────────
OLD2 = '  #app-main{padding:12px 10px calc(var(--nav-h) + var(--safe-bottom) + 12px)}'
NEW2 = '  #app-main{padding:12px 10px 12px}'
if OLD2 in html:
    html = html.replace(OLD2, NEW2, 1)
    bugs_fixed.append('FIX 2 ✅ @media(480px) #app-main bottom padding simplified')
else:
    bugs_failed.append('FIX 2 ❌ @media #app-main padding string not found')

# ─────────────────────────────────────────────────────────────────────────────
# FIX 3: .bottom-nav — add will-change:transform for GPU compositor layer
#   Prevents iOS from blending nav into the scrolling layer, which causes
#   the nav to flicker or disappear during momentum scroll.
# ─────────────────────────────────────────────────────────────────────────────
OLD3 = (
    '.bottom-nav{position:fixed;bottom:0;left:0;right:0;'
    'height:calc(var(--nav-h) + var(--safe-bottom));'
    'padding-bottom:var(--safe-bottom);background:rgba(7,7,16,.97);'
    'backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);'
    'border-top:1px solid var(--border2);display:flex;align-items:stretch;z-index:200}'
)
NEW3 = (
    '.bottom-nav{position:fixed;bottom:0;left:0;right:0;'
    'height:calc(var(--nav-h) + var(--safe-bottom));'
    'padding-bottom:var(--safe-bottom);background:rgba(7,7,16,.97);'
    'backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);'
    'border-top:1px solid var(--border2);display:flex;align-items:stretch;'
    'z-index:200;will-change:transform}'
)
if OLD3 in html:
    html = html.replace(OLD3, NEW3, 1)
    bugs_fixed.append('FIX 3 ✅ .bottom-nav: will-change:transform added (GPU compositor layer)')
else:
    bugs_failed.append('FIX 3 ❌ .bottom-nav CSS string not found')

# ─────────────────────────────────────────────────────────────────────────────
# FIX 4: Add id="app-nav" to <nav class="bottom-nav">
# ─────────────────────────────────────────────────────────────────────────────
OLD4 = '<nav class="bottom-nav">'
NEW4 = '<nav class="bottom-nav" id="app-nav">'
if OLD4 in html:
    html = html.replace(OLD4, NEW4, 1)
    bugs_fixed.append('FIX 4 ✅ <nav>: id="app-nav" added')
else:
    bugs_failed.append('FIX 4 ❌ <nav class="bottom-nav"> not found')

# ─────────────────────────────────────────────────────────────────────────────
# Write patched file
# ─────────────────────────────────────────────────────────────────────────────
with open(FILE, 'w', encoding='utf-8') as f:
    f.write(html)

# ─────────────────────────────────────────────────────────────────────────────
# Report patch results
# ─────────────────────────────────────────────────────────────────────────────
print('PATCHES APPLIED:')
for msg in bugs_fixed:
    print(f'  {msg}')

if bugs_failed:
    print('\nPATCHES FAILED:')
    for msg in bugs_failed:
        print(f'  {msg}')

# ─────────────────────────────────────────────────────────────────────────────
# Structural verification
# ─────────────────────────────────────────────────────────────────────────────
with open(FILE, 'r', encoding='utf-8') as f:
    result = f.read()

print('\n=== STRUCTURAL VERIFICATION ===')
checks = [
    ('id="app-nav"',                                    'nav has id="app-nav"'),
    ('nav-btn',                                         '.nav-btn elements exist'),
    ('data-action="tab"',                               'nav buttons have data-action="tab"'),
    ('showTab',                                         'showTab() function exists'),
    ('safe-area-inset-bottom',                          'safe-area-inset-bottom handled'),
    ('bottom:calc(var(--nav-h) + var(--safe-bottom))',  '#app-main bottom fixed (no overlap)'),
    ('z-index:1',                                       '#app-main has explicit z-index:1'),
    ('z-index:200',                                     'nav has z-index:200'),
    ('will-change:transform',                           'nav GPU compositing (will-change)'),
    ('padding:16px 13px 18px',                          '#app-main bottom padding simplified'),
    ('padding:12px 10px 12px',                          '@media padding simplified'),
    ('data-action="tab" data-param="home"',             'home nav button'),
    ('data-action="tab" data-param="learn"',            'learn nav button'),
    ('data-action="tab" data-param="quiz"',             'quiz nav button'),
    ('data-action="tab" data-param="sim"',              'sim nav button'),
    ('data-action="tab" data-param="perf"',             'perf nav button'),
]

all_ok = True
for check, label in checks:
    found = check in result
    status = '✅' if found else '❌'
    print(f'  {status} {label}')
    if not found:
        all_ok = False

# Sanity: file size shouldn't change drastically
size_diff = len(result) - original_len
print(f'\n  📄 File size delta: {size_diff:+d} bytes ({original_len} → {len(result)})')

print()
if bugs_failed:
    print('⚠️  Some patches could not be applied. The file may have been modified already.')
    print('   Check the FAILED items above and apply manually.')
    sys.exit(1)
elif all_ok:
    print('✅ ALL CHECKS PASSED — פס הניווט תוקן בהצלחה!')
else:
    print('❌ SOME CHECKS FAILED — review output above')
    sys.exit(1)
