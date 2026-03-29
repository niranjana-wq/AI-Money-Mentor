const { formatINR, formatPct } = window.MentorUtils || {
  formatINR: v => '₹' + Math.round(v || 0).toLocaleString('en-IN'),
  formatPct: v => ((v || 0) * 100).toFixed(1) + '%',
};

const COLORS = {
  equity: '#1D9E75',
  debt:   '#534AB7',
  gold:   '#BA7517',
  cash:   '#888780',
};

const DIM_COLOR = {
  on_track:        '#1D9E75',
  needs_attention: '#BA7517',
  critical:        '#E24B4A',
};

// ── SVG Icons (no emojis) ──
const ICONS = {
  fire: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2c0 0-5 4-5 9a5 5 0 0 0 10 0c0-5-5-9-5-9z"/><path d="M12 12c0 0-2 1.5-2 3a2 2 0 0 0 4 0c0-1.5-2-3-2-3z"/></svg>`,
  score: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>`,
  tax: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="18" rx="2"/><line x1="8" y1="9" x2="16" y2="9"/><line x1="8" y1="13" x2="14" y2="13"/><line x1="8" y1="17" x2="11" y2="17"/></svg>`,
  target: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>`,
  microscope: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 18h8"/><path d="M3 22h18"/><path d="M14 22a7 7 0 1 0 0-14h-1"/><path d="M9 14l-2-7 7-2 2 7"/><path d="M9 14l-1 4"/></svg>`,
  couple: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="7" r="4"/><path d="M3 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2"/><circle cx="19" cy="7" r="2"/><path d="M23 21v-2a2 2 0 0 0-2-2h-2"/></svg>`,
  warning: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`,
  check: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`,
  trend_up: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>`,
  calendar: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>`,
  rupee: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="6" y1="3" x2="18" y2="3"/><line x1="6" y1="8" x2="18" y2="8"/><line x1="6" y1="13" x2="12" y2="21"/><path d="M6 8a6 6 0 0 0 0 12"/></svg>`,
  person: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M4 20v-2a8 8 0 0 1 16 0v2"/></svg>`,
  shield: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>`,
  split: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="3" x2="12" y2="21"/><polyline points="9 7 12 3 15 7"/><path d="M3 12h9"/><path d="M12 12h9"/></svg>`,
};

function scoreColor(score) {
  if (score >= 75) return '#1D9E75';
  if (score >= 50) return '#BA7517';
  return '#E24B4A';
}

function renderScoreRing(score, size = 140) {
  const r    = (size / 2) - 12;
  const c    = size / 2;
  const circ = 2 * Math.PI * r;
  const dash = (score / 100) * circ;
  const color = scoreColor(score);
  return `
    <div class="score-ring" style="width:${size}px;height:${size}px">
      <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
        <circle cx="${c}" cy="${c}" r="${r}" fill="none" stroke="#F0EEE9" stroke-width="10"/>
        <circle cx="${c}" cy="${c}" r="${r}" fill="none" stroke="${color}" stroke-width="10"
          stroke-dasharray="${dash.toFixed(1)} ${circ.toFixed(1)}"
          stroke-linecap="round" style="transition:stroke-dasharray 1.2s ease"/>
      </svg>
      <div class="score-ring__value">
        <span class="score-ring__number" style="color:${color}">${score}</span>
        <span class="score-ring__label">/ 100</span>
      </div>
    </div>`;
}

function renderDimensions(dimensions) {
  return Object.entries(dimensions).map(([key, dim]) => {
    const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    const color = DIM_COLOR[dim.status] || '#888';
    return `
      <div>
        <div class="dimension-row">
          <span class="dimension-label">${label}</span>
          <div class="dimension-track">
            <div class="dimension-fill" style="width:${dim.score}%;background:${color}"></div>
          </div>
          <span class="dimension-score" style="color:${color}">${dim.score}</span>
          <span class="risk-badge risk-badge--${dim.status}" style="margin-left:8px;font-size:11px">
            ${dim.status.replace(/_/g, ' ')}
          </span>
        </div>
        ${dim.fix ? `<div class="dimension-fix">${dim.fix}</div>` : ''}
      </div>`;
  }).join('');
}

