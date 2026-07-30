# RASH-HIT Fractal Studio

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-green.svg)](https://www.python.org/)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.21693694-blue.svg)](https://doi.org/10.5281/zenodo.21693694)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0005--3423--255X-green.svg)](https://orcid.org/0009-0005-3423-255X)

**RASH-HIT Fractal Studio** is a research-grade, raster-free computational software engine for SVG vector geometry analysis, grid occupancy mapping, box-counting fractal dimension ($D_b$) estimation, SVG Coordinate Map rendering, and academic research package generation.

Unlike conventional fractal analysis tools that convert vector artwork into PNG/JPEG pixels—introducing resolution loss, anti-aliasing artifacts, and scaling distortion—RASH-HIT Fractal Studio evaluates raw SVG vector geometry directly in floating-point coordinate space using C++ GEOS spatial predicates via Shapely.

---

## Key Features

- **Direct Vector Geometry Analysis**: Evaluates SVG `path`, `rect`, `circle`, `ellipse`, `line`, `polyline`, and `polygon` elements without rasterization.
- **Complete Fill & Stroke Predicates**: Evaluates closed shape fills (handling `nonzero` and `evenodd` fill rules) and stroke line widths.
- **Strict $2^i$ Power-of-Two Grid Planner**: Generates aspect-ratio-aware grid resolution series ($W_{\text{cell}} \approx H_{\text{cell}}$) that strictly double in grid count ($2^i$) across levels, guaranteeing quadtree parent-child containment without rounding drift.
- **Unlimited Level Scaling**: Supports arbitrary level depth (`--levels N`, $N \ge 1$). Default is 7 levels ($L01$--$L07$).
- **Robust Curve Flattening**: Converts Cubic/Quadratic Bézier curves and elliptical arcs (`A` commands) to vector segments with adaptive step tolerance.
- **Hardened XML Parser**: Uses `defusedxml` to prevent XML External Entity (XXE) vulnerabilities and enforces bounds checking across all SVG path commands.
- **Publication-Ready Academic Export**: Generates PDF reports, interactive HTML viewers, Markdown summaries, Excel workbooks (`.xlsx`), per-level cell datasets, pure vector SVG grid maps, terminal execution logs, and SHA-256 reproducibility manifests.

---

## Computational Method & Grid Complexity

### Box-Counting Fractal Dimension ($D_b$)
The engine places a multi-level grid over the SVG bounding box and tests vector intersection for each grid cell:
$$\log N(\varepsilon) = D_b \cdot \log\left(\frac{1}{\varepsilon}\right) + C$$

Where:
- $N(\varepsilon)$ = Number of occupied (filled/stroke-intersecting) grid cells
- $\varepsilon = \max(W_{\text{cell}}, H_{\text{cell}}) / \max(W_{\text{analysis}}, H_{\text{analysis}})$ = Normalized scale factor
- $D_b$ = Slope of the linear least-squares regression line
- $R^2 = 1 - \frac{SS_{\text{res}}}{SS_{\text{tot}}}$ = Coefficient of determination

### Grid Level Scaling & CPU Workload
There is **no hard limit** on the number of levels (`--levels N`). However, because grid resolution doubles at each step ($2^i$), total cell count scales quadratically (approximately **$4\times$ more cells per level**):

| Level | Grid Dimensions | Total Cells | Relative CPU & Memory Scale |
|:---|:---|:---|:---|
| **L01** | $4 \times 8$ | 32 | $1\times$ (Base) |
| **L02** | $8 \times 16$ | 128 | $\approx 4\times$ |
| **L03** | $16 \times 32$ | 512 | $\approx 16\times$ |
| **L04** | $32 \times 64$ | 2,048 | $\approx 64\times$ |
| **L05** | $64 \times 128$ | 8,192 | $\approx 256\times$ |
| **L06** | $128 \times 256$ | 32,768 | $\approx 1,024\times$ |
| **L07** | $256 \times 512$ | 131,072 | $\approx 4,096\times$ (Default cutoff) |
| **L08** | $512 \times 1024$ | 524,288 | $\approx 16,384\times$ |
| **L09** | $1024 \times 2048$ | 2,097,152 | $\approx 65,536\times$ |

> [!NOTE]
> Increasing `--levels` provides finer spatial resolution, but computation time and memory usage grow with cell count. For levels $L08$ and above, cell-level XLSX table exports are omitted by default (`--export-high-level-tables` to force $L08$) to keep export packages lightweight and avoid Excel cell limits.

---

## Installation & Setup

### Requirements
- Python 3.9+ (Python 3.11 or 3.12 recommended)
- 64-bit OS (Windows, Linux, macOS)

```bash
git clone https://github.com/rasitnarcicek/RASH-HIT-Fractal-Studio.git
cd RASH-HIT-Fractal-Studio
pip install -r requirements.txt
```

---

## Quick Start & CLI Usage

### Basic Analysis (Default: 7 Levels)
```bash
python run_analysis.py --input input_svgs/16D.svg
```

### High-Resolution Analysis (e.g. 10 Levels)
```bash
python run_analysis.py --input input_svgs/16D.svg --levels 10
```

### Batch Directory Analysis
```bash
python run_analysis.py --dir input_svgs/ --levels 7
```

### Options Reference
| Argument | Description | Default |
|:---|:---|:---|
| `--input` | Path to single input SVG file | `None` |
| `--dir` | Path to directory for batch SVG analysis | `None` |
| `--levels` | Number of grid levels ($N \ge 1$) | `7` |
| `--measure` | Measurement mode (`area`) | `area` |
| `--engine` | Computation engine (`cpu`) | `cpu` |
| `--profile` | Output profile (`lean`, `reproducible`, `debug`, `presentation`) | `lean` |
| `--output-dir` | Target export directory | `outputs/` |
| `--export-high-level-tables` | Force full XLSX cell table generation for Level 08 | `False` |

---

## Output Package Structure

Each analyzed SVG file generates a structured, self-contained output directory:

```text
outputs/[motif_name]/
├── report/
│   ├── report.pdf      # Publication PDF report
│   ├── report.html     # Interactive browser report
│   └── report.md       # Markdown summary
├── excel/
│   └── workbook.xlsx   # Multi-sheet summary workbook
├── tables/
│   ├── 01_4x8_cells.xlsx
│   └── tables.html     # Interactive cell data table viewer
├── figures/
│   └── 01_4x8_map.svg  # Pure vector SVG grid occupancy maps
├── terminal/
│   └── terminal.txt    # Execution log
└── manifest/
    └── manifest.json   # Reproducibility metadata with SHA-256 hash
```

---

## Dependencies & Third-Party Notices

- **Shapely / GEOS**: C++ spatial predicate engine for exact vector intersection queries (BSD / LGPL).
- **NumPy**: Vectorized 2D grid matrix indexing and numerical regression (BSD).
- **defusedxml**: Secure XML parsing against XXE attacks (Python PSF).
- **openpyxl**: Multi-sheet XLSX workbook generation (MIT).
- **PyMuPDF**: PDF report rendering engine (AGPL v3.0 / Commercial).
- **PyYAML, Pillow, tinycss2**: Configuration parsing, image validation, and inline CSS parsing.

See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) for full licensing details.

