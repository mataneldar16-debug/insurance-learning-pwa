#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""patch3.py - Insurance PWA v3: 6 new features"""

FILE = r"C:\Users\Eldar\AppData\Local\Temp\insurance-pwa\index.html"

with open(FILE, 'r', encoding='utf-8') as f:
    c = f.read()

ok = []

###############################################################
# 1. CSS - insert before /* QUIZ STATS CARD */
###############################################################
CSS_NEW = (
"/* 3D CARD FLIP */\n"
".card-scene{perspective:800px;width:100%;margin-bottom:10px}\n"
".card-3d{position:relative;width:100%;transform-style:preserve-3d;transition:transform .6s cubic-bezier(.4,0,.2,1)}\n"
".card-3d.flipped{transform:rotateY(180deg)}\n"
".card-face{position:absolute;width:100%;backface-visibility:hidden;-webkit-backface-visibility:hidden}\n"
".card-front{transform:rotateY(0deg)}\n"
".card-back{transform:rotateY(180deg);background:var(--card2);border:1px solid var(--border2);border-radius:var(--r);padding:15px}\n"
"/* CONFETTI */\n"
"@keyframes confettiFall{0%{transform:translateY(-10px) rotate(0deg);opacity:1}100%{transform:translateY(100vh) rotate(720deg);opacity:0}}\n"
"/* TIMER */\n"
".q-timer{font-size:.72rem;color:var(--muted);margin-right:8px}\n"
"/* TODAY PLAN */\n"
".plan-card{background:linear-gradient(135deg,rgba(99,102,241,.08),rgba(168,85,247,.05));border:1px solid var(--blue-ring);border-radius:var(--r);padding:13px;margin-bottom:13px}\n"
".plan-item{display:flex;align-items:center;gap:8px;padding:5px 0;border-bottom:1px solid var(--border);font-size:.83rem}\n"
".plan-item:last-child{border-bottom:none}\n"
".plan-check{width:18px;height:18px;border-radius:4px;background:var(--blue-dim);border:1px solid var(--blue-ring);flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:.7rem}\n"
"/* KEYBOARD HINT */\n"
".kb-hint{font-size:.65rem;color:var(--dim);text-align:center;margin-top:6px}\n"
)
assert '/* QUIZ STATS CARD */' in c, "QUIZ STATS CARD marker not found"
c = c.replace('/* QUIZ STATS CARD */', CSS_NEW + '/* QUIZ STATS CARD */', 1)
ok.append('css'); print('OK css')

###############################################################
# 2. Plan card HTML in HOME tab
###############################################################
OLD_PHtml = '    </div>\n  </div>\n  <div class="today-grid">'
NEW_PHtml = (
'    </div>\n'
'  </div>\n'
'  <div class="plan-card" id="today-plan">\n'
'    <div class="tip-lbl">\U0001F4CB תוכנית היום</div>\n'
'    <div id="plan-items"></div>\n'
'  </div>\n'
'  <div class="today-grid">'
)
assert OLD_PHtml in c, "today-grid marker not found"
c = c.replace(OLD_PHtml, NEW_PHtml, 1)
ok.append('plan-card-html'); print('OK plan-card-html')

###############################################################
# 3. Replace showQuestion()
###############################################################
sq_s = c.index('function showQuestion() {')
sq_e = c.index('function submitAnswer(ansIdx, el) {')

