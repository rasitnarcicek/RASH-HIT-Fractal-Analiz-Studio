/**
 * RASH-HIT Fractal Studio - UI Interactions & Modal Controls
 */

let pendingConfirmAction = null;

function formatLvl(lvl) {
  if (lvl == null) return '';
  const s = String(lvl).trim();
  const m = s.match(/^L+(\d+)$/i);
  if (m) return 'L' + String(parseInt(m[1], 10)).padStart(2, '0');
  const num = parseInt(s, 10);
  if (!isNaN(num)) return 'L' + String(num).padStart(2, '0');
  return s;
}

function toggleAccordion(id) {
  const el = document.getElementById(id);
  if (!el) return;
  el.classList.toggle('closed');
  // Keep aria-expanded in sync so screen readers know the panel state.
  const hdr = el.querySelector('.sb-acc-hdr');
  if (hdr) {
    hdr.setAttribute('aria-expanded', el.classList.contains('closed') ? 'false' : 'true');
  }
}

function openConfirmModal(title, msg, onConfirm) {
  const modal = document.getElementById('confirmDeleteModal');
  if (!modal) {
    if (confirm(msg) && typeof onConfirm === 'function') onConfirm();
    return;
  }
  document.getElementById('confirmModalTitle').textContent = title;
  document.getElementById('confirmModalMsg').textContent = msg;
  pendingConfirmAction = onConfirm;
  modal._prevFocus = document.activeElement;  // ISSUE-011: remember focus for restore
  modal.classList.add('open');

  document.getElementById('btnConfirmDeleteYes').onclick = async function() {
    closeConfirmModal();
    if (typeof pendingConfirmAction === 'function') {
      await pendingConfirmAction();
    }
  };
}

function closeConfirmModal() {
  const modal = document.getElementById('confirmDeleteModal');
  if (modal) modal.classList.remove('open');
  if (modal && modal._prevFocus && typeof modal._prevFocus.focus === 'function') {
    modal._prevFocus.focus();  // ISSUE-011: restore focus on close
  }
  pendingConfirmAction = null;
}

/* ============ SVG Preview Modal (wheel-zoom + gallery navigation) ============ */
let SVG_GALLERY_INDEX = -1;
let SVG_GALLERY_ZOOM = 1;
let SVG_PAN_X = 0;
let SVG_PAN_Y = 0;
let svgDragState = { isDragging: false, startX: 0, startY: 0, initialPinchDist: null, initialZoom: 1 };
let svgModalEventsBound = false;
let svgArrowKeysBound = false;

/** Gallery items come from window.RASH_HIT_GALLERY (set by the gallery renderers). */
function svgGalleryItems() {
  return (typeof window.RASH_HIT_GALLERY !== 'undefined' && Array.isArray(window.RASH_HIT_GALLERY))
    ? window.RASH_HIT_GALLERY
    : [];
}

function initSvgModalEvents() {
  if (svgModalEventsBound) return;
  const img = document.getElementById('svgModalImg');
  if (!img) return;
  const container = img.parentElement;
  if (!container) return;
  svgModalEventsBound = true;

  container.style.cursor = 'grab';

  container.addEventListener('mousedown', function(e) {
    if (e.target.closest('.gallery-arrow')) return;
    if (e.button !== 0) return; // Only main left click
    svgDragState.isDragging = true;
    svgDragState.startX = e.clientX - SVG_PAN_X;
    svgDragState.startY = e.clientY - SVG_PAN_Y;
    container.style.cursor = 'grabbing';
    img.style.transition = 'none'; // Disable transition during drag
    e.preventDefault();
  });

  window.addEventListener('mousemove', function(e) {
    if (!svgDragState.isDragging) return;
    SVG_PAN_X = e.clientX - svgDragState.startX;
    SVG_PAN_Y = e.clientY - svgDragState.startY;
    svgApplyZoom();
  });

  window.addEventListener('mouseup', function() {
    if (svgDragState.isDragging) {
      svgDragState.isDragging = false;
      if (container) container.style.cursor = 'grab';
      if (img) img.style.transition = 'transform .1s ease, opacity .2s ease';
    }
  });

  // Touch Events (pan & pinch-zoom)
  container.addEventListener('touchstart', function(e) {
    if (e.target.closest('.gallery-arrow')) return;
    if (e.touches.length === 1) {
      svgDragState.isDragging = true;
      svgDragState.startX = e.touches[0].clientX - SVG_PAN_X;
      svgDragState.startY = e.touches[0].clientY - SVG_PAN_Y;
      img.style.transition = 'none';
    } else if (e.touches.length === 2) {
      svgDragState.isDragging = false;
      svgDragState.initialPinchDist = Math.hypot(
        e.touches[0].clientX - e.touches[1].clientX,
        e.touches[0].clientY - e.touches[1].clientY
      );
      svgDragState.initialZoom = SVG_GALLERY_ZOOM;
      img.style.transition = 'none';
    }
  }, { passive: true });

  container.addEventListener('touchmove', function(e) {
    if (e.touches.length === 1 && svgDragState.isDragging) {
      SVG_PAN_X = e.touches[0].clientX - svgDragState.startX;
      SVG_PAN_Y = e.touches[0].clientY - svgDragState.startY;
      svgApplyZoom();
      if (e.cancelable) e.preventDefault();
    } else if (e.touches.length === 2 && svgDragState.initialPinchDist != null) {
      const currentDist = Math.hypot(
        e.touches[0].clientX - e.touches[1].clientX,
        e.touches[0].clientY - e.touches[1].clientY
      );
      if (svgDragState.initialPinchDist > 0) {
        SVG_GALLERY_ZOOM = Math.max(0.25, Math.min(8, svgDragState.initialZoom * (currentDist / svgDragState.initialPinchDist)));
        svgApplyZoom();
      }
      if (e.cancelable) e.preventDefault();
    }
  }, { passive: false });

  container.addEventListener('touchend', function(e) {
    if (e.touches.length === 0) {
      svgDragState.isDragging = false;
      svgDragState.initialPinchDist = null;
      if (img) img.style.transition = 'transform .1s ease, opacity .2s ease';
    } else if (e.touches.length === 1) {
      svgDragState.isDragging = true;
      svgDragState.startX = e.touches[0].clientX - SVG_PAN_X;
      svgDragState.startY = e.touches[0].clientY - SVG_PAN_Y;
      svgDragState.initialPinchDist = null;
    }
  });
}

