/**
 * RASH-HIT Fractal Studio - Analysis Studio controller.
 * STRICT RULE: no direct fetch/XHR - all HTTP goes through API (api.js).
 */
let ACTIVE_JOB_ID = null;
let streamTimer = null;
let streamPolling = false;
let knownLevels = new Set();
let renderedLogCount = 0;
// Last job payload rendered by the live stream, so the stream panel can be
// re-rendered from the cached payload without re-polling.
let lastStreamJob = null;

const MODE_LEVEL_MAP = { fast: 5, balanced: 7, precise: 9, academic: 10 };
let TARGET_TYPE = 'single';
let SELECTED_SINGLE_FILE = null;
let SELECTED_BATCH_FILES = [];


// escapeHtml is needed on analysis.html, which loads only api.js + this file
// (package-manager.js, the dashboard's copy, is not loaded here). The typeof
// guard keeps this definition from ever clobbering a copy that might be loaded
// first on another page.
if (typeof escapeHtml !== 'function') {
  window.escapeHtml = function(str) {
    if (str == null) return '';
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  };
}
// jsQuote is defined in package-manager.js (dashboard only) - provide a local
// copy for this page (analysis.html does not load package-manager.js).
if (typeof jsQuote !== 'function') {
  window.jsQuote = function(str) {
    return String(str == null ? '' : str).replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/"/g, '&quot;');
  };
}
// attrSafe is defined in package-manager.js (dashboard only). Without this
// local copy, opening a package detail from Recently Analyzed Files throws a
// ReferenceError and the modal stays stuck on "Loading package details…".
if (typeof attrSafe !== 'function') {
  window.attrSafe = function(str) {
    return String(str == null ? '' : str).replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  };
}

if (typeof formatLvl !== 'function') {
  window.formatLvl = function(lvl) {
    if (lvl == null) return '';
    const s = String(lvl).trim();
    const m = s.match(/^L+(\d+)$/i);
    if (m) return 'L' + String(parseInt(m[1], 10)).padStart(2, '0');
    const num = parseInt(s, 10);
    if (!isNaN(num)) return 'L' + String(num).padStart(2, '0');
    return s;
  };
}

function setText(id, val) { const el = document.getElementById(id); if (el) el.textContent = val; }
function setHtml(id, html) { const el = document.getElementById(id); if (el) el.innerHTML = html; }

/* ---------- Target type + file selection ---------- */
function selectTargetType(type) {
  TARGET_TYPE = type;
  SELECTED_SINGLE_FILE = null;
  SELECTED_BATCH_FILES = [];
  const btnS = document.getElementById('btnTargetSingle');
  const btnF = document.getElementById('btnTargetFolder');
  const lbl = document.getElementById('lblInputPath');
  const runBtn = document.getElementById('btnRunWeb');
  const countLabel = document.getElementById('folderCountLabel');
  if (btnS) btnS.className = type === 'single' ? 'btn btn-primary' : 'btn';
  if (btnF) btnF.className = type === 'folder' ? 'btn btn-primary' : 'btn';
  if (lbl) lbl.textContent = type === 'folder' ? 'SVG Directory / Folder Path:' : 'SVG File Path:';
  if (countLabel) countLabel.style.display = 'none';
  if (runBtn) runBtn.disabled = true;
}

function triggerBrowse() {
  const el = document.getElementById(TARGET_TYPE === 'folder' ? 'folderBatchInput' : 'singleSvgInput');
  if (el) el.click();
}

function handleSingleSvgSelect(event) {
  const file = event.target.files[0];
  if (!file) return;
  SELECTED_SINGLE_FILE = file;
  const inp = document.getElementById('webInputPath');
  if (inp) inp.value = file.name;
  const runBtn = document.getElementById('btnRunWeb');
  if (runBtn) runBtn.disabled = false;
}

function handleFolderBatchSelect(event) {
  const files = Array.from(event.target.files).filter(f => f.name.toLowerCase().endsWith('.svg'));
  SELECTED_BATCH_FILES = files;
  const inp = document.getElementById('webInputPath');
  const countLabel = document.getElementById('folderCountLabel');
  const runBtn = document.getElementById('btnRunWeb');
  if (files.length === 0) {
    if (countLabel) countLabel.style.display = 'none';
    if (runBtn) runBtn.disabled = true;
    return;
  }
  if (files[0] && files[0].webkitRelativePath && inp) {
    inp.value = files[0].webkitRelativePath.split('/')[0];
  }
  if (countLabel) {
    countLabel.textContent = files.length + ' SVG file(s) found in selected folder.';
    countLabel.style.display = 'block';
  }
  if (runBtn) runBtn.disabled = false;
}

