#!/usr/bin/env python3
# navrewrite.py — Complete nav system rewrite for insurance-pwa
import sys

path = r'C:\Users\Eldar\AppData\Local\Temp\insurance-pwa\index.html'

with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

original_len = len(html)
changes = []

# ─────────────────────────────────────────────
# 1. REPLACE NAV HTML
# ─────────────────────────────────────────────
nav_marker = '<nav class="bottom-nav" id="app-nav">'
nav_start = html.find(nav_marker)
if nav_start >= 0:
    nav_end = html.find('</nav>', nav_start) + len('</nav>')
    new_nav = (
        '<nav class="bottom-nav" id="app-nav">\n'
        '  <button class="nav-btn active" data-action="tab" data-param="home">'
        '<span class="nav-icon">\U0001f3e0</span><span class="nav-label">בית</span></button>\n'
        '  <button class="nav-btn" data-action="tab" data-param="learn">'
        '<span class="nav-icon">\U0001f4da</span><span class="nav-label">למידה</span></button>\n'
        '  <button class="nav-btn" data-action="tab" data-param="quiz">'
        '<span class="nav-icon">\U0001f3af</span><span class="nav-label">חידון</span></button>\n'
        '  <button class="nav-btn" data-action="tab" data-param="sim">'
        '<span class="nav-icon">\U0001f3ae</span><span class="nav-label">סימולטור</span></button>\n'
        '  <button class="nav-btn" data-action="tab" data-param="perf">'
        '<span class="nav-icon">\U0001f3c6</span><span class="nav-label">ביצועים</span></button>\n'
        '</nav>'
    )
    html = html[:nav_start] + new_nav + html[nav_end:]
    changes.append('Nav HTML replaced')
else:
    changes.append('ERROR: nav HTML marker not found')

# ─────────────────────────────────────────────
# 2. REPLACE .bottom-nav CSS
# ─────────────────────────────────────────────
bn_start = html.find('.bottom-nav{')
if bn_start >= 0:
    bn_end = html.find('}', bn_start) + 1
    new_bn = (
        '.bottom-nav{position:fixed;bottom:0;left:0;right:0;'
        'height:calc(var(--nav-h) + env(safe-area-inset-bottom,0px));'
        'padding-bottom:env(safe-area-inset-bottom,0px);'
        'background:var(--surface);border-top:1px solid var(--border);'
        'display:flex;align-items:center;z-index:10001;will-change:transform}'
    )
    html = html[:bn_start] + new_bn + html[bn_end:]
    changes.append('.bottom-nav CSS replaced')
else:
    changes.append('ERROR: .bottom-nav{ not found')

# ─────────────────────────────────────────────
# 3. REPLACE .nav-btn CSS BLOCK
#    Matches: .nav-btn{} .nav-btn.active{} .nav-btn .ni{} .nav-btn.active .ni{} .nav-btn .nl{}
# ─────────────────────────────────────────────
nb_start = html.find('\n.nav-btn{')
if nb_start >= 0:
    nb_start += 1  # skip leading \n, keep it clean
    # Find end: after .nav-btn .nl{...}
    nl_marker = '.nav-btn .nl{'
    nl_pos = html.find(nl_marker, nb_start)
    if nl_pos >= 0:
        nb_end = html.find('}', nl_pos) + 1
    else:
        # fallback: just cut to next #app-main or end of .nav-btn block
        nb_end = html.find('\n#app-main{', nb_start)
        if nb_end < 0:
            nb_end = nb_start + 500
    new_nb = (
        '.nav-btn{flex:1;display:flex;flex-direction:column;align-items:center;'
        'justify-content:center;gap:2px;padding:8px 0;background:none;border:none;'
        'cursor:pointer;color:var(--muted);font-size:.6rem;'
        '-webkit-tap-highlight-color:transparent;touch-action:manipulation}\n'
        '.nav-btn.active{color:var(--blue)}\n'
        '.nav-icon{font-size:1.2rem;line-height:1}\n'
        '.nav-label{font-size:.6rem;font-weight:700}'
    )
    html = html[:nb_start] + new_nb + html[nb_end:]
    changes.append('.nav-btn CSS block replaced')
else:
    changes.append('ERROR: .nav-btn{ block not found')

# ─────────────────────────────────────────────
# 4. REPLACE showTab FUNCTION (brace-counting)
# ─────────────────────────────────────────────
new_showtab = (
    'function showTab(id) {\n'
    "  document.querySelectorAll('.tab-pane').forEach(p => p.style.display = 'none');\n"
    "  const target = document.getElementById('tab-' + id);\n"
    "  if (target) target.style.display = 'block';\n"
    "  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));\n"
    "  const btn = document.querySelector('.nav-btn[data-param=\"' + id + '\"]');\n"
    "  if (btn) btn.classList.add('active');\n"
    "  const main = document.getElementById('app-main');\n"
    '  if (main) main.scrollTop = 0;\n'
    "  if (id === 'home') renderHome();\n"
    "  if (id === 'learn') renderLearn();\n"
    "  if (id === 'quiz') renderQuizShell();\n"
    "  if (id === 'sim') showSimSelect();\n"
    "  if (id === 'perf') renderPerf();\n"
    '}'
)

fn_start = html.find('function showTab(id)')
if fn_start >= 0:
    brace_pos = html.find('{', fn_start)
    depth = 0
    fn_end = -1
    for i in range(brace_pos, len(html)):
        if html[i] == '{':
            depth += 1
        elif html[i] == '}':
            depth -= 1
            if depth == 0:
                fn_end = i + 1
                break
    if fn_end > 0:
        html = html[:fn_start] + new_showtab + html[fn_end:]
        changes.append('showTab function replaced')
    else:
        changes.append('ERROR: could not find showTab closing brace')
else:
    changes.append('ERROR: showTab function not found')

# ─────────────────────────────────────────────
# 5. VERIFY click handler has ACTIONS routing
# ─────────────────────────────────────────────
if "'tab': id => showTab(id)" in html or '"tab": id => showTab(id)' in html:
    changes.append('ACTIONS[tab] routing confirmed present')
else:
    changes.append('WARNING: ACTIONS[tab] routing not confirmed')

# ─────────────────────────────────────────────
# WRITE
# ─────────────────────────────────────────────
with open(path, 'w', encoding='utf-8') as f:
    f.write(html)

print('Nav rewrite complete!')
print(f'Original: {original_len} chars')
print(f'New:      {len(html)} chars')
print()
for c in changes:
    icon = 'OK' if not c.startswith('ERROR') and not c.startswith('WARNING') else ('WARN' if c.startswith('WARNING') else 'FAIL')
    print(f'  [{icon}] {c}')