function renderActions(actions) {
  if (!actions?.length) return '<p class="text-muted">No actions available</p>';
  return actions.map(a => `
    <div class="action-item">
      <div class="action-item__number">${a.priority}</div>
      <div class="action-item__body">
        <div class="action-item__text">${a.action}</div>
        <div class="action-item__sub">${a.impact || a.reason || ''}</div>
      </div>
      ${a.amount ? `<span class="action-item__amount">${formatINR(a.amount)}</span>` : ''}
    </div>`).join('');
}

function renderAllocation(allocation) {
  const total = Object.values(allocation).reduce((s, v) => s + (v || 0), 0);
  if (!total) return '';
  const segments = Object.entries(allocation).map(([k, v]) => ({
    key: k, pct: (v || 0) / total, color: COLORS[k] || '#888'
  }));
  let offset = 0;
  const size = 120, r = 40, c = size / 2;
  const strokes = segments.map(seg => {
    const circ = 2 * Math.PI * r;
    const dash = seg.pct * circ;
    const gap  = circ - dash;
    const rot  = offset * 360;
    offset += seg.pct;
    return `<circle cx="${c}" cy="${c}" r="${r}" fill="none" stroke="${seg.color}"
      stroke-width="20" stroke-dasharray="${dash.toFixed(1)} ${gap.toFixed(1)}"
      transform="rotate(${rot - 90} ${c} ${c})" stroke-linecap="butt"/>`;
  }).join('');
  const legend = segments.map(seg => `
    <div class="allocation-item">
      <div class="allocation-dot" style="background:${seg.color}"></div>
      <span class="allocation-item__label">${seg.key}</span>
      <span class="allocation-item__pct">${(seg.pct * 100).toFixed(0)}%</span>
    </div>`).join('');
  return `
    <div class="allocation-wrap">
      <svg width="${size}" height="${size}" style="flex-shrink:0">
        <circle cx="${c}" cy="${c}" r="${r}" fill="none" stroke="#F0EEE9" stroke-width="20"/>
        ${strokes}
      </svg>
      <div class="allocation-legend">${legend}</div>
    </div>`;
}

function renderSixMonthPlan(plan) {
  if (!plan?.length) return '';
  return plan.map(m => `
    <div class="month-item">
      <span class="month-item__num">${ICONS.calendar} Month ${m.month}</span>
      <div>
        <div class="month-item__focus">${m.focus}</div>
        <div class="month-item__target">${m.target}</div>
      </div>
    </div>`).join('');
}

function renderMentorInsight(text) {
  if (!text) return '';
  return `
    <div class="mentor-insight">
      <div class="mentor-insight__avatar">AI</div>
      <div class="mentor-insight__text">"${text}"</div>
    </div>`;
}

