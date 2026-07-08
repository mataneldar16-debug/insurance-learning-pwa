import re, sys

path = r'C:\Users\Eldar\AppData\Local\Temp\insurance-pwa\index.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

original = html
changes = []

# ── Fix 1: pointer-events:none on .levelup-overlay ─────────────────────────
# This is the critical fix: overlay is position:fixed;inset:0 during 2.5s animation.
# Even though nav is z-index:10001 > 10000, iOS can route touch events to the overlay.
old1 = '.levelup-overlay{position:fixed;inset:0;background:rgba(0,0,0,.7);display:flex;align-items:center;justify-content:center;z-index:10000;animation:fadeInOut 2.5s ease forwards}'
new1 = '.levelup-overlay{position:fixed;inset:0;background:rgba(0,0,0,.7);display:flex;align-items:center;justify-content:center;z-index:10000;animation:fadeInOut 2.5s ease forwards;pointer-events:none}'
if old1 in html:
    html = html.replace(old1, new1)
    changes.append('✅ Fix 1: pointer-events:none added to .levelup-overlay')
else:
    changes.append('⚠️  Fix 1 SKIPPED — .levelup-overlay string not matched exactly (may already patched)')

# ── Fix 2: explicit z-index:1 on .card-3d ──────────────────────────────────
old2 = '.card-3d{position:relative;width:100%;transform-style:preserve-3d;transition:transform .6s cubic-bezier(.4,0,.2,1)}'
new2 = '.card-3d{position:relative;z-index:1;width:100%;transform-style:preserve-3d;transition:transform .6s cubic-bezier(.4,0,.2,1)}'
if old2 in html:
    html = html.replace(old2, new2)
    changes.append('✅ Fix 2: z-index:1 added to .card-3d')
else:
    changes.append('⚠️  Fix 2 SKIPPED — .card-3d string not matched exactly')

# ── Fix 3: click-to-close backdrop on modal-overlay ────────────────────────
old3 = '<div class="modal-overlay" id="modal" style="display:none">'
new3 = '<div class="modal-overlay" id="modal" style="display:none" onclick="if(event.target===this)closeModal()">'
if old3 in html:
    html = html.replace(old3, new3)
    changes.append('✅ Fix 3: onclick close-on-backdrop added to #modal overlay')
else:
    changes.append('⚠️  Fix 3 SKIPPED — modal-overlay HTML not matched exactly')

# Save
if html != original:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print('\n'.join(changes))
    print(f'\nFile saved ({len(html)} bytes)')
else:
    print('NO CHANGES MADE — nothing matched')
    sys.exit(1)
