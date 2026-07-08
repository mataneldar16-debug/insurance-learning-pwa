# -*- coding: utf-8 -*-
"""
patch4.py – Adds FSRS-lite + Hearts + Topic Accuracy + Level-Up to insurance-pwa
"""

path = r'C:\Users\Eldar\AppData\Local\Temp\insurance-pwa\index.html'

with open(path, encoding='utf-8') as f:
    content = f.read()

original = content
applied = []

def sub(name, old, new):
    global content
    if old not in content:
        print(f'❌ NOT FOUND: {name}')
        return
    count = content.count(old)
    if count > 1:
        print(f'⚠️  AMBIGUOUS ({count} matches): {name}')
    content = content.replace(old, new, 1)
    applied.append(name)
    print(f'✅ Applied: {name}')

# ─────────────────────────────────────────────────
# 1. CSS — hearts, topic-acc, level-up animations
# ─────────────────────────────────────────────────
sub('CSS: hearts/topic-acc/levelup',
'.q-timer{font-size:.72rem;color:var(--muted);margin-right:8px}',
'''.q-timer{font-size:.72rem;color:var(--muted);margin-right:8px}
.q-hearts{font-size:1.1rem;letter-spacing:2px;margin-left:8px}
.q-hearts.pulse{animation:heartPulse .3s ease}
@keyframes heartPulse{0%,100%{transform:scale(1)}50%{transform:scale(1.3)}}
.topic-acc{font-size:.72rem;color:var(--muted);margin-top:5px;padding-top:5px;border-top:1px solid var(--border)}
.levelup-overlay{position:fixed;inset:0;background:rgba(0,0,0,.7);display:flex;align-items:center;justify-content:center;z-index:10000;animation:fadeInOut 2.5s ease forwards}
@keyframes fadeInOut{0%{opacity:0}15%{opacity:1}75%{opacity:1}100%{opacity:0}}
.levelup-card{background:linear-gradient(135deg,var(--blue),var(--purple));border-radius:16px;padding:30px 40px;text-align:center;transform:scale(0);animation:popIn .4s .2s ease forwards}
@keyframes popIn{to{transform:scale(1)}}
.levelup-icon{font-size:3rem;margin-bottom:8px}
.levelup-title{font-size:1.4rem;font-weight:800;color:#fff}
.levelup-sub{font-size:1rem;color:rgba(255,255,255,.8);margin-top:4px}''')

# ─────────────────────────────────────────────────
# 2. QS state — add hearts field
# ─────────────────────────────────────────────────
sub('QS state: add hearts',
"let QS = { // Quiz state\n  mode:'srs', filter:'all', pool:[], idx:0,\n  correct:0, total:0, sessionDone:false, sessionAnswers:[]\n};",
"let QS = { // Quiz state\n  mode:'srs', filter:'all', pool:[], idx:0,\n  correct:0, total:0, sessionDone:false, sessionAnswers:[], hearts:3\n};")

# ─────────────────────────────────────────────────
# 3. startQuiz — reset hearts
# ─────────────────────────────────────────────────
sub('startQuiz: reset hearts',
"function startQuiz() {\n  QS.pool = getQuizPool();\n  QS.idx = 0;\n  QS.correct = 0;",
"function startQuiz() {\n  QS.pool = getQuizPool();\n  QS.idx = 0;\n  QS.correct = 0;\n  QS.hearts = 3;")

# ─────────────────────────────────────────────────
# 4. showQuestion — add q-hearts to qprog-wrap
# ─────────────────────────────────────────────────
sub('showQuestion: add q-hearts',
"      <span class=\"q-timer\" id=\"q-timer\">⏱ 0:00</span>\n      <div class=\"qprog-txt\">${QS.idx+1}/${QS.total}</div>",
"      <span class=\"q-timer\" id=\"q-timer\">⏱ 0:00</span>\n      <div class=\"q-hearts\" id=\"q-hearts\">${QS.mode !== 'srs' ? '❤️'.repeat(QS.hearts||3)+'\U0001f5a4'.repeat(Math.max(0,3-(QS.hearts||3))) : ''}</div>\n      <div class=\"qprog-txt\">${QS.idx+1}/${QS.total}</div>")

