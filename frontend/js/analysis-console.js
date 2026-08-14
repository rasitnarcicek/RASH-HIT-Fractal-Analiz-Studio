/**
 * RASH-HIT Fractal Studio - Scientific Analysis Console Controller
 * STRICT RULE: No direct fetch/XHR calls. Interacts with backend purely via API object in api.js.
 */

let currentPollJobId = null;
let pollTimer = null;
let isPollingJob = false;
let knownScaleRowLevels = new Set();
let showTechnicalScaleColumns = false;
let lastRenderedStepHash = "";
let lastRenderedLogCount = 0;
// Last job payload rendered by the console, so the open console can be
// re-rendered from the cached payload without re-polling.
let lastPolledJob = null;

function perfLog(name, startTimeMs) {
  // Debug features removed
}

function formatLvl(lvl) {
  if (lvl == null) return '';
  const s = String(lvl).trim();
  const m = s.match(/^L+(\d+)$/i);
  if (m) return 'L' + String(parseInt(m[1], 10)).padStart(2, '0');
  const num = parseInt(s, 10);
  if (!isNaN(num)) return 'L' + String(num).padStart(2, '0');
  return s;
}

function toggleTechnicalScaleColumns(showTech) {
  showTechnicalScaleColumns = !!showTech;
  const cb = document.getElementById('chkShowTechnicalScaleColumns');
  if (cb) cb.checked = showTechnicalScaleColumns;
  document.querySelectorAll('.scale-tech-col').forEach(el => {
    if (showTechnicalScaleColumns) {
      el.classList.remove('is-hidden');
    } else {
      el.classList.add('is-hidden');
    }
  });
}

function openAnalysisConsole(jobId, mode, initialFile) {
  currentPollJobId = jobId;
  knownScaleRowLevels.clear();
  lastRenderedStepHash = "";
  lastRenderedLogCount = 0;

  const modal = document.getElementById('scientificConsoleModal');
  if (modal) {
    modal._prevFocus = document.activeElement;  // ISSUE-011
    modal.classList.add('open');
  }

  const statusPanel = document.getElementById('consoleStatusPanel');
  if (statusPanel) { statusPanel.classList.remove('is-success', 'is-error'); statusPanel.classList.add('is-running'); }

  document.getElementById('consoleJobId').textContent = jobId || 'N/A';
  document.getElementById('consoleMode').textContent = (mode || 'single').toUpperCase();
  document.getElementById('consoleCurrentFile').textContent = initialFile || 'Initializing…';
  document.getElementById('consoleStatusChip').textContent = 'RUNNING';
  document.getElementById('consoleStatusChip').className = 'badge badge-warn';
  
  // Clear previous live table rows and logs
  document.getElementById('liveScaleTableBody').innerHTML = '<tr><td colspan="16" style="text-align:center;color:var(--muted);padding:14px;">' + 'Awaiting level computation metrics…' + '</td></tr>';
  document.getElementById('consoleEventLog').innerHTML = '';
  document.getElementById('finalConsoleActions').style.display = 'none';

  startJobPolling(jobId);
}

function openScientificConsole() {
  openAnalysisConsole(currentPollJobId);
}

function closeAnalysisConsole() {
  stopJobPolling();
  const modal = document.getElementById('scientificConsoleModal');
  if (modal) modal.classList.remove('open');
  if (modal && modal._prevFocus && typeof modal._prevFocus.focus === 'function') {
    modal._prevFocus.focus();  // ISSUE-011: restore focus on close
  }
  const statusPanel = document.getElementById('consoleStatusPanel');
  if (statusPanel) statusPanel.classList.remove('is-running', 'is-success', 'is-error');
}

function startJobPolling(jobId) {
  stopJobPolling();
  pollJobStatus();
  pollTimer = setInterval(pollJobStatus, 500);
}

function stopJobPolling() {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
}

