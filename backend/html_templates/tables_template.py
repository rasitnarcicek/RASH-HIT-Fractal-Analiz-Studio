"""Lightweight Tables HTML Viewer Shell Generator using Shared Design System."""

from backend.html_templates.components import (
    render_head, render_header, render_nav_dynamic, render_footer
)

def build_tables_html_page(
    motif: str,
    package_id: str,
    db_val: float,
    r2_val: float,
    levels_count: int,
    gen_date: str,
    rel_home: str = "../../index.html",
    rel_report: str = "../report/report.html",
    rel_excel: str = "../excel/workbook.xlsx",
    rel_manifest: str = "../manifest/manifest.json"
) -> str:
    extra_css = """
    .tables-container { padding: 24px; max-width: 1400px; margin: 0 auto; }
    .tables-controls {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px;
      margin-bottom: 20px;
      display: flex;
      gap: 12px;
      align-items: center;
      flex-wrap: wrap;
    }
    .ctrl-group { display: flex; align-items: center; gap: 6px; }
    .ctrl-label { font-size: 11px; font-weight: 700; color: var(--muted); text-transform: uppercase; }
    .search-input {
      padding: 6px 12px;
      border-radius: 6px;
      border: 1px solid var(--border);
      background: var(--bg);
      color: var(--text);
      font-size: 12px;
      min-width: 200px;
    }
    .table-wrapper {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 1px 3px rgba(0,0,0,.05);
      max-height: 70vh;
      overflow-y: auto;
    }
    .table-wrapper table th { position: sticky; top: 0; z-index: 10; }
    """

    meta_tag = f'<meta name="rash-hit-package-id" content="{package_id}">'
    head = render_head(f"RASH-HIT Fractal Studio - {motif} Technical Tables", meta_tags=meta_tag, extra_css=extra_css)
    header = render_header(f"{motif} Technical Tables Viewer", "Box-Counting Spatial Cell Metrics &middot; by Mehmet Raşit NARÇİÇEK")
    
    nav_html = render_nav_dynamic("tables", rel_home, rel_report, "#", rel_excel, rel_manifest)
    
    kpi_section = """<section class="kpi-grid" style="padding: 20px 24px 0 24px;">
  <div class="kpi-card"><div class="kpi-lbl">Selected Level</div><div class="kpi-val" id="kpiLevel">L01</div><div class="kpi-sub">Grid dimension</div></div>
  <div class="kpi-card"><div class="kpi-lbl">Total Cells</div><div class="kpi-val" id="kpiTotalCells">0</div><div class="kpi-sub">Spatial grid count</div></div>
  <div class="kpi-card"><div class="kpi-lbl">Filled Cells</div><div class="kpi-val" id="kpiFilledCells" style="color:var(--ok);">0</div><div class="kpi-sub">Geometry hits</div></div>
  <div class="kpi-card"><div class="kpi-lbl">Empty Cells</div><div class="kpi-val" id="kpiEmptyCells" style="color:var(--muted);">0</div><div class="kpi-sub">Background cells</div></div>
  <div class="kpi-card"><div class="kpi-lbl">Occupancy Rate</div><div class="kpi-val" id="kpiOccupancy">0.0%</div><div class="kpi-sub">Coverage ratio</div></div>
</section>"""

    body_html = f"""<div class="tables-container">
  <div class="tables-controls">
    <div class="ctrl-group">
      <span class="ctrl-label">Grid Level:</span>
      <select id="levelSelect" class="btn" style="padding:5px 10px;" onchange="renderCurrentLevelTable()">
        <!-- Dynamic options appended -->
      </select>
    </div>

    <div class="ctrl-group">
      <span class="ctrl-label">Search / Filter:</span>
      <input type="text" id="searchInput" class="search-input" placeholder="Search cell ID, row, col..." oninput="filterTableRows()">
    </div>

    <div class="ctrl-group">
      <span class="ctrl-label">State:</span>
      <select id="stateSelect" class="btn" style="padding:5px 10px;" onchange="filterTableRows()">
        <option value="all" selected>All Cells</option>
        <option value="filled">Filled Only</option>
        <option value="empty">Empty Only</option>
      </select>
    </div>

    <div style="margin-left:auto;display:flex;gap:8px;">
      <a id="xlsxBtn" class="btn btn-primary btn-sm" href="{rel_excel}" target="_blank">Download XLSX</a>
    </div>
  </div>

  <!-- Capped Data warning box -->
  <div id="truncationWarning" style="display:none;background:var(--warn-bg);color:var(--warn);border:1px solid var(--warn);padding:10px 14px;border-radius:8px;font-size:12px;margin-bottom:12px;font-weight:700;">
    ⚠️ This level is shown as a sampled/capped cell list. Summary metrics represent the full grid.
  </div>

  <div class="table-wrapper">
    <table id="metricsTable">
      <thead>
        <tr>
          <th>Cell Index</th>
          <th>Level</th>
          <th>Grid Row</th>
          <th>Grid Col</th>
          <th>Bounding Box (Xmin,Ymin &rarr; Xmax,Ymax)</th>
          <th>State</th>
          <th>Hit Count</th>
        </tr>
      </thead>
      <tbody id="metricsTbody">
        <tr><td colspan="7" style="text-align:center;padding:20px;color:var(--muted);">Loading table dataset...</td></tr>
      </tbody>
    </table>
  </div>
</div>

<script>
let DATASET = null;
let currentLevelData = null;

async function loadTableDataset(){{
  try {{
    let res = await fetch('./tables_data.json');
    if(!res.ok){{
      res = await fetch('/api/package/{package_id}/tables');
    }}
    if(res.ok){{
      DATASET = await res.json();
      initLevelDropdown();
    }} else {{
      showError('Cell dataset file (tables_data.json) could not be loaded.');
    }}
  }} catch(e){{
    showError('Error loading tables dataset: ' + e.message);
  }}
}}

function initLevelDropdown(){{
  if(!DATASET || !DATASET.levels) return;
  const select = document.getElementById('levelSelect');
  select.innerHTML = '';
  const lvls = Object.keys(DATASET.levels).sort();
  lvls.forEach(l => {{
    const opt = document.createElement('option');
    opt.value = l;
    opt.textContent = l + ' (' + (DATASET.levels[l].grid || '') + ')';
    select.appendChild(opt);
  }});
  if(lvls.length > 0) {{
    select.value = lvls[0];
    renderCurrentLevelTable();
  }}
}}

function renderCurrentLevelTable(){{
  if(!DATASET || !DATASET.levels) return;
  const lvl = document.getElementById('levelSelect').value;
  currentLevelData = DATASET.levels[lvl];
  if(!currentLevelData) return;

  document.getElementById('kpiLevel').textContent = lvl;
  document.getElementById('kpiTotalCells').textContent = currentLevelData.total_cells || 0;
  document.getElementById('kpiFilledCells').textContent = currentLevelData.filled || 0;
  document.getElementById('kpiEmptyCells').textContent = currentLevelData.empty || 0;
  document.getElementById('kpiOccupancy').textContent = (currentLevelData.occupancy_pct !== undefined ? Number(currentLevelData.occupancy_pct).toFixed(2) : '0.00') + '%';

  const warn = document.getElementById('truncationWarning');
  if(warn) {{
    warn.style.display = currentLevelData.is_truncated ? 'block' : 'none';
  }}

  const xlsxBtn = document.getElementById('xlsxBtn');
  if(xlsxBtn) {{
    xlsxBtn.href = `./${{lvl}}.xlsx`;
  }}

  filterTableRows();
}}

function filterTableRows(){{
  if(!currentLevelData || !currentLevelData.cells) return;
  const q = (document.getElementById('searchInput').value || '').toLowerCase();
  const st = document.getElementById('stateSelect').value;
  const tbody = document.getElementById('metricsTbody');

  const filtered = currentLevelData.cells.filter(c => {{
    if(st === 'filled' && !c.filled) return false;
    if(st === 'empty' && c.filled) return false;
    if(q){{
      const str = (c.cell_id + ' ' + c.row + ' ' + c.col).toLowerCase();
      if(!str.includes(q)) return false;
    }}
    return true;
  }});

  if(filtered.length === 0){{
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:20px;color:var(--muted);">No matching cell records found.</td></tr>';
    return;
  }}

  tbody.innerHTML = filtered.map(c => `
    <tr>
      <td><code>\${{c.cell_id || ''}}</code></td>
      <td><strong>\${{c.level || ''}}</strong></td>
      <td>\${{c.row != null ? c.row : ''}}</td>
      <td>\${{c.col != null ? c.col : ''}}</td>
      <td style="font-family:'Consolas',monospace;font-size:11px;">\${{c.bbox || ''}}</td>
      <td><span class="\${{c.filled ? 'badge badge-ok' : 'badge badge-missing'}}">\${{c.filled ? 'FILLED' : 'EMPTY'}}</span></td>
      <td>\${{c.hit_count != null ? c.hit_count : (c.filled ? 1 : 0)}}</td>
    </tr>
  `).join('');
}}

function showError(msg){{
  document.getElementById('metricsTbody').innerHTML = `<tr><td colspan="7" style="text-align:center;padding:20px;color:var(--err);">\${{msg}}</td></tr>`;
}}

loadTableDataset();
</script>"""

    footer = render_footer("RASH-HIT Technical Tables Engine")
    res = head + "\n" + header + "\n" + nav_html + "\n" + kpi_section + "\n" + body_html + "\n" + footer
    return res