// ── FIRE Result ──
function renderFIREResult(data) {
  const ai   = data.result.ai_analysis || {};
  const calc = data.result.calculated  || {};
  const hs   = calc.health_score       || {};

  return `
    <div class="result-header">
      <div class="result-header__meta">FIRE Path Planner · Powered by Groq AI</div>
      <div class="result-header__title">Your financial independence roadmap</div>
      <div class="result-header__subtitle">Personalised analysis based on your profile</div>
    </div>
    <div class="result-grid">
      <div class="result-sidebar">
        <div class="card card--elevated" style="text-align:center;padding:32px 24px">
          <div class="section-title" style="justify-content:center">Money Health Score</div>
          ${renderScoreRing(hs.overall_score || 0)}
          <div style="margin-top:12px;font-size:20px;font-weight:800;color:var(--brand-green-dark)">
            ${hs.grade_label || ''}
          </div>
        </div>
        <div class="card">
          <div class="section-title">Asset allocation</div>
          ${ai.asset_allocation ? renderAllocation(ai.asset_allocation) : ''}
        </div>
        <div class="card">
          <div class="section-title">Key risks</div>
          ${(ai.risks || []).map(r => `
            <div class="action-item" style="margin-bottom:8px">
              <div class="action-item__number" style="background:var(--brand-red)">${ICONS.warning}</div>
              <div class="action-item__body">
                <div class="action-item__text" style="font-size:13px">${r}</div>
              </div>
            </div>`).join('')}
        </div>
      </div>
      <div class="result-main">
        <div class="card">
          <div class="section-title">FIRE numbers</div>
          <div class="stat-grid">
            <div class="stat-card stat-card--green">
              <div class="stat-card__label">Financial independence</div>
              <div class="stat-card__value">Age ${ai.fire_age || '—'}</div>
              <div class="stat-card__sub">${ai.years_to_fire || '—'} years away · ${ai.fire_year || ''}</div>
            </div>
            <div class="stat-card">
              <div class="stat-card__label">Corpus needed</div>
              <div class="stat-card__value">${formatINR(ai.corpus_needed)}</div>
              <div class="stat-card__sub">at 6% inflation</div>
            </div>
            <div class="stat-card">
              <div class="stat-card__label">Monthly SIP needed</div>
              <div class="stat-card__value">${formatINR(ai.monthly_sip_needed)}</div>
              <div class="stat-card__sub">currently ${formatINR(ai.current_monthly_sip)}</div>
            </div>
            <div class="stat-card ${(ai.sip_gap || 0) > 0 ? 'stat-card--amber' : 'stat-card--green'}">
              <div class="stat-card__label">Savings rate</div>
              <div class="stat-card__value">${formatPct(ai.savings_rate)}</div>
              <div class="stat-card__sub">target ${formatPct(ai.target_savings_rate)}</div>
            </div>
          </div>
          <div class="gap-highlight">
            <span class="gap-highlight__label">Monthly investment gap</span>
            <span class="gap-highlight__value">${formatINR(ai.sip_gap)} short</span>
          </div>
        </div>
        <div class="card">
          <div class="section-title">Top actions this month</div>
          <div class="action-list">${renderActions(ai.top_actions)}</div>
        </div>
        <div class="card">
          <div class="section-title">6-month roadmap</div>
          <div class="month-plan">${renderSixMonthPlan(ai.six_month_plan)}</div>
        </div>
        ${renderMentorInsight(ai.mentor_insight)}
      </div>
    </div>`;
}

// ── Health Score Result ──
function renderScoreResult(data) {
  const ai   = data.result.ai_analysis || {};
  const dims = ai.dimensions || {};
  return `
    <div class="result-header">
      <div class="result-header__meta">Money Health Score · Powered by Groq AI</div>
      <div class="result-header__title">Your financial wellness report</div>
    </div>
    <div class="result-grid">
      <div class="result-sidebar">
        <div class="card card--elevated" style="text-align:center;padding:32px 24px">
          <div class="section-title" style="justify-content:center">Overall score</div>
          ${renderScoreRing(ai.overall_score || 0)}
          <div style="margin-top:12px;font-size:22px;font-weight:800;color:var(--brand-green-dark)">
            ${ai.grade || ''} — ${ai.grade_label || ''}
          </div>
        </div>
        <div class="card card--amber">
          <div class="section-title">Top priority</div>
          <p style="font-size:14px;color:var(--text-primary);line-height:1.6">${ai.top_priority || ''}</p>
        </div>
      </div>
      <div class="result-main">
        <div class="card">
          <div class="section-title">Score breakdown</div>
          <div class="dimension-list">${renderDimensions(dims)}</div>
        </div>
        ${renderMentorInsight(ai.mentor_insight)}
      </div>
    </div>`;
}