async function pollJobStatus() {
  if (!currentPollJobId || isPollingJob) return;
  isPollingJob = true;
  const t0 = performance.now();

  try {
    const job = await API.getJobStatus(currentPollJobId);
    if (!job || job.error) return;
    lastPolledJob = job;

    // Normalize status strings
    const rawStatus = (job.status || 'running').toLowerCase();
    const isSuccess = ['success', 'done', 'complete', 'completed'].includes(rawStatus);
    const isFailed = ['failed', 'error'].includes(rawStatus);

    renderLiveStreamBanner(job, isSuccess, isFailed);
    renderConsoleTopPanel(job);
    renderConsoleSteps(job.steps || [], job.current_step, isSuccess, isFailed);
    renderConsoleScaleRows(job.scale_rows || [], job.requested_levels || 7, job.current_level || 0, isSuccess, isFailed, job);
    renderConsoleRegression(job.regression || {});
    renderConsoleBatchQueue(job.batch_queue || []);
    renderConsoleLogs(job.logs || []);

    if (isSuccess) {
      stopJobPolling();
      onJobCompletedSuccess(job);
    } else if (isFailed) {
      stopJobPolling();
      onJobCompletedFailed(job);
    }
  } catch (err) {
    // Suppress transient poll errors silently
  } finally {
    isPollingJob = false;
    perfLog(`pollJobStatus (${currentPollJobId})`, t0);
  }
}

function renderLiveStreamBanner(job, isSuccess, isFailed) {
  const banner = document.getElementById('liveStreamBanner');
  const title = document.getElementById('liveStreamTitle');
  const sub = document.getElementById('liveStreamSub');
  if (!banner) return;

  if (isSuccess || isFailed) {
    banner.classList.remove('active');
    return;
  }

  banner.classList.add('active');
  if (title) title.textContent = 'Analysis Job Running — ' + (job.current_file || 'Processing…');
  if (sub) sub.textContent = 'Current Step: ' + (job.current_step || 'Computing') + ' (Level ' + (job.current_level || 0) + '/' + (job.requested_levels || 7) + ')';
}

function renderConsoleTopPanel(job) {
  document.getElementById('consoleCurrentFile').textContent = job.current_file || 'N/A';
  document.getElementById('consoleElapsed').textContent = formatElapsed(job.elapsed_seconds || 0);

  const stepEl = document.getElementById('consoleCurrentStep');
  if (stepEl) {
    const currLevelStr = job.current_level ? ' (Level ' + job.current_level + '/' + (job.requested_levels || 7) + ')' : '';
    stepEl.innerHTML = `<span class="console-spinner" style="margin-right:6px;"></span>${escapeHtml(job.current_step || 'Processing')}${currLevelStr}`;
  }
  
  const chip = document.getElementById('consoleStatusChip');
  if (chip) {
    const rawSt = (job.status || 'running').toLowerCase();
    const isOk = ['success', 'done', 'complete', 'completed'].includes(rawSt);
    const isErr = ['failed', 'error'].includes(rawSt);
    
    chip.textContent = isOk ? 'SUCCESS' : isErr ? 'FAILED' : 'RUNNING';
    chip.className = 'badge ' + (isOk ? 'badge-ok' : isErr ? 'badge-missing' : 'badge-warn');
  }

  const pBar = document.getElementById('consoleProgressBar');
  if (pBar) {
    const total = job.requested_levels || 7;
    const curr = job.current_level || 0;
    const rawSt = (job.status || '').toLowerCase();
    const isOk = ['success', 'done', 'complete', 'completed'].includes(rawSt);
    const pct = isOk ? 100 : Math.min(99, Math.round((curr / total) * 100));
    pBar.style.width = pct + '%';
  }
}

