import re
import sys

path = r"C:\Users\Eldar\AppData\Local\Temp\insurance-pwa\index.html"
with open(path, "r", encoding="utf-8") as f:
    html = f.read()

results = []

# ── 1. Modal padding-bottom ────────────────────────────────────────────────
pb_matches = re.findall(r'\.modal-body\s*\{[^}]*padding-bottom\s*:\s*([^;}\n]+)', html)
if pb_matches:
    val = pb_matches[0].strip()
    # check if value contains calc or px value >=80
    nums = re.findall(r'(\d+)', val)
    big_enough = any(int(n) >= 80 for n in nums) or 'safe-area' in val
    if big_enough:
        results.append(("✅", "1. modal-body padding-bottom", f"נמצא: {val}"))
    else:
        results.append(("❌", "1. modal-body padding-bottom", f"קטן מ-80px: '{val}'"))
else:
    results.append(("❌", "1. modal-body padding-bottom", "אין padding-bottom ב-.modal-body כלל"))

# ── 2. כפתורי action בתחתית מודל ────────────────────────────────────────
action_funcs = re.findall(r'(?:renderLesson|showLessonModal|openLesson|showModal|buildLesson)[^}]{0,3000}', html, re.DOTALL)
action_text = " ".join(action_funcs)
# look for buttons near end of modal content
btn_patterns = re.findall(r'(btn[^"\'<>]{0,60}(?:המשך|סיום|בוצע|continue|finish|done)[^"\'<>]{0,60})', action_text, re.IGNORECASE)
if not btn_patterns:
    btn_patterns = re.findall(r'(?:המשך|סיום שיעור|בוצע)[^<]{0,200}', html[:len(html)])
mb_found = bool(re.search(r'margin-bottom\s*:\s*1[6-9]px|margin-bottom\s*:\s*[2-9]\d', action_text))
if btn_patterns and mb_found:
    results.append(("✅", "2. action buttons margin-bottom", f"כפתורים נמצאו עם margin-bottom"))
elif btn_patterns:
    results.append(("❌", "2. action buttons margin-bottom", f"נמצאו {len(btn_patterns)} כפתורי action ללא margin-bottom מתאים"))
else:
    results.append(("⚠️", "2. action buttons margin-bottom", "לא זוהו כפתורי action בתוך פונקציות מודל — בדוק ידנית"))

# ── 3. Z-index: modal vs nav ─────────────────────────────────────────────
nav_z = re.findall(r'\.nav(?:bar|-bar|bottom|-bottom|[- ]tabs?)?[^}]*z-index\s*:\s*(\d+)', html)
modal_z = re.findall(r'\.modal(?:-overlay|-backdrop|-wrapper|-container)?[^}]*z-index\s*:\s*(\d+)', html)
nav_max = max((int(x) for x in nav_z), default=0)
modal_max = max((int(x) for x in modal_z), default=0)
if modal_max >= 500 and (nav_max == 0 or modal_max > nav_max):
    results.append(("✅", "3. Z-index modal vs nav", f"modal z-index={modal_max}, nav z-index={nav_max}"))
elif modal_max == 0:
    results.append(("❌", "3. Z-index modal vs nav", f"לא נמצא z-index למודל! nav={nav_max}"))
else:
    results.append(("❌", "3. Z-index modal vs nav", f"modal z-index={modal_max} < nav z-index={nav_max}"))

# ── 4. Modal header sticky ───────────────────────────────────────────────
header_block = re.findall(r'\.modal-header\s*\{[^}]*\}', html)
header_text = " ".join(header_block)
has_sticky = 'sticky' in header_text or 'fixed' in header_text
has_top0 = re.search(r'top\s*:\s*0', header_text)
if has_sticky and has_top0:
    results.append(("✅", "4. modal-header sticky top:0", "נמצא position:sticky + top:0"))
elif has_sticky:
    results.append(("❌", "4. modal-header sticky", "position:sticky אך אין top:0"))
else:
    results.append(("❌", "4. modal-header sticky", f"אין position:sticky ב-.modal-header"))

# ── 5. Tab IDs (5 tabs) ──────────────────────────────────────────────────
tab_ids = re.findall(r'id=["\']([^"\']*tab[^"\']*)["\']', html, re.IGNORECASE)
# also look for data-tab or tab switching logic
tab_switches = re.findall(r'(?:showTab|switchTab|activeTab)\(["\']([^"\']+)["\']', html)
all_tabs = set(tab_ids) | set(tab_switches)
if len(all_tabs) >= 5:
    results.append(("✅", "5. Tab IDs (5 tabs)", f"נמצאו {len(all_tabs)} tabs: {list(all_tabs)[:5]}"))
