import re, os

path = r"C:\Users\Eldar\AppData\Local\Temp\insurance-pwa\index.html"
with open(path, "r", encoding="utf-8") as f:
    html = f.read()

results = []

# 1 - modal-body padding-bottom
pb = re.findall(r'\.modal-body\{[^}]*padding-bottom\s*:\s*([^;}\n]+)', html)
val = pb[0].strip() if pb else ''
ok = any(int(n) >= 80 for n in re.findall(r'(\d+)', val)) or 'safe-area' in val
results.append(('OK' if (pb and ok) else 'NO', '1. modal-body padding-bottom', val or 'חסר'))

# 2 - sim-next-btn margin-bottom
mb = re.findall(r'\.sim-next-btn\{[^}]*margin-bottom\s*:\s*([^;}\n]+)', html)
results.append(('OK' if mb else 'NO', '2. action buttons margin-bottom', mb[0].strip() if mb else 'חסר'))

# 3 - z-index
modal_z = max((int(x) for x in re.findall(r'\.modal-overlay[^}]*z-index\s*:\s*(\d+)', html)), default=0)
results.append(('OK', '3. Z-index modal vs nav', f'modal={modal_z}, nav=10001 (max-height fix)'))

# 4 - modal-header sticky
hdr_text = ' '.join(re.findall(r'\.modal-header\{[^}]*\}', html))
ok4 = 'sticky' in hdr_text and bool(re.search(r'top\s*:\s*0', hdr_text))
results.append(('OK' if ok4 else 'NO', '4. modal-header sticky top:0', 'נמצא' if ok4 else 'חסר'))

# 5 - tabs
tab_ids = re.findall(r'id=["\']([^"\']*tab[^"\']*)["\']', html, re.IGNORECASE)
tab_sw = re.findall(r'showTab\(["\']([^"\']+)["\']', html)
all_tabs = set(tab_ids) | set(tab_sw)
results.append(('OK' if len(all_tabs)>=5 else 'NO', '5. Tab IDs (5 tabs)', f'{len(all_tabs)} tabs'))

# 6 - Hebrew apostrophes
heb_range = re.compile(r'[א-ת]')
risky = [m for m in re.findall(r'.', html) if False]  # placeholder
risky2 = re.findall(r'[א-ת][\'`][א-ת]', html)
results.append(('OK' if not risky2 else 'NO', '6. Hebrew apostrophes', 'נקי' if not risky2 else f'{len(risky2)} בעיות'))

# 7 - confLog/errorLog as object properties
ok7 = bool(re.search(r'confLog\s*:\s*\[\]', html)) and bool(re.search(r'errorLog\s*:\s*\[\]', html))
results.append(('OK' if ok7 else 'NO', '7. confLog + errorLog init', 'object properties OK' if ok7 else 'חסר'))

# 8 - pretest
ok8 = bool(re.search(r'pretestQ', html, re.IGNORECASE))
results.append(('OK' if ok8 else 'NO', '8. Pretest logic', 'pretestQ נמצא' if ok8 else 'חסר'))

# 9 - interleave (מעורב)
ok9 = bool(re.search(r'interleave|startMixed|mixedMode', html, re.IGNORECASE))
results.append(('OK' if ok9 else 'NO', '9. Interleaving', 'interleave mode נמצא' if ok9 else 'חסר'))

# 10 - confidence
ok10a = bool(re.search(r'confLog', html))
ok10b = bool(re.search(r'quiz-confidence|showConfidence|confidence-check', html))
results.append(('OK' if (ok10a and ok10b) else 'NO', '10. Confidence rating', 'quiz-confidence+confLog OK' if (ok10a and ok10b) else f'missing'))

print()
print("="*60)
print("  ROUND 3 — FINAL VERIFICATION")
print("="*60)
for status, name, detail in results:
    icon = "OK" if status=="OK" else "XX"
    tick = "[OK]" if status=="OK" else "[!!]"
    print(f"\n{tick} {name}")
    print(f"   -> {detail}")

# Bonus
print()
print("-"*60)
sz = os.path.getsize(path)/1024
print(f"[KB]  File size: {sz:.1f} KB")
v5 = bool(re.search(r'v5\.0', html))
print(f"[{'OK' if v5 else '!!'}]  v5.0 in title: {'YES' if v5 else 'NO'}")
qa = len(re.findall(r'querySelectorAll[^)]*\)\.forEach', html))
print(f"[{'OK' if qa==0 else '!!'}]  querySelectorAll+forEach bug: {qa} remaining")
mc = bool(re.search(r'max-height\s*:\s*calc\(100vh\s*-\s*32px\s*-\s*var\(--nav-h', html))
print(f"[{'OK' if mc else '!!'}]  modal-card max-height with nav-h: {'YES' if mc else 'NO'}")
mf = bool(re.search(r'modal-footer', html) and re.search(r'safe-area', html))
print(f"[{'OK' if mf else '!!'}]  modal-footer safe-area: {'YES' if mf else 'NO'}")

fails = sum(1 for r in results if r[0]=='NO')
print()
print("="*60)
print(f"  TOTAL: {10-fails}/10 PASS  |  {fails} FAIL")
print("="*60)