function updateModeDefaultLevels(sel) {
  const mode = sel ? sel.value : (document.getElementById('webModeSelect') || {}).value;
  const lvlInput = document.getElementById('webLevelsInput');
  if (!lvlInput) return;
  if (mode && mode !== 'custom' && MODE_LEVEL_MAP[mode]) lvlInput.value = MODE_LEVEL_MAP[mode];
}

/* ---------- Run analysis ---------- */
async function startAnalysis() {
  const levels = parseInt(document.getElementById('webLevelsInput')?.value || 7, 10);
  const overwrite = document.getElementById('chkOverwrite')?.checked === true;
  const mode = document.getElementById('webModeSelect')?.value || 'balanced';
  const runBtn = document.getElementById('btnRunWeb');
  let res;
  let label = '';

  try {
    if (TARGET_TYPE === 'folder') {
      if (!SELECTED_BATCH_FILES || SELECTED_BATCH_FILES.length === 0) {
        alert('Please select a folder containing SVG files first.');
        return;
      }
      const fd = new FormData();
      SELECTED_BATCH_FILES.forEach(file => fd.append('files[]', file, file.webkitRelativePath || file.name));
      fd.append('levels', levels); fd.append('mode', mode); fd.append('overwrite', overwrite ? 'true' : 'false');
      if (runBtn) { runBtn.disabled = true; runBtn.textContent = 'Running...'; }
      res = await API.runBatchAnalysis(fd);
      label = SELECTED_BATCH_FILES[0].webkitRelativePath || SELECTED_BATCH_FILES[0].name;
    } else {
      if (!SELECTED_SINGLE_FILE) {
        alert('Please select an SVG file to analyze.');
        return;
      }
      const fd = new FormData();
      fd.append('file', SELECTED_SINGLE_FILE, SELECTED_SINGLE_FILE.name);
      fd.append('levels', levels); fd.append('mode', mode); fd.append('overwrite', overwrite ? 'true' : 'false');
      if (runBtn) { runBtn.disabled = true; runBtn.textContent = 'Running...'; }
      res = await API.runSingleAnalysis(fd);
      label = SELECTED_SINGLE_FILE.name;
    }
  } catch (err) {
    alert('Analysis run error: ' + err.message);
    if (runBtn) { runBtn.disabled = false; runBtn.textContent = 'Start Analysis'; }
    return;
  }

  if (runBtn) { runBtn.disabled = false; runBtn.textContent = 'Start Analysis'; }
  if (res && res.job_id) {
    beginStreaming(res.job_id, label);
  }
}

/* ---------- Live stream polling ---------- */
function beginStreaming(jobId, fileLabel) {
  stopStreaming();
  ACTIVE_JOB_ID = jobId;
  knownLevels.clear();
  renderedLogCount = 0;
  setText('streamJobId', jobId || '-');
  setText('streamFile', fileLabel || '-');
  const chip = document.getElementById('streamStatusChip');
  if (chip) { chip.textContent = 'QUEUED'; chip.className = 'plain-status'; }
  document.getElementById('streamFinalActions').style.display = 'none';
  setHtml('streamScaleBody', '<tr><td colspan="10" style="text-align:center;color:var(--muted);padding:14px;">' + 'Awaiting level computation metrics...' + '</td></tr>');
  setHtml('streamLog', '');
  setText('streamPct', '0%');
  streamTimer = setInterval(pollStream, 400);
  pollStream();
  refreshHistory();
}

function stopStreaming() {
  if (streamTimer) { clearInterval(streamTimer); streamTimer = null; }
}

async function pollStream() {
  if (!ACTIVE_JOB_ID || streamPolling) return;
  streamPolling = true;
  try {
    const job = await API.getJobStatus(ACTIVE_JOB_ID);
    if (!job || job.error) return;
    lastStreamJob = job;
    const raw = (job.status || 'running').toLowerCase();
    const done = ['success', 'done', 'complete', 'completed'].includes(raw);
    const failed = ['failed', 'error'].includes(raw);

    renderStreamMeta(job, done, failed);
    renderStreamScaleRows(job.scale_rows || [], job.requested_levels || 7, job.current_level || 0, done, failed);
    renderStreamLog(job.logs || []);
    renderStreamFinalActions(job, done);

    if (done || failed) {
      stopStreaming();
      const chip = document.getElementById('streamStatusChip');
      if (chip) { chip.textContent = done ? 'SUCCESS' : 'FAILED'; chip.className = 'plain-status'; }
      refreshHistory();
      refreshRecentFiles();
    }
  } catch (err) {
    // transient poll errors are ignored
  } finally {
    streamPolling = false;
  }
}

function renderStreamMeta(job, done, failed) {
  setText('streamFile', job.current_file || '-');
  setText('streamElapsed', formatElapsed(job.elapsed_seconds || 0));
  setText('streamStep', (job.current_step || 'Processing') + (job.current_level ? ' (Level ' + job.current_level + '/' + (job.requested_levels || 7) + ')' : ''));
  const total = job.requested_levels || 7;
  const curr = job.current_level || 0;
  const pct = done ? 100 : Math.min(99, Math.round((curr / total) * 100));
  const bar = document.getElementById('streamProgressBar');
  if (bar) bar.style.width = pct + '%';
  setText('streamPct', pct + '%');
  if (!done && !failed) {
    const chip = document.getElementById('streamStatusChip');
    if (chip) {
      const raw = (job.status || 'RUNNING').toUpperCase();
      chip.textContent = raw === 'RUNNING' ? raw : raw;
      chip.className = 'plain-status';
    }
  }
}

function renderStreamScaleRows(rows, requestedLevels, currentLevel, done, failed) {
  const tbody = document.getElementById('streamScaleBody');
  if (!tbody) return;
  const total = Math.max(requestedLevels || 7, rows ? rows.length : 0);
  const rowMap = new Map();
  (rows || []).forEach(r => {
    const lvl = r.level != null ? r.level : (r.grid_level != null ? r.grid_level : 0);
    rowMap.set(lvl, r);
  });

  // currentLevel = last completed; the next one being computed = currentLevel + 1
  const computingLevel = done ? null : (currentLevel < total ? currentLevel + 1 : null);
  let html = '';
  for (let i = 1; i <= total; i++) {
    const r = rowMap.get(i);
    const lvlCode = 'L' + String(i).padStart(2, '0');
    const isNew = r && !knownLevels.has(i);
    if (r) knownLevels.add(i);
    const flashClass = isNew ? ' is-new' : '';
    if (r) {
      const filled = r.occupied_count != null ? Number(r.occupied_count).toLocaleString() : 'N/A';
      const totCells = r.total_count != null ? Number(r.total_count).toLocaleString() : 'N/A';
      const empty = r.empty_count != null ? Number(r.empty_count).toLocaleString() :
        (r.total_count != null && r.occupied_count != null ? (r.total_count - r.occupied_count).toLocaleString() : 'N/A');
      const occ = r.occupancy_percent != null ? parseFloat(r.occupancy_percent).toFixed(2) + '%' : 'N/A';
      const cellSize = (r.box_size_w && r.box_size_h) ? r.box_size_w + ' x ' + r.box_size_h : 'N/A';
      const dur = r.duration_seconds != null ? parseFloat(r.duration_seconds).toFixed(3) + 's' : 'N/A';
      const fit = r.included_in_fit !== false ? '<b>' + 'Fit' + '</b>' : '<b>' + 'Excluded' + '</b>';
      html += '<tr class="scale-row is-done' + flashClass + '">' +
        '<td><b>' + lvlCode + '</b></td>' +
        '<td><code>' + escapeHtml(r.grid_label || (r.box_size_w ? r.box_size_w + 'x' + r.box_size_h : 'N/A')) + '</code></td>' +
        '<td class="num"><b>' + totCells + '</b></td>' +
        '<td class="num"><b>' + filled + '</b></td>' +
        '<td class="num">' + empty + '</td>' +
        '<td class="num"><b>' + occ + '</b></td>' +
        '<td><code>' + cellSize + '</code></td>' +
        '<td class="num">' + dur + '</td>' +
        '<td>' + fit + '</td>' +
        '<td><b>' + 'DONE' + '</b></td></tr>';
    } else if (i === computingLevel && !done && !failed) {
      html += '<tr class="scale-row is-running"><td><b>' + lvlCode + '</b></td>' +
        '<td><code>' + 'Computing…' + '</code></td>' +
        '<td class="num">-</td><td class="num">-</td><td class="num">-</td>' +
        '<td class="num">-</td><td><code>-</code></td><td class="num">-</td>' +
        '<td><b>' + 'Pending' + '</b></td>' +
        '<td><b>' + 'RUNNING' + '</b></td></tr>';
    } else {
      html += '<tr class="scale-row is-waiting"><td><b>' + lvlCode + '</b></td>' +
        '<td><code>-</code></td>' +
        '<td class="num">-</td><td class="num">-</td><td class="num">-</td>' +
        '<td class="num">-</td><td><code>-</code></td><td class="num">-</td>' +
        '<td><b>' + 'Pending' + '</b></td>' +
        '<td><b>' + 'WAITING' + '</b></td></tr>';
    }
  }
  tbody.innerHTML = html;
}

function renderStreamLog(logs) {
  const container = document.getElementById('streamLog');
  if (!container || !logs || logs.length === 0) return;
  if (logs.length === renderedLogCount) return;
  const frag = document.createDocumentFragment();
  logs.slice(renderedLogCount).forEach(l => {
    const lvl = (l.level || 'info').toLowerCase();
    const cls = lvl === 'error' || lvl === 'failed' ? 'log-error'
      : (lvl === 'success' || lvl === 'done' ? 'log-success'
      : (lvl === 'warn' || lvl === 'warning' ? 'log-warning' : 'log-info'));
    const div = document.createElement('div');
    div.className = cls;
    div.textContent = '[' + (l.time || '') + '] ' + (l.message || '');
    frag.appendChild(div);
  });
  container.appendChild(frag);
  renderedLogCount = logs.length;
  container.scrollTop = container.scrollHeight;
}

function renderStreamFinalActions(job, done) {
  const actions = document.getElementById('streamFinalActions');
  if (!actions || !done || !job || !job.final_package) {
    if (actions) actions.style.display = 'none';
    return;
  }
  const pkg = job.final_package;
  const links = [['btnStreamReport', pkg.report_url], ['btnStreamTables', pkg.tables_url], ['btnStreamWorkbook', pkg.workbook_url]];
  links.forEach(([id, url]) => {
    const el = document.getElementById(id);
    if (el) { el.href = url || '#'; el.style.display = url ? '' : 'none'; }
  });
  actions.style.display = 'flex';
}

function formatElapsed(sec) {
  const m = Math.floor(sec / 60);
  const s = Math.floor(sec % 60);
  return String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0');
}

/* ---------- Job history (advanced panel) ---------- */
// Full job list cache (unfiltered) + jobs whose package was deleted this session.
let ALL_JOBS = [];
let deletedJobPackages = new Set();

async function refreshHistory() {
  try {
    const data = await API.getJobs();
    ALL_JOBS = data.jobs || [];
    const badge = document.getElementById('jobCountBadge');
    if (badge) badge.textContent = ALL_JOBS.length;
    populateJobMotifFilter();
    applyJobFilters();
  } catch (err) { /* ignore */ }
}

/** Derive the motif label of a job (final package > folder > source SVG stem). */
function jobMotif(j) {
  const fp = (j && j.final_package) || {};
  return String(fp.motif || fp.folder || String((j && j.current_file) || '').replace(/\.svg$/i, '') || '');
}

/** Rebuild the motif dropdown from the completed jobs' final packages. */
function populateJobMotifFilter() {
  const sel = document.getElementById('jobMotifFilter');
  if (!sel) return;
  const current = sel.value;
  const motifs = new Set();
  ALL_JOBS.forEach(j => {
    const m = jobMotif(j);
    if (m) motifs.add(m);
  });
  const sorted = Array.from(motifs).sort((a, b) => a.localeCompare(b));
  sel.innerHTML = '<option value="" selected>All motifs</option>' +
    sorted.map(m => '<option value="' + escapeHtml(m) + '"' + (m === current ? ' selected' : '') + '>' + escapeHtml(m) + '</option>').join('');
}

/** Read the time-range + motif filters and re-render the history list. */
function applyJobFilters() {
  const timeSel = document.getElementById('jobTimeFilter');
  const motifSel = document.getElementById('jobMotifFilter');
  const range = timeSel ? timeSel.value : 'all';
  const motif = motifSel ? motifSel.value : '';
  const now = Date.now() / 1000;
  const cutoff = { '24h': now - 24 * 3600, '7d': now - 7 * 24 * 3600, '30d': now - 30 * 24 * 3600 }[range];

  const filtered = (ALL_JOBS || []).filter(j => {
    if (cutoff != null && (!j.start_time || j.start_time < cutoff)) return false;
    if (motif && jobMotif(j) !== motif) return false;
    return true;
  });
  renderJobHistory(filtered);
}

function clearJobFilters() {
  const t = document.getElementById('jobTimeFilter');
  const m = document.getElementById('jobMotifFilter');
  if (t) t.value = 'all';
  if (m) m.value = '';
  applyJobFilters();
}

/** Delete the package folder behind a completed job (server-side safe delete). */
async function deleteJobPackage(jobId, folder) {
  if (!jobId || !folder) return;
  const ok = confirm('Delete package "' + folder + '"?\nThis permanently removes the entire outputs/' + folder + ' folder (report/excel/tables/manifest files included).\nThis cannot be undone.');
  if (!ok) return;
  try {
    await API.deletePackages([folder]);
    deletedJobPackages.add(folder);
    // Drop the detail cache so a stale package never re-renders.
    if (typeof pkgDetailCache !== 'undefined' && pkgDetailCache[folder]) delete pkgDetailCache[folder];
    await refreshHistory();
    await refreshRecentFiles();
  } catch (err) {
    alert('Delete operation failed: ' + (err && err.message ? err.message : err));
  }
}

function renderJobHistory(jobs) {
  const list = document.getElementById('jobHistoryList');
  if (!list) return;
  if (!jobs.length) {
    const noJobsAtAll = !(ALL_JOBS && ALL_JOBS.length);
    list.innerHTML = noJobsAtAll
      ? '<div class="empty-hint">' + 'No analyses have been run yet.' + '</div>'
      : '<div class="empty-hint">' + 'No analyses match the current filters.' + '</div>';
    return;
  }
  const statusLabel = (st) => {
    const s = (st || '').toLowerCase();
    if (['success', 'done', 'complete', 'completed'].includes(s)) return 'DONE';
    if (s === 'failed' || s === 'error') return 'FAILED';
    if (s === 'running') return 'RUNNING';
    if (s === 'queued') return 'QUEUED';
    return (st || '?').toUpperCase();
  };

  list.innerHTML = jobs.map(j => {
    const isActive = j.job_id === ACTIVE_JOB_ID;
    const fp = j.final_package || {};
    const done = ['success', 'done', 'complete', 'completed'].includes((j.status || '').toLowerCase());
    const metrics = (done && fp.db != null)
      ? 'Db' + ' ' + parseFloat(fp.db).toFixed(4) + ' | ' + 'R2' + ' ' + parseFloat(fp.r2).toFixed(4) + ' | ' + (fp.levels || 0) + ' levels'
      : (j.completed_files ? j.completed_files + '/' + j.total_files + ' ' + 'files' : '');
    // Always show the direct source file name (e.g. 16D.svg); fall back to the
    // job's current_file / motif when the source is unknown.
    const srcName = fp.source_file
      ? String(fp.source_file).split(/[\\/]/).pop()
      : (j.current_file ? String(j.current_file).split(/[\\/]/).pop() : '');
    const file = srcName || (fp.motif || j.mode || '-');
    const sub = [fp.folder || '', fp.motif ? ('motif: ' + fp.motif) : '', j.started_at || ''].filter(Boolean).join(' | ');
    const reportLink = (done && fp.report_url)
      ? '<a class="recent-link" href="' + escapeHtml(fp.report_url) + '" target="_blank" rel="noopener" onclick="event.stopPropagation()">' + 'Open Report' + '</a>'
      : '';
    const clickFn = done && fp.folder
      ? 'showPackageDetail(\'' + escapeHtml(String(fp.folder)).replace(/\\/g, '\\\\').replace(/'/g, "\\'") + '\')'
      : 'viewJob(\'' + escapeHtml(j.job_id) + '\')';

    // Job History enhancement: list ALL generated artifacts for finished jobs
    // (SVG, JSON, CSV, XLSX, reports, images, exports) - not just the source SVG.
    let filesHtml = '';
    if (done && Array.isArray(fp.files) && fp.files.length) {
      const chips = fp.files.map(f =>
        '<a class="job-file-chip" href="' + escapeHtml(f.url || '#') + '" target="_blank" rel="noopener" onclick="event.stopPropagation()" title="' + escapeHtml((f.label || f.kind || '') + ' - ' + (f.size ? Math.round(parseInt(f.size,10)/1024) + ' KB' : '')) + '">' +
        escapeHtml((f.kind === 'svg' ? '🖼️ ' : f.kind === 'xlsx' ? '📈 ' : f.kind === 'pdf' ? '📕 ' : f.kind === 'json' ? '🧾 ' : '📄 ') + f.name) +
        '</a>'
      ).join('');
      filesHtml = '<span class="history-files">' + chips + '</span>';
    } else if (done) {
      // Legacy fallback when the job predates the files[] field.
      const legacy = [fp.report_url, fp.tables_url, fp.workbook_url, fp.manifest_url].filter(Boolean);
      if (legacy.length) {
        filesHtml = '<span class="history-files">' + legacy.map(u =>
          '<a class="job-file-chip" href="' + escapeHtml(u) + '" target="_blank" rel="noopener" onclick="event.stopPropagation()">' + escapeHtml(u.split('/').pop()) + '</a>'
        ).join('') + '</span>';
      }
    }

    // A job whose package folder no longer exists on disk (deleted this session
    // OR via the dashboard / another tab) shows a Deleted badge and hides the
    // artifact chips instead of rendering 404 links. Backend sets
    // folder_exists:false when the folder is missing on enrichment.
    const folder = fp.folder || '';
    const pkgDeleted = done && folder && (deletedJobPackages.has(folder) || fp.folder_exists === false);
    const deleteBtn = (done && fp.folder && !pkgDeleted)
      ? '<button type="button" class="job-delete-btn" title="Delete package ' + escapeHtml(fp.folder) + '" data-testid="job-delete-btn" onclick="event.stopPropagation();deleteJobPackage(\'' + escapeHtml(String(j.job_id)).replace(/\\/g, '\\\\').replace(/'/g, "\\'") + '\',\'' + escapeHtml(String(fp.folder)).replace(/\\/g, '\\\\').replace(/'/g, "\\'") + '\')">🗑️</button>'
      : '';
    const statusBadge = pkgDeleted
      ? '<b style="font-size:10px;text-transform:uppercase;letter-spacing:.04em;color:var(--text);">' + 'DELETED' + '</b>'
      : (reportLink || '<b style="font-size:10px;text-transform:uppercase;letter-spacing:.04em;color:var(--text);">' + statusLabel(j.status) + '</b>');

    return '<div class="history-item' + (isActive ? ' active' : '') + (pkgDeleted ? ' is-deleted' : '') + '" data-job="' + escapeHtml(j.job_id) + '" onclick="' + clickFn + '" role="button" tabindex="0">' +
      '<div class="history-item-top"><span class="history-file" title="' + escapeHtml(j.job_id) + '">' + escapeHtml(file) + '</span>' +
      deleteBtn + statusBadge + '</div>' +
      '<span class="history-sub">' + escapeHtml(sub) + '</span>' +
      (metrics ? '<span class="history-metrics">' + escapeHtml(metrics) + '</span>' : '') +
      (pkgDeleted ? '' : filesHtml) +
      '</div>';
  }).join('');
}

async function viewJob(jobId) {
  if (!jobId) return;
  const job = await API.getJobStatus(jobId);
  if (!job || job.error) { alert('Job not found or expired.'); return; }
  beginStreaming(jobId, job.current_file || '');
}

/* ---------- Recently analyzed files ---------- */
async function refreshRecentFiles() {
  try {
    const data = await API.getPackages();
    const pkgs = data.packages || [];
    const list = document.getElementById('recentFilesList');
    if (!list) return;
    if (!pkgs.length) {
      list.innerHTML = '<div class="empty-hint">' + 'No packages found yet.' + '</div>';
      return;
    }
    list.innerHTML = pkgs.slice(0, 20).map(p => {
      const folder = p.folder || '';
      const db = p.db != null ? 'Db' + ' ' + parseFloat(p.db).toFixed(4) : '';
      const r2 = p.r2 != null ? 'R2' + ' ' + parseFloat(p.r2).toFixed(4) : '';
      const lv = p.levels || p.computed_levels_count || 0;
      // Whole row is clickable: show the package detail inline (no extra Open click).
      return '<div class="history-item" data-pkg="' + escapeHtml(folder) + '" onclick="showPackageDetail(\'' + escapeHtml(folder).replace(/\\/g, '\\\\').replace(/'/g, "\\'") + '\')" role="button" tabindex="0" onkeydown="if(event.key===\'Enter\'){showPackageDetail(\'' + escapeHtml(folder).replace(/\\/g, '\\\\').replace(/'/g, "\\'") + '\');}">' +
        '<div class="history-item-top"><span class="history-file" title="' + escapeHtml(folder) + '">' + escapeHtml(p.motif || folder) + '</span>' +
        '<b style="font-size:10px;font-weight:800;color:var(--text);border:1px solid var(--border);border-radius:999px;padding:1px 8px;background:var(--panel2);">' + escapeHtml(p.package_version || 'v1') + '</b></div>' +
        '<span class="history-sub">' + escapeHtml(p.generated_at || '') + ' | ' + escapeHtml(folder) + '</span>' +
        '<span class="history-metrics">' + escapeHtml([db, r2, lv + ' levels', (p.status || 'complete')].filter(Boolean).join(' | ')) + '</span>' +
        '</div>';
    }).join('');
  } catch (err) { /* ignore */ }
}

/* ---------- Package detail modal (full-screen window like report.html) ---------- */
let pkgDetailCache = {};
async function showPackageDetail(folder) {
  if (!folder) return;
  const panel = document.getElementById('pkgDetailPanel');
  const body = document.getElementById('pkgDetailBody');
  if (!panel || !body) return;
  const title = document.getElementById('pkgDetailTitle');
  if (title) title.textContent = '📦 Package Details';
  const sub = document.getElementById('pkgDetailSub');
  if (sub) sub.textContent = 'outputs/' + folder;
  panel._prevFocus = document.activeElement;  // ISSUE-011: focus restore
  panel.classList.add('open');
  body.innerHTML = '<div class="empty-hint">' + 'Loading package details…' + '</div>';
  try {
    const pkg = pkgDetailCache[folder] || (pkgDetailCache[folder] = await API.getPackage(folder));
    if (!pkg || pkg.error) {
      body.innerHTML = '<div class="empty-hint">' + 'Failed to load package.' + '</div>';
      return;
    }
    renderPackageDetail(pkg);
  } catch (err) {
    body.innerHTML = '<div class="empty-hint">' + 'Package load error: ' + escapeHtml(err.message || err) + '</div>';
  }
}

function closePackageDetail() {
  const panel = document.getElementById('pkgDetailPanel');
  if (panel) panel.classList.remove('open');
  if (panel && panel._prevFocus && typeof panel._prevFocus.focus === 'function') {
    panel._prevFocus.focus();  // ISSUE-011: restore focus
  }
}

/**
 * Open the package folder on the local machine via the local server.
 * package-manager.js is NOT loaded on analysis.html, so this page defines its
 * own copy of the handler used by the package detail "📂 Folder" button.
 */
async function openPackageFolder(folder) {
  if (!folder) return;
  // ui.js is loaded on this page: render the folder contents on screen.
  if (typeof openFolderBrowser === 'function') {
    openFolderBrowser(folder);
    return;
  }
  // Fallback: show the plain path in an alert.
  const res = await API.openFolder(folder).catch(() => null);
  if (!res || !res.ok) {
    alert('Package folder path: outputs/' + folder);
  }
}

function renderPackageDetail(pkg) {
  const body = document.getElementById('pkgDetailBody');
  if (!body) return;
  const folder = pkg.folder || '';
  const report = pkg.report_url || (folder ? folder + '/report/report.html' : '#');
  const tables = pkg.tables_url || (folder ? folder + '/tables/tables.html' : '#');
  const workbook = pkg.workbook_url || (folder ? folder + '/excel/workbook.xlsx' : '#');
  const manifest = pkg.manifest_url || (folder ? folder + '/manifest/manifest.json' : '#');
  const db = pkg.db != null ? parseFloat(pkg.db).toFixed(4) : 'N/A';
  const r2 = pkg.r2 != null ? parseFloat(pkg.r2).toFixed(4) : 'N/A';
  const lv = pkg.levels || pkg.computed_levels_count || 'N/A';
  const timeMs = pkg.total_time_ms != null ? parseFloat(pkg.total_time_ms).toFixed(2) + ' ms' : 'N/A';
  const srcName = pkg.source_file ? String(pkg.source_file).split(/[\\/]/).pop() : 'N/A';

  // Header block: motif + source + action buttons.
  const head =
    '<div style="background:var(--panel2);border:1px solid var(--border);border-radius:12px;padding:16px;margin-bottom:14px;">' +
      '<div style="font-size:20px;font-weight:800;color:var(--text);">' + escapeHtml(pkg.motif || folder) + '</div>' +
      '<div class="history-sub" style="margin-top:4px;">' + escapeHtml(srcName) + ' &middot; ' + escapeHtml(folder) + ' &middot; ' + escapeHtml(pkg.generated_at || '') + '</div>' +
      '<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:12px;">' +
        '<a class="btn btn-primary" href="' + escapeHtml(report) + '" target="_blank" rel="noopener" data-testid="detail-report-btn">' + 'Open Full Report ↗' + '</a>' +
        '<a class="btn" href="' + escapeHtml(tables) + '" target="_blank" rel="noopener">' + 'Tables Viewer' + '</a>' +
        '<a class="btn" href="' + escapeHtml(workbook) + '" target="_blank" rel="noopener">' + 'Workbook (.xlsx)' + '</a>' +
        '<a class="btn" href="' + escapeHtml(manifest) + '" target="_blank" rel="noopener">' + 'Manifest (.json)' + '</a>' +
        '<button class="btn" onclick="openPackageFolder(\'' + escapeHtml(String(folder)).replace(/\\/g, '\\\\').replace(/'/g, "\\'") + '\')" data-testid="detail-open-folder-btn">' + '📂 Folder' + '</button>' +
      '</div>' +
    '</div>';

  // KPI grid (report.html style) — no Version/Status/Confidence clutter.
  const kpis =
    '<div class="kpi-row" style="margin-bottom:14px;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));">' +
      '<div class="kpi-card"><div class="kpi-lbl">' + 'Fractal Dimension (Db)' + '</div><div class="kpi-val">' + db + '</div><div class="kpi-sub">' + 'box-counting' + '</div></div>' +
      '<div class="kpi-card"><div class="kpi-lbl">' + 'Log-Log Fit (R&sup2;)' + '</div><div class="kpi-val">' + r2 + '</div><div class="kpi-sub">' + 'linear fit' + '</div></div>' +
      '<div class="kpi-card"><div class="kpi-lbl">' + 'Grid Levels' + '</div><div class="kpi-val">' + lv + '</div><div class="kpi-sub">' + 'computed' + '</div></div>' +
      '<div class="kpi-card"><div class="kpi-lbl">' + 'Execution Time' + '</div><div class="kpi-val" style="font-size:15px;">' + timeMs + '</div><div class="kpi-sub">' + 'pipeline' + '</div></div>' +
    '</div>';

  // Package files as horizontal chips grouped by category (report.html style).
  const knownFiles = [
    ['📄 report.html', pkg.report_url],
    ['📕 report.pdf', pkg.report_pdf_url],
    ['📊 tables.html', pkg.tables_url],
    ['📈 workbook.xlsx', pkg.workbook_url],
    ['🔒 manifest.json', pkg.manifest_url],
  ].filter(f => f[1]);
  const files = knownFiles.length
    ? '<div class="panel-sub-hdr">' + 'Package Files' + '</div><div class="file-chip-list" style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:14px;">' +
      knownFiles.map(f => '<a class="file-chip" href="' + escapeHtml(f[1]) + '" target="_blank" rel="noopener"><span>' + f[0] + '</span></a>').join('') +
      '</div>'
    : '';

  // SVG maps gallery grid with inline preview (L01 labels + modal gallery feed).
  const maps = pkg.svg_maps || [];
  window.RASH_HIT_GALLERY = maps.map(m => ({
    src: m.url,
    label: (pkg.motif || '') + ' · ' + formatLvl(m.level || '?'),
  }));
  const lvlTag = (m) => formatLvl(m.level || '?');
  const gallery = maps.length
    ? '<div class="panel-sub-hdr">' + 'SVG Gallery' + '</div><div class="svg-gallery-grid" style="margin-bottom:14px;">' +
      maps.map(m => {
        const lt = lvlTag(m);
        const lb = (pkg.motif || '') + ' · ' + lt;
        return '<div class="svg-thumb-card">' +
          '<div style="display:flex;justify-content:space-between;align-items:center;font-size:11px;font-weight:700;margin-bottom:2px;">' +
            '<b style="font-size:10px;font-weight:800;color:var(--text);">' + lt + '</b></div>' +
          '<button type="button" class="svg-img-container" onclick="openSvgModal(\'' + jsQuote(m.url) + '\', \'' + jsQuote(lb) + '\')">' +
            '<img src="' + attrSafe(m.url) + '" alt="' + lt + '" loading="lazy" decoding="async">' +
          '</button>' +
          '<div style="display:flex;gap:6px;margin-top:2px;">' +
            '<button class="btn btn-sm btn-soft" style="flex:1;" onclick="openSvgModal(\'' + jsQuote(m.url) + '\', \'' + jsQuote(lb) + '\')">' + 'Preview' + '</button>' +
            '<a class="btn btn-sm" style="flex:1;" href="' + attrSafe(m.url) + '" target="_blank" rel="noopener">' + 'SVG' + '</a>' +
          '</div>' +
        '</div>';
      }).join('') + '</div>'
    : '';

  const scale = (pkg.scale_rows && pkg.scale_rows.length)
    ? '<div class="panel-sub-hdr">' + 'Level Scale Rows' + '</div>' + renderScaleRowsCompact(pkg.scale_rows)
    : '';

  body.innerHTML = head + kpis + gallery + files + scale;
}

function renderScaleRowsCompact(rows) {
  let html = '<div style="overflow-x:auto;"><table class="scale-table"><thead><tr><th>' + 'Level' + '</th><th>' + 'Grid' + '</th><th class="num">' + 'Total' + '</th><th class="num">' + 'Filled' + '</th><th class="num">' + 'Empty' + '</th><th class="num">' + 'Occ %' + '</th></tr></thead><tbody>';
  rows.forEach(r => {
    const empty = (r.empty_count != null) ? r.empty_count : ((r.total_count != null && r.occupied_count != null) ? r.total_count - r.occupied_count : (r.empty_cells != null ? r.empty_cells : ''));
    html += '<tr><td><b>' + escapeHtml(formatLvl(r.level != null ? r.level : '')) + '</b></td><td><code>' + escapeHtml(r.grid_label || r.grid || '') + '</code></td>' +
      '<td class="num">' + escapeHtml(r.total_count != null ? r.total_count : '') + '</td>' +
      '<td class="num">' + escapeHtml(r.occupied_count != null ? r.occupied_count : '') + '</td>' +
      '<td class="num">' + escapeHtml(empty) + '</td>' +
      '<td class="num">' + escapeHtml(r.occupancy_percent != null ? parseFloat(r.occupancy_percent).toFixed(2) : '') + '</td></tr>';
  });
  return html + '</tbody></table></div>';
}

/* ---------- Init ---------- */
async function init() {
  const isFile = window.location.protocol === 'file:';
  if (isFile) {
    const banner = document.getElementById('fileProtocolBanner');
    if (banner) banner.style.display = 'block';
    const btn = document.getElementById('btnRunWeb');
    if (btn) btn.disabled = true;
    const badge = document.getElementById('serverBadge');
    if (badge) { badge.textContent = 'Static Mode'; badge.classList.remove('online'); }
  } else {
    const health = await API.getHealth();
    const badge = document.getElementById('serverBadge');
    if (health && health.status === 'OK') {
      if (badge) { badge.textContent = 'Connected'; badge.classList.add('online'); }
    } else {
      if (badge) { badge.textContent = 'Offline'; badge.classList.remove('online'); }
    }
  }
  const idleChip = document.getElementById('streamStatusChip');
  if (idleChip) { idleChip.textContent = 'IDLE'; idleChip.className = 'plain-status'; }
  await refreshHistory();
  await refreshRecentFiles();
  setInterval(() => { refreshHistory(); }, 5000);
}

document.addEventListener('DOMContentLoaded', init);