NEW_SQ = """function showQuestion() {
  const q = QS.pool[QS.idx];
  if (!q) { showQuizResult(); return; }
  const pct = QS.total > 1 ? Math.round(QS.idx / QS.total * 100) : 0;
  const topicName = TOPIC_NAMES[q.topic] || q.topic || '';
  const qRealId = q.id ?? QS.pool[QS.idx].idx;
  const h = S.quizHistory[qRealId];
  const isNR = S.notRelevant.includes(qRealId);

  document.getElementById('quiz-area').innerHTML = `
    <div class="qprog-wrap">
      <div class="qprog-bg"><div class="qprog-fill" style="width:${pct}%"></div></div>
      <span class="q-timer" id="q-timer">⏱ 0:00</span>
      <div class="qprog-txt">${QS.idx+1}/${QS.total}</div>
    </div>
    <div class="card-scene">
      <div class="card-3d" id="quiz-card-3d">
        <div class="card-face card-front">
          <div class="q-topic-tag">${topicName}</div>
          <div class="q-text">${q.q}</div>
          <div class="q-options">
            ${q.opts.map((opt, i) => `<button class="q-opt" data-action="quiz-answer" data-param="${i}">
              <span class="ol">${String.fromCharCode(65+i)}</span>
              <span>${opt}</span>
            </button>`).join('')}
          </div>
          <div class="q-not-rel">
            <button class="nr-btn ${isNR?'marked':''}" data-action="not-relevant" data-param="${qRealId}">
              ${isNR ? '✓ לא רלוונטי' : 'לא רלוונטי לי'}
            </button>
            ${h ? `<span>ניסיונות: ${h.attempts||0} | נכון: ${h.correct||0}</span>` : ''}
          </div>
        </div>
        <div class="card-face card-back" id="quiz-card-back"></div>
      </div>
    </div>
  `;
  setTimeout(() => {
    const c3d = document.getElementById('quiz-card-3d');
    const cf = c3d && c3d.querySelector('.card-front');
    if (c3d && cf) c3d.style.height = cf.scrollHeight + 'px';
  }, 50);
}

"""
c = c[:sq_s] + NEW_SQ + c[sq_e:]
ok.append('showQuestion'); print('OK showQuestion')

###############################################################
# 4. Replace submitAnswer()
###############################################################
sa_s = c.index('function submitAnswer(ansIdx, el) {')
sa_e = c.index('function nextQuestion() {')

NEW_SA = """function submitAnswer(ansIdx, el) {
  const q = QS.pool[QS.idx];
  if (!q) return;
  const opts = document.querySelectorAll('.q-opt');
  opts.forEach(b => { b.classList.add('locked'); b.dataset.action = ''; });

  const isCorrect = ansIdx === q.ans;
  opts[ansIdx].classList.add(isCorrect ? 'correct' : 'wrong');
  if (!isCorrect) opts[q.ans].classList.add('correct');

  if (isCorrect) {
    QS.correct++;
    addXP(XP_CONFIG.quizCorrect, 'תשובה נכונה');
  }
  QS.sessionAnswers = QS.sessionAnswers || [];
  QS.sessionAnswers.push({topic: q.topic || 'other', correct: isCorrect});

  const qid = q.id ?? QS.pool[QS.idx].idx;
  const h = S.quizHistory[qid] || {correct:0, attempts:0, interval:1, ease:2.5, nextSeen:null};
  h.attempts = (h.attempts||0) + 1;
  if (isCorrect) h.correct = (h.correct||0) + 1;
  S.quizHistory[qid] = h;

  const iv = h.interval || 1;
  const ease = h.ease || 2.5;
  const ivAgain = 1;
  const ivHard = Math.max(1, Math.round(iv * 1.2));
  const ivGood = Math.max(1, Math.round(iv * ease));
  const ivEasy = Math.max(1, Math.round(iv * ease * 1.3));
  function ivLabel(d) { return d === 1 ? '1 יום' : d + ' ימים'; }

  const back = document.getElementById('quiz-card-back');
  const qRealId = q.id ?? QS.pool[QS.idx].idx;
  const isNR = S.notRelevant.includes(qRealId);
  if (back) {
    back.innerHTML = `
      <div class="q-fb show ${isCorrect ? 'ok' : 'err'}">
        <strong>${isCorrect ? '✅ נכון!' : '❌ לא נכון'}</strong>${q.exp}
      </div>
      <div class="quiz-confidence">
        <div class="confidence-label">כמה ידעת?</div>
        <div class="confidence-btns">
          <button class="conf-btn conf-again" data-action="quiz-rate" data-param="0">
            \U0001f534 שכחתי<span class="conf-interval">${ivLabel(ivAgain)}</span>
          </button>
          <button class="conf-btn conf-hard" data-action="quiz-rate" data-param="3">
            \U0001f7e1 קשה<span class="conf-interval">${ivLabel(ivHard)}</span>
          </button>
          <button class="conf-btn conf-good" data-action="quiz-rate" data-param="4">
            \U0001f7e2 ידעתי<span class="conf-interval">${ivLabel(ivGood)}</span>
          </button>
          <button class="conf-btn conf-easy" data-action="quiz-rate" data-param="5">
            ⚡ קל<span class="conf-interval">${ivLabel(ivEasy)}</span>
          </button>
        </div>
      </div>
      <div class="q-not-rel" style="margin-top:8px">
        <button class="nr-btn ${isNR?'marked':''}" data-action="not-relevant" data-param="${qRealId}">
          ${isNR ? '✓ לא רלוונטי' : 'לא רלוונטי לי'}
        </button>
      </div>
      <div class="kb-hint">מקשי קיצור: 1 \xb7 2 \xb7 3 \xb7 4</div>
    `;
    setTimeout(() => {
      const c3d = document.getElementById('quiz-card-3d');
      const cf = c3d && c3d.querySelector('.card-front');
      if (c3d && cf && back) {
        c3d.style.height = Math.max(cf.scrollHeight, back.scrollHeight) + 'px';
        c3d.classList.add('flipped');
      }
    }, 50);
  }

  const _today = new Date().toISOString().split('T')[0];
  S.activityLog = S.activityLog || {};
  S.activityLog[_today] = (S.activityLog[_today]||0)+1;
  save();
}

"""
c = c[:sa_s] + NEW_SA + c[sa_e:]
ok.append('submitAnswer'); print('OK submitAnswer')

