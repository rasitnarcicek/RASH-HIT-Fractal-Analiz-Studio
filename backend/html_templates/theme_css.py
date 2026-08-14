"""Unified CSS Design System Tokens & Shared Styling Rules."""

SHARED_CSS = """
:root {
  --bg: #F8FAFC;
  --panel: #FFFFFF;
  --panel2: #F1F5F9;
  --sb: #0F172A;
  --sb-txt: #F8FAFC;
  --text: #0F172A;
  --muted: #64748B;
  --border: #E2E8F0;
  --accent: #2563EB;
  --accent-hover: #1D4ED8;
  --soft: #EFF6FF;
  --ok: #166534;
  --ok-bg: #DCFCE7;
  --warn: #9A3412;
  --warn-bg: #FFEDD5;
  --err: #991B1B;
  --err-bg: #FEE2E2;
}

[data-theme="dark"] {
  --bg: #0B0F19;
  --panel: #111827;
  --panel2: #1F2937;
  --sb: #030712;
  --sb-txt: #F9FAFB;
  --text: #F9FAFB;
  --muted: #9CA3AF;
  --border: #374151;
  --accent: #3B82F6;
  --accent-hover: #60A5FA;
  --soft: #1E3A8A;
  --ok: #4ADE80;
  --ok-bg: #064E3B;
  --warn: #FB923C;
  --warn-bg: #7C2D12;
  --err: #F87171;
  --err-bg: #7F1D1D;
}

* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.5;
  font-size: 13px;
  -webkit-font-smoothing: antialiased;
}

/* Header & Hero */
.app-header {
  background: var(--sb);
  color: var(--sb-txt);
  padding: 20px 24px;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}
.app-title {
  font-size: 24px;
  font-weight: 800;
  letter-spacing: -.03em;
  color: #FFFFFF;
}
.app-author {
  font-size: 13px;
  font-weight: 600;
  color: #93C5FD;
  margin-top: 2px;
}
.theme-toggle {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  border: 1px solid rgba(255,255,255,.2);
  background: rgba(255,255,255,.1);
  color: #FFF;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all .2s;
}
.theme-toggle:hover { background: rgba(255,255,255,.25); transform: scale(1.05); }
.theme-toggle::before { content: "☾"; }
[data-theme="dark"] .theme-toggle::before { content: "☀"; }

/* Navigation Bar */
.nav-bar {
  background: var(--panel);
  border-bottom: 1px solid var(--border);
  padding: 10px 24px;
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}
.nav-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  text-decoration: none;
  background: var(--panel2);
  color: var(--text);
  border: 1px solid var(--border);
  transition: all .15s;
}
.nav-btn:hover { border-color: var(--accent); color: var(--accent); }
.nav-btn.active { background: var(--accent); color: #FFF; border-color: var(--accent); }

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 7px 14px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid var(--border);
  background: var(--panel);
  color: var(--text);
  text-decoration: none;
  transition: all .15s;
}
.btn:hover { border-color: var(--accent); color: var(--accent); }
.btn-primary { background: var(--accent); color: #FFF; border-color: var(--accent); }
.btn-primary:hover { background: var(--accent-hover); color: #FFF; }
.btn-sm { padding: 4px 9px; font-size: 11px; }

/* Status Badges (package cards) */
.badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 9.5px;
  font-weight: 800;
  letter-spacing: .04em;
  text-transform: uppercase;
  white-space: nowrap;
}
.badge-ok { background: var(--ok-bg); color: var(--ok); }
.badge-warn { background: var(--warn-bg); color: var(--warn); }
.badge-missing { background: var(--err-bg); color: var(--err); }

/* Package Cards (index dashboard) */
.pkg-card .badge { flex-shrink: 0; }


/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}
.kpi-card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 1px 3px rgba(0,0,0,.05);
}
.kpi-lbl { font-size: 10px; font-weight: 700; color: var(--muted); text-transform: uppercase; }
.kpi-val { font-size: 18px; font-weight: 800; color: var(--accent); margin: 2px 0; }
.kpi-sub { font-size: 10px; color: var(--muted); }

/* Sections & Cards */
.section {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,.05);
}
.section h2 {
  font-size: 16px;
  font-weight: 800;
  margin-bottom: 12px;
  border-bottom: 1px solid var(--border);
  padding-bottom: 8px;
  color: var(--text);
}

/* Table container with rounded & closed borders */
.table-container {
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
  background: var(--panel);
  margin-bottom: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,.05);
}
.table-container tr:last-child td { border-bottom: none; }

/* Tables */
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}
th, td {
  padding: 9px 12px;
  border-bottom: 1px solid var(--border);
  text-align: left;
}
th {
  background: var(--sb, #0F172A);
  font-weight: 800;
  color: #FFFFFF;
  text-transform: uppercase;
  font-size: 11px;
  letter-spacing: .04em;
}
td { color: var(--text); }
td.num { text-align: right; font-variant-numeric: tabular-nums; }
tr:hover td { background: var(--soft); }

/* Modal Lightbox */
.modal {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,.75);
  z-index: 999;
  align-items: center;
  justify-content: center;
  padding: 20px;
}
.modal.open { display: flex; }
.modal-box {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 18px;
  max-width: 90vw;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

/* SVG Gallery Modal (big preview + wheel zoom + prev/next) */
.gallery-modal-box {
  width: min(96vw, 1200px);
  max-height: 94vh;
  padding: 16px;
}
.gallery-modal-hdr {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}
.gallery-modal-hdr strong { font-size: 14px; font-weight: 800; color: var(--text); }
.gallery-modal-tools { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; }
.gallery-counter {
  font-size: 11px;
  font-weight: 800;
  color: var(--muted);
  background: var(--panel2);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 3px 10px;
  margin-right: 4px;
}
.gallery-stage {
  position: relative;
  flex: 1;
  min-height: 60vh;
  background: #0B1220;
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}
.gallery-viewport {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  padding: 14px;
}
.gallery-viewport img {
  max-width: 100%;
  max-height: 74vh;
  object-fit: contain;
  background: #FFF;
  border-radius: 6px;
  transition: transform .08s ease;
  box-shadow: 0 6px 24px rgba(0,0,0,.35);
}
.gallery-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: 1px solid rgba(255,255,255,.25);
  background: rgba(255,255,255,.12);
  color: #FFF;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 5;
  transition: all .15s;
}
.gallery-arrow:hover { background: rgba(255,255,255,.3); transform: translateY(-50%) scale(1.08); }
.gallery-prev { left: 12px; }
.gallery-next { right: 12px; }
.gallery-hint {
  text-align: center;
  font-size: 11px;
  color: var(--muted);
  margin-top: 10px;
}

/* Gallery cards grid (modern compact) */
.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 8px;
}
.gallery-card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 6px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  box-shadow: var(--shadow);
}
.gallery-card:hover {
  border-color: var(--accent);
  box-shadow: var(--shadow-lg);
}
.gallery-visual {
  width: 100%;
  height: 100px;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  padding: 0;
  cursor: pointer;
  font: inherit;
  color: inherit;
  -webkit-appearance: none;
  appearance: none;
}
.gallery-visual img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  transition: transform .25s ease;
}
.gallery-card:hover .gallery-visual img { transform: scale(1.05); }
.card-actions {
  display: flex;
  gap: 6px;
  margin-top: 2px;
}
.card-actions .btn { flex: 1; }

/* Output Files table — folder header row + vertical file rows */
.file-folder-row {
  background: var(--sb, #0F172A);
  color: #FFFFFF;
  font-weight: 800;
  font-size: 12px;
  font-family: Consolas, monospace;
  padding: 10px 14px;
  border-radius: 8px 8px 0 0;
  letter-spacing: .02em;
}
.file-table { border-top: 0; }
.file-table th { background: var(--sb, #0F172A); }
.file-table td { font-size: 12px; }
.file-table .btn { font-size: 11px; }
.file-cat-row td {
  background: var(--panel2);
  font-weight: 800;
  color: var(--text);
  text-transform: uppercase;
  letter-spacing: .06em;
  font-size: 10.5px;
  padding: 6px 12px;
}

/* SHA-256 Manifest panel (modern) */
.manifest-panel {
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  background: var(--panel);
}
.manifest-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
  padding: 16px 18px;
  background: linear-gradient(135deg, var(--panel2), var(--panel));
  border-bottom: 1px solid var(--border);
}
.manifest-title { font-size: 14px; font-weight: 800; color: var(--text); }
.manifest-head p { font-size: 11px; color: var(--muted); margin-top: 3px; }
.manifest-head .card-actions { display: flex; gap: 8px; padding: 0; margin: 0; }
.manifest-head .card-actions .btn { flex: none; }
.manifest-body {
  max-height: 0;
  overflow: hidden;
  transition: max-height .3s ease;
}
.manifest-body.open {
  max-height: 480px;
  overflow-y: auto;
}
.manifest-table th {
  background: var(--sb, #0F172A);
  color: #FFF;
}
.manifest-table code {
  font-family: Consolas, monospace;
  font-size: 11px;
  word-break: break-all;
}
.copy-btn {
  border: 1px solid var(--border);
  background: var(--panel);
  color: var(--text);
  border-radius: 6px;
  padding: 3px 10px;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  transition: all .15s;
}
.copy-btn:hover { border-color: var(--accent); color: var(--accent); }

/* Footer */
.app-footer {
  text-align: center;
  color: var(--muted);
  font-size: 12px;
  padding: 24px 0;
  border-top: 1px solid var(--border);
  margin-top: 30px;
}
"""
