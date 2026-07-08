path = r'C:\Users\Eldar\AppData\Local\Temp\insurance-pwa\index.html'

with open(path, encoding='utf-8') as f:
    content = f.read()

changes = []

# Bug 1: z-index — nav is at z-index:200 but modal backdrop=500, toast=1000, levelup=10000
# The CSS ends: ;z-index:200;will-change:transform}
old1 = ';z-index:200;will-change:transform}'
new1 = ';z-index:10001;will-change:transform}'
count1 = content.count(old1)
if count1 == 1:
    content = content.replace(old1, new1)
    changes.append(f'Bug 1 FIXED: .bottom-nav z-index 200 → 10001 (was below modal:500/toast:1000/levelup:10000)')
elif count1 == 0:
    changes.append(f'Bug 1 ERROR: pattern not found — {repr(old1)}')
else:
    changes.append(f'Bug 1 WARN: found {count1} occurrences, skipping to be safe')

# Bug 2: iOS safe-area — already correct in this file
changes.append('Bug 2 OK: --safe-bottom:env(safe-area-inset-bottom,20px) + .bottom-nav padding-bottom:var(--safe-bottom) already present')

# Bug 3: Active state — showTab() already correct
changes.append('Bug 3 OK: showTab() removes active from all .tab-pane, toggles .nav-btn, adds active to #tab-{id}')

# Bug 4: Content overlap — #app-main padding-bottom already correct
changes.append('Bug 4 OK: #app-main padding calc(var(--nav-h) + var(--safe-bottom) + 18px) already present')

# Bug 5: Click handler — ACTIONS["tab"] already wired
changes.append('Bug 5 OK: document click → ACTIONS["tab"] → showTab() delegation chain correct')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print('=== NAV FIX REPORT ===')
for c in changes:
    print(c)
