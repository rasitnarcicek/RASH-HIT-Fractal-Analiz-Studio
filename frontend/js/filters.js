/**
 * RASH-HIT Fractal Studio - Output & Metric Filter Engine
 */

let filterDebounceTimer = null;

/** ISSUE-010: debounced filter entry point - avoids rebuilding the full card
 * grid on every keystroke (search input) while keeping instant behavior for
 * explicit button clicks (applyFilters() is called directly there). */
function debouncedApplyFilters() {
  if (filterDebounceTimer) clearTimeout(filterDebounceTimer);
  filterDebounceTimer = setTimeout(() => {
    filterDebounceTimer = null;
    applyFilters();
  }, 150);
}

/** Return true when the package matches the currently checked Output Filters
 *  (fltHtml / fltPdf / fltXlsx / fltTables / fltSvg / fltManifest). A package
 *  must own at least ONE of the checked output types to pass; when no output
 *  filter is checked, every package passes (no output-type restriction). */
function packagePassesOutputTypeFilters(p) {
  const types = [
    ['fltHtml', !!p.report_url],
    ['fltPdf', !!p.report_pdf_url],
    ['fltXlsx', !!p.workbook_url],
    ['fltTables', !!p.tables_url],
    ['fltSvg', !!(p.svg_maps && p.svg_maps.length)],
    ['fltManifest', !!p.manifest_url],
  ];
  const active = types.filter(([id]) => {
    const el = document.getElementById(id);
    return el && el.checked;
  });
  if (!active.length) return true; // no output-type restriction active
  return active.some(([, has]) => has);
}

/** Return the list of checked Report Sections ids (secResult/secGrid/secGallery/
 *  secFiles/secValidation) - mirrors the reference dashboard's cb-sec getter. */
function getReportSections() {
  return ['secResult', 'secGrid', 'secGallery', 'secFiles', 'secValidation']
    .filter(id => {
      const el = document.getElementById(id);
      return el && el.checked;
    });
}

function applyFilters() {
  const q = (document.getElementById('searchInput')?.value || '').toLowerCase();
  const idf = (document.getElementById('idFilterInput')?.value || '').trim();
  const minDb = parseFloat(document.getElementById('minDb')?.value || -999);
  const maxDb = parseFloat(document.getElementById('maxDb')?.value || 999);
  const minR2 = parseFloat(document.getElementById('minR2')?.value || -999);
  const maxR2 = parseFloat(document.getElementById('maxR2')?.value || 999);
  const minL = parseInt(document.getElementById('minLevelCount')?.value || 0, 10);
  const maxL = parseInt(document.getElementById('maxLevelFilter')?.value || 999, 10);
  const maxRuntime = parseFloat(document.getElementById('maxRuntime')?.value || 9999999);
  const idTerms = idf ? idf.split(',').map(s => s.trim().toLowerCase()).filter(Boolean) : [];

  const baseList = PACKAGES || [];

  visiblePackages = baseList.filter(p => {
    if (q) {
      const matchName = (p.motif || '').toLowerCase().includes(q) || (p.folder || '').toLowerCase().includes(q) || (p.source_file || '').toLowerCase().includes(q);
      if (!matchName) return false;
    }
    if (idTerms.length > 0) {
      // ID filter: match motif / folder / source file against any comma-separated term
      const ns = ((p.motif || '') + ' ' + (p.source_file || '') + ' ' + (p.folder || '')).toLowerCase();
      if (!idTerms.some(t => ns.includes(t))) return false;
    }
    if (!packagePassesOutputTypeFilters(p)) return false;

    const db = p.db || 0;
    if (db < minDb || db > maxDb) return false;

    const r2 = p.r2 || 0;
    if (r2 < minR2 || r2 > maxR2) return false;

    const lvls = p.levels || p.computed_levels_count || 0;
    if (lvls < minL || lvls > maxL) return false;

    const timeMs = p.total_time_ms || 0;
    if (timeMs > maxRuntime) return false;

    return true;
  });

  applySorting();
  populateLibraryChecklist();
  updateViewBadges();
}

function resetFilters() {
  const ids = ['searchInput', 'idFilterInput', 'minDb', 'maxDb', 'minR2', 'maxR2', 'minLevelCount', 'maxLevelFilter', 'maxRuntime', 'librarySearch'];
  ids.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });
  // Re-check every output-type and report-section checkbox.
  document.querySelectorAll('#acc-outputs input[type=checkbox]').forEach(c => { c.checked = true; });
  document.querySelectorAll('#acc-sections input[type=checkbox]').forEach(c => { c.checked = true; });

  applyFilters();
}

/** Filter the library checklist by the library search box (client-side). */
function applyLibrarySearch(value) {
  const q = (value || '').toLowerCase().trim();
  const container = document.getElementById('libraryChecklist');
  if (!container) return;
  const rows = container.querySelectorAll('label.cb-label');
  if (!q) {
    rows.forEach(r => { r.style.display = ''; });
    return;
  }
  rows.forEach(r => {
    r.style.display = (r.textContent || '').toLowerCase().includes(q) ? '' : 'none';
  });
}

function populateLibraryChecklist() {
  const container = document.getElementById('libraryChecklist');
  if (!container) return;

  const list = visiblePackages || [];
  if (!list.length) {
    container.innerHTML = `<div style="font-size:11px;color:var(--muted);">${'No packages available'}</div>`;
    return;
  }

  container.innerHTML = list.map(p => {
    const folder = p.folder || '';
    const isChecked = selectedFolders.has(folder);
    return `
      <label class="cb-label" style="font-size:11px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
        <input type="checkbox" data-folder="${folder}" ${isChecked ? 'checked' : ''} onchange="onAnalysisCbChange('${folder}', this.checked)">
        <span>${escapeHtml(p.motif || folder)}</span>
      </label>
    `;
  }).join('');

  // Re-apply the live library search box filter (if any).
  const search = document.getElementById('librarySearch');
  if (search && search.value) applyLibrarySearch(search.value);
}

function selectAllPackages(checked) {
  if (checked) {
    (visiblePackages || []).forEach(p => {
      if (p.folder) selectedFolders.add(p.folder);
    });
  } else {
    selectedFolders.clear();
  }
  if (typeof updateSelectionToolbar === 'function') updateSelectionToolbar();
  if (typeof renderCurrentView === 'function') renderCurrentView();
  populateLibraryChecklist();
  updateViewBadges();
}

function selectVisible() {
  selectAllPackages(true);
}

function clearSelection() {
  selectAllPackages(false);
}
