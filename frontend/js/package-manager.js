/**
 * RASH-HIT Fractal Studio - Package Renderer & List Manager
 * Card links use backend-provided URL fields (report_url, tables_url, ...)
 * with folder-based fallback ONLY when a field is missing.
 */

function escapeHtml(str) {
  if (str == null) return '';
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
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

function attrSafe(str) {
  return escapeHtml(str);
}

/** Escape a value for embedding inside a single-quoted JS string in an onclick attribute. */
function jsQuote(str) {
  return String(str == null ? '' : str).replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/"/g, '&quot;');
}

function escapeJsString(str) {
  return jsQuote(str);
}

/** Build an anchor button. Returns '' when href is null so no dead button renders. */
function actionBtn(href, label, cls, testid) {
  if (!href) return '';
  return `<a href="${attrSafe(href)}" target="_blank" rel="noopener" class="btn btn-sm ${cls || ''}"${testid ? ` data-testid="${testid}"` : ''}>${label}</a>`;
}

/**
 * Packages used by the detail / metrics-table / files / gallery / tables views:
 * the user's selection wins (old-dashboard behavior), otherwise all visible ones.
 */
function getViewPackages() {
  if (typeof selectedFolders !== 'undefined' && selectedFolders.size > 0) {
    return PACKAGES.filter(p => selectedFolders.has(p.folder));
  }
  return visiblePackages;
}

function renderOverviewView() {
  const t0 = performance.now();
  const container = document.getElementById('cardsGrid');
  const emptyEl = document.getElementById('emptyOverview');
  if (!container) return;

  // Reference-dashboard behavior: when packages are selected, unselected cards
  // are hidden via classList (kept in the DOM so their checkboxes remain
  // selectable state) - NOT removed and re-rendered from scratch.
  let list = visiblePackages.length > 0 ? visiblePackages : [];
  if (list.length === 0) {
    container.innerHTML = '';
    if (emptyEl) emptyEl.style.display = 'block';
    updateSelectionToolbar();
    return;
  }

  if (emptyEl) emptyEl.style.display = 'none';

  // Render every visible card once, then toggle .hidden to echo the selection
  // without destroying the checkbox DOM (reference behavior).
  container.innerHTML = list.map(p => {
    const db_str = p.db != null ? parseFloat(p.db).toFixed(4) : 'N/A';
    const r2_str = p.r2 != null ? parseFloat(p.r2).toFixed(4) : 'N/A';
    const levels_s = p.levels || p.computed_levels_count || 'N/A';
    const gen_at = p.generated_at || 'N/A';
    const motif = p.motif || 'N/A';
    const folder = p.folder || '';

    // Versioning metadata: distinguish multiple runs of the same motif.
    const package_version = p.package_version || 'v1';
    const is_versioned = !!(p.package_version && p.package_version !== 'v1');

    // Status badge (complete / partial / broken) styled using design-system badges.
    const st = (p.status || '').toLowerCase();
    let badgeClass = 'badge-muted';
    if (st.includes('complete') || st === 'ok' || st === 'done') {
      badgeClass = 'badge-ok';
    } else if (st.includes('partial') || st.includes('warn')) {
      badgeClass = 'badge-warn';
    } else if (st.includes('broken') || st.includes('err') || st.includes('fail') || st.includes('missing')) {
      badgeClass = 'badge-missing';
    }
    const statusBadge = st
      ? `<span class="badge ${badgeClass}" style="margin-left:auto;">${escapeHtml(p.status || '')}</span>`
      : '';

    const isChecked = selectedFolders.has(folder) ? 'checked' : '';
    const selClass = isChecked ? 'style="border-color:var(--accent);background:var(--soft);"' : '';

    // Prefer backend-provided URL fields when present; fall back to relative subfolder path.
    const report_href = p.report_url || (folder ? folder + '/report/report.html' : '#');

    // Version chip element rendered next to the motif title if present (plain).
    const versionChip = is_versioned
      ? `<b title="${'Run Version'}" style="font-size:10px;font-weight:800;color:var(--text);border:1px solid var(--border);border-radius:999px;padding:1px 8px;background:var(--panel2);">${escapeHtml(package_version)}</b>`
      : '';

    return `
      <div class="pkg-card" data-testid="pkg-card" data-folder="${escapeHtml(folder)}" ${selClass}>
        <div class="pkg-card-header">
          <input type="checkbox" class="pkg-check" aria-label="${escapeHtml('Select ' + motif)}" onchange="togglePackageSelection('${escapeJsString(folder)}')" ${isChecked}>
          <div class="pkg-name" title="${escapeHtml(motif)}">${escapeHtml(motif)}</div>
          ${versionChip}
          ${statusBadge}
        </div>
        <div class="pkg-meta">
          <span>${'Db:'} <b>${db_str}</b></span>
          <span>${'R²:'} <b>${r2_str}</b></span>
          <span>${'Levels:'} <b>${levels_s}</b></span>
          <span style="grid-column:1/-1;">${'Generated:'} <b>${escapeHtml(gen_at)}</b></span>
        </div>
        <div style="display:flex;gap:6px;margin-top:12px;flex-wrap:wrap;">
          ${actionBtn(report_href, 'Open Report', 'btn-primary', 'card-report-btn')}
          <button class="btn btn-sm" data-testid="card-folder-btn" onclick="openPackageFolder('${escapeJsString(folder)}')">${'📂 Open Folder'}</button>
          <button class="btn btn-sm btn-soft" data-testid="card-details-btn" onclick="openPackageDrawer('${escapeJsString(folder)}')">${'Details'}</button>
        </div>
      </div>
    `;
  }).join('');

  // Selection no longer hides other cards (item 4): selecting a card must NOT
  // filter the grid. We only mark the selected card visually via .is-selected.
  container.querySelectorAll('[data-testid="pkg-card"]').forEach(card => {
    const f = card.getAttribute('data-folder');
    card.classList.toggle('is-selected', selectedFolders.has(f));
  });

  if (emptyEl) {
    const visCount = container.querySelectorAll('[data-testid="pkg-card"]').length;
    emptyEl.style.display = visCount === 0 ? 'block' : 'none';
  }

  updateSelectionToolbar();
  if (typeof perfLog === 'function') perfLog(`renderOverviewView (packages=${list.length})`, t0);
}

/**
 * Open the package folder: render its contents directly on screen via the
 * Folder Browser modal (server provides the file listing). Falls back to the
 * path-copy modal when the server is unavailable (file:// mode).
 */
async function openPackageFolder(folder) {
  if (!folder) return;
  if (typeof openFolderBrowser === 'function') {
    openFolderBrowser(folder);
    return;
  }
  // Legacy fallback when ui.js is not loaded on the current page.
  try {
    const res = await API.openFolder(folder);
    if (res && res.ok) return;
    if (typeof openFolderPathModal === 'function') openFolderPathModal(folder);
  } catch (err) {
    if (typeof openFolderPathModal === 'function') openFolderPathModal(folder);
  }
}

/**
 * Whole-card click handler: card click selection is disabled to restrict
 * selection ONLY to checkboxes.
 */
function onCardClick(folder, ev) {
  // Disabled
}

function togglePackageSelection(folder, forcedState) {
  if (!folder) return;
  if (forcedState !== undefined) {
    if (forcedState) selectedFolders.add(folder);
    else selectedFolders.delete(folder);
  } else {
    if (selectedFolders.has(folder)) {
      selectedFolders.delete(folder);
    } else {
      selectedFolders.add(folder);
    }
  }
  updateSelectionToolbar();
  if (typeof updateExportModalCounts === 'function') updateExportModalCounts();
  if (typeof updateViewBadges === 'function') updateViewBadges();
  // Live-update the overview grid so non-selected cards collapse immediately
  // (old-dashboard behavior: the overview echoes the current selection).
  if (CURRENT_VIEW_MODE === 'overview' && typeof renderOverviewView === 'function') {
    renderOverviewView();
  }
}

function onCardCbChange(folder, checked) {
  togglePackageSelection(folder, checked);
}

function applySorting() {
  const sel = document.getElementById('sortSelect');
  if (!sel) return;
  const val = sel.value;

  visiblePackages.sort((a, b) => {
    if (val === 'date-desc') return (b.generated_at || '').localeCompare(a.generated_at || '');
    if (val === 'date-asc') return (a.generated_at || '').localeCompare(b.generated_at || '');
    if (val === 'name-asc') return (a.motif || '').localeCompare(b.motif || '');
    if (val === 'name-desc') return (b.motif || '').localeCompare(a.motif || '');
    if (val === 'db-desc') return (b.db || 0) - (a.db || 0);
    if (val === 'db-asc') return (a.db || 0) - (b.db || 0);
    if (val === 'r2-desc') return (b.r2 || 0) - (a.r2 || 0);
    if (val === 'r2-asc') return (a.r2 || 0) - (b.r2 || 0);
    if (val === 'levels-desc') return (b.levels || 0) - (a.levels || 0);
    if (val === 'levels-asc') return (a.levels || 0) - (b.levels || 0);
    return 0;
  });

  renderCurrentView();
}

function openSelectedReports() {
  selectedFolders.forEach(folder => {
    // Prefer backend URL when available; fall back to folder-based path.
    const p = PACKAGES.find(x => x.folder === folder);
    const href = (p && p.report_url) ? p.report_url : (folder + '/report/report.html');
    window.open(href, '_blank');
  });
}

/** Render current active view depending on CURRENT_VIEW_MODE */
function renderCurrentView() {
  const mode = typeof CURRENT_VIEW_MODE !== 'undefined' ? CURRENT_VIEW_MODE : 'overview';
  if (mode === 'overview') renderOverviewView();
  else if (mode === 'detail') renderDetailView();
  else if (mode === 'grid-overview') renderGridOverviewView();
  else if (mode === 'svg-maps') renderSvgMapsView();
  else if (mode === 'files') renderFilesView();
  else if (mode === 'compare') renderCompareView();
  else if (mode === 'tables') renderTablesView();
}

function renderDetailView() {
  const container = document.getElementById('detailContainer');
  if (!container) return;

  // Reference-dashboard behavior: when several packages are selected, show an
  // "Active Package" dropdown; activeDetailFolder remembers the last choice.
  const sel = (selectedFolders.size > 0) ? Array.from(selectedFolders) : (visiblePackages || []).map(p => p.folder);
  const targetFolder = (activeDetailFolder && sel.includes(activeDetailFolder))
    ? activeDetailFolder
    : (sel[0] || '');
  const pkg = PACKAGES.find(p => p.folder === targetFolder);

  if (!pkg) {
    container.innerHTML = `<div class="empty-state"><div class="es-i">📄</div><h2>${'No analysis package selected'}</h2><p>${'Please select a package from the library.'}</p></div>`;
    return;
  }

  const folder = pkg.folder || '';
  const report_href = pkg.report_url || (folder ? folder + '/report/report.html' : '#');
  const pdf_href = pkg.report_pdf_url || (folder ? folder + '/report/report.pdf' : '#');
  const tables_href = pkg.tables_url || (folder ? folder + '/tables/tables.html' : '#');
  const wb_href = pkg.workbook_url || (folder ? folder + '/excel/workbook.xlsx' : '#');
  const manifest_href = pkg.manifest_url || (folder ? folder + '/manifest/manifest.json' : '#');

  // Report Section toggles (secResult / secGrid / secGallery / secFiles / secValidation).
  const secs = (typeof getReportSections === 'function')
    ? getReportSections()
    : ['secResult', 'secGrid', 'secGallery', 'secFiles', 'secValidation'];
  const hasSec = id => secs.includes(id);

  let dropdown = '';
  if (sel.length > 1) {
    dropdown = `<div style="display:flex;align-items:center;gap:10px;background:var(--panel2);padding:10px 14px;border-radius:8px;border:1px solid var(--border);margin-bottom:16px;flex-wrap:wrap;">
      <strong style="font-size:12px;color:var(--muted);">${'Active Package ('}${sel.length}${' selected):'}</strong>
      <select aria-label="Active package" class="sb-input" style="width:auto;margin:0;padding:5px 10px;font-size:12px;" onchange="activeDetailFolder=this.value;renderDetailView();">
        ${sel.map(f2 => {
          const p2 = PACKAGES.find(x => x.folder === f2);
          return `<option value="${escapeHtml(f2)}" ${f2 === folder ? 'selected' : ''}>${escapeHtml((p2 && (p2.motif || p2.source_file)) || f2)}</option>`;
        }).join('')}
      </select>
    </div>`;
  }

  const srcName = pkg.source_file ? String(pkg.source_file).split(/[\\/]/).pop() : 'N/A';
  const genAt = pkg.generated_at ? ` &middot; ${escapeHtml(pkg.generated_at)}` : '';
  const header = `<div style="display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid var(--border);padding-bottom:14px;margin-bottom:20px;flex-wrap:wrap;gap:12px;">
    <div>
      <h2 style="font-size:22px;font-weight:800;color:var(--text);margin:0;">${escapeHtml(pkg.motif || 'N/A')}</h2>
      <div style="font-size:12px;color:var(--muted);margin-top:2px;">${escapeHtml(srcName)} &middot; Folder: <code style="color:var(--accent);">${escapeHtml(folder)}</code>${genAt}</div>
    </div>
    <div style="display:flex;gap:8px;flex-wrap:wrap;">
      ${actionBtn(report_href, 'Open Full Report ↗', 'btn-primary')}
      ${actionBtn(pdf_href, 'PDF')}
      ${actionBtn(tables_href, 'Tables Viewer')}
      ${actionBtn(wb_href, 'Workbook (.xlsx)')}
      ${actionBtn(manifest_href, 'Manifest (.json)')}
    </div>
  </div>`;

  const resultCard = hasSec('secResult') ? `<div style="background:var(--panel);border:1px solid var(--border);border-radius:var(--radius-lg);padding:16px;box-shadow:var(--shadow);margin-bottom:16px;">
    <h3 style="font-size:14px;font-weight:800;margin-bottom:10px;">${'Fractal Analysis Result'}</h3>
    <div class="kpi-row">
      <div class="kpi-card"><div class="kpi-lbl">${'Db Dimension'}</div><div class="kpi-val">${pkg.db != null ? parseFloat(pkg.db).toFixed(4) : 'N/A'}</div><div class="kpi-sub">${'box-counting'}</div></div>
      <div class="kpi-card"><div class="kpi-lbl">${'Linear Fit (R²)'}</div><div class="kpi-val">${pkg.r2 != null ? parseFloat(pkg.r2).toFixed(4) : 'N/A'}</div><div class="kpi-sub">${'regression fit'}</div></div>
      <div class="kpi-card"><div class="kpi-lbl">${'Grid Levels'}</div><div class="kpi-val">${pkg.levels || pkg.computed_levels_count || 'N/A'}</div><div class="kpi-sub">${'total levels'}</div></div>
      <div class="kpi-card"><div class="kpi-lbl">${'Execution Time'}</div><div class="kpi-val">${pkg.total_time_ms != null ? parseFloat(pkg.total_time_ms).toFixed(2) + ' ms' : 'N/A'}</div><div class="kpi-sub">${'pipeline ms'}</div></div>
    </div>
  </div>` : '';

  const gridCard = hasSec('secGrid') ? `<div style="background:var(--panel);border:1px solid var(--border);border-radius:var(--radius-lg);padding:16px;box-shadow:var(--shadow);margin-bottom:16px;">
    <h3 style="font-size:14px;font-weight:800;margin-bottom:10px;">${'Calculated Grid Levels Preview'}</h3>
    <div style="overflow-x:auto;">
      <table>
        <thead><tr><th>${'Level'}</th><th>${'Grid (WxH)'}</th><th>${'1/r'}</th><th>${'Occupied'}</th><th>${'Total'}</th><th>${'Occupancy %'}</th></tr></thead>
        <tbody>
          ${(pkg.scale_rows || pkg.scale_table || []).map(r => `
            <tr>
              <td>${formatLvl(r.level || r.grid_level || 0)}</td>
              <td>${r.grid_label || (r.box_size_w ? `${r.box_size_w}x${r.box_size_h}` : 'N/A')}</td>
              <td class="num">${r.inv_box_size != null ? parseFloat(r.inv_box_size).toFixed(2) : 'N/A'}</td>
              <td class="num">${r.occupied_count != null ? r.occupied_count : 'N/A'}</td>
              <td class="num">${r.total_count != null ? r.total_count : 'N/A'}</td>
              <td class="num">${r.occupancy_percent != null ? parseFloat(r.occupancy_percent).toFixed(2) + '%' : 'N/A'}</td>
            </tr>
          `).join('') || '<tr><td colspan="6" style="text-align:center;color:var(--muted);">' + 'Grid occupancy rows available in HTML report.' + '</td></tr>'}
        </tbody>
      </table>
    </div>
  </div>` : '';

  const galleryCard = hasSec('secGallery') ? `<div style="background:var(--panel);border:1px solid var(--border);border-radius:var(--radius-lg);padding:16px;box-shadow:var(--shadow);margin-bottom:16px;">
    <h3 style="font-size:14px;font-weight:800;margin-bottom:10px;">${'SVG Gallery'}</h3>
    ${(pkg.svg_maps && pkg.svg_maps.length) ? `<div class="svg-gallery-grid">
      ${pkg.svg_maps.map(m => {
        const lt = formatLvl(m.level || '?');
        const lb = (pkg.motif || '') + ' · ' + lt;
        return `<div class="svg-thumb-card">
        <div style="display:flex;justify-content:space-between;align-items:center;font-size:11.5px;font-weight:700;margin-bottom:2px;">
          <b style="font-size:10px;font-weight:800;color:var(--text);">${lt}</b>
        </div>
        <button type="button" class="svg-img-container" aria-label="${escapeHtml('Preview ' + lt)}" onclick="openSvgModal('${jsQuote(m.url)}', '${jsQuote(lb)}')">
          <img src="${attrSafe(m.url)}" alt="${escapeHtml(pkg.motif)} ${lt}" loading="lazy" decoding="async">
        </button>
        <div style="display:flex;gap:6px;margin-top:2px;">
          <a href="${attrSafe(m.url)}" target="_blank" rel="noopener" class="btn btn-sm" style="flex:1;">${'SVG'}</a>
        </div>
      </div>`;
      }).join('')}
    </div>` : '<div style="text-align:center;padding:14px;color:var(--muted);font-size:12px;">' + 'No SVG maps available for this package.' + '</div>'}
  </div>` : '';
  window.RASH_HIT_GALLERY = (pkg.svg_maps || []).map(m => ({
    src: m.url,
    label: (pkg.motif || '') + ' · ' + formatLvl(m.level || '?'),
  }));

  const filesCard = hasSec('secFiles') ? `<div style="background:var(--panel);border:1px solid var(--border);border-radius:var(--radius-lg);padding:16px;box-shadow:var(--shadow);margin-bottom:16px;">
    <h3 style="font-size:14px;font-weight:800;margin-bottom:10px;">${'Package Files'}</h3>
    <div style="display:flex;flex-direction:column;gap:6px;">
      ${actionBtn(report_href, '📄 report.html')}
      ${actionBtn(pdf_href, '📕 report.pdf')}
      ${actionBtn(tables_href, '📊 tables.html')}
      ${actionBtn(wb_href, '📈 workbook.xlsx')}
      ${actionBtn(manifest_href, '🔒 manifest.json')}
    </div>
  </div>` : '';

  const warnCard = hasSec('secValidation') ? `<div style="background:var(--panel);border:1px solid var(--border);border-radius:var(--radius-lg);padding:16px;box-shadow:var(--shadow);">
    <h3 style="font-size:14px;font-weight:800;margin-bottom:10px;">${'Validation / Warnings'}</h3>
    ${(pkg.warnings && pkg.warnings.length) ? pkg.warnings.map(w => `<div style="font-size:12px;padding:6px 10px;background:var(--warn-bg);color:var(--warn);border-radius:6px;margin-bottom:4px;">${escapeHtml(typeof w === 'string' ? w : (w.message || w))}</div>`).join('') : '<div style="text-align:center;padding:14px;color:var(--muted);font-size:12px;">' + 'No warnings recorded for this package.' + '</div>'}
  </div>` : '';

  container.innerHTML = `<div>${dropdown}${header}${resultCard}${gridCard}${galleryCard}${filesCard}${warnCard}</div>`;
}

function renderGridOverviewView() {
  const container = document.getElementById('gridOverviewContainer');
  if (!container) return;

  // Old-dashboard behavior: each selected (or visible) package renders its own
  // Level Metrics Table card with the per-level grid occupancy rows.
  const list = getViewPackages();
  if (!list.length) {
    const hint = (typeof selectedFolders !== 'undefined' && selectedFolders.size > 0)
      ? 'Your selection contains no packages. Clear the selection to see all visible packages.'
      : 'No packages available for grid metrics table';
    container.innerHTML = `<div class="empty-state"><div class="es-i">📊</div><h2>${hint}</h2></div>`;
    return;
  }

  // The container (#gridOverviewContainer) is a responsive 2-column grid; every
  // package renders its own Level Metrics Table card side by side.
  container.innerHTML = list.map(p => {
      const folder = p.folder || '';
      const report_href = p.report_url || (folder ? folder + '/report/report.html' : '#');
      const rows = p.scale_rows || [];
      const levelRows = rows.length
        ? `<div style="overflow-x:auto;">
            <table>
              <thead><tr><th>${'Level'}</th><th>${'Grid'}</th><th class="num">${'Total Cells'}</th><th class="num">${'Filled'}</th><th class="num">${'Empty'}</th><th class="num">${'Occupancy %'}</th><th>${'Cell Size'}</th></tr></thead>
              <tbody>
                ${rows.map(r => `
                  <tr>
                    <td><b>${formatLvl(r.level != null ? r.level : '')}</b></td>
                    <td><code>${escapeHtml(r.grid_label || r.grid || 'N/A')}</code></td>
                    <td class="num">${r.total_count != null ? r.total_count : 'N/A'}</td>
                    <td class="num">${r.occupied_count != null ? r.occupied_count : 'N/A'}</td>
                    <td class="num">${r.empty_count != null ? r.empty_count : 'N/A'}</td>
                    <td class="num">${r.occupancy_percent != null ? r.occupancy_percent + '%' : 'N/A'}</td>
                    <td><code>${escapeHtml(r.cell_size || 'N/A')}</code></td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>`
        : '<div style="text-align:center;padding:14px;color:var(--muted);font-size:12px;">' + 'No level metrics available for this package.' + '</div>';

      return `
        <div style="background:var(--panel);border:1px solid var(--border);border-radius:var(--radius-lg);padding:16px;box-shadow:var(--shadow);">
          <div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;border-bottom:1px solid var(--border);padding-bottom:10px;margin-bottom:12px;">
            <div>
              <strong style="font-size:14px;color:var(--text);">${escapeHtml(p.motif || 'N/A')}</strong>
              <div style="font-size:11px;color:var(--accent);font-weight:700;margin-top:2px;">${'Db:'} ${p.db != null ? parseFloat(p.db).toFixed(4) : 'N/A'}</div>
            </div>
            <a href="${attrSafe(report_href)}" target="_blank" rel="noopener" class="btn btn-sm btn-primary">${'Open Report'}</a>
          </div>
          ${levelRows}
        </div>
      `;
    }).join('');
}

function renderSvgMapsView() {
  const container = document.getElementById('svgGalleryContainer');
  if (!container) return;

  const list = getViewPackages();
  const maps = [];
  list.forEach(p => {
    if (p.svg_maps && p.svg_maps.length) {
      p.svg_maps.forEach(m => {
        const lt = formatLvl(m.level || '?');
        maps.push({
          motif: p.motif, folder: p.folder, level: m.level, url: m.url,
          label: (p.motif || 'N/A') + ' · ' + lt,
        });
      });
    }
  });

  if (!maps.length) {
    container.innerHTML = `<div class="empty-state"><div class="es-i">🖼️</div><h2>${'No SVG maps available in visible packages'}</h2></div>`;
    return;
  }

  // Feed the preview modal so arrows/zoom can browse every visible map.
  window.RASH_HIT_GALLERY = maps.map(m => ({ src: m.url, label: m.label }));
  const lvlLabel = (lvl) => formatLvl(lvl || '?');

  // Group each package's maps under its own category header so the gallery
  // never mixes different packages' images together.
  container.innerHTML = list.map(p => {
    const pmaps = (p.svg_maps || []).filter(Boolean);
    if (!pmaps.length) return '';
    return `
      <div class="svg-pkg-group">
        <div class="svg-pkg-group-hdr">
          <strong>${escapeHtml(p.motif || 'N/A')}</strong>
          <code>${escapeHtml(p.folder || '')}</code>
        </div>
        <div class="svg-gallery-grid">
          ${pmaps.map(m => {
            const lt = lvlLabel(m.level);
            const lb = (p.motif || 'N/A') + ' · ' + lt;
            return `
            <div class="svg-thumb-card">
              <div style="display:flex;justify-content:space-between;align-items:center;font-size:11.5px;font-weight:700;margin-bottom:2px;">
                <b style="font-size:10px;font-weight:800;color:var(--text);">${lt}</b>
              </div>
              <button type="button" class="svg-img-container" aria-label="${escapeHtml('Preview ' + p.motif + ' ' + lt)}" onclick="openSvgModal('${jsQuote(m.url)}', '${jsQuote(lb)}')">
                <img src="${attrSafe(m.url)}" alt="${escapeHtml(p.motif)} ${lt}" loading="lazy" decoding="async">
              </button>
              <div style="display:flex;gap:6px;margin-top:2px;">
                <a href="${attrSafe(m.url)}" target="_blank" rel="noopener" class="btn btn-sm" style="flex:1;">${'SVG'}</a>
              </div>
            </div>
          `;
          }).join('')}
        </div>
      </div>
    `;
  }).join('');
}

function renderFilesView() {
  const container = document.getElementById('filesContainer');
  if (!container) return;

  const list = getViewPackages();
  if (!list.length) {
    const hint = (typeof selectedFolders !== 'undefined' && selectedFolders.size > 0)
      ? 'Your selection contains no packages. Clear the selection to see all visible packages.'
      : 'No package files available';
    container.innerHTML = `<div class="empty-state" style="grid-column:1/-1;"><div class="es-i">📁</div><h2>${hint}</h2></div>`;
    return;
  }

  container.innerHTML = list.map(p => {
    const folder = p.folder || '';
    const report_href = p.report_url || (folder ? folder + '/report/report.html' : '#');
    const pdf_href = p.report_pdf_url || (folder ? folder + '/report/report.pdf' : '#');
    const tables_href = p.tables_url || (folder ? folder + '/tables/tables.html' : '#');
    const wb_href = p.workbook_url || (folder ? folder + '/excel/workbook.xlsx' : '#');
    const manifest_href = p.manifest_url || (folder ? folder + '/manifest/manifest.json' : '#');
    const data_href = p.tables_data_url || (folder ? folder + '/tables/tables_data.json' : '#');

    // Reference-dashboard style grouping (Academic Reports / Excel & Tables /
    // Reproducibility / Grid Figures / Cell Tables).
    const reports = [
      ['📄 report.html', report_href, 'HTML'],
      ['📕 report.pdf', pdf_href, 'PDF'],
    ].filter(x => x[1] !== '#');
    const excelTables = [
      ['📊 tables.html', tables_href, 'Tables'],
      ['📈 workbook.xlsx', wb_href, 'Excel'],
    ].filter(x => x[1] !== '#');
    const repro = [
      ['🔒 manifest.json', manifest_href, 'Manifest'],
      ['🧾 tables_data.json', data_href, 'JSON'],
    ].filter(x => x[1] !== '#');
    const figures = (p.svg_maps || []).map(m => [
      `🖼️ ${m.file_name || (formatLvl(m.level || '?')) + '.svg'}`, m.url || (folder + '/' + (m.rel_path || '')), 'SVG'
    ]);
    const cellTables = (p.xlsx_cells || []).map(c => [
      `📊 ${c.file_name || ''}`, c.url || (folder + '/' + (c.rel_path || '')), 'XLSX'
    ]);

    // Compact single table per package: columns Motif | File | Type | Open.
    // Replaces the previous chunk-grouped boxes that wasted horizontal space.
    const allFiles = [
      ...reports.map(x => ({ t: x[0], href: x[1], badge: x[2] })),
      ...excelTables.map(x => ({ t: x[0], href: x[1], badge: x[2] })),
      ...repro.map(x => ({ t: x[0], href: x[1], badge: x[2] })),
      ...figures.map(x => ({ t: x[0], href: x[1], badge: x[2] })),
      ...cellTables.map(x => ({ t: x[0], href: x[1], badge: x[2] })),
    ].filter(f => f.href !== '#');

    if (!allFiles.length) {
      return `
        <div class="matrix-col">
          <div class="matrix-col-hdr">
            <strong style="color:var(--text);">${escapeHtml(p.motif || 'N/A')}</strong>
          </div>
          <div style="padding:14px;color:var(--muted);font-size:12px;">${'No package files available.'}</div>
        </div>`;
    }

    return `
      <div class="matrix-col">
        <div class="matrix-col-hdr">
          <strong style="color:var(--text);">${escapeHtml(p.motif || 'N/A')}</strong>
        </div>
        <div style="overflow-x:auto;">
          <table class="files-table">
            <thead><tr><th>${'File'}</th><th>${'Type'}</th><th class="num"></th></tr></thead>
            <tbody>
              ${allFiles.map(f => `
                <tr>
                  <td style="font-family:Consolas,monospace;font-size:12px;">${escapeHtml(f.t)}</td>
                  <td><span class="badge badge-version">${escapeHtml(f.badge)}</span></td>
                  <td class="num"><a class="btn btn-sm" href="${attrSafe(f.href)}" target="_blank" rel="noopener">${'Open'}</a></td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  }).join('');
}

function renderTablesView() {
  const container = document.getElementById('tablesContainer');
  if (!container) return;

  const list = getViewPackages();
  if (!list.length) {
    const hint = (typeof selectedFolders !== 'undefined' && selectedFolders.size > 0)
      ? 'Your selection contains no packages. Clear the selection to see all visible packages.'
      : 'No spatial table files available';
    container.innerHTML = `<div class="empty-state"><div class="es-i">🔢</div><h2>${hint}</h2></div>`;
    return;
  }

  container.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>${'Motif Package'}</th>
          <th>${'Spatial Coordinates File'}</th>
          <th>${'Level Tables'}</th>
          <th>${'Workbook'}</th>
          <th>${'Actions'}</th>
        </tr>
      </thead>
      <tbody>
        ${list.map(p => {
          const folder = p.folder || '';
          const tables_href = p.tables_url || (folder ? folder + '/tables/tables.html' : '#');
          const wb_href = p.workbook_url || (folder ? folder + '/excel/workbook.xlsx' : '#');
          return `
            <tr>
              <td><strong>${escapeHtml(p.motif || 'N/A')}</strong><br><code style="font-size:11px;color:var(--muted);">${escapeHtml(folder)}</code></td>
              <td>tables_data.json</td>
              <td>${(p.levels || p.computed_levels_count || 0) + ' Level XLSX Sheets'}</td>
              <td>workbook.xlsx</td>
              <td>
                <a href="${attrSafe(tables_href)}" target="_blank" rel="noopener" class="btn btn-sm btn-primary">${'Open Interactive Viewer'}</a>
                <a href="${attrSafe(wb_href)}" target="_blank" rel="noopener" class="btn btn-sm">${'Download XLSX'}</a>
              </td>
            </tr>
          `;
        }).join('')}
      </tbody>
    </table>
  `;
}

function renderCompareView() {
  const container = document.getElementById('compareContainer');
  if (!container) return;

  // Use selected packages if any exist; otherwise compare all visible packages
  const pkgs = selectedFolders.size > 0
    ? PACKAGES.filter(p => selectedFolders.has(p.folder))
    : visiblePackages;

  if (!pkgs.length) {
    container.innerHTML = `<div class="empty-state"><div class="es-i">⚖️</div><h2>${'No packages selected for comparison'}</h2><p>${'Please select packages using checkboxes in the library view.'}</p></div>`;
    return;
  }

  const dbs = pkgs.map(p => p.db || 0);
  const r2s = pkgs.map(p => p.r2 || 0);
  const avgDb = dbs.reduce((a, b) => a + b, 0) / (dbs.length || 1);
  const avgR2 = r2s.reduce((a, b) => a + b, 0) / (r2s.length || 1);

  const maxDbPkg = pkgs.reduce((prev, current) => ((prev.db || 0) > (current.db || 0)) ? prev : current, pkgs[0]);
  const minDbPkg = pkgs.reduce((prev, current) => ((prev.db || 0) < (current.db || 0)) ? prev : current, pkgs[0]);

  container.innerHTML = `
    <div class="compare-summary-row">
      <div class="kpi-card"><div class="kpi-lbl">${'Compared Packages'}</div><div class="kpi-val">${pkgs.length}</div><div class="kpi-sub">${'selected items'}</div></div>
      <div class="kpi-card"><div class="kpi-lbl">${'Average Db'}</div><div class="kpi-val">${avgDb.toFixed(4)}</div><div class="kpi-sub">${'mean fractal dimension'}</div></div>
      <div class="kpi-card"><div class="kpi-lbl">${'Average R²'}</div><div class="kpi-val">${avgR2.toFixed(4)}</div><div class="kpi-sub">${'mean linear fit'}</div></div>
      <div class="kpi-card"><div class="kpi-lbl">${'Max Db Motif'}</div><div class="kpi-val" style="font-size:15px;padding-top:4px;">${escapeHtml(maxDbPkg.motif || 'N/A')}</div><div class="kpi-sub">${'Db:'} ${(maxDbPkg.db || 0).toFixed(4)}</div></div>
      <div class="kpi-card"><div class="kpi-lbl">${'Min Db Motif'}</div><div class="kpi-val" style="font-size:15px;padding-top:4px;">${escapeHtml(minDbPkg.motif || 'N/A')}</div><div class="kpi-sub">${'Db:'} ${(minDbPkg.db || 0).toFixed(4)}</div></div>
    </div>

    <div style="overflow-x:auto;background:var(--panel);border:1px solid var(--border);border-radius:var(--radius-lg);padding:16px;box-shadow:var(--shadow);">
      <table>
        <thead>
          <tr>
            <th>${'Motif Name'}</th>
            <th>${'Folder'}</th>
            <th class="num">${'Db Dimension'}</th>
            <th class="num">${'R² Fit'}</th>
            <th class="num">${'Grid Levels'}</th>
            <th class="num">${'Runtime (ms)'}</th>
            <th>${'Version'}</th>
            <th>${'Report Link'}</th>
            <th>${'Excel Link'}</th>
          </tr>
        </thead>
        <tbody>
          ${pkgs.map(p => {
            const folder = p.folder || '';
            const report_href = p.report_url || (folder ? folder + '/report/report.html' : '#');
            const wb_href = p.workbook_url || (folder ? folder + '/excel/workbook.xlsx' : '#');
            return `
              <tr>
                <td><strong>${escapeHtml(p.motif || 'N/A')}</strong></td>
                <td><code>${escapeHtml(folder)}</code></td>
                <td class="num" style="font-weight:700;">${p.db != null ? parseFloat(p.db).toFixed(4) : 'N/A'}</td>
                <td class="num" style="font-weight:700;">${p.r2 != null ? parseFloat(p.r2).toFixed(4) : 'N/A'}</td>
                <td class="num">${p.levels || p.computed_levels_count || 'N/A'}</td>
                <td class="num">${p.total_time_ms != null ? parseFloat(p.total_time_ms).toFixed(2) : 'N/A'}</td>
                <td><b>${escapeHtml(p.package_version || 'v1')}</b></td>
                <td><a href="${attrSafe(report_href)}" target="_blank" rel="noopener" class="btn btn-sm btn-primary">${'Open Report'}</a></td>
                <td><a href="${attrSafe(wb_href)}" target="_blank" rel="noopener" class="btn btn-sm">${'Workbook'}</a></td>
              </tr>
            `;
          }).join('')}
        </tbody>
      </table>
    </div>
  `;
}