else:
    results.append(("❌", "5. Tab IDs (5 tabs)", f"נמצאו רק {len(all_tabs)} tabs: {list(all_tabs)}"))

# ── 6. Hebrew apostrophes (JS syntax) ───────────────────────────────────
heb_apos = re.findall(r"(?<![\\])(['\"])([^'\"]*[֐-׿][^'\"]*\')['\"]", html)
# more targeted: look for JS strings with Hebrew that contain unescaped apostrophe
js_strings = re.findall(r"['\"]([^'\"]{0,80}[֐-׿][^'\"]{0,80})['\"]", html)
danger = [s for s in js_strings if "'" in s and not s.startswith('"')]
# Actually look for JS lines where Hebrew word has apostrophe mid-string
risky = re.findall(r"(?:var |let |const |=\s*)[\"']([^\"']{0,60}ש['׳][^\"']{0,60})[\"']", html)
if not risky:
    # also check for things like ל'יזום or similar
    risky2 = re.findall(r"[֐-׿][''][֐-׿]", html)
    if risky2:
        results.append(("❌", "6. Hebrew apostrophes", f"נמצאו {len(risky2)} apostrophes בין אותיות עבריות — סיכון syntax"))
    else:
        results.append(("✅", "6. Hebrew apostrophes", "לא נמצאו apostrophes מסוכנים בעברית"))
else:
    results.append(("❌", "6. Hebrew apostrophes", f"נמצאו {len(risky)} מחרוזות JS עם Hebrew apostrophe"))

# ── 7. confLog / errorLog init ──────────────────────────────────────────
has_confLog = bool(re.search(r'(?:let|var|const)\s+confLog\s*=', html))
has_errorLog = bool(re.search(r'(?:let|var|const)\s+errorLog\s*=', html))
if has_confLog and has_errorLog:
    results.append(("✅", "7. confLog + errorLog init", "שניהם מוגדרים"))
elif has_confLog:
    results.append(("❌", "7. confLog + errorLog init", "confLog ✅ אך errorLog ❌"))
elif has_errorLog:
    results.append(("❌", "7. confLog + errorLog init", "errorLog ✅ אך confLog ❌"))
else:
    results.append(("❌", "7. confLog + errorLog init", "שניהם חסרים"))

# ── 8. Pretest logic ────────────────────────────────────────────────────
has_pretestQ = bool(re.search(r'pretestQ|pretest_q|pretestQuestions?|preTestQ', html, re.IGNORECASE))
has_pretest_fn = bool(re.search(r'function\s+(?:runPretest|startPretest|showPretest)', html, re.IGNORECASE))
if has_pretestQ:
    results.append(("✅", "8. Pretest logic", f"pretestQ נמצא" + (" + פונקציה" if has_pretest_fn else "")))
else:
    results.append(("❌", "8. Pretest logic", "pretestQ לא נמצא בקוד"))

# ── 9. Interleaving (startMixed / mixedMode) ───────────────────────────
has_mixed = bool(re.search(r'startMixed|mixedMode|mixed_mode|interleav', html, re.IGNORECASE))
if has_mixed:
    results.append(("✅", "9. Interleaving", "startMixed / mixedMode נמצא"))
else:
    results.append(("❌", "9. Interleaving", "לא נמצא startMixed/mixedMode"))

# ── 10. Confidence rating ───────────────────────────────────────────────
has_confLog2 = bool(re.search(r'confLog|confidence.log', html, re.IGNORECASE))
has_showConf = bool(re.search(r'showConfidence|confidence.check|confidence-check|confRating|confScore', html, re.IGNORECASE))
if has_confLog2 and has_showConf:
    results.append(("✅", "10. Confidence rating", "confLog + showConfidence נמצאו"))
elif has_confLog2:
    results.append(("⚠️", "10. Confidence rating", "confLog נמצא אך showConfidence/confidence-check חסר"))
elif has_showConf:
    results.append(("⚠️", "10. Confidence rating", "showConfidence נמצא אך confLog חסר"))
else:
    results.append(("❌", "10. Confidence rating", "לא נמצא confLog ולא showConfidence"))

# ── הדפסת תוצאות ───────────────────────────────────────────────────────
print("\n" + "="*60)
print("  סבב 1 — תוצאות סריקה סטטית")
print("="*60)
for icon, name, detail in results:
    print(f"\n{icon} {name}")
    print(f"   → {detail}")

fails = [r for r in results if r[0] == "❌"]
warns = [r for r in results if r[0] == "⚠️"]
print(f"\n{'='*60}")
print(f"  סה\"כ: {len(results)-len(fails)-len(warns)} ✅  |  {len(warns)} ⚠️  |  {len(fails)} ❌")
print("="*60)
