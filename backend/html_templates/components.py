"""Reusable HTML UI Components Generator."""

from backend.html_templates.theme_css import SHARED_CSS

def render_head(title: str, meta_tags: str = "", extra_css: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  {meta_tags}
  <title>{title}</title>
  <style>
{SHARED_CSS}
{extra_css}
  </style>
</head>
<body>"""

def render_header(title: str = "RASH-HIT Fractal Studio — Output Library", subtitle: str = "by Mehmet Raşit NARÇİÇEK") -> str:
    return f"""<header class="app-header">
  <div style="max-width: 1400px; margin: 0 auto; width: 100%; display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap;">
    <div>
      <h1 class="app-title">{title}</h1>
      <div class="app-author">{subtitle}</div>
    </div>
    <button class="theme-toggle" onclick="toggleTheme()" title="Toggle theme" aria-label="Toggle theme"></button>
  </div>
</header>"""

def render_nav(active_page: str = "index", rel_prefix: str = "") -> str:
    def _active(name):
        return ' active' if active_page == name else ''

    prefix = rel_prefix if rel_prefix else ""
    home_link = f"{prefix}index.html"
    report_link = f"{prefix}report/report.html" if not rel_prefix else "report.html"
    tables_link = f"{prefix}tables/tables.html" if not rel_prefix else "../tables/tables.html"
    excel_link = f"{prefix}excel/workbook.xlsx" if not rel_prefix else "../excel/workbook.xlsx"
    manifest_link = f"{prefix}manifest/manifest.json" if not rel_prefix else "../manifest/manifest.json"

    return f"""<nav class="nav-bar">
  <div style="max-width: 1400px; margin: 0 auto; width: 100%; display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
    <a class="nav-btn{_active('index')}" href="{home_link}">Home Dashboard</a>
    <a class="nav-btn{_active('report')}" href="{report_link}">Report</a>
    <a class="nav-btn{_active('tables')}" href="{tables_link}">Tables</a>
    <a class="nav-btn{_active('workbook')}" href="{excel_link}">Workbook</a>
    <a class="nav-btn{_active('manifest')}" href="{manifest_link}">Manifest</a>
  </div>
</nav>"""

def render_nav_dynamic(active_page: str, home_link: str, report_link: str, tables_link: str, excel_link: str, manifest_link: str) -> str:
    def _active(name):
        return ' active' if active_page == name else ''
    return f"""<nav class="nav-bar">
  <div style="max-width: 1400px; margin: 0 auto; width: 100%; display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
    <a class="nav-btn{_active('index')}" href="{home_link}">Home Dashboard</a>
    <a class="nav-btn{_active('report')}" href="{report_link}">Report</a>
    <a class="nav-btn{_active('tables')}" href="{tables_link}">Tables</a>
    <a class="nav-btn{_active('workbook')}" href="{excel_link}">Workbook</a>
    <a class="nav-btn{_active('manifest')}" href="{manifest_link}">Manifest</a>
  </div>
</nav>"""

def render_svg_modal() -> str:
    return """<div id="svgModal" class="modal gallery-modal" onclick="closeSvgModal()">
  <div class="modal-box gallery-modal-box" onclick="event.stopPropagation()">
    <div class="gallery-modal-hdr">
      <strong id="svgModalLabel">SVG Preview</strong>
      <div class="gallery-modal-tools">
        <span id="galleryCounter" class="gallery-counter"></span>
        <button class="btn btn-sm" onclick="svgZoomOut()" title="Zoom out">−</button>
        <button class="btn btn-sm" onclick="svgZoomIn()" title="Zoom in">+</button>
        <button class="btn btn-sm" onclick="svgZoomReset()" title="Reset zoom">⤾</button>
        <a id="svgModalOpenBtn" href="#" target="_blank" rel="noopener" class="btn btn-sm" style="margin-left:2px;">SVG</a>
        <button class="btn btn-sm" onclick="closeSvgModal()" style="margin-left:2px;">&times;</button>
      </div>
    </div>
    <div class="gallery-stage" id="galleryStage" onwheel="svgOnWheel(event)">
      <button class="gallery-arrow gallery-prev" onclick="svgNav(-1)" aria-label="Previous image">&#10094;</button>
      <div class="gallery-viewport">
        <img id="svgModalImg" src="" alt="Preview" draggable="false">
      </div>
      <button class="gallery-arrow gallery-next" onclick="svgNav(1)" aria-label="Next image">&#10095;</button>
    </div>
    <div class="gallery-hint">Scroll to zoom &middot; Arrow keys to browse &middot; Double-click to reset</div>
  </div>
</div>
<script>
let GALLERY_INDEX = -1;
let GALLERY_ZOOM = 1;
function svgGalleryItems(){
  return (typeof RASH_HIT_GALLERY !== 'undefined' && Array.isArray(RASH_HIT_GALLERY)) ? RASH_HIT_GALLERY : [];
}
function openSvgModal(src, label){
  const items = svgGalleryItems();
  GALLERY_INDEX = items.findIndex(i => i.src === src);
  if (GALLERY_INDEX < 0){ GALLERY_INDEX = 0; }
  GALLERY_ZOOM = 1;
  svgApplyImage();
  document.getElementById('svgModal').classList.add('open');
  document.getElementById('svgModalImg').focus && document.getElementById('svgModalImg').focus();
}
function svgApplyImage(){
  const items = svgGalleryItems();
  const img = document.getElementById('svgModalImg');
  if (!img) return;
  if (items.length && GALLERY_INDEX >= 0 && GALLERY_INDEX < items.length){
    const it = items[GALLERY_INDEX];
    img.src = it.src;
    document.getElementById('svgModalLabel').textContent = it.label || ('Level ' + (GALLERY_INDEX + 1));
    document.getElementById('svgModalOpenBtn').href = it.src;
    document.getElementById('galleryCounter').textContent = (GALLERY_INDEX + 1) + ' / ' + items.length;
  } else {
    img.src = '';
  }
  svgApplyZoom();
}
function svgApplyZoom(){
  const img = document.getElementById('svgModalImg');
  if (!img) return;
  img.style.transform = 'scale(' + GALLERY_ZOOM + ')';
  img.style.transformOrigin = 'center center';
}
function svgZoomIn(){ GALLERY_ZOOM = Math.min(8, GALLERY_ZOOM + 0.35); svgApplyZoom(); }
function svgZoomOut(){ GALLERY_ZOOM = Math.max(0.25, GALLERY_ZOOM - 0.35); svgApplyZoom(); }
function svgZoomReset(){ GALLERY_ZOOM = 1; svgApplyZoom(); }
function svgOnWheel(e){
  e.preventDefault();
  if (e.deltaY < 0){ svgZoomIn(); } else { svgZoomOut(); }
}
function svgNav(dir){
  const items = svgGalleryItems();
  if (!items.length) return;
  GALLERY_INDEX = (GALLERY_INDEX + dir + items.length) % items.length;
  GALLERY_ZOOM = 1;
  svgApplyImage();
}
function closeSvgModal(){
  document.getElementById('svgModal').classList.remove('open');
}
document.addEventListener('keydown', function(e){
  const modal = document.getElementById('svgModal');
  if (!modal || !modal.classList.contains('open')) return;
  if (e.key === 'ArrowLeft'){ svgNav(-1); }
  else if (e.key === 'ArrowRight'){ svgNav(1); }
  else if (e.key === 'Escape'){ closeSvgModal(); }
});
document.getElementById('galleryStage').addEventListener('dblclick', svgZoomReset);
</script>"""

def render_footer(engine_info: str = "RASH-HIT Vector Geometry Engine") -> str:
    return f"""<footer class="app-footer">
  Generated by RASH-HIT Fractal Studio &middot; {engine_info} &middot; by Mehmet Raşit NARÇİÇEK
</footer>
<script>
function applySavedTheme(){{
  const saved = localStorage.getItem('rash-hit-report-theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
}}
function toggleTheme(){{
  const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('rash-hit-report-theme', next);
}}
applySavedTheme();
</script>
</body>
</html>"""

def render_index_nav() -> str:
    return """<nav class="nav-bar">
  <a class="nav-btn active" href="index.html">Home Dashboard</a>
</nav>"""
