import re, shutil, os

path = r"C:\Users\Eldar\AppData\Local\Temp\insurance-pwa\index.html"
backup = path + ".bak_round2"

# גיבוי
shutil.copy2(path, backup)
print(f"✅ גיבוי נוצר: {backup}")

with open(path, "r", encoding="utf-8") as f:
    html = f.read()

original_len = len(html)
changes = []

# ══════════════════════════════════════════════════════════════════
# תיקון 1 — modal-card max-height: אל יכנס מתחת לנאב בר
# ══════════════════════════════════════════════════════════════════
old1 = ".modal-card{background:var(--surface);border:1px solid var(--border2);border-radius:var(--r-lg);width:100%;max-width:640px;max-height:calc(100vh - 32px);overflow:hidden;display:flex;flex-direction:column;animation:slideUp .28s cubic-bezier(.16,1,.3,1);box-sizing:border-box}"
new1 = ".modal-card{background:var(--surface);border:1px solid var(--border2);border-radius:var(--r-lg);width:100%;max-width:640px;max-height:calc(100vh - 32px - var(--nav-h,60px) - env(safe-area-inset-bottom,0px));overflow:hidden;display:flex;flex-direction:column;animation:slideUp .28s cubic-bezier(.16,1,.3,1);box-sizing:border-box}"

if old1 in html:
    html = html.replace(old1, new1)
    changes.append("✅ תיקון 1: modal-card max-height מוגבל מעל הנאב")
else:
    # try flexible match
    html2 = re.sub(
        r'(\.modal-card\{[^}]*max-height\s*:\s*)calc\(100vh\s*-\s*32px\)',
        r'\1calc(100vh - 32px - var(--nav-h,60px) - env(safe-area-inset-bottom,0px))',
        html
    )
    if html2 != html:
        html = html2
        changes.append("✅ תיקון 1 (regex): modal-card max-height מוגבל מעל הנאב")
    else:
        changes.append("⚠️ תיקון 1: modal-card לא נמצא — בדוק ידנית")

# ══════════════════════════════════════════════════════════════════
# תיקון 2 — modal-body padding-bottom (כנדרש בבקשה)
# ══════════════════════════════════════════════════════════════════
old2 = ".modal-body{padding:17px;overflow-y:auto;flex:1;-webkit-overflow-scrolling:touch}"
new2 = ".modal-body{padding:17px;padding-bottom:calc(env(safe-area-inset-bottom,0px) + 80px);overflow-y:auto;flex:1;-webkit-overflow-scrolling:touch}"

if old2 in html:
    html = html.replace(old2, new2)
    changes.append("✅ תיקון 2: modal-body padding-bottom 80px הוסף")
else:
    html2 = re.sub(
        r'(\.modal-body\{padding:[^;};]+)',
        r'\1;padding-bottom:calc(env(safe-area-inset-bottom,0px) + 80px)',
        html
    )
    if html2 != html:
        html = html2
        changes.append("✅ תיקון 2 (regex): modal-body padding-bottom הוסף")
    else:
        changes.append("⚠️ תיקון 2: modal-body block לא נמצא")

# ══════════════════════════════════════════════════════════════════
# תיקון 3 — modal-footer padding-bottom: גם הפוטר יהיה מעל הנאב
# ══════════════════════════════════════════════════════════════════
old3 = ".modal-footer{padding:12px 17px 16px;border-top:1px solid var(--border);display:flex;align-items:center;gap:9px;flex-shrink:0;background:var(--surface)}"
new3 = ".modal-footer{padding:12px 17px calc(env(safe-area-inset-bottom,0px) + 16px);border-top:1px solid var(--border);display:flex;align-items:center;gap:9px;flex-shrink:0;background:var(--surface)}"

if old3 in html:
    html = html.replace(old3, new3)
    changes.append("✅ תיקון 3: modal-footer padding-bottom עם safe-area")
else:
    html2 = re.sub(
        r'(\.modal-footer\{padding\s*:\s*12px\s+17px\s+)16px',
        r'\1calc(env(safe-area-inset-bottom,0px) + 16px)',
        html
    )
    if html2 != html:
        html = html2
        changes.append("✅ תיקון 3 (regex): modal-footer padding-bottom עם safe-area")
    else:
        changes.append("⚠️ תיקון 3: modal-footer block לא נמצא")

# ══════════════════════════════════════════════════════════════════
# תיקון 4 — sim-next-btn margin-bottom (כפתור בתוך body)
# ══════════════════════════════════════════════════════════════════
old4_pattern = r'(\.sim-next-btn\{[^}]*?)(display\s*:\s*none)'
match4 = re.search(old4_pattern, html)
if match4 and 'margin-bottom' not in match4.group(0):
    html = re.sub(
        old4_pattern,
        r'\1margin-bottom:16px;\2',
        html
    )
    changes.append("✅ תיקון 4: sim-next-btn margin-bottom:16px הוסף")
else:
    changes.append("⚠️ תיקון 4: sim-next-btn כבר יש margin-bottom או לא נמצא")

# ══════════════════════════════════════════════════════════════════
# כתוב את הקובץ המתוקן
# ══════════════════════════════════════════════════════════════════
with open(path, "w", encoding="utf-8") as f:
    f.write(html)

new_len = len(html)
print(f"\n📂 קובץ מקורי: {original_len:,} bytes")
print(f"📂 קובץ מתוקן: {new_len:,} bytes")
print(f"📊 הפרש: {new_len - original_len:+} bytes\n")

print("תיקונים שבוצעו:")
for c in changes:
    print(f"  {c}")