function openSvgModal(src, label) {
  if (!src) return;
  const items = svgGalleryItems();
  SVG_GALLERY_INDEX = items.findIndex(i => i.src === src);
  if (SVG_GALLERY_INDEX < 0) SVG_GALLERY_INDEX = 0;
  SVG_GALLERY_ZOOM = 1;
  SVG_PAN_X = 0;
  SVG_PAN_Y = 0;

  const img = document.getElementById('svgModalImg');
  if (img) {
    img.style.opacity = '0.45';  // loading state while the (potentially large) SVG decodes
    img.onload = function () { img.style.opacity = '1'; };
    img.src = src;
  }
  const lbl = document.getElementById('svgModalLabel');
  if (lbl) lbl.textContent = label || src;
  const openBtn = document.getElementById('svgModalOpenBtn');
  if (openBtn) openBtn.href = src;
  const counter = document.getElementById('galleryCounter');
  if (counter) counter.textContent = items.length ? (SVG_GALLERY_INDEX + 1) + ' / ' + items.length : '';
  svgApplyZoom();

  const modal = document.getElementById('svgModal');
  if (modal) {
    modal._prevFocus = document.activeElement;  // ISSUE-011
    modal.classList.add('open');
  }
  initSvgModalEvents();
  bindSvgArrowKeys();
}

function svgApplyZoom() {
  const img = document.getElementById('svgModalImg');
  if (!img) return;
  img.style.transform = 'translate(' + SVG_PAN_X + 'px, ' + SVG_PAN_Y + 'px) scale(' + SVG_GALLERY_ZOOM + ')';
  img.style.transformOrigin = 'center center';
}

function svgZoomIn() { SVG_GALLERY_ZOOM = Math.min(8, SVG_GALLERY_ZOOM + 0.35); svgApplyZoom(); }
function svgZoomOut() { SVG_GALLERY_ZOOM = Math.max(0.25, SVG_GALLERY_ZOOM - 0.35); svgApplyZoom(); }
function svgZoomReset() {
  SVG_GALLERY_ZOOM = 1;
  SVG_PAN_X = 0;
  SVG_PAN_Y = 0;
  svgApplyZoom();
}

function svgOnWheel(e) {
  if (!e) return;
  e.preventDefault();
  if (e.ctrlKey) {
    SVG_GALLERY_ZOOM = Math.max(0.25, Math.min(8, SVG_GALLERY_ZOOM - e.deltaY * 0.01));
  } else {
    if (e.deltaY < 0) svgZoomIn(); else svgZoomOut();
  }
  svgApplyZoom();
}

function svgNav(dir) {
  const items = svgGalleryItems();
  if (!items.length) return;
  SVG_GALLERY_INDEX = (SVG_GALLERY_INDEX + dir + items.length) % items.length;
  SVG_GALLERY_ZOOM = 1;
  SVG_PAN_X = 0;
  SVG_PAN_Y = 0;
  const it = items[SVG_GALLERY_INDEX];
  openSvgModal(it.src, it.label);
}