function renderConsoleSteps(steps, currentStep, isSuccess, isFailed) {
  const container = document.getElementById('consoleStepsTimeline');
  if (!container) return;

  if (!steps || steps.length === 0) {
    container.innerHTML = '<div style="color:var(--muted);font-size:11px;">' + 'Initializing execution steps…' + '</div>';
    return;
  }

  const hash = steps.map(s => `${s.name}:${s.status}:${s.started_at || ''}:${s.finished_at || ''}`).join('|');
  if (hash === lastRenderedStepHash) return;
  lastRenderedStepHash = hash;

  const t0 = performance.now();
  container.innerHTML = steps.map((st, idx) => {
    const rawSt = (st.status || 'waiting').toLowerCase();
    let stateClass = 'is-waiting';
    let icon = '⏳';
    let badgeClass = 'badge-warn';

    if (rawSt === 'done' || rawSt === 'success' || rawSt === 'complete') {
      stateClass = 'is-done'; icon = '✅'; badgeClass = 'badge-ok';
    } else if (rawSt === 'failed' || rawSt === 'error') {
      stateClass = 'is-failed'; icon = '❌'; badgeClass = 'badge-missing';
    } else if (rawSt === 'running') {
      stateClass = 'is-running'; icon = '🔄'; badgeClass = 'badge-warn';
    }

    const timeStr = st.finished_at ? `[${st.finished_at}]` : st.started_at ? `[${st.started_at}]` : '';
    const prefix = /^\d+\.\s/.test(st.name || '') ? '' : (idx + 1) + '. ';
    const statusText = rawSt === 'done' || rawSt === 'success' || rawSt === 'complete'
      ? 'DONE'
      : rawSt === 'failed' || rawSt === 'error' ? 'FAILED'
      : rawSt === 'running' ? 'RUNNING'
      : 'WAITING';

    return `
      <div class="console-step-item ${stateClass}">
        <span style="font-size:12px;">${icon}</span>
        <span style="flex:1;"><b>${prefix}${escapeHtml(st.name)}</b></span>
        <span style="color:var(--muted);font-family:monospace;font-size:10px;">${timeStr} <span class="badge ${badgeClass}">${statusText}</span></span>
      </div>
    `;
  }).join('');
  perfLog('renderConsoleSteps', t0);
}

/**
 * Build the Phase 8 NegSpace cell tooltip: the per-level negative-space cache
 * metrics (children of empty parents never evaluated) plus the package-level
 * Phase 8 policy summary (cells-omitted / row-run markers from final_package).
 */
function buildPhase8Tooltip(r, job) {
  const lines = [];
  const fp = (job && job.final_package) || {};

  // Per-level actuals (from the real _build_scale_row job stream).
  const pruned = r && r.negative_space_cached_cells;
  const skipped = r && r.empty_parents_skipped;
  if (pruned != null || skipped != null) {
    lines.push('Phase 8 negative-space cache (this level):');
    if (pruned != null) lines.push('  child cells pruned: ' + Number(pruned).toLocaleString());
    if (skipped != null) lines.push('  empty parents skipped: ' + Number(skipped).toLocaleString());
    if (r.candidate_count != null) {
      lines.push('  candidates: ' + Number(r.candidate_count).toLocaleString()
        + ' (active parents: ' + Number(r.active_parent_count || 0).toLocaleString()
        + ', empty: ' + Number(r.empty_candidate_count || 0).toLocaleString() + ')');
    }
    if (r.cell_storage_mode) lines.push('  cell storage: ' + r.cell_storage_mode);
    if (r.output_policy_note) lines.push('  policy note: ' + r.output_policy_note);
  } else {
    lines.push('Phase 8 negative-space cache: child cells of empty parents never evaluated at this level');
  }

  // Package-level RASH-HIT Engine markers (from job.final_package).
  const omitted = Array.isArray(fp.rh_engine_cells_omitted_levels) ? fp.rh_engine_cells_omitted_levels : [];
  const rowRuns = Array.isArray(fp.rh_engine_row_run_levels) ? fp.rh_engine_row_run_levels : [];
  if (omitted.length || rowRuns.length) {
    lines.push('Package RASH-HIT policy:');
    if (omitted.length) {
      lines.push('  per-cell data omitted at: ' + omitted.map(l => formatLvl(l)).join(', '));
    }
    if (rowRuns.length) {
      lines.push('  row-run SVG maps at: ' + rowRuns.map(l => formatLvl(l)).join(', '));
    }
  }
  return lines.join('\n');
}