---

## Citation

If you use RASH-HIT Fractal Studio in your research, please cite:

- **Concept DOI**: [10.5281/zenodo.21693694](https://doi.org/10.5281/zenodo.21693694)
- **Version DOI (v1.0.4)**: [10.5281/zenodo.21694567](https://doi.org/10.5281/zenodo.21694567)

```bibtex
@software{Narcicek_RASH_HIT_Fractal_Studio_2026,
  author    = {Nar{\c{c}}i{\c{c}}ek, Mehmet Ra{\s}it},
  title     = {RASH-HIT Fractal Studio: Vector Geometry Analysis and Box-Counting Engine},
  year      = {2026},
  version   = {1.0.4},
  publisher = {GitHub},
  doi       = {10.5281/zenodo.21694567},
  url       = {https://doi.org/10.5281/zenodo.21694567},
  orcid     = {https://orcid.org/0009-0005-3423-255X},
  license   = {Apache-2.0}
}
```

---

## License & Author

Distributed under the **Apache License, Version 2.0**. See [`LICENSE`](LICENSE) for details.

- **Author**: Mehmet Raşit Narçiçek
- **ORCID**: [0009-0005-3423-255X](https://orcid.org/0009-0005-3423-255X)
- **Copyright**: © 2026 Mehmet Raşit Narçiçek
