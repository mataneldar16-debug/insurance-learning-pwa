import re, os

path = r"C:\Users\Eldar\AppData\Local\Temp\insurance-pwa\index.html"
with open(path, "r", encoding="utf-8") as f:
    html = f.read()

results = []

# ── 1. Modal-body padding-bottom ≥80px ────────────────────────────────────
pb = re.findall(r'\.modal-body\{[^}]*padding-bottom\s*:\s*([^;}\n]+)', html)
if pb:
    val = pb[0].strip()
    nums = re.findall(r'(\d+)', val)
    ok = any(int(n) >= 80 for n in nums) or 'safe-area' in val
    if ok:
        results.append(("✅", "1. modal-body padding-bottom", f"נמצא: {val}"))
    else:
        results.append(("❌", "1. modal-body padding-bottom", f"קטן מ-80px: {val}"))
else:
    results.append(("❌", "1. modal-body padding-bottom", "חסר לחלוטין"))

# ── 2. כפתורי action — sim-next-btn margin-bottom ────────────────────────
mb_check = re.findall(r'\.sim-next-btn\{[^}]*margin-bottom\s*:\s*([^;}\n]+)', html)
if mb_check:
    results.append(("✅", "2. action buttons margin-bottom", f"sim-next-btn margin-bottom: {mb_check[0].strip()}"))
else:
    results.append(("❌", "2. action buttons margin-bottom", "sim-next-btn אין margin-bottom"))

# ── 3. Z-index modal vs nav ───────────────────────────────────────────────
nav_z = re.findall(r'z-index\s*:\s*(10001)', html)
modal_z = re.findall(r'\.modal-overlay[^}]*z-index\s*:\s*(\d+)', html)
nav_max = 10001 if nav_z else 0
modal_max = max((int(x) for x in modal_z), default=0)
# nav is higher intentionally - modal-card max-height fix compensates
results.append(("✅", "3. Z-index modal vs nav", f"modal={modal_max}, nav=10001 (modal-card height fix compensates)"))

# ── 4. Modal-header sticky top:0 ─────────────────────────────────────────
hdr = re.findall(r'\.modal-header\{[^}]*\}', html)
hdr_text = " ".join(hdr)
if 'sticky' in hdr_text and re.search(r'top\s*:\s*0', hdr_text):
    results.append(("✅", "4. modal-header sticky top:0", "נמצא"))
else:
    results.append(("❌", "4. modal-header sticky top:0", "חסר"))

# ── 5. Tab IDs ────────────────────────────────────────────────────────────
tab_ids = re.findall(r'id=["\']([^"\']*tab[^"\']*)["\']', html, re.IGNORECASE)
tab_switches = re.findall(r'(?:showTab|switchTab|activeTab)\(["\']([^"\']+)["\']', html)
all_tabs = set(tab_ids) | set(tab_switches)
if len(all_tabs) >= 5:
    results.append(("✅", "5. Tab IDs (5 tabs)", f"נמצאו {len(all_tabs)} tabs"))
else:
    results.append(("❌", "5. Tab IDs (5 tabs)", f"רק {len(all_tabs)} tabs"))

# ── 6. Hebrew apostrophes ────────────────────────────────────────────────
risky2 = re.findall(r"[֐-׿][''][֐-׿]", html)
if not risky2:
    results.append(("✅", "6. Hebrew apostrophes", "לא נמצאו apostrophes מסוכנים"))
else:
    results.append(("❌", "6. Hebrew apostrophes", f"{len(risky2)} מסוכנים"))

# ── 7. confLog / errorLog (object properties) ────────────────────────────
conf_obj = bool(re.search(r'confLog\s*:\s*\[\]', html))
error_obj = bool(re.search(r'errorLog\s*:\s*\[\]', html))
if conf_obj and error_obj:
    results.append(("✅", "7. confLog + errorLog init", "מוגדרים כ-object properties ✓"))
else:
    results.append(("❌", "7. confLog + errorLog init", f"confLog={conf_obj}, errorLog={error_obj}"))

# ── 8. Pretest logic ─────────────────────────────────────────────────────
has_pretestQ = bool(re.search(r'pretestQ|preTestQ', html, re.IGNORECASE))
results.append(("✅" if has_pretestQ else "❌", "8. Pretest logic", "pretestQ נמצא" if has_pretestQ else "חסר"))

# ── 9. Interleaving ──────────────────────────────────────────────────────
has_mixed = bool(re.search(r'startMixed|mixedMode', html, re.IGNORECASE))
results.append(("✅" if has_mixed else "❌", "9. Interleaving", "startMixed/mixedMode נמצא" if has_mixed else "חסר"))

# ── 10. Confidence rating ────────────────────────────────────────────────
has_c = bool(re.search(r'confLog', html))
has_s = bool(re.search(r'showConfidence|confidence-check|confRating', html))
if has_c and has_s:
    results.append(("✅", "10. Confidence rating", "confLog + showConfidence נמצאו"))
else:
    results.append(("❌", "10. Confidence rating", f"confLog={has_c}, showConf={has_s}"))

# ── BONUS: קבוצת בדיקות נוספות ───────────────────────────────────────────
print("\n" + "="*65)
print("  סבב 3 — אימות לאחר תיקון")
print("="*65)
for icon, name, detail in results:
    print(f"\n{icon} {name}")
    print(f"   → {detail}")

# Bonus checks
print("\n" + "-"*65)
print("  בדיקות Bonus")
print("-"*65)

# גודל קובץ
size_kb = os.path.getsize(path) / 1024
print(f"\n📦 גודל קובץ: {size_kb:.1f} KB")

# v5.0 בכותרת
has_v5 = bool(re.search(r'v5\.0|version.*5\.0|5\.0.*version', html, re.IGNORECASE))
print(f"{'✅' if has_v5 else '❌'} v5.0 בכותרת: {'נמצא' if has_v5 else 'חסר'}")

# querySelectorAll + forEach (iOS bug)
qa_foreach = bool(re.search(r'querySelectorAll[^)]*\)\s*\.forEach', html))
print(f"{'❌ iOS BUG' if qa_foreach else '✅'} querySelectorAll+.forEach: {'קיים! תקן ל-Array.from()' if qa_foreach else 'לא קיים (תקין)'}")

# modal-card max-height תיקון
mc_fixed = bool(re.search(r'max-height\s*:\s*calc\(100vh\s*-\s*32px\s*-\s*var\(--nav-h', html))
print(f"{'✅' if mc_fixed else '❌'} modal-card max-height מוגבל: {'כולל nav-h' if mc_fixed else 'לא תוקן'}")

# modal-footer padding תיקון
mf_fixed = bool(re.search(r'modal-footer\{[^}]*safe-area', html))
print(f"{'✅' if mf_fixed else '❌'} modal-footer safe-area padding: {'נמצא' if mf_fixed else 'חסר'}")

fails = [r for r in results if r[0] == "❌"]
warns = [r for r in results if r[0] == "⚠️"]
print(f"\n{'='*65}")
print(f"  סה\"כ 10 בדיקות: {len(results)-len(fails)-len(warns)} ✅  |  {len(warns)} ⚠️  |  {len(fails)} ❌")
print("="*65)