function renderConsoleScaleRows(realRows, requestedLevels, currentLevel, isSuccess, isFailed, job) {
  const tbody = document.getElementById('liveScaleTableBody');
  if (!tbody) return;
  const t0 = performance.now();

  const total = Math.max(requestedLevels || 7, realRows ? realRows.length : 0);
  // Level currently being computed = the first level after the last completed
  // one. Mirrors analysis-page.js renderStreamScaleRows (the "Computing…" row).
  const computingLevel = isSuccess ? null : (currentLevel < total ? currentLevel + 1 : null);
  const rowMap = new Map();
  (realRows || []).forEach(r => {
    const lvlNum = r.level != null ? r.level : (r.grid_level != null ? r.grid_level : 0);
    rowMap.set(lvlNum, r);
  });

  const techHiddenCls = showTechnicalScaleColumns ? '' : 'is-hidden';
  let html = '';
  for (let i = 1; i <= total; i++) {
    const r = rowMap.get(i);
    const lvlCode = 'L' + String(i).padStart(2, '0');
    const isNew = r && !knownScaleRowLevels.has(i);
    if (r) knownScaleRowLevels.add(i);

    const flashClass = isNew ? 'is-new' : '';

    if (r) {
      const filled = r.occupied_count != null ? r.occupied_count : 'N/A';
      const totCells = r.total_count != null ? r.total_count : 'N/A';
      const empty = r.empty_count != null ? r.empty_count : (r.total_count != null && r.occupied_count != null ? r.total_count - r.occupied_count : 'N/A');
      const occ_pct = r.occupancy_percent != null ? parseFloat(r.occupancy_percent).toFixed(2) + '%' : 'N/A';
      const cellSize = (r.box_size_w && r.box_size_h) ? `${r.box_size_w} x ${r.box_size_h}` : 'N/A';
      const duration = r.duration_seconds != null ? parseFloat(r.duration_seconds).toFixed(3) + 's' : 'N/A';
      const fitStatus = r.included_in_fit !== false ? '<b>' + 'Fit' + '</b>' : `<b title="${escapeHtml(r.exclusion_reason || 'Excluded')}">${'Excluded'}</b>`;

      html += `
        <tr class="scale-row is-done ${flashClass}">
          <td><b>${lvlCode}</b></td>
          <td><code>${escapeHtml(r.grid_label || (r.box_size_w ? `${r.box_size_w}x${r.box_size_h}` : 'N/A'))}</code></td>
          <td class="num"><b>${totCells}</b></td>
          <td class="num"><b>${filled}</b></td>
          <td class="num">${empty}</td>
          <td class="num"><b>${occ_pct}</b></td>
          <td><code>${cellSize}</code></td>
          <td class="num">${duration}</td>
          <td>${fitStatus}</td>
          <td><b>${String(r.status || 'DONE').toLowerCase() === 'done' ? 'DONE' : String(r.status || '').toUpperCase()}</b></td>
          <td class="num scale-tech-col ${techHiddenCls}">${r.box_size_w || 'N/A'}</td>
          <td class="num scale-tech-col ${techHiddenCls}">${r.box_size_h || 'N/A'}</td>
          <td class="num scale-tech-col ${techHiddenCls}">${r.inv_box_size != null ? parseFloat(r.inv_box_size).toFixed(4) : 'N/A'}</td>
          <td class="num scale-tech-col ${techHiddenCls}">${r.log_inv_r != null ? parseFloat(r.log_inv_r).toFixed(4) : 'N/A'}</td>
          <td class="num scale-tech-col ${techHiddenCls}">${r.log_nr != null ? parseFloat(r.log_nr).toFixed(4) : 'N/A'}</td>
          <td class="num scale-tech-col ${techHiddenCls}" title="${escapeHtml(buildPhase8Tooltip(r, job))}">${r.negative_space_cached_cells != null ? Number(r.negative_space_cached_cells).toLocaleString() : 'N/A'}</td>
        </tr>
      `;
    } else if (i === computingLevel && !isSuccess && !isFailed) {
      html += `
        <tr class="scale-row is-running">
          <td><b>${lvlCode}</b></td>
          <td><code>${'Computing…'}</code></td>
          <td class="num">-</td><td class="num">-</td><td class="num">-</td>
          <td class="num">-</td><td><code>-</code></td><td class="num">-</td>
          <td><b>${'Pending'}</b></td>
          <td><b>${'RUNNING'}</b></td>
          <td class="num scale-tech-col ${techHiddenCls}">-</td>
          <td class="num scale-tech-col ${techHiddenCls}">-</td>
          <td class="num scale-tech-col ${techHiddenCls}">-</td>
          <td class="num scale-tech-col ${techHiddenCls}">-</td>
          <td class="num scale-tech-col ${techHiddenCls}">-</td>
          <td class="num scale-tech-col ${techHiddenCls}">-</td>
        </tr>
      `;
    } else {
      html += `
        <tr class="scale-row is-waiting">
          <td><b>${lvlCode}</b></td>
          <td><code>-</code></td>
          <td class="num">-</td><td class="num">-</td><td class="num">-</td>
          <td class="num">-</td><td><code>-</code></td><td class="num">-</td>
          <td><b>${'Pending'}</b></td>
          <td><b>${'WAITING'}</b></td>
          <td class="num scale-tech-col ${techHiddenCls}">-</td>
          <td class="num scale-tech-col ${techHiddenCls}">-</td>
          <td class="num scale-tech-col ${techHiddenCls}">-</td>
          <td class="num scale-tech-col ${techHiddenCls}">-</td>
          <td class="num scale-tech-col ${techHiddenCls}">-</td>
          <td class="num scale-tech-col ${techHiddenCls}">-</td>
        </tr>
      `;
    }
  }

  tbody.innerHTML = html;
  perfLog(`renderConsoleScaleRows (rows=${total})`, t0);
}