function bindSvgArrowKeys() {
  if (svgArrowKeysBound) return;
  svgArrowKeysBound = true;
  document.addEventListener('keydown', function (e) {
    const modal = document.getElementById('svgModal');
    if (!modal || !modal.classList.contains('open')) return;
    if (e.key === 'ArrowLeft') { e.preventDefault(); svgNav(-1); }
    else if (e.key === 'ArrowRight') { e.preventDefault(); svgNav(1); }
  });
}

function closeSvgModal() {
  const modal = document.getElementById('svgModal');
  if (modal) modal.classList.remove('open');
  if (modal && modal._prevFocus && typeof modal._prevFocus.focus === 'function') {
    modal._prevFocus.focus();  // ISSUE-011: restore focus on close
  }
  const img = document.getElementById('svgModalImg');
  if (img) img.src = '';
  SVG_GALLERY_ZOOM = 1;
  SVG_PAN_X = 0;
  SVG_PAN_Y = 0;
}

/**
 * Open Folder web fallback: instead of opening a blank new tab, show the
 * package folder path in a modal with a Copy Path button (the local machine
 * opens the real folder via /api/open-folder).
 */
function openFolderPathModal(pkgId) {
  const modal = document.getElementById('folderPathModal');
  const val = document.getElementById('folderPathValue');
  if (!modal || !val) return;
  // Prefer the known package folder name; default to the raw identifier.
  let folder = pkgId || '';
  if (typeof PACKAGES !== 'undefined') {
    const pkg = PACKAGES.find(p => p.folder === pkgId || p.package_id === pkgId || p.id === pkgId);
    if (pkg && pkg.folder) folder = pkg.folder;
  }
  const display = 'outputs/' + folder;
  val.textContent = display;
  val.dataset.path = display;
  modal._prevFocus = document.activeElement;  // ISSUE-011
  modal.classList.add('open');
}

function closeFolderPathModal() {
  const modal = document.getElementById('folderPathModal');
  if (modal) modal.classList.remove('open');
  if (modal && modal._prevFocus && typeof modal._prevFocus.focus === 'function') {
    modal._prevFocus.focus();  // ISSUE-011: restore focus on close
  }
}

/**
 * Open Folder: the local server opens the real package folder in the OS file
 * explorer (os.startfile / xdg-open). No modal window is shown anymore — the
 * folder opens directly on the user's machine. Falls back to the plain
 * path-copy modal only when the server cannot resolve/open the folder.
 */
let FOLDER_BROWSER_FILES = [];

function openFolderBrowser(folder) {
  if (!folder) return;
  API.openFolder(folder).then(res => {
    if (res && res.ok && res.opened_in_os !== false) {
      showToast('📂 Folder opened in File Explorer: outputs/' + (res.folder || folder));
      return;
    }
    // Server unreachable or folder unresolved: show the path-copy fallback.
    openFolderPathModal(folder);
  }).catch(() => {
    openFolderPathModal(folder);
  });
}

/* Lightweight transient toast used by openFolderBrowser (no modal window). */
let toastTimer = null;
function showToast(msg) {
  let el = document.getElementById('appToast');
  if (!el) {
    el = document.createElement('div');
    el.id = 'appToast';
    el.setAttribute('role', 'status');
    el.style.cssText = 'position:fixed;bottom:22px;left:50%;transform:translateX(-50%);background:var(--sb,#0F172A);color:#FFF;font-size:12px;font-weight:700;padding:10px 18px;border-radius:999px;box-shadow:0 8px 24px rgba(0,0,0,.28);z-index:12000;opacity:0;transition:opacity .2s ease;pointer-events:none;max-width:90vw;text-align:center;';
    document.body.appendChild(el);
  }
  el.textContent = msg;
  el.style.opacity = '1';
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.style.opacity = '0'; }, 2800);
}