###############################################################
# 5. Replace showQuizResult()
###############################################################
sqr_s = c.index('function showQuizResult() {')
sqr_e = c.index('function toggleNotRelevant(i) {')

NEW_SQR = """function showQuizResult() {
  QS.sessionDone = true;
  stopTimer();
  const pct = QS.total > 0 ? Math.round(QS.correct / QS.total * 100) : 0;
  if (S.quizBestPct == null || pct > S.quizBestPct) S.quizBestPct = pct;
  addXP(XP_CONFIG.quizComplete, `חידון הושלם: ${pct}%`);
  checkBadges();
  save();

  if (QS.correct === QS.total && QS.total >= 5) launchConfetti();

  const secs = QS_startTime ? Math.floor((Date.now() - QS_startTime) / 1000) : 0;
  const timeStr = secs > 0 ? ` \xb7 ⏱ ${Math.floor(secs/60)}:${(secs%60).toString().padStart(2,'0')}` : '';

  const msg = pct >= 90 ? '\U0001f3c6 מצוין! מסיים ברמה גבוהה' : pct >= 70 ? '✅ כל הכבוד!' : '\U0001f4aa המשך להתאמן';

  const topicBreakdown = {};
  (QS.sessionAnswers || []).forEach(a => {
    if (!topicBreakdown[a.topic]) topicBreakdown[a.topic] = {c:0, t:0};
    topicBreakdown[a.topic].t++;
    if (a.correct) topicBreakdown[a.topic].c++;
  });
  const topicHtml = Object.entries(topicBreakdown).map(([t,v]) => {
    const p = Math.round(v.c / v.t * 100);
    const color = p >= 75 ? 'var(--green)' : p >= 50 ? 'var(--gold)' : 'var(--red)';
    return `<div style="display:flex;align-items:center;gap:8px;margin-bottom:5px">`
      + `<span style="font-size:.78rem;color:#ccc;flex:1">${TOPIC_NAMES[t] || t}</span>`
      + `<span style="font-size:.78rem;font-weight:700;color:${color}">${v.c}/${v.t}</span>`
      + `</div>`;
  }).join('');

  document.getElementById('quiz-area').innerHTML = `
    <div class="quiz-result">
      <div class="res-circle"><div class="res-score">${pct}%</div><div class="res-of">${QS.correct}/${QS.total}</div></div>
      <div class="res-msg">${msg}</div>
      <div class="res-sub">נכון: ${QS.correct} \xb7 טעויות: ${QS.total-QS.correct}${timeStr}</div>
      ${topicHtml ? `<div class="result-topics" style="margin:14px 0;text-align:right;border-top:1px solid var(--border);padding-top:12px">${topicHtml}</div>` : ''}
      <button class="q-next-btn show" data-action="start-quiz">שחק שוב →</button>
    </div>
  `;
  updateHeader();
}

"""
c = c[:sqr_s] + NEW_SQR + c[sqr_e:]
ok.append('showQuizResult'); print('OK showQuizResult')

