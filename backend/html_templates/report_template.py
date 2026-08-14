"""Academic Report HTML Generator using Shared Design System."""

import json
import os
from pathlib import Path
from backend.html_templates.components import (
    render_head, render_header, render_nav_dynamic, render_svg_modal, render_footer
)

def build_relative_link(from_path: Path, to_path: Path) -> str:
    """Generate clean POSIX relative hyperlink between any two file paths."""
    try:
        rel = os.path.relpath(to_path, start=from_path.parent)
        return rel.replace("\\", "/")
    except Exception:
        return "#"

def build_academic_report_html(
    report_file_path: Path,
    output_root: Path,
    model: any,
    motif_h: str,
    src_name: str,
    package_id: str,
    total_levels: int,
    max_level: int,
    level_table_rows: str,
    gallery_html: str,
    fig_chips_html: str,
    cell_chips_html: str,
    embedded_manifest_json: str,
    has_pdf_report: bool = True,
    has_tables_html: bool = False,
    has_tables_json: bool = False,
    has_workbook: bool = True,
    has_manifest: bool = True,
    has_terminal_log: bool = False
) -> str:
    engine_h = f"CPU Exact Vector Geometry Engine &middot; Levels: {total_levels}"

    # Calculate relative paths dynamically using build_relative_link
    home_link = build_relative_link(report_file_path, output_root / "index.html")
    report_link = "#"
    excel_link = build_relative_link(report_file_path, report_file_path.parent.parent / "excel" / "workbook.xlsx")
    tables_link = build_relative_link(report_file_path, report_file_path.parent.parent / "tables" / "tables.html")
    manifest_link = build_relative_link(report_file_path, report_file_path.parent.parent / "manifest" / "manifest.json")
    terminal_link = build_relative_link(report_file_path, report_file_path.parent.parent / "terminal" / "terminal.txt")

    meta_tag = f'<meta name="rash-hit-package-id" content="{package_id}">'
    head = render_head(f"RASH-HIT Fractal Studio - {motif_h} Report", meta_tags=meta_tag)
    header = render_header("RASH-HIT FRACTAL STUDIO", f"{motif_h} Analysis Report · Box-Counting Fractal Dimension Analysis &middot; by Mehmet Raşit NARÇİÇEK")

    nav_html = render_nav_dynamic("report", home_link, report_link, tables_link, excel_link, manifest_link)

    kpi_section = f"""<section class="kpi-grid">
  <div class="kpi-card"><div class="kpi-lbl">Fractal Dimension (Db)</div><div class="kpi-val">{model.db:.4f}</div><div class="kpi-sub">Box-counting method</div></div>
  <div class="kpi-card"><div class="kpi-lbl">Log-Log Fit (R&sup2;)</div><div class="kpi-val">{model.r2:.4f}</div><div class="kpi-sub">Linear fit quality</div></div>
  <div class="kpi-card"><div class="kpi-lbl">Grid Levels</div><div class="kpi-val">{total_levels}</div><div class="kpi-sub">L01 &rarr; L{max_level:02d}</div></div>
  <div class="kpi-card"><div class="kpi-lbl">Execution Time</div><div class="kpi-val">{model.total_time_ms:.2f} ms</div><div class="kpi-sub">Complete pipeline</div></div>
</section>"""

    # Dynamically build output files categories & rows
    rows_html = []

    # Reports & Documents
    rows_html.append('          <tr class="file-cat-row"><td colspan="2">Reports &amp; Documents</td></tr>')
    rows_html.append('          <tr><td>📄 <a href="report.html">report.html</a></td><td>HTML</td></tr>')
    if has_pdf_report:
        rows_html.append('          <tr><td>📕 <a href="report.pdf" target="_blank" rel="noopener">report.pdf</a></td><td>PDF</td></tr>')

    # Data & Workbooks
    if has_workbook or has_tables_html or has_tables_json or cell_chips_html:
        rows_html.append('          <tr class="file-cat-row"><td colspan="2">Data &amp; Workbooks</td></tr>')
        if has_workbook:
            rows_html.append(f'          <tr><td>📈 <a href="{excel_link}" target="_blank" rel="noopener">workbook.xlsx</a></td><td>XLSX</td></tr>')
        if has_tables_html:
            rows_html.append(f'          <tr><td>📊 <a href="{tables_link}" target="_blank" rel="noopener">tables.html</a></td><td>HTML</td></tr>')
        if has_tables_json:
            tables_data_link = build_relative_link(report_file_path, report_file_path.parent.parent / "tables" / "tables_data.json")
            rows_html.append(f'          <tr><td>🧾 <a href="{tables_data_link}" target="_blank" rel="noopener">tables_data.json</a></td><td>JSON</td></tr>')
        if cell_chips_html:
            rows_html.append(cell_chips_html)

    # Vector Figure Maps
    if fig_chips_html:
        rows_html.append('          <tr class="file-cat-row"><td colspan="2">Vector Figure Maps (SVG)</td></tr>')
        rows_html.append(fig_chips_html)

    # Integrity & Verification
    if has_manifest or has_terminal_log:
        rows_html.append('          <tr class="file-cat-row"><td colspan="2">Integrity &amp; Verification</td></tr>')
        if has_manifest:
            rows_html.append(f'          <tr><td>🔒 <a href="{manifest_link}" target="_blank" rel="noopener">manifest.json</a></td><td>JSON</td></tr>')
        if has_terminal_log:
            rows_html.append(f'          <tr><td>📋 <a href="{terminal_link}" target="_blank" rel="noopener">terminal.txt</a></td><td>TXT</td></tr>')

    tbody_html = "\n".join(rows_html)

    content = f"""<div style="padding: 24px; max-width: 1400px; margin: 0 auto;">
  {kpi_section}

  <section class="section">
    <h2>Fractal Analysis Result</h2>
    <div class="table-container" style="overflow-x:auto;">
      <table>
        <thead><tr><th>Parameter</th><th>Value</th><th>Description</th></tr></thead>
        <tbody>
          <tr><td>Fractal Dimension (Db)</td><td style="font-weight:700;">{model.db:.4f}</td><td>Box-counting log-log regression slope</td></tr>
          <tr><td>Regression Fit (R&sup2;)</td><td style="font-weight:700;">{model.r2:.4f}</td><td>Log-log linear regression score</td></tr>
          <tr><td>Analysis Engine</td><td>{engine_h}</td><td>Vector geometry intersection engine</td></tr>
          <tr><td>Total Execution Time</td><td>{model.total_time_ms:.2f} ms</td><td>Pipeline execution time</td></tr>
        </tbody>
      </table>
    </div>
  </section>

  <section class="section">
    <h2>Grid Level Occupancy Overview</h2>
    <div class="table-container" style="overflow-x:auto;">
      <table>
        <thead><tr><th>Level</th><th>Grid</th><th>Total Cells</th><th>Filled</th><th>Empty</th><th>Occupancy (%)</th><th>Cell Size (WxH)</th><th>Time (ms)</th></tr></thead>
        <tbody>
          {level_table_rows}
        </tbody>
      </table>
    </div>
  </section>

  <section class="section">
    <h2>SVG Gallery</h2>
    <p style="color:var(--muted);margin-bottom:14px;">Interactive SVG map previews for each computed grid level. Click <b>Preview</b> to open the full-screen viewer (scroll to zoom, arrow keys to browse levels).</p>
    <div class="gallery-grid">
      {gallery_html}
    </div>
  </section>

  <section class="section">
    <h2>Output Files</h2>
    <p style="color:var(--muted);margin-bottom:14px;">Every generated file of this analysis package, listed in order under its folder.</p>
    <div class="table-container">
      <div class="file-folder-row">📁 outputs/{package_id}/</div>
      <div style="overflow-x:auto;">
        <table class="file-table" style="border-top:0;">
          <thead>
            <tr><th>File Name</th><th>Format</th></tr>
          </thead>
          <tbody>
            {tbody_html}
          </tbody>
        </table>
      </div>
    </div>
  </section>

  <section class="section">
    <h2>Checksum</h2>
    <div class="manifest-panel">
      <div class="manifest-head">
        <div>
          <div class="manifest-title">SHA-256 Checksum</div>
          <p>Open or expand generated file checksums for reproducibility review.</p>
        </div>
        <div class="card-actions">
          <a class="btn" href="{manifest_link}" target="_blank" rel="noopener">Open Manifest</a>
          <button class="btn soft" onclick="toggleManifestPanel()">Expand Checksums</button>
        </div>
      </div>
      <div id="manifestBody" class="manifest-body">
        <div class="table-container" style="margin: 16px; overflow-x: auto;">
          <table class="manifest-table" id="manifestTable" style="width:100%;">
            <thead><tr><th>File</th><th>SHA-256</th><th style="text-align:right;">Action</th></tr></thead>
            <tbody id="manifestRows"></tbody>
          </table>
        </div>
        <div id="manifestFallbackMsg" style="display:none;padding:14px;color:var(--muted);font-size:12px;font-weight:700;">
          ℹ️ Checksums are available in manifest.json. Use the "Open Manifest" button to verify file integrity.
        </div>
      </div>
    </div>
  </section>
</div>

<script>
const EMBEDDED_MANIFEST = {embedded_manifest_json};
async function toggleManifestPanel(){{
  const body = document.getElementById('manifestBody');
  body.classList.toggle('open');
  if(body.dataset.loaded === '1') return;
  await renderManifestBody();
}}
async function renderManifestBody(){{
  const body = document.getElementById('manifestBody');
  const target = document.getElementById('manifestRows');
  let rows = EMBEDDED_MANIFEST || [];
  if(!rows.length){{
    try{{
      const res = await fetch('{manifest_link}');
      if(res.ok){{
        const data = await res.json();
        rows = normalizeManifest(data);
      }}
    }}catch(e){{ rows = []; }}
  }}
  if(!rows.length){{
    document.getElementById('manifestTable').style.display = 'none';
    document.getElementById('manifestFallbackMsg').style.display = 'block';
  }}else{{
    document.getElementById('manifestTable').style.display = 'table';
    document.getElementById('manifestFallbackMsg').style.display = 'none';
    target.innerHTML = rows.map(r => `<tr><td>${{esc(r.file)}}</td><td><code>${{esc(r.sha256)}}</code></td><td style="text-align:right;"><button class="copy-btn" onclick="copyHash('${{esc(r.sha256)}}')">Copy</button></td></tr>`).join('');
  }}
  body.dataset.loaded = '1';
}}
function normalizeManifest(data){{
  if(Array.isArray(data)) return data.map(x => ({{file:x.file||x.path||x.name||'', sha256:x.sha256||x.hash||''}})).filter(x=>x.file||x.sha256);
  if(data && typeof data === 'object'){{
    if(Array.isArray(data.files)) return normalizeManifest(data.files);
    return Object.entries(data).map(([k,v]) => {{
      if(v && typeof v === 'object') return {{file:v.file||v.path||k, sha256:v.sha256||v.hash||""}};
      return {{file:k, sha256:String(v)}};
    }}).filter(x=>x.file||x.sha256);
  }}
  return [];
}}
async function copyHash(hash){{
  try{{ await navigator.clipboard.writeText(hash); }}catch(e){{}}
}}
function esc(v){{
  return String(v ?? '').replace(/[&<>"']/g, ch => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[ch]));
}}
</script>
"""

    modal = render_svg_modal()
    footer = render_footer(engine_h)

    # Embed the gallery items (src + label) so the modal can browse levels.
    gallery_items = []
    for lv in model.levels:
        lf = f"{lv.level:02d}"
        rs = f"{lv.cols}x{lv.rows}"
        gallery_items.append({
            "src": f"../figures/{lf}_{rs}_map.svg",
            "label": f"L{lf} · {rs} · {motif_h}",
        })
    gallery_js = "<script>const RASH_HIT_GALLERY = " + json.dumps(gallery_items) + ";</script>"

    res = head + "\n" + header + "\n" + nav_html + "\n" + content + "\n" + modal + "\n" + gallery_js + "\n" + footer
    return res