// ── Tax Result ──
function renderTaxResult(data) {
  const ai = data.result.ai_analysis || {};
  return `
    <div class="result-header">
      <div class="result-header__meta">Tax Wizard · Powered by Groq AI · FY 2024-25</div>
      <div class="result-header__title">Your tax optimisation report</div>
    </div>
    <div class="result-grid">
      <div class="result-sidebar">
        <div class="card card--elevated" style="text-align:center;padding:28px">
          <div class="section-title" style="justify-content:center">Recommended regime</div>
          <div style="font-size:28px;font-weight:800;color:var(--brand-green-dark);text-transform:uppercase;margin:12px 0">
            ${ai.recommended_regime || '—'} regime
          </div>
          <p style="font-size:13px;color:var(--text-muted)">${ai.regime_reasoning || ''}</p>
          <div style="margin-top:16px;padding:14px;background:var(--brand-green-light);border-radius:var(--radius-md)">
            <div style="font-size:11px;font-weight:700;color:var(--brand-green-dark);text-transform:uppercase">You save</div>
            <div style="font-size:28px;font-weight:800;color:var(--brand-green-dark)">${formatINR(ai.tax_saving)}</div>
          </div>
        </div>
        <div class="card">
          <div class="section-title">Regime comparison</div>
          <div class="stat-grid" style="grid-template-columns:1fr 1fr">
            <div class="stat-card">
              <div class="stat-card__label">Old regime</div>
              <div class="stat-card__value" style="font-size:18px">${formatINR(ai.old_regime?.tax_payable)}</div>
              <div class="stat-card__sub">${formatPct(ai.old_regime?.effective_rate)} eff. rate</div>
            </div>
            <div class="stat-card">
              <div class="stat-card__label">New regime</div>
              <div class="stat-card__value" style="font-size:18px">${formatINR(ai.new_regime?.tax_payable)}</div>
              <div class="stat-card__sub">${formatPct(ai.new_regime?.effective_rate)} eff. rate</div>
            </div>
          </div>
        </div>
      </div>
      <div class="result-main">
        <div class="card">
          <div class="section-title">Missed deductions</div>
          ${(ai.missed_deductions || []).map(d => `
            <div class="action-item" style="margin-bottom:10px">
              <div class="action-item__number" style="background:var(--brand-amber);border-radius:6px;padding:4px 6px;font-size:10px;width:auto">${d.section}</div>
              <div class="action-item__body">
                <div class="action-item__text">${d.description}</div>
                <div class="action-item__sub">Max: ${formatINR(d.max_limit)} · Used: ${formatINR(d.currently_used)}</div>
              </div>
              <span class="action-item__amount" style="background:var(--brand-amber-light);color:var(--brand-amber)">
                Save ${formatINR(d.potential_saving)}
              </span>
            </div>`).join('')}
        </div>
        <div class="card">
          <div class="section-title">Recommended investments</div>
          <div class="action-list">
            ${(ai.recommended_investments || []).map(inv => `
              <div class="action-item">
                <div class="action-item__number" style="background:var(--brand-purple)">${ICONS.rupee}</div>
                <div class="action-item__body">
                  <div class="action-item__text">${inv.instrument}</div>
                  <div class="action-item__sub">${inv.reason}</div>
                </div>
                <span class="action-item__amount">${formatINR(inv.amount)}</span>
              </div>`).join('')}
          </div>
        </div>
        ${renderMentorInsight(ai.mentor_insight)}
      </div>
    </div>`;
}