###############################################################
# 6. startQuiz() - add startTimer()
###############################################################
OLD_START = "  QS.sessionAnswers = [];"
NEW_START = "  QS.sessionAnswers = [];\n  startTimer();"
assert OLD_START in c, "QS.sessionAnswers not found"
c = c.replace(OLD_START, NEW_START, 1)
ok.append('startTimer-call'); print('OK startTimer call')

###############################################################
# 7. New functions before XP section
###############################################################
XP_MARKER = '// ===== XP & GAMIFICATION ====='
assert XP_MARKER in c

NEW_FUNCS = """// ===== TIMER =====
let QS_timer = null;
let QS_startTime = null;

function startTimer() {
  stopTimer();
  QS_startTime = Date.now();
  QS_timer = setInterval(() => {
    const secs = Math.floor((Date.now() - QS_startTime) / 1000);
    const m = Math.floor(secs/60), s = secs%60;
    const el = document.getElementById('q-timer');
    if (el) el.textContent = `⏱ ${m}:${s.toString().padStart(2,'0')}`;
  }, 1000);
}

function stopTimer() {
  if (QS_timer) { clearInterval(QS_timer); QS_timer = null; }
}

// ===== CONFETTI =====
function launchConfetti() {
  const colors = ['#6366f1','#a855f7','#10b981','#f59e0b','#ef4444'];
  for (let i = 0; i < 60; i++) {
    setTimeout(() => {
      const el = document.createElement('div');
      el.style.cssText = `position:fixed;top:0;left:${Math.random()*100}vw;width:8px;height:8px;background:${colors[Math.floor(Math.random()*colors.length)]};border-radius:${Math.random()>0.5?'50%':'2px'};pointer-events:none;z-index:9999;animation:confettiFall ${1.5+Math.random()*1.5}s ease forwards`;
      document.body.appendChild(el);
      setTimeout(() => el.remove(), 3500);
    }, i * 30);
  }
}

// ===== KEYBOARD SHORTCUTS =====
function handleKeyPress(e) {
  if (!['1','2','3','4'].includes(e.key)) return;
  const idx = parseInt(e.key) - 1;
  const btns = document.querySelectorAll('.conf-btn');
  if (btns[idx]) btns[idx].click();
}
document.addEventListener('keydown', handleKeyPress);

// ===== TODAY'S PLAN =====
function buildTodayPlan() {
  const plan = [];
  const dueCount = getDueCount();
  if (dueCount > 0) plan.push({icon:'\U0001f501', text:`חזור על ${Math.min(dueCount,20)} שאלות SRS`, action:'tab:quiz'});
  const allIds = Object.keys(LESSONS);
  const nextLesson = allIds.find(id => !S.completedLessons.includes(id));
  if (nextLesson) plan.push({icon:'\U0001f4d6', text:`למד: ${LESSONS[nextLesson]?.title}`, action:'lesson:'+nextLesson});
  const stats = getTopicStats();
  const weakest = Object.entries(stats).filter(([,v])=>v.total>0).sort((a,b)=>a[1].correct/a[1].total-b[1].correct/b[1].total)[0];
  if (weakest) plan.push({icon:'\U0001f3af', text:`חזק נושא חלש: ${TOPIC_NAMES[weakest[0]]||weakest[0]}`, action:'tab:quiz'});
  if (plan.length === 0) plan.push({icon:'\U0001f3c6', text:'כל המשימות הושלמו! נהדר', action:''});
  return plan;
}

// ===== STREAK XP MULTIPLIER =====
function getStreakMultiplier() {
  const s = S.streak.count;
  if (s >= 30) return 2.0;
  if (s >= 14) return 1.5;
  if (s >= 7) return 1.25;
  if (s >= 3) return 1.1;
  return 1.0;
}

"""
c = c.replace(XP_MARKER, NEW_FUNCS + XP_MARKER, 1)
ok.append('new-funcs'); print('OK new functions')