function renderFolderBrowserList(query) {
  const list = document.getElementById('folderBrowserList');
  if (!list) return;
  const q = (query || '').toLowerCase();
  const files = FOLDER_BROWSER_FILES.filter(f => !q || (f.name || '').toLowerCase().includes(q) || (f.path || '').toLowerCase().includes(q));
  if (!files.length) {
    list.innerHTML = '<div class="empty-hint">' + (FOLDER_BROWSER_FILES.length ? 'No files match the filter.' : 'This package has no files.') + '</div>';
    return;
  }
  const kindIcon = (k) => {
    if (k === 'svg') return '🖼️';
    if (k === 'xlsx') return '📈';
    if (k === 'pdf') return '📕';
    if (k === 'html') return '📄';
    if (k === 'json') return '🧾';
    if (k === 'csv' || k === 'txt') return '📊';
    if (k === 'png' || k === 'jpg' || k === 'jpeg' || k === 'gif') return '🖼️';
    return '📁';
  };
  list.innerHTML = '<table style="width:100%;font-size:12px;"><thead><tr>' +
    '<th>File</th><th>Type</th><th style="text-align:right;">Size</th><th style="text-align:right;">Action</th>' +
    '</tr></thead><tbody>' + files.map(f => {
    const kb = (f.size || 0) / 1024;
    const sizeStr = kb >= 1024 ? (kb / 1024).toFixed(2) + ' MB' : kb.toFixed(1) + ' KB';
    return '<tr>' +
      '<td style="font-family:Consolas,monospace;word-break:break-all;">' + kindIcon(f.kind) + ' ' + escapeHtml(f.name) + '</td>' +
      '<td><b>' + escapeHtml(f.kind || 'file') + '</b></td>' +
      '<td style="text-align:right;">' + sizeStr + '</td>' +
      '<td style="text-align:right;"><a class="btn btn-sm" href="' + attrSafe(f.url) + '" target="_blank" rel="noopener">Open</a></td>' +
      '</tr>';
  }).join('') + '</tbody></table>';
}

function filterFolderBrowser() {
  const search = document.getElementById('folderBrowserSearch');
  renderFolderBrowserList(search ? search.value : '');
}

function copyFolderBrowserPath() {
  const val = document.getElementById('folderBrowserPath');
  const btn = document.querySelector('#folderBrowserModal [data-testid="folder-browser-copy"]');
  if (!val) return;
  const text = val.textContent || '';
  const done = function() {
    if (btn) { btn.textContent = 'Copied ✓'; setTimeout(() => { btn.textContent = 'Copy Path'; }, 1600); }
  };
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(done).catch(() => { fallbackCopyText(text); done(); });
  } else {
    fallbackCopyText(text);
    done();
  }
}

function closeFolderBrowserModal() {
  const modal = document.getElementById('folderBrowserModal');
  if (modal) modal.classList.remove('open');
  if (modal && modal._prevFocus && typeof modal._prevFocus.focus === 'function') {
    modal._prevFocus.focus();  // ISSUE-011: restore focus on close
  }
  FOLDER_BROWSER_FILES = [];
}

function formatBytes(bytes) {
  if (!bytes) return '0 B';
  const kb = bytes / 1024;
  if (kb >= 1024) return (kb / 1024).toFixed(2) + ' MB';
  return kb.toFixed(1) + ' KB';
}

function copyFolderPath() {
  const val = document.getElementById('folderPathValue');
  const btn = document.querySelector('#folderPathModal [data-testid="folder-path-copy"]');
  if (!val) return;
  const text = val.dataset.path || val.textContent || '';
  const done = function() {
    if (btn) { btn.textContent = 'Copied ✓'; setTimeout(() => { btn.textContent = 'Copy Path'; }, 1600); }
  };
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(done).catch(() => {
      fallbackCopyText(text);
      done();
    });
  } else {
    fallbackCopyText(text);
    done();
  }
}

function fallbackCopyText(text) {
  try {
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
  } catch (e) { /* clipboard unavailable */ }
}

/**
 * Single ESC-to-close handler (merged): scientific console first (it owns
 * polling), then the SVG preview, confirm delete, export dialog, and finally
 * the right details drawer. Each guard checks the open class so a closed
 * modal is never touched.
 */

function updateSelectionToolbar() {
  const bar = document.getElementById('selectionToolbar');
  const cnt = document.getElementById('selectionCount');
  if (!bar || !cnt) return;
  const num = selectedFolders.size;
  cnt.textContent = num;
  bar.style.display = num > 0 ? 'flex' : 'none';
  // Contextual Clear Selection in the sidebar Actions panel (item 23).
  const sbClear = document.getElementById('sidebarClearSelection');
  if (sbClear) sbClear.style.display = num > 0 ? 'block' : 'none';
}

function selectTargetType(type) {
  CURRENT_TARGET_TYPE = type;
  // Reset stale selection when switching target type
  SELECTED_SINGLE_FILE = null;
  SELECTED_BATCH_FILES = [];
  const btnRun = document.getElementById('btnRunWeb');
  if (btnRun) btnRun.disabled = true;
  const btnS = document.getElementById('btnTargetSingle');
  const btnF = document.getElementById('btnTargetFolder');
  const lbl = document.getElementById('lblInputPath');
  const countLabel = document.getElementById('folderCountLabel');

  if (type === 'folder') {
    if (btnS) { btnS.className = 'btn'; }
    if (btnF) { btnF.className = 'btn btn-primary'; }
    if (lbl) lbl.textContent = 'SVG Directory / Folder Path:';
  } else {
    if (btnS) { btnS.className = 'btn btn-primary'; }
    if (btnF) { btnF.className = 'btn'; }
    if (lbl) lbl.textContent = 'SVG File Path:';
    if (countLabel) countLabel.style.display = 'none';
  }
}

