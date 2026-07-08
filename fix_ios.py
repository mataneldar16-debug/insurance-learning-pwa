import re, shutil

path = r"C:\Users\Eldar\AppData\Local\Temp\insurance-pwa\index.html"

with open(path, "r", encoding="utf-8") as f:
    html = f.read()

original_len = len(html)
changes = []

# ══════════════════════════════════════════════════════════════════
# תיקון iOS — querySelectorAll().forEach → Array.from().forEach
# ══════════════════════════════════════════════════════════════════
def fix_qsa_foreach(m):
    expr = m.group(1)  # e.g. document.querySelectorAll('.track-btn')
    return f"Array.from({expr}).forEach"

# Pattern: someExpr.querySelectorAll('...').forEach
count_before = len(re.findall(r'((?:document|[a-zA-Z_$][a-zA-Z0-9_$.]*)\s*\.\s*querySelectorAll\s*\([^)]+\))\s*\.forEach', html))
html_new = re.sub(
    r'((?:document|[a-zA-Z_$][a-zA-Z0-9_$.]*)\s*\.\s*querySelectorAll\s*\([^)]+\))\s*\.forEach',
    fix_qsa_foreach,
    html
)
count_after = len(re.findall(r'querySelectorAll[^)]*\)\s*\.forEach', html_new))
fixed = count_before - count_after
if fixed > 0:
    html = html_new
    changes.append(f"✅ iOS fix: {fixed} querySelectorAll+.forEach → Array.from().forEach")
else:
    changes.append("⚠️ iOS fix: לא הוחל (בדוק regex)")

with open(path, "w", encoding="utf-8") as f:
    f.write(html)

new_len = len(html)
print(f"📂 לפני: {original_len:,} chars  →  אחרי: {new_len:,} chars  (Δ {new_len-original_len:+})")
for c in changes:
    print(f"  {c}")