###############################################################
# 8. Replace addXP()
###############################################################
axp_s = c.index('function addXP(amount, reason) {')
axp_e = c.index('function showXPToast(msg) {')

NEW_AXP = """function addXP(amount, reason) {
  const mult = getStreakMultiplier();
  const actual = Math.round(amount * mult);
  S.xp += actual;
  const ts = new Date().toLocaleTimeString('he-IL', {hour:'2-digit',minute:'2-digit'});
  S.xpLog.unshift({amount: actual, reason, ts});
  if (S.xpLog.length > 30) S.xpLog.pop();
  const newLevel = LEVELS.findIndex(l => S.xp >= l.min && S.xp <= l.max);
  if (newLevel !== -1 && newLevel + 1 !== S.level) {
    S.level = newLevel + 1;
  }
  save();
  const multStr = mult > 1 ? ` \U0001f525\xd7${mult}` : '';
  showXPToast(`+${actual} XP${multStr} \xb7 ${reason}`);
  updateHeader();
}

"""
c = c[:axp_s] + NEW_AXP + c[axp_e:]
ok.append('addXP'); print('OK addXP')

###############################################################
# 9. Replace updateHeader()
###############################################################
uh_s = c.index('function updateHeader() {')
uh_e = c.index('// ===== HOME TAB =====')

NEW_UH = """function updateHeader() {
  const lv = getLevel();
  document.getElementById('header-xp').textContent = `⭐ ${S.xp} XP \xb7 ${lv.name} ${lv.icon}`;
  const strkEl = document.getElementById('header-streak');
  if (strkEl) {
    const mult = getStreakMultiplier();
    const multStr = mult > 1 ? ` \xd7${mult}` : '';
    strkEl.textContent = `\U0001f525 ${S.streak.count}${multStr}`;
  }
}

"""
c = c[:uh_s] + NEW_UH + c[uh_e:]
ok.append('updateHeader'); print('OK updateHeader')

###############################################################
# 10. renderHome() - add today's plan rendering
###############################################################
PLAN_MARKER = "  examBadgeHtml('eb-yesodot', '2026-12-09');"
PLAN_NEW = (
"  // Today plan\n"
"  const planItems = document.getElementById('plan-items');\n"
"  if (planItems) {\n"
"    const plan = buildTodayPlan();\n"
"    planItems.innerHTML = plan.map(p =>\n"
"      `<div class=\"plan-item\"><div class=\"plan-check\">${p.icon}</div><span>${p.text}</span></div>`\n"
"    ).join('');\n"
"  }\n"
"  examBadgeHtml('eb-yesodot', '2026-12-09');"
)
assert PLAN_MARKER in c, "examBadgeHtml marker not found"
c = c.replace(PLAN_MARKER, PLAN_NEW, 1)
ok.append('renderHome'); print('OK renderHome')

###############################################################
# VERIFY
###############################################################
checks = ['confettiFall', 'card-3d', 'kb-hint', 'q-timer', 'plan-card', 'getStreakMultiplier', 'launchConfetti', 'startTimer']
print('\n--- VERIFICATION ---')
for ch in checks:
    found = ch in c
    print(f'  CHECK {ch}: {"OK" if found else "MISSING!"}')
    assert found, f"MISSING: {ch}"

###############################################################
# WRITE
###############################################################
with open(FILE, 'w', encoding='utf-8') as f:
    f.write(c)

print(f'\nDone! Changes: {ok}')
print(f'File written: {FILE}')