function triggerBrowseTarget() {
  if (CURRENT_TARGET_TYPE === 'folder') {
    const el = document.getElementById('folderBatchInput');
    if (el) el.click();
  } else {
    const el = document.getElementById('singleSvgInput');
    if (el) el.click();
  }
}

function handleSingleSvgSelect(event) {
  const file = event.target.files[0];
  if (file) {
    SELECTED_SINGLE_FILE = file;
    const inp = document.getElementById('webInputPath');
    if (inp) inp.value = file.name;
    const btn = document.getElementById('btnRunWeb');
    if (btn) btn.disabled = false;
  }
}

/**
 * Inline oninput/onchange handler wired to #webInputPath on both the dashboard
 * (index.html) and the Analysis Studio (analysis.html). The path field is a
 * display-only label of the user's real File selection, so a manual edit or
 * clear invalidates the selection instead of letting a stale target run.
 */
function onInputPathChange() {
  const inp = document.getElementById('webInputPath');
  if (!inp) return;
  const val = (inp.value || '').trim();
  const btn = document.getElementById('btnRunWeb');

  if (!val) {
    if (typeof SELECTED_SINGLE_FILE !== 'undefined') SELECTED_SINGLE_FILE = null;
    if (typeof SELECTED_BATCH_FILES !== 'undefined') SELECTED_BATCH_FILES = [];
    if (btn) btn.disabled = true;
    return;
  }

  // A manual edit that no longer matches the picked single file clears the
  // selection (folder mode keeps its webkitRelativePath folder label).
  const selectedName = (typeof SELECTED_SINGLE_FILE !== 'undefined' && SELECTED_SINGLE_FILE) ? SELECTED_SINGLE_FILE.name : '';
  if (selectedName && val !== selectedName) {
    if (typeof SELECTED_SINGLE_FILE !== 'undefined') SELECTED_SINGLE_FILE = null;
    if (btn) btn.disabled = true;
  }
}

function handleFolderBatchSelect(event) {
  const files = Array.from(event.target.files).filter(f => f.name.toLowerCase().endsWith('.svg'));
  // Store the REAL File objects - these are uploaded as files[] FormData.
  SELECTED_BATCH_FILES = files;
  const inp = document.getElementById('webInputPath');
  const countLabel = document.getElementById('folderCountLabel');
  const btn = document.getElementById('btnRunWeb');

  if (files.length === 0) {
    alert('No SVG files found in the selected folder.');
    SELECTED_BATCH_FILES = [];
    if (countLabel) countLabel.style.display = 'none';
    if (btn) btn.disabled = true;
    return;
  }

  if (files[0] && files[0].webkitRelativePath) {
    const parts = files[0].webkitRelativePath.split('/');
    if (parts.length > 1 && inp) {
      inp.value = parts[0];
    }
  }

  if (countLabel) {
    countLabel.textContent = `📁 ${files.length} SVG files found in selected folder.`;
    countLabel.style.display = 'block';
  }
  if (btn) btn.disabled = false;
}

/** Global active view mode state */
let CURRENT_VIEW_MODE = 'overview';

/** Switch view mode section safely without modifying API data */
function switchView(viewName) {
  CURRENT_VIEW_MODE = viewName || 'overview';

  // Toggle active view section
  const sections = document.querySelectorAll('.view-section');
  sections.forEach(sec => {
    if (sec.id === `view-${CURRENT_VIEW_MODE}`) {
      sec.classList.add('active');
    } else {
      sec.classList.remove('active');
    }
  });

  // Hide stats panel when not in Library mode (overview)
  const kpiRow = document.getElementById('mainKpiRow');
  if (kpiRow) {
    kpiRow.style.display = (CURRENT_VIEW_MODE === 'overview') ? 'grid' : 'none';
  }

  // Sync view mode radio buttons
  const radios = document.querySelectorAll('input[name="viewModeRadio"]');
  radios.forEach(r => {
    r.checked = (r.value === CURRENT_VIEW_MODE);
  });

  // Render content for current active view
  if (typeof renderCurrentView === 'function') {
    renderCurrentView();
  }
}

/** Drawer controls & detail renderer */
function openPackageDrawer(folderOrId) {
  const overlay = document.getElementById('drawerOverlay');
  const drawer = document.getElementById('drawer');
  const title = document.getElementById('drawerTitle');
  const content = document.getElementById('drawerContent');
  if (!overlay || !drawer) return;

  const pkg = (typeof PACKAGES !== 'undefined') ? PACKAGES.find(p => p.folder === folderOrId || p.id === folderOrId || p.motif === folderOrId) : null;

  if (title) title.textContent = 'Package Details';
  if (content && pkg) renderDrawerPackageDetails(pkg);

  overlay.classList.add('open');
  drawer.classList.add('open');
}