# ─────────────────────────────────────────────────
# 5. submitAnswer — hearts decrement on wrong answer
# ─────────────────────────────────────────────────
sub('submitAnswer: hearts decrement',
"  if (isCorrect) {\n    QS.correct++;\n    addXP(XP_CONFIG.quizCorrect, 'תשובה נכונה');\n  }\n  QS.sessionAnswers = QS.sessionAnswers || [];",
"""  if (isCorrect) {
    QS.correct++;
    addXP(XP_CONFIG.quizCorrect, 'תשובה נכונה');
  } else if (QS.mode !== 'srs') {
    QS.hearts = (QS.hearts !== undefined) ? QS.hearts - 1 : 2;
    updateHearts();
    if (QS.hearts <= 0) {
      const _todayH = new Date().toISOString().split('T')[0];
      S.activityLog = S.activityLog || {};
      S.activityLog[_todayH] = (S.activityLog[_todayH]||0)+1;
      save();
      setTimeout(() => showQuizResult(), 800);
      return;
    }
  }
  QS.sessionAnswers = QS.sessionAnswers || [];""")

# ─────────────────────────────────────────────────
# 6. submitAnswer — FSRS-lite IV preview + topic accuracy prep
# ─────────────────────────────────────────────────
sub('submitAnswer: FSRS preview + topicAcc',
"  const iv = h.interval || 1;\n  const ease = h.ease || 2.5;\n  const ivAgain = 1;\n  const ivHard = Math.max(1, Math.round(iv * 1.2));\n  const ivGood = Math.max(1, Math.round(iv * ease));\n  const ivEasy = Math.max(1, Math.round(iv * ease * 1.3));\n  function ivLabel(d) { return d === 1 ? '1 יום' : d + ' ימים'; }",
"""  const iv = h.interval || 1;
  const ease = h.ease || 2.5;
  const _fsD = h.D || 5;
  const _fsS = h.S || 1;
  const ivAgain = 1;
  const ivHard = Math.max(1, Math.round(iv * 1.2));
  const ivGood = Math.max(1, Math.round(_fsS * (1 + 0.1 * (11 - _fsD))));
  const ivEasy = Math.max(1, Math.round(_fsS * (1 + 0.15 * (11 - _fsD)) * 1.3));
  const _topicAcc = getTopicAccuracy(q.topic);
  const _topicAccHtml = _topicAcc !== null ? `<div class="topic-acc">\U0001f4ca דיוק שלך ב${TOPIC_NAMES[q.topic]||q.topic}: ${_topicAcc}%</div>` : '';
  function ivLabel(d) { return d === 1 ? '1 יום' : d + ' ימים'; }""")

# ─────────────────────────────────────────────────
# 7. submitAnswer — inject topicAccHtml into q-fb div
# ─────────────────────────────────────────────────
sub('submitAnswer: topic-acc in feedback',
'        <strong>${isCorrect ? \'✅ נכון!\' : \'❌ לא נכון\'}</strong>${q.exp}\n      </div>',
'        <strong>${isCorrect ? \'✅ נכון!\' : \'❌ לא נכון\'}</strong>${q.exp}${_topicAccHtml}\n      </div>')

# ─────────────────────────────────────────────────
# 8. Replace rateAnswer (SM-2) with FSRS-lite
# ─────────────────────────────────────────────────
OLD_RATE = """function rateAnswer(rating) {
  const q = QS.pool[QS.idx];
  if (!q) return;
  const qid = q.id ?? QS.pool[QS.idx].idx;
  const h = S.quizHistory[qid] || {correct:0, attempts:0, interval:1, ease:2.5, nextSeen:null};
  const iv = h.interval || 1;
  const ease = h.ease || 2.5;

  if (rating === 0) { // שכחתי - Again
    h.interval = 1;
    h.ease = Math.max(1.3, ease - 0.2);
  } else if (rating === 3) { // קשה - Hard
    h.interval = Math.max(1, Math.round(iv * 1.2));
    h.ease = Math.max(1.3, ease - 0.15);
  } else if (rating === 4) { // ידעתי - Good
    h.interval = Math.max(1, Math.round(iv * ease));
  } else if (rating === 5) { // קל - Easy
    h.interval = Math.max(1, Math.round(iv * ease * 1.3));
    h.ease = Math.min(4.0, ease + 0.15);
  }

  const nextDate = new Date();
  nextDate.setDate(nextDate.getDate() + h.interval);
  h.nextSeen = nextDate.toISOString();
  S.quizHistory[qid] = h;
  save();
  nextQuestion();
}"""

