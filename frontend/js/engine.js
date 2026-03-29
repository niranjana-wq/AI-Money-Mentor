const API_BASE = (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost')
  ? 'http://127.0.0.1:8000'
  : 'https://ai-money-mentor-backend.onrender.com';

const LOADING_MESSAGES = [
  'Crunching your FIRE numbers...',
  'Analysing 6 financial dimensions...',
  'Consulting the AI mentor...',
  'Building your personalised roadmap...',
  'Almost there...',
];

function showLoading() {
  const overlay = document.getElementById('loadingOverlay');
  const text    = document.getElementById('loadingText');
  if (!overlay) return;
  overlay.classList.add('active');
  let i = 0;
  const interval = setInterval(() => {
    if (text) text.textContent = LOADING_MESSAGES[i % LOADING_MESSAGES.length];
    i++;
  }, 2200);
  overlay._interval = interval;
}

function hideLoading() {
  const overlay = document.getElementById('loadingOverlay');
  if (!overlay) return;
  overlay.classList.remove('active');
  clearInterval(overlay._interval);
}

function showToast(message, type = '') {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = message;
  toast.className   = `toast show ${type}`;
  setTimeout(() => { toast.className = 'toast'; }, 3500);
}

function formatINR(amount) {
  if (!amount && amount !== 0) return '—';
  const n = Math.round(amount);
  if (n >= 10000000) return '₹' + (n / 10000000).toFixed(1) + ' Cr';
  if (n >= 100000)   return '₹' + (n / 100000).toFixed(1) + ' L';
  if (n >= 1000)     return '₹' + (n / 1000).toFixed(1) + 'K';
  return '₹' + n.toLocaleString('en-IN');
}

function formatPct(val) {
  if (val === null || val === undefined) return '—';
  return (val * 100).toFixed(1) + '%';
}

async function callAPI(endpoint, data) {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `API error ${res.status}`);
  }
  return res.json();
}

function getFeatureFromURL() {
  return new URLSearchParams(window.location.search).get('feature') || 'fire';
}

function autofillSavings() {
  const income   = parseFloat(document.getElementById('monthly_income')?.value) || 0;
  const expenses = parseFloat(document.getElementById('monthly_expenses')?.value) || 0;
  const savings  = document.getElementById('monthly_savings');
  if (savings && income > expenses) savings.value = income - expenses;
}

function configureFormForFeature(feature) {
  const titles = {
    fire:       ['FIRE Path Planner', 'Build your complete roadmap to financial independence'],
    score:      ['Money Health Score', 'Get your financial wellness score across 6 dimensions'],
    tax:        ['Tax Wizard', 'Find every deduction you are missing this year'],
    life_event: ['Life Event Advisor', 'Get advice tailored to your specific financial event'],
    couples:    ["Couple's Money Planner", 'Optimise finances across both incomes'],
  };
  const [title, subtitle] = titles[feature] || titles.fire;
  const t = document.getElementById('formTitle');
  const s = document.getElementById('formSubtitle');
  if (t) t.textContent = title;
  if (s) s.textContent = subtitle;

  if (feature === 'life_event') {
    const le = document.getElementById('lifeEventSection');
    const gs = document.getElementById('goalsSection');
    if (le) le.style.display = 'block';
    if (gs) gs.style.display = 'none';
  }
}

function validateForm() {
  const required = ['monthly_income', 'monthly_expenses', 'age'];
  let valid = true;
  required.forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    if (!el.value || isNaN(el.value) || Number(el.value) <= 0) {
      el.classList.add('error');
      valid = false;
    } else {
      el.classList.remove('error');
    }
  });
  return valid;
}

function collectFormData() {
  const g = id => parseFloat(document.getElementById(id)?.value) || 0;
  const s = id => document.getElementById(id)?.value || '';
  const goals = Array.from(document.querySelectorAll('input[name="goals"]:checked')).map(c => c.value);
  return {
    age:                    Math.round(g('age')),
    monthly_income:         g('monthly_income'),
    monthly_expenses:       g('monthly_expenses'),
    monthly_savings:        g('monthly_savings') || g('monthly_income') - g('monthly_expenses'),
    existing_investments:   g('existing_investments'),
    existing_sip:           g('existing_sip'),
    emergency_fund:         g('emergency_fund'),
    total_debt_emi:         g('total_debt_emi'),
    life_insurance_cover:   g('life_insurance_cover'),
    health_insurance_cover: g('health_insurance_cover'),
    tax_saving_investments: g('tax_saving_investments'),
    gross_annual_salary:    g('gross_annual_salary'),
    risk_profile:           s('risk_profile') || 'moderate',
    city:                   s('city_type') || 'metro',
    city_type:              s('city_type') || 'metro',
    goals,
    event_type:    s('event_type'),
    event_amount:  g('event_amount'),
    event_details: s('event_details'),
  };
}

function getEndpointForFeature(feature) {
  const map = {
    fire:       '/api/fire',
    score:      '/api/score',
    tax:        '/api/tax',
    life_event: '/api/life-event',
    couples:    '/api/couples',
  };
  return map[feature] || '/api/fire';
}

// ── Main Form Handler ──
const form = document.getElementById('mainForm');
if (form) {
  const income   = document.getElementById('monthly_income');
  const expenses = document.getElementById('monthly_expenses');
  if (income)   income.addEventListener('input', autofillSavings);
  if (expenses) expenses.addEventListener('input', autofillSavings);

  const feature = getFeatureFromURL();
  configureFormForFeature(feature);

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!validateForm()) {
      showToast('Please fill in all required fields', 'error');
      return;
    }

    const data     = collectFormData();
    const endpoint = getEndpointForFeature(feature);

    showLoading();
    document.getElementById('submitBtn').classList.add('btn--loading');

    try {
      const result = await callAPI(endpoint, data);
      sessionStorage.setItem('mentorResult', JSON.stringify({ feature, data, result }));
      window.location.href = 'result.html';
    } catch (err) {
      hideLoading();
      document.getElementById('submitBtn').classList.remove('btn--loading');
      showToast('Something went wrong. Please try again.', 'error');
      console.error(err);
    }
  });
}

// Export helpers for render.js
window.MentorUtils = { formatINR, formatPct, showToast };

// Wake up Render backend on page load
(async () => {
  try { await fetch(`${API_BASE}/api/health`); } catch (_) {}
})();