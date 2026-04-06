// static/js/script.js

async function summarize() {
  const input = document.getElementById('urlInput');
  const loader = document.getElementById('loading');
  const outputBox = document.getElementById('outputBox');
  const statusBadge = document.getElementById('statusBadge');
  const url = input.value.trim();

  if (!url) {
    shakeInput(input);
    return;
  }

  // ── Show loading state ────────────────────────────────────────────
  loader.classList.add('active');
  outputBox.innerHTML = '';
  statusBadge.style.display = 'none';

  try {
    const csrfToken = getCookie('csrftoken');

    const response = await fetch('/summarize/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
      body: JSON.stringify({ url }),
    });

    const data = await response.json();

    if (!response.ok || data.error) {
      showError(data.error || 'Something went wrong. Please try again.');
      return;
    }

    renderSummary(data.summary);
    statusBadge.style.display = 'flex';

  } catch (err) {
    showError('Network error. Check your connection and try again.');
  } finally {
    loader.classList.remove('active');
  }
}


// ── Render the structured summary cards ──────────────────────────────
function renderSummary(s) {
  const box = document.getElementById('outputBox');

  const riskColors = {
    low:    { bg: '#e1f5ee', text: '#085041', dot: '#1d8e75' },
    medium: { bg: '#faeeda', text: '#633806', dot: '#BA7517' },
    high:   { bg: '#fcebeb', text: '#501313', dot: '#E24B4A' },
  };
  const risk = riskColors[s.risk_level] || riskColors.medium;

  const typeIcon = { warning: '⚠', good: '✓', info: 'i' };
  const typeBg   = { warning: '#faeeda', good: '#e1f5ee', info: '#e6f1fb' };
  const typeColor = { warning: '#633806', good: '#085041', info: '#0C447C' };

  const keyPointsHTML = (s.key_points || []).map(p => `
    <div class="kp-item">
      <div class="kp-icon" style="background:${typeBg[p.type]}; color:${typeColor[p.type]}">${typeIcon[p.type]}</div>
      <div>
        <div class="kp-title">${escHtml(p.title)}</div>
        <div class="kp-detail">${escHtml(p.detail)}</div>
      </div>
    </div>
  `).join('');

  const pillsHTML = (arr, color) => (arr || [])
    .map(item => `<span class="pill" style="background:${color.bg};color:${color.text}">${escHtml(item)}</span>`)
    .join('');

  box.innerHTML = `
    <div class="summary-header">
      <div>
        <div class="summary-site">${escHtml(s.site_name || 'Unknown site')}</div>
        <div class="summary-oneliner">${escHtml(s.one_liner || '')}</div>
      </div>
      <div class="risk-badge" style="background:${risk.bg}; color:${risk.text}">
        <span class="risk-dot" style="background:${risk.dot}"></span>
        ${s.risk_level?.toUpperCase() || 'UNKNOWN'} RISK
      </div>
    </div>

    <div class="watchout-box">
      <span class="watchout-label">⚡ Watch out</span>
      <span>${escHtml(s.watchout || '')}</span>
    </div>

    <div class="section-label" style="margin-top:1.25rem">Key clauses</div>
    <div class="kp-list">${keyPointsHTML}</div>

    <div class="two-col">
      <div>
        <div class="section-label">Data collected</div>
        <div class="pill-group">${pillsHTML(s.data_collected, { bg: '#fcebeb', text: '#501313' })}</div>
      </div>
      <div>
        <div class="section-label">Your rights</div>
        <div class="pill-group">${pillsHTML(s.user_rights, { bg: '#e1f5ee', text: '#085041' })}</div>
      </div>
    </div>
  `;
}


// ── Helpers ──────────────────────────────────────────────────────────
function showError(msg) {
  const box = document.getElementById('outputBox');
  box.innerHTML = `<div class="error-msg">
    <span style="font-size:18px">✕</span>
    <span>${escHtml(msg)}</span>
  </div>`;
}

function shakeInput(el) {
  el.style.animation = 'shake 0.35s ease';
  el.addEventListener('animationend', () => { el.style.animation = ''; }, { once: true });
}

function escHtml(str) {
  return String(str ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function getCookie(name) {
  const val = `; ${document.cookie}`;
  const parts = val.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return '';
}

// Enter key support
document.getElementById('urlInput')?.addEventListener('keydown', e => {
  if (e.key === 'Enter') summarize();
});