NEW_RATE = """function fsrsUpdate(card, rating) {
  // rating: 1=Again, 2=Hard, 3=Good, 4=Easy
  card.D = card.D || 5;
  card.S = card.S || 1;
  card.reps = (card.reps || 0) + 1;
  if (rating === 1) { // Again
    card.D = Math.min(10, card.D + 2);
    card.S = Math.max(0.5, card.S * 0.5);
    card.interval = 1;
  } else if (rating === 2) { // Hard
    card.D = Math.min(10, card.D + 0.5);
    card.S = card.S * 0.8;
    card.interval = Math.max(1, Math.round((card.interval || 1) * 1.2));
  } else if (rating === 3) { // Good
    card.D = Math.max(1, card.D - 0.2);
    card.S = card.S * (1 + 0.1 * (11 - card.D));
    card.interval = Math.round(card.S);
  } else { // Easy
    card.D = Math.max(1, card.D - 0.5);
    card.S = card.S * (1 + 0.15 * (11 - card.D));
    card.interval = Math.round(card.S * 1.3);
  }
  card.interval = Math.max(1, Math.min(card.interval, 365));
  return card;
}

function rateAnswer(rating) {
  const q = QS.pool[QS.idx];
  if (!q) return;
  const qid = q.id ?? QS.pool[QS.idx].idx;
  const h = S.quizHistory[qid] || {correct:0, attempts:0, interval:1, ease:2.5, nextSeen:null, D:5, S:1, reps:0};
  // Map button params (0/3/4/5) → FSRS ratings (1/2/3/4)
  const fsrsRating = rating === 0 ? 1 : rating === 3 ? 2 : rating === 4 ? 3 : 4;
  fsrsUpdate(h, fsrsRating);
  const nextDate = new Date();
  nextDate.setDate(nextDate.getDate() + h.interval);
  h.nextSeen = nextDate.toISOString();
  S.quizHistory[qid] = h;
  save();
  nextQuestion();
}"""

sub('rateAnswer: replace SM-2 with FSRS-lite', OLD_RATE, NEW_RATE)

# ─────────────────────────────────────────────────
# 9. addXP — trigger showLevelUp when level changes
# ─────────────────────────────────────────────────
sub('addXP: showLevelUp on level change',
"  if (newLevel !== -1 && newLevel + 1 !== S.level) {\n    S.level = newLevel + 1;\n  }",
"  if (newLevel !== -1 && newLevel + 1 !== S.level) {\n    S.level = newLevel + 1;\n    showLevelUp(S.level);\n  }")

# ─────────────────────────────────────────────────
# 10. Add helper functions before showXPToast
# ─────────────────────────────────────────────────
HELPERS = '''function updateHearts() {
  const el = document.getElementById('q-hearts');
  if (!el) return;
  el.textContent = '❤️'.repeat(QS.hearts) + '\U0001f5a4'.repeat(Math.max(0, 3 - QS.hearts));
  el.classList.remove('pulse');
  void el.offsetWidth;
  el.classList.add('pulse');
}

function getTopicAccuracy(topic) {
  const entries = Object.entries(S.quizHistory).filter(([id, c]) => {
    const qObj = QUIZ_DATA.find(q => q.id === parseInt(id));
    return qObj && qObj.topic === topic && (c.attempts || 0) > 0;
  });
  if (entries.length === 0) return null;
  const correct = entries.filter(([id, c]) => (c.correct || 0) > 0).length;
  return Math.round(correct / entries.length * 100);
}

function showLevelUp(level) {
  const lvl = LEVELS.find(l => l.num === level);
  const name = lvl ? lvl.name : 'רמה ' + level;
  const overlay = document.createElement('div');
  overlay.className = 'levelup-overlay';
  overlay.innerHTML = `<div class="levelup-card"><div class="levelup-icon">⭐</div><div class="levelup-title">עלית רמה!</div><div class="levelup-sub">${name}</div></div>`;
  document.body.appendChild(overlay);
  setTimeout(() => overlay.remove(), 2500);
}

'''

sub('add updateHearts / getTopicAccuracy / showLevelUp',
'function showXPToast(msg) {',
HELPERS + 'function showXPToast(msg) {')

# ─────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────
print(f'\nApplied {len(applied)}/10 patches')

if content == original:
    print('⚠️  WARNING: File unchanged!')
else:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ File saved.\n')

checks = ['fsrsUpdate', 'q-hearts', 'updateHearts', 'topic-acc', 'levelup-overlay', 'showLevelUp', 'getTopicAccuracy', '_topicAccHtml', 'heartPulse', 'QS.hearts']
for c in checks:
    print(c, '✅' if c in content else '❌ MISSING')