function renderConsoleRegression(reg) {
  const card = document.getElementById('consoleRegressionCard');
  if (!card) return;

  if (!reg || reg.db == null) {
    card.innerHTML = '<div style="color:var(--muted);font-size:11px;text-align:center;padding:12px;">' + 'Regression slope (Db, R²) will be computed upon box-counting completion.' + '</div>';
    return;
  }

  const commentHtml = reg.academic_comment
    ? `<div style="grid-column:1/-1;font-size:11px;color:var(--muted);margin-top:6px;border-top:1px dashed var(--border);padding-top:6px;">ℹ️ <b>${'Academic Note:'}</b> ${escapeHtml(reg.academic_comment)}</div>`
    : '';

  card.innerHTML = `
    <div class="console-reg-grid">
      <div class="console-reg-cell">
        <div class="console-reg-lbl">${'FRACTAL DIM (Db)'}</div>
        <div class="console-reg-val">${parseFloat(reg.db).toFixed(4)}</div>
      </div>
      <div class="console-reg-cell">
        <div class="console-reg-lbl">${'LOG-LOG FIT (R²)'}</div>
        <div class="console-reg-val" style="color:var(--ok);">${parseFloat(reg.r2).toFixed(4)}</div>
      </div>
      <div class="console-reg-cell">
        <div class="console-reg-lbl">${'CONFIDENCE'}</div>
        <div class="console-reg-val" style="font-size:16px;">${reg.confidence_score || 100} / 100</div>
        <div style="font-size:10px;color:var(--muted);">${escapeHtml(reg.confidence_label || 'High')}</div>
      </div>
      ${commentHtml}
    </div>
  `;
}

function renderConsoleBatchQueue(queue) {
  const sec = document.getElementById('consoleBatchQueueSection');
  const tbody = document.getElementById('consoleBatchQueueBody');
  if (!sec || !tbody) return;

  if (!queue || queue.length === 0) {
    sec.style.display = 'none';
    return;
  }

  sec.style.display = 'block';
  tbody.innerHTML = queue.map(q => `
    <tr>
      <td><b>${escapeHtml(q.file)}</b></td>
      <td><span class="badge ${q.status === 'done' ? 'badge-ok' : q.status === 'failed' ? 'badge-missing' : 'badge-warn'}">${(q.status || 'queued').toUpperCase()}</span></td>
      <td class="num">${q.current_level || 0}</td>
      <td class="num">${q.completed_levels || 0}</td>
      <td class="num">${q.db != null ? parseFloat(q.db).toFixed(4) : 'N/A'}</td>
      <td class="num">${q.r2 != null ? parseFloat(q.r2).toFixed(4) : 'N/A'}</td>
      <td class="num">${q.runtime || 'N/A'}</td>
      <td>${escapeHtml(q.error || '')}</td>
    </tr>
  `).join('');
}