// ── Couples Result ──
function renderCouplesResult(data) {
  const ai = data.result.ai_analysis || {};
  const hra  = ai.hra_optimization       || {};
  const nps  = ai.nps_recommendation     || {};
  const ins  = ai.insurance_recommendation || {};
  const sips = ai.sip_split              || [];
  const goals = ai.joint_goals           || [];

  return `
    <div class="result-header">
      <div class="result-header__meta">Couple's Money Planner · Powered by Groq AI</div>
      <div class="result-header__title">Your joint financial optimisation report</div>
      <div class="result-header__subtitle">Combined income · tax efficiency · shared goals</div>
    </div>

    <div class="result-grid">
      <div class="result-sidebar">

        <div class="card card--elevated">
          <div class="section-title">Combined overview</div>
          <div class="stat-grid" style="grid-template-columns:1fr">
            <div class="stat-card stat-card--green">
              <div class="stat-card__label">Combined monthly income</div>
              <div class="stat-card__value">${formatINR(ai.combined_income)}</div>
            </div>
            <div class="stat-card">
              <div class="stat-card__label">Combined savings rate</div>
              <div class="stat-card__value">${formatPct(ai.combined_savings_rate)}</div>
            </div>
            <div class="stat-card stat-card--green">
              <div class="stat-card__label">Combined net worth</div>
              <div class="stat-card__value">${formatINR(ai.combined_net_worth)}</div>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="section-title">${ICONS.shield} Insurance plan</div>
          <div style="padding:14px;background:var(--bg-secondary);border-radius:var(--radius-md);margin-bottom:10px">
            <div style="font-size:12px;color:var(--text-muted);margin-bottom:4px">Recommendation</div>
            <div style="font-size:14px;font-weight:600;color:var(--text-primary);text-transform:capitalize">${ins.joint_vs_individual || '—'} insurance</div>
            <div style="font-size:12px;color:var(--text-muted);margin-top:4px">${ins.reasoning || ''}</div>
          </div>
          <div class="stat-grid" style="grid-template-columns:1fr 1fr">
            <div class="stat-card">
              <div class="stat-card__label">${ICONS.person} Partner 1 cover</div>
              <div class="stat-card__value" style="font-size:16px">${formatINR(ins.partner1_cover)}</div>
            </div>
            <div class="stat-card">
              <div class="stat-card__label">${ICONS.person} Partner 2 cover</div>
              <div class="stat-card__value" style="font-size:16px">${formatINR(ins.partner2_cover)}</div>
            </div>
          </div>
        </div>

      </div>

      <div class="result-main">

        <div class="card">
          <div class="section-title">${ICONS.rupee} HRA optimisation</div>
          <div style="display:flex;align-items:center;justify-content:space-between;padding:16px;background:var(--brand-green-light);border-radius:var(--radius-md)">
            <div>
              <div style="font-size:13px;color:var(--brand-green-dark);font-weight:600">
                ${hra.recommended_claimant === 'partner1' ? 'Partner 1' : hra.recommended_claimant === 'partner2' ? 'Partner 2' : 'Both partners'} should claim HRA
              </div>
              <div style="font-size:12px;color:var(--brand-green-dark);margin-top:3px;opacity:0.8">${hra.reasoning || ''}</div>
            </div>
            <div style="text-align:right;flex-shrink:0;margin-left:16px">
              <div style="font-size:11px;color:var(--brand-green-dark);font-weight:600;text-transform:uppercase">Annual saving</div>
              <div style="font-size:22px;font-weight:800;color:var(--brand-green-dark)">${formatINR(hra.annual_saving)}</div>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="section-title">${ICONS.rupee} NPS contribution plan</div>
          <div class="stat-grid" style="grid-template-columns:1fr 1fr 1fr">
            <div class="stat-card">
              <div class="stat-card__label">Partner 1 NPS</div>
              <div class="stat-card__value" style="font-size:18px">${formatINR(nps.partner1_contribution)}</div>
              <div class="stat-card__sub">per year</div>
            </div>
            <div class="stat-card">
              <div class="stat-card__label">Partner 2 NPS</div>
              <div class="stat-card__value" style="font-size:18px">${formatINR(nps.partner2_contribution)}</div>
              <div class="stat-card__sub">per year</div>
            </div>
            <div class="stat-card stat-card--green">
              <div class="stat-card__label">Combined tax saving</div>
              <div class="stat-card__value" style="font-size:18px">${formatINR(nps.combined_tax_saving)}</div>
              <div class="stat-card__sub">via NPS</div>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="section-title">${ICONS.split} SIP allocation by goal</div>
          <div style="display:flex;flex-direction:column;gap:10px">
            ${sips.map(s => `
              <div style="padding:14px 16px;background:var(--bg-secondary);border-radius:var(--radius-md);border-left:3px solid var(--brand-green)">
                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
                  <span style="font-size:14px;font-weight:600;color:var(--text-primary);text-transform:capitalize">${s.goal?.replace(/_/g,' ')}</span>
                  <span style="font-size:14px;font-weight:700;color:var(--brand-green-dark)">${formatINR(s.total_sip)}/mo</span>
                </div>
                <div style="display:flex;gap:16px">
                  <div style="font-size:12px;color:var(--text-muted)">
                    ${ICONS.person} Partner 1: <strong style="color:var(--text-primary)">${formatINR(s.partner1_sip)}</strong>
                  </div>
                  <div style="font-size:12px;color:var(--text-muted)">
                    ${ICONS.person} Partner 2: <strong style="color:var(--text-primary)">${formatINR(s.partner2_sip)}</strong>
                  </div>
                </div>
                <div style="font-size:12px;color:var(--text-muted);margin-top:4px">${s.reason || ''}</div>
              </div>`).join('')}
          </div>
        </div>

        ${goals.length ? `
        <div class="card">
          <div class="section-title">${ICONS.target} Joint financial goals</div>
          <div style="display:flex;flex-direction:column;gap:10px">
            ${goals.map(g => `
              <div class="month-item">
                <span class="month-item__num" style="width:60px;font-size:11px">${g.target_year || ''}</span>
                <div style="flex:1">
                  <div class="month-item__focus" style="text-transform:capitalize">${g.goal?.replace(/_/g,' ')}</div>
                  <div class="month-item__target">${formatINR(g.target_amount)} · SIP ${formatINR(g.monthly_sip)}/mo</div>
                </div>
              </div>`).join('')}
          </div>
        </div>` : ''}

        ${renderMentorInsight(ai.mentor_insight)}

      </div>
    </div>`;
}