function closeDrawer() {
  const overlay = document.getElementById('drawerOverlay');
  const drawer = document.getElementById('drawer');
  if (overlay) overlay.classList.remove('open');
  if (drawer) drawer.classList.remove('open');
}

function renderDrawerPackageDetails(pkg) {
  const content = document.getElementById('drawerContent');
  if (!content) return;

  const db = pkg.db != null ? parseFloat(pkg.db).toFixed(4) : 'N/A';
  const r2 = pkg.r2 != null ? parseFloat(pkg.r2).toFixed(4) : 'N/A';
  const lvls = pkg.levels || pkg.computed_levels_count || 'N/A';
  const timeMs = pkg.total_time_ms != null ? parseFloat(pkg.total_time_ms).toFixed(2) + ' ms' : 'N/A';
  const folder = pkg.folder || '';
  const srcName = pkg.source_file ? String(pkg.source_file).split(/[\\/]/).pop() : 'N/A';

  const report_href = pkg.report_url || (folder ? folder + '/report/report.html' : '#');
  const pdf_href = pkg.report_pdf_url || (folder ? folder + '/report/report.pdf' : '#');
  const tables_href = pkg.tables_url || (folder ? folder + '/tables/tables.html' : '#');
  const wb_href = pkg.workbook_url || (folder ? folder + '/excel/workbook.xlsx' : '#');
  const manifest_href = pkg.manifest_url || (folder ? folder + '/manifest/manifest.json' : '#');

  const maps = pkg.svg_maps || [];
  // Feed the shared preview modal so arrows/zoom can browse every level of
  // this package.
  window.RASH_HIT_GALLERY = maps.map(m => ({
    src: m.url,
    label: (pkg.motif || '') + ' · ' + formatLvl(m.level || '?'),
  }));
  const lvlTag = (lvl) => formatLvl(lvl || '?');
  const gallery = maps.length
    ? `<div style="margin-top:4px;"><div style="font-size:11px;color:var(--muted);font-weight:700;margin-bottom:8px;">${'SVG GALLERY'}</div>
       <div class="svg-gallery-grid">
         ${maps.map(m => {
           const lt = lvlTag(m.level);
           const lb = (pkg.motif || '') + ' · ' + lt;
           return `
           <div class="svg-thumb-card">
             <div style="display:flex;justify-content:space-between;align-items:center;font-size:11.5px;font-weight:700;margin-bottom:2px;">
               <b style="font-size:10px;font-weight:800;color:var(--text);">${lt}</b>
             </div>
             <button type="button" class="svg-img-container" onclick="openSvgModal('${jsQuote(m.url)}','${jsQuote(lb)}')">
               <img src="${attrSafe(m.url)}" alt="${lt}" loading="lazy" decoding="async">
             </button>
             <div style="display:flex;gap:6px;margin-top:2px;">
               <a href="${attrSafe(m.url)}" target="_blank" rel="noopener" class="btn btn-sm" style="flex:1;">${'SVG'}</a>
             </div>
           </div>
         `;
         }).join('')}
       </div></div>`
    : '';

  const scaleRows = pkg.scale_rows || pkg.scale_table || [];
  const scale = scaleRows.length
    ? `<div style="margin-top:4px;"><div style="font-size:11px;color:var(--muted);font-weight:700;margin-bottom:8px;">${'LEVEL TABLE'}</div>${renderScaleRowsCompact(scaleRows)}</div>`
    : '';

  content.innerHTML = `
    <div style="display:flex;flex-direction:column;gap:14px;">
      <div style="background:var(--panel2);border:1px solid var(--border);border-radius:10px;padding:14px;">
        <div style="font-size:18px;font-weight:800;color:var(--text);">${escapeHtml(pkg.motif || folder)}</div>
        <div style="font-size:11px;color:var(--muted);margin-top:4px;">
          ${escapeHtml(pkg.generated_at || 'N/A')}
        </div>
        <div style="font-size:11px;color:var(--muted);margin-top:6px;display:grid;grid-template-columns:auto 1fr;gap:2px 10px;">
          <span style="font-weight:700;">Folder:</span><code style="color:var(--accent);word-break:break-all;">${escapeHtml(folder)}</code>
          <span style="font-weight:700;">File:</span><code style="color:var(--accent);word-break:break-all;">${escapeHtml(srcName)}</code>
        </div>
      </div>

      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px;">
        <div style="background:var(--panel2);border:1px solid var(--border);padding:10px;border-radius:8px;">
          <div style="font-size:10px;color:var(--muted);font-weight:700;">${'FRACTAL DIMENSION (Db)'}</div>
          <div style="font-size:18px;font-weight:800;color:var(--accent);">${db}</div>
        </div>
        <div style="background:var(--panel2);border:1px solid var(--border);padding:10px;border-radius:8px;">
          <div style="font-size:10px;color:var(--muted);font-weight:700;">${'FIT QUALITY (R²)'}</div>
          <div style="font-size:18px;font-weight:800;color:var(--ok);">${r2}</div>
        </div>
        <div style="background:var(--panel2);border:1px solid var(--border);padding:10px;border-radius:8px;">
          <div style="font-size:10px;color:var(--muted);font-weight:700;">${'GRID LEVELS'}</div>
          <div style="font-size:16px;font-weight:800;color:var(--text);">${lvls}</div>
        </div>
        <div style="background:var(--panel2);border:1px solid var(--border);padding:10px;border-radius:8px;">
          <div style="font-size:10px;color:var(--muted);font-weight:700;">${'EXECUTION TIME'}</div>
          <div style="font-size:16px;font-weight:800;color:var(--text);">${timeMs}</div>
        </div>
      </div>

      ${scale}

      ${gallery}

      <div style="display:flex;flex-direction:column;gap:8px;">
        <div style="font-size:11px;color:var(--muted);font-weight:700;">${'DIRECT ARTIFACT LINKS'}</div>
        <a href="${attrSafe(report_href)}" target="_blank" rel="noopener" class="btn btn-primary" style="justify-content:center;">${'Open HTML Report'}</a>
        <a href="${attrSafe(pdf_href)}" target="_blank" rel="noopener" class="btn" style="justify-content:center;">${'Open PDF Document'}</a>
        <a href="${attrSafe(tables_href)}" target="_blank" rel="noopener" class="btn" style="justify-content:center;">${'Spatial Tables Viewer'}</a>
        <a href="${attrSafe(wb_href)}" target="_blank" rel="noopener" class="btn" style="justify-content:center;">${'Excel Workbook (.xlsx)'}</a>
        <a href="${attrSafe(manifest_href)}" target="_blank" rel="noopener" class="btn" style="justify-content:center;">${'SHA-256 Manifest (.json)'}</a>
      </div>
    </div>
  `;
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

/** Export Configuration Modal controls */
function openExportDialog(defaultScope) {
  const modal = document.getElementById('exportModal');
  if (!modal) return;

  const selCount = typeof selectedFolders !== 'undefined' ? selectedFolders.size : 0;
  const visCount = typeof visiblePackages !== 'undefined' ? visiblePackages.length : 0;
  const allCount = typeof PACKAGES !== 'undefined' ? PACKAGES.length : 0;

  const elSel = document.getElementById('exportSelectedCount');
  const elVis = document.getElementById('exportVisibleCount');
  const elAll = document.getElementById('exportAllCount');

  if (elSel) elSel.textContent = selCount;
  if (elVis) elVis.textContent = visCount;
  if (elAll) elAll.textContent = allCount;

  const radios = document.querySelectorAll('input[name="exportScope"]');
  radios.forEach(r => {
    if (r.value === defaultScope) r.checked = true;
  });

  modal._prevFocus = document.activeElement;  // ISSUE-011: remember focus for restore
  modal.classList.add('open');
}

function closeExportDialog() {
  const modal = document.getElementById('exportModal');
  if (modal) modal.classList.remove('open');
  if (modal && modal._prevFocus && typeof modal._prevFocus.focus === 'function') {
    modal._prevFocus.focus();  // ISSUE-011: restore focus on close
  }
}

function updateExportModalCounts() {
  const selCount = typeof selectedFolders !== 'undefined' ? selectedFolders.size : 0;
  const visCount = typeof visiblePackages !== 'undefined' ? visiblePackages.length : 0;
  const allCount = typeof PACKAGES !== 'undefined' ? PACKAGES.length : 0;

  const elSel = document.getElementById('exportSelectedCount');
  const elVis = document.getElementById('exportVisibleCount');
  const elAll = document.getElementById('exportAllCount');

  if (elSel) elSel.textContent = selCount;
  if (elVis) elVis.textContent = visCount;
  if (elAll) elAll.textContent = allCount;
}

/**
 * Mode selector -> level-count preset (mirrors backend MODE_LEVEL_MAP so the
 * analysis mode the user picks actually changes the run). "custom" leaves the
 * Level Count field untouched for a manual override.
 */
const WEB_MODE_LEVEL_MAP = { fast: 5, balanced: 7, precise: 9, academic: 10 };

function updateModeDefaultLevels(sel) {
  const mode = sel ? sel.value : (document.getElementById('webModeSelect') || {}).value;
  const lvlInput = document.getElementById('webLevelsInput');
  if (!lvlInput) return;
  if (mode && mode !== 'custom' && WEB_MODE_LEVEL_MAP[mode]) {
    lvlInput.value = WEB_MODE_LEVEL_MAP[mode];
  }
}

/**
 * View-mode count badges were removed at the user's request (2026-08-04).
 * The function name is kept as a no-op so legacy call sites and the frontend
 * restoration contract stay stable without any DOM work.
 */
function updateViewBadges() {
  // Intentionally empty: per-view count badges are gone.
}

function selectOnlyOneFolder(folder) {
  if (typeof selectedFolders !== 'undefined') {
    selectedFolders.clear();
    selectedFolders.add(folder);
    if (typeof updateSelectionToolbar === 'function') updateSelectionToolbar();
    if (typeof renderCurrentView === 'function') renderCurrentView();
  }
}

function onAnalysisCbChange(folder, checked) {
  if (typeof onCardCbChange === 'function') {
    onCardCbChange(folder, checked);
  }
}

// Global Escape-to-close for open modals/drawers (accessibility).
// This is the single ESC handler (the former duplicate listener was removed).
function handleModalEscape(e) {
  if (e.key !== 'Escape') return;
  if (document.getElementById('scientificConsoleModal') && document.getElementById('scientificConsoleModal').classList.contains('open')) {
    closeAnalysisConsole();
  } else if (document.getElementById('svgModal') && document.getElementById('svgModal').classList.contains('open')) {
    closeSvgModal();
  } else if (document.getElementById('confirmDeleteModal') && document.getElementById('confirmDeleteModal').classList.contains('open')) {
    closeConfirmModal();
  } else if (document.getElementById('exportModal') && document.getElementById('exportModal').classList.contains('open')) {
    closeExportDialog();
  } else if (document.getElementById('folderPathModal') && document.getElementById('folderPathModal').classList.contains('open')) {
    closeFolderPathModal();
  } else if (document.getElementById('folderBrowserModal') && document.getElementById('folderBrowserModal').classList.contains('open')) {
    closeFolderBrowserModal();
  } else if (document.getElementById('drawer') && document.getElementById('drawer').classList.contains('open')) {
    closeDrawer();
  }
}
document.addEventListener('keydown', handleModalEscape);

/**
 * ISSUE-003 (a11y focus trap): gather focusable descendants of a modal.
 * Hidden/disabled elements (hidden attr, aria-hidden, disabled, display:none,
 * visibility:hidden) are excluded so Tab focus can never land on invisible controls.
 */
function getFocusableElements(modal) {
  const FOCUSABLE =
    'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), ' +
    'textarea:not([disabled]), [tabindex]:not([tabindex="-1"]), [contenteditable="true"]';
  return Array.prototype.filter.call(
    modal.querySelectorAll(FOCUSABLE),
    function (el) {
      if (el.hasAttribute('hidden') || el.getAttribute('aria-hidden') === 'true') return false;
      var st = el.style;
      if (st.display === 'none' || st.visibility === 'hidden') return false;
      return true;
    }
  );
}

/**
 * ISSUE-003 (a11y focus trap): keep Tab/Shift+Tab focus cycling inside the
 * currently open modal or drawer instead of leaking to the page behind it.
 */
function trapFocusInModal(e) {
  if (e.key !== 'Tab') return;
  var modal = null;
  var ids = ['scientificConsoleModal', 'svgModal', 'confirmDeleteModal', 'exportModal'];
  for (var i = 0; i < ids.length; i++) {
    var el = document.getElementById(ids[i]);
    if (el && el.classList.contains('open')) { modal = el; break; }
  }
  if (!modal) {
    var drawer = document.getElementById('drawer');
    if (drawer && drawer.classList.contains('open')) modal = drawer;
  }
  if (!modal) return;
  var focusable = getFocusableElements(modal);
  if (focusable.length === 0) return;
  var first = focusable[0];
  var last = focusable[focusable.length - 1];
  var active = document.activeElement;
  if (e.shiftKey) {
    if (active === first || !modal.contains(active)) {
      e.preventDefault();
      last.focus();
    }
  } else if (active === last || !modal.contains(active)) {
    e.preventDefault();
    first.focus();
  }
}
document.addEventListener('keydown', trapFocusInModal);

// Inject a call-to-action into the empty overview state (invitation to act)
function initEmptyStateCta() {
  var emptyOverview = document.getElementById('emptyOverview');
  if (!emptyOverview || emptyOverview.dataset.ctaInjected === 'true') return;
  var btn = document.createElement('button');
  btn.className = 'empty-cta';
  btn.textContent = 'Start your first analysis';
    btn.onclick = function () {
      window.location.href = 'analysis.html';
    };
  emptyOverview.appendChild(btn);
  emptyOverview.dataset.ctaInjected = 'true';
}