function renderConsoleLogs(logs) {
  const container = document.getElementById('consoleEventLog');
  if (!container || !logs || logs.length === 0) return;

  // Incremental append optimization
  if (logs.length === lastRenderedLogCount) return;

  const t0 = performance.now();
  const newLogs = logs.slice(lastRenderedLogCount);
  lastRenderedLogCount = logs.length;

  const isNearBottom = (container.scrollHeight - container.scrollTop - container.clientHeight) < 40;

  const frag = document.createDocumentFragment();
  newLogs.forEach(l => {
    const lvl = (l.level || 'info').toLowerCase();
    let cls = 'log-info';
    if (lvl === 'error' || lvl === 'failed') cls = 'log-error';
    if (lvl === 'success' || lvl === 'done') cls = 'log-success';
    if (lvl === 'warn' || lvl === 'warning') cls = 'log-warning';

    const div = document.createElement('div');
    div.className = cls;
    div.textContent = `[${l.time || ''}] ${l.message || ''}`;
    frag.appendChild(div);
  });

  container.appendChild(frag);

  // Cap DOM children at 500
  while (container.childNodes.length > 500) {
    container.removeChild(container.firstChild);
  }

  if (isNearBottom || logs.length <= newLogs.length) {
    container.scrollTop = container.scrollHeight;
  }
  perfLog(`renderConsoleLogs (added=${newLogs.length})`, t0);
}

function onJobCompletedSuccess(job) {
  document.getElementById('consoleStatusChip').textContent = 'SUCCESS';
  document.getElementById('consoleStatusChip').className = 'badge badge-ok';

  const statusPanel = document.getElementById('consoleStatusPanel');
  if (statusPanel) { statusPanel.classList.remove('is-running', 'is-error'); statusPanel.classList.add('is-success'); }

  const actions = document.getElementById('finalConsoleActions');
  if (actions) {
    actions.style.display = 'flex';
    const pkg = job.final_package || {};
    const reportBtn = document.getElementById('btnConsoleOpenReport');
    const tablesBtn = document.getElementById('btnConsoleOpenTables');
    const xlsxBtn = document.getElementById('btnConsoleOpenWorkbook');
    const figuresBtn = document.getElementById('btnConsoleOpenFigures');
    const manifestBtn = document.getElementById('btnConsoleOpenManifest');

    if (reportBtn && pkg.report_url) reportBtn.href = pkg.report_url;
    if (tablesBtn && pkg.tables_url) tablesBtn.href = pkg.tables_url;
    if (xlsxBtn && pkg.workbook_url) xlsxBtn.href = pkg.workbook_url;
    if (figuresBtn && pkg.figures_url) figuresBtn.href = pkg.figures_url;
    if (manifestBtn && pkg.manifest_url) manifestBtn.href = pkg.manifest_url;

    // Show only buttons with real valid URLs; hide the rest.
    [['btnConsoleOpenReport', pkg.report_url], ['btnConsoleOpenTables', pkg.tables_url],
     ['btnConsoleOpenWorkbook', pkg.workbook_url], ['btnConsoleOpenFigures', pkg.figures_url],
     ['btnConsoleOpenManifest', pkg.manifest_url]].forEach(([id, url]) => {
      const el = document.getElementById(id);
      if (el) el.style.display = (url && url !== '#') ? '' : 'none';
    });
  }

  // Trigger live dashboard card list refresh
  if (typeof initDashboardLive === 'function') {
    initDashboardLive();
  }
}

function onJobCompletedFailed(job) {
  document.getElementById('consoleStatusChip').textContent = 'FAILED';
  document.getElementById('consoleStatusChip').className = 'badge badge-missing';

  const statusPanel = document.getElementById('consoleStatusPanel');
  if (statusPanel) { statusPanel.classList.remove('is-running', 'is-success'); statusPanel.classList.add('is-error'); }
  
  let msg = 'Unknown error';
  const logs = (job && job.logs) || [];
  for (let i = logs.length - 1; i >= 0; i--) {
    if (logs[i] && (logs[i].level === 'error' || logs[i].level === 'failed') && logs[i].message) {
      msg = logs[i].message;
      break;
    }
  }
  alert('Analysis failed: ' + msg);
}

function formatElapsed(sec) {
  const m = Math.floor(sec / 60);
  const s = Math.floor(sec % 60);
  return String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0');
}