// ── Life Event Result ──
function renderLifeEventResult(data) {
  const ai = data.result.ai_analysis || {};
  return `
    <div class="result-header">
      <div class="result-header__meta">Life Event Advisor · Powered by AI</div>
      <div class="result-header__title">Your ${(ai.event_type || 'life event').replace(/_/g,' ')} financial plan</div>
      <div class="result-header__subtitle">${ai.summary || ''}</div>
    </div>
    <div class="result-grid">
      <div class="result-sidebar">
        <div class="card card--elevated">
          <div class="section-title">Allocation plan</div>
          ${(ai.allocation_plan || []).map(a => `
            <div style="margin-bottom:12px">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
                <span style="font-size:13px;font-weight:600;text-transform:capitalize;color:var(--text-primary)">${a.bucket}</span>
                <span style="font-size:13px;font-weight:700;color:var(--brand-green-dark)">${formatINR(a.amount)}</span>
              </div>
              <div style="height:6px;background:var(--bg-tertiary);border-radius:3px;overflow:hidden">
                <div style="height:100%;width:${(a.percentage * 100).toFixed(0)}%;background:var(--brand-green);border-radius:3px"></div>
              </div>
              <div style="font-size:11px;color:var(--text-muted);margin-top:3px">${a.instrument}</div>
            </div>`).join('')}
        </div>
        <div class="card card--red">
          <div class="section-title">Risks to avoid</div>
          ${(ai.risks_to_avoid || []).map(r => `
            <div class="action-item" style="margin-bottom:8px">
              <div class="action-item__number" style="background:var(--brand-red)">${ICONS.warning}</div>
              <div class="action-item__body">
                <div class="action-item__text" style="font-size:13px">${r}</div>
              </div>
            </div>`).join('')}
        </div>
      </div>
      <div class="result-main">
        <div class="card">
          <div class="section-title">Immediate actions</div>
          <div class="action-list">
            ${(ai.immediate_actions || []).map(a => `
              <div class="action-item">
                <div class="action-item__number">${a.priority}</div>
                <div class="action-item__body">
                  <div class="action-item__text">${a.action}</div>
                  <div class="action-item__sub">${a.deadline || ''} · ${a.reason || ''}</div>
                </div>
                ${a.amount ? `<span class="action-item__amount">${formatINR(a.amount)}</span>` : ''}
              </div>`).join('')}
          </div>
        </div>
        ${renderMentorInsight(ai.mentor_insight)}
      </div>
    </div>`;
}

// ── Bootstrap ──
document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('resultContainer');
  if (!container) return;

  const raw = sessionStorage.getItem('mentorResult');
  if (!raw) {
    container.innerHTML = `
      <div class="state-empty">
        <div class="state-empty__icon">${ICONS.target}</div>
        <div class="state-empty__title">No analysis found</div>
        <div class="state-empty__sub" style="margin-top:16px">
          <a href="index.html" class="btn btn--primary">Start a new analysis</a>
        </div>
      </div>`;
    return;
  }

  try {
    const data = JSON.parse(raw);
    const renderers = {
      fire:       renderFIREResult,
      score:      renderScoreResult,
      tax:        renderTaxResult,
      couples:    renderCouplesResult,
      life_event: renderLifeEventResult,
    };
    const renderer = renderers[data.feature] || renderFIREResult;
    container.innerHTML = renderer(data);
  } catch (e) {
    container.innerHTML = `
      <div class="state-empty">
        <div class="state-empty__title">Error rendering results</div>
        <div class="state-empty__sub">${e.message}</div>
        <a href="index.html" class="btn btn--primary" style="margin-top:16px">Try again</a>
      </div>`;
  }
});