/**
 * RASH-HIT Fractal Studio - Main Application Controller
 */

let PACKAGES = [];
let visiblePackages = [];
let selectedFolders = new Set();
let CURRENT_TARGET_TYPE = 'single';
let dashboardRefreshTimer = null;
// Analysis Detail view: remembers which package is shown when several are
// selected (reference-dashboard behavior).
let activeDetailFolder = null;

// Real File state selected by the user (the source of truth for analysis).
// webInputPath only mirrors the selection as a human-readable label.
let SELECTED_SINGLE_FILE = null;
let SELECTED_BATCH_FILES = [];

async function refreshServerBadge() {
  const badge = document.getElementById('serverBadge');
  if (!badge) return;
  const health = await API.getHealth();
  if (health && health.status === 'OK') {
    badge.textContent = 'Connected';
    badge.classList.add('online');
  } else {
    badge.textContent = 'Offline';
    badge.classList.remove('online');
  }
}

async function fetchDashboardData() {
  const t0 = performance.now();
  const data = await API.getPackages();
  PACKAGES = data.packages || [];
  visiblePackages = [...PACKAGES];

  const stats = await API.getStats();
  if (stats) {
    updateKpiCards(stats);
  } else {
    computeKpisFromPackages();
  }

  applyFilters();
  if (typeof initEmptyStateCta === 'function') initEmptyStateCta();
  if (typeof perfLog === 'function') perfLog('fetchDashboardData total', t0);
}

function initDashboardLive(immediate = false) {
  if (immediate) {
    if (dashboardRefreshTimer) clearTimeout(dashboardRefreshTimer);
    return fetchDashboardData();
  }
  if (dashboardRefreshTimer) {
    clearTimeout(dashboardRefreshTimer);
  }
  return new Promise(resolve => {
    dashboardRefreshTimer = setTimeout(async () => {
      await fetchDashboardData();
      resolve();
    }, 300);
  });
}

function updateKpiCards(stats) {
  const elTot = document.getElementById('kpiTotal');
  const elDb = document.getElementById('kpiAvgDb');
  const elR2 = document.getElementById('kpiAvgR2');
  const elMaps = document.getElementById('kpiSvgMaps');
  const elXlsx = document.getElementById('kpiXlsxTables');
  const elLat = document.getElementById('kpiLatest');

  // Support both legacy (package_index) and dashboard field names.
  const total = stats.total_packages != null ? stats.total_packages : stats.total_count;
  const figures = stats.total_figures != null ? stats.total_figures : stats.total_svg_maps;
  const xlsx = stats.total_xlsx != null ? stats.total_xlsx : stats.total_xlsx_cells;
  const latest = stats.latest_generated != null ? stats.latest_generated : stats.latest_str;

  if (elTot) elTot.textContent = total || 0;
  if (elDb) elDb.textContent = (stats.avg_db != null) ? stats.avg_db.toFixed(4) : '0.0000';
  if (elR2) elR2.textContent = (stats.avg_r2 != null) ? stats.avg_r2.toFixed(4) : '0.0000';
  if (elMaps) elMaps.textContent = figures || 0;
  if (elXlsx) elXlsx.textContent = xlsx || 0;
  if (elLat) elLat.textContent = latest || 'N/A';
}

function computeKpisFromPackages() {
  const elTot = document.getElementById('kpiTotal');
  const elDb = document.getElementById('kpiAvgDb');
  const elR2 = document.getElementById('kpiAvgR2');
  if (elTot) elTot.textContent = PACKAGES.length;
  if (PACKAGES.length > 0) {
    const sumDb = PACKAGES.reduce((a, b) => a + (b.db || 0), 0);
    const sumR2 = PACKAGES.reduce((a, b) => a + (b.r2 || 0), 0);
    if (elDb) elDb.textContent = (sumDb / PACKAGES.length).toFixed(4);
    if (elR2) elR2.textContent = (sumR2 / PACKAGES.length).toFixed(4);
  }
}

async function startWebAnalysis() {
  const levels = parseInt(document.getElementById('webLevelsInput')?.value || 7, 10);
  const btn = document.getElementById('btnRunWeb');
  const overwrite = document.getElementById('chkOverwrite')?.checked === true;
  const mode = (document.getElementById('webModeSelect')?.value || 'balanced');

  let res;
  let consoleLabel = '';

  if (CURRENT_TARGET_TYPE === 'folder') {
    if (!SELECTED_BATCH_FILES || SELECTED_BATCH_FILES.length === 0) {
      alert('Please select a folder containing SVG files first.');
      return;
    }
    const formData = new FormData();
    SELECTED_BATCH_FILES.forEach(file => {
      formData.append('files[]', file, file.webkitRelativePath || file.name);
    });
    formData.append('levels', levels);
    formData.append('mode', mode);
    formData.append('overwrite', overwrite ? 'true' : 'false');

    if (btn) { btn.disabled = true; btn.textContent = 'Running…'; btn.classList.add('is-loading'); }
    try {
      res = await API.runBatchAnalysis(formData);
      consoleLabel = SELECTED_BATCH_FILES[0].webkitRelativePath || SELECTED_BATCH_FILES[0].name;
    } catch (err) {
      alert('Analysis run error: ' + err.message);
      if (btn) { btn.disabled = false; btn.textContent = 'Start Analysis'; btn.classList.remove('is-loading'); }
      return;
    }
  } else {
    if (!SELECTED_SINGLE_FILE) {
      alert('Please select an SVG file to analyze.');
      return;
    }
    const formData = new FormData();
    formData.append('file', SELECTED_SINGLE_FILE, SELECTED_SINGLE_FILE.name);
    formData.append('levels', levels);
    formData.append('mode', mode);
    formData.append('overwrite', overwrite ? 'true' : 'false');

    if (btn) { btn.disabled = true; btn.textContent = 'Running…'; btn.classList.add('is-loading'); }
    try {
      res = await API.runSingleAnalysis(formData);
      consoleLabel = SELECTED_SINGLE_FILE.name;
    } catch (err) {
      alert('Analysis run error: ' + err.message);
      if (btn) { btn.disabled = false; btn.textContent = 'Start Analysis'; btn.classList.remove('is-loading'); }
      return;
    }
  }

  if (btn) { btn.disabled = false; btn.textContent = 'Start Analysis'; btn.classList.remove('is-loading'); }

  if (res && res.job_id) {
    if (typeof openAnalysisConsole === 'function') {
      openAnalysisConsole(res.job_id, CURRENT_TARGET_TYPE, consoleLabel);
    }
  } else {
    await initDashboardLive();
  }
}

async function deleteSelectedPackages() {
  const selected = Array.from(selectedFolders);
  if (selected.length === 0) {
    alert('Please select at least one package to delete first.');
    return;
  }

  openConfirmModal(
    'Delete Selected Packages?',
    `Are you sure you want to permanently delete the ${selected.length} selected package(s) from disk?`,
    async function() {
      try {
        await API.deletePackages(selected);
        selectedFolders.clear();
        await initDashboardLive(true);
      } catch (err) {
        alert('Delete operation failed: ' + err.message);
      }
    }
  );
}

document.addEventListener('DOMContentLoaded', () => {
  if (window.location.protocol === 'file:') {
    const banner = document.getElementById('fileProtocolBanner');
    if (banner) banner.style.display = 'block';
    const badge = document.getElementById('serverBadge');
    if (badge) badge.textContent = 'Static Mode';
    if (badge) badge.classList.remove('online');
  } else {
    refreshServerBadge();
  }
  initDashboardLive();
});

