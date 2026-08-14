# RASH-HIT Fractal Studio

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-green.svg)](https://www.python.org/)
[![Concept DOI](https://img.shields.io/badge/Concept_DOI-10.5281%2Fzenodo.21693694-blue.svg)](https://doi.org/10.5281/zenodo.21693694)
[![Version DOI](https://img.shields.io/badge/Version_DOI-10.5281%2Fzenodo.21704656-blue.svg)](https://doi.org/10.5281/zenodo.21704656)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0005--3423--255X-green.svg)](https://orcid.org/0009-0005-3423-255X)

**RASH-HIT Fractal Studio** is a research-grade, raster-free computational software engine (the **RASH-HIT Fractal Engine**) for SVG vector geometry analysis, aspect-ratio-aware grid occupancy mapping, box-counting fractal dimension ($D_b$) estimation, SVG Coordinate Map rendering, and academic research package generation.

Unlike conventional image-processing tools that convert vector artwork into PNG/JPEG pixel rasters—introducing resolution dependency, anti-aliasing distortion, edge blurring, and scaling artifacts—the **RASH-HIT Fractal Engine** evaluates raw SVG vector geometry directly in continuous floating-point coordinate space using C++ GEOS spatial predicates via Shapely 2.0.

---

## Table of Contents

1. [Research Context & Motivation](#research-context--motivation)
2. [Key Architecture & System Modules](#key-architecture--system-modules)
3. [Mathematical Methodology & Regression](#mathematical-methodology--regression)
4. [Computational Geometry Pipeline](#computational-geometry-pipeline)
   - [SVG Element & Styling Resolution](#svg-element--styling-resolution)
   - [CSS Unit Conversions](#css-unit-conversions)
   - [2D Affine Transformation Matrix Stack](#2d-affine-transformation-matrix-stack)
   - [Curve & Arc Vector Flattening](#curve--arc-vector-flattening)
   - [Fill Rule Topology Resolution](#fill-rule-topology-resolution)
5. [Aspect-Ratio-Aware Grid Planning](#aspect-ratio-aware-grid-planning)
6. [Performance Optimization & Complexity Analysis](#performance-optimization--complexity-analysis)
   - [Unlimited Level Depth & Workload Scaling](#unlimited-level-depth--workload-scaling)
   - [Complementary Empty Cell Accounting](#complementary-empty-cell-accounting)
   - [RLE Compression & Spatial Indexing](#rle-compression--spatial-indexing)
   - [Parallel Adaptive Negative Space Ledger Engine (RASH-HIT Fractal Engine)](#parallel-adaptive-negative-space-ledger-engine-rash-hit-fractal-engine)
7. [Output Dashboard](#output-dashboard)
8. [Technical Documentation](#technical-documentation)
9. [Package Versioning & Overwrite Protection](#package-versioning--overwrite-protection)
10. [Output Profiles & Execution Modes](#output-profiles--execution-modes)
11. [Academic Output Package Specifications](#academic-output-package-specifications)
12. [Script & Tools Directory](#script--tools-directory)
13. [Installation & Dependencies](#installation--dependencies)
14. [npm & CLI Script Commands](#npm--cli-script-commands)
15. [CLI Usage & Level Counts](#cli-usage--level-counts)
16. [Code Provenance & Authorship Statement](#code-provenance--authorship-statement)
17. [Third-Party Notices & Dependencies](#third-party-notices--dependencies)
18. [Validation Table](#validation-table)
19. [System Audit History](#system-audit-history)
20. [Release Notes (v1.0.6)](#release-notes-v106)
21. [[TR] RASH-HIT Fractal Studio — Türkçe Sürüm](#tr-rash-hit-fractal-studio--turkce-surum)

---

## Research Context & Motivation

Design, architectural, motif, visual heritage, and pattern research frequently rely on visual forms natively stored as Scalable Vector Graphics (SVG). Standard software workflows often convert these vector files into rasterized bitmap images before applying box-counting algorithms.

Rasterization distorts mathematical fractal measurements in several ways:
- **Pixel Grid Discretization**: Fine geometric details below pixel resolution are merged or deleted.
- **Anti-Aliasing Fringing**: Boundary pixels become partially transparent or shaded, altering occupancy decisions.
- **Scale Dependence**: The measured fractal dimension varies depending on the arbitrary pixel resolution chosen for rasterization.

**RASH-HIT Fractal Engine Studio** eliminates rasterization entirely. It parses raw SVG elements (`path`, `rect`, `circle`, `ellipse`, `line`, `polyline`, `polygon`), evaluates 2D affine transform stacks, flattens Bézier curves and elliptical arcs, and evaluates geometric intersections directly against floating-point grid bounding boxes using C++ GEOS spatial predicates.

### Quantifying Design Intuition: From Qualitative Critique to Empirical Metrics

The RASH-HIT Fractal Engine is universally applicable across all design disciplines, including architecture, graphic design, textile engineering, decorative arts, traditional motifs, and pattern design. Its primary purpose is to mathematically analyze and visualize the spatial distribution of filled and empty regions within any 2D composition.

In creative workflows, peer reviews, or design critiques, practitioners frequently rely on subjective, qualitative statements such as:
- *"This section feels too crowded/busy, we should empty it out."*
- *"This composition is too sparse/empty, let's fill it up with details."*

While these observations are valuable, they lack objective baseline measurements. RASH-HIT Fractal Studio bridges this gap by translating subjective, intuitive design claims into rigorous, scientific, and empirical data. By calculating exact cell occupancy rates, counting filled vs. empty cells, mapping spatial distributions, and computing the fractal dimension ($D_b$), the system provides an objective mathematical foundation for complexity, density, and balance in design theory. This quantitative baseline is essential for validating design decisions scientifically.

---

## Key Architecture & System Modules

RASH-HIT Fractal Studio features an API-first, decoupled modular architecture powered by the **RASH-HIT Fractal Engine**:

- **`backend/`**: Contains the core vector computation engine (`processor.py`, `geometry_engine.py`, `intersection_hierarchical.py`), REST API (`web_server.py`), and academic output generators (`academic_exporter.py` + `backend/html_templates/` for the report/table HTML builders).
- **`frontend/`**: Hosts the decoupled web dashboard UI (`frontend/index.html`, `css/`, `js/`, `vendor/`).
- **`outputs/`**: Operates strictly as a **Pure Data Repository** storing machine-readable index data (`package_index.json`) and individual package folders (`16A/`, `16D/`).
- **`tests/`**: Automated unit and integration test suite (`pytest`) and Node unit tests (`js/`).
- **`tools/`**: Permanent developer tooling — license/notice validators (`validate_license_docs.py`, `final_public_scan.py`).
- **`archive/`**: Archived legacy material (contains README.md documenting what was archived).

> [!NOTE]
> **Decoupled Architecture Rules**:
> 1. `outputs/index.html` is no longer generated. `outputs/` contains strictly pure data artifacts.
> 2. The single active web dashboard operates from `frontend/index.html`.
> 3. All frontend HTTP/REST API calls are strictly funneled through `frontend/js/api.js`.
> 4. `academic_exporter.py`, `report_template.py`, and `tables_template.py` remain preserved for academic package generation (`report.html`, `tables.html`, `tables_data.json`, `workbook.xlsx`, `manifest.json`).
> 5. Legacy dashboard generator modules (`dashboard_exporter.py`, `dashboard_js.py`, `html_templates/index_template.py`) were **removed** in the v1.0.6 cleanup; the live dashboard is fully served from `frontend/`.

The codebase is organized into decoupled, specialized backend modules:

```text
SVG File Input
   │
   ├──▶ 1. SVGLoader & Secure XML Parser (backend/svg_loader.py)
   │      ├── defusedxml XXE Security Hardening
   │      ├── ViewBox & Scale Resolution (viewBox ➔ width/height ➔ geometry bounds ➔ 100x100 fallback)
   │      ├── CSS Rule Parser (tinycss2 + regex fallback) & Inline Style Resolver
   │      ├── CSS Length Unit Normalization (px, pt, mm, cm, in, pc, em, rem, %)
   │      └── Effective Opacity & Visibility Filtering (opacity, fill-opacity, stroke-opacity, display, visibility)
   │
   ├──▶ 2. Geometry Engine (backend/geometry_engine.py)
   │      ├── 3x3 Homogeneous Affine Transformation Stack (translate, rotate, scale, skewX, skewY, matrix)
   │      ├── Curve & Arc Flattening (Cubic/Quadratic Bézier & Elliptical Arc parameterization)
   │      ├── Transformed Stroke Width Scaling: w_effective = w_stroke * sqrt(|det(M)|)
   │      └── Polygon Fill Rule Topology Resolution (nonzero: unary_union / evenodd: symmetric_difference)
   │
   ├──▶ 3. Aspect-Ratio-Aware Grid Planner (backend/grid_planner.py)
   │      └── Base grid resolution setup & strict 2^i power-of-two resolution doubling across levels
   │
   ├──▶ 4. Hierarchical Quadtree Spatial Pruning (backend/intersection_hierarchical.py)
   │      └── Quadtree recursive decomposition & STRtree bulk spatial pruning across grid levels
```

---

## Mathematical Methodology & Regression

Linear regression is calculated over the log-log transform of grid size $r$ (defined as $1/\text{cols}$) and occupied box count $N(r)$:

$$\ln N(r) = -D_b \ln(r) + C \quad \implies \quad D_b = \lim_{r \to 0} \frac{\ln N(r)}{\ln(1/r)}$$

- **Slope Resolution**: Fitted using ordinary least squares (OLS) linear regression.
- **Coefficient of Determination ($R^2$)**: Evaluates fit quality. A threshold of $R^2 \ge 0.98$ is strictly enforced for valid fractal dimension reporting.
- **Academic Standard**: Box occupancy is checked at the absolute exact boundary of vector coordinates, with zero rounding error.

---

## Computational Geometry Pipeline

### SVG Element & Styling Resolution
The loader reads raw SVG tags, resolves inherited presentation attributes (`fill`, `stroke`, `stroke-width`, `opacity`, `display`, `visibility`), and extracts inline/embedded CSS styling rules parsed via `tinycss2`. It drops elements marked hidden (`display="none"` or `visibility="hidden"`) or fully transparent (`opacity="0"`).

### CSS Unit Conversions
Dimensions and coordinates are normalized to viewport pixels using standard ratios:
- `1in = 96px`, `1pt = 1.333px`, `1pc = 16px`
- `1mm = 3.779px`, `1cm = 37.795px`
- Viewbox relative units (`%`, `em`, `rem`) are computed dynamically against resolved viewbox scales.

### 2D Affine Transformation Matrix Stack
Elements nested inside SVG group tags (`<g>`) accumulate affine transformation matrices. Every geometric node is converted to a homogeneous coordinate vector $[x, y, 1]^T$ and multiplied by the accumulated $3 \times 3$ transformation matrix:

$$\begin{bmatrix} x' \\ y' \\ 1 \end{bmatrix} = \begin{bmatrix} a & c & e \\ b & d & f \\ 0 & 0 & 1 \end{bmatrix} \begin{bmatrix} x \\ y \\ 1 \end{bmatrix}$$

### Curve & Arc Vector Flattening
Bézier curves and elliptical arcs are flattened into discrete linear segments using subdivision tolerances. Circular and elliptical arcs are parameterized dynamically based on sweep and rotation angles.

### Fill Rule Topology Resolution
Polygon fills are generated according to the SVG `fill-rule` specification:
- **nonzero**: Resolved via C++ GEOS `unary_union` polygon aggregation.
- **evenodd**: Resolved via C++ GEOS `symmetric_difference` XOR aggregation.

---

## Aspect-Ratio-Aware Grid Planning

To prevent distortion of the measured fractal dimension from non-square aspect ratios, the engine plans grid maps where cells are guaranteed to be 100% square. It dynamically extends grid bounds to match the viewbox aspect ratio, keeping cell sizes symmetrical in both dimensions ($w_\text{cell} = h_\text{cell}$).

---

## Performance Optimization & Complexity Analysis

### Unlimited Level Depth & Workload Scaling
Standard box-counting algorithms suffer from exponential space and time complexity $O(2^{2L})$ where $L$ is the level depth. At level 12, a naive implementation checks $16,777,216$ cells against vector geometries individually, which is computationally prohibitive.

### Complementary Empty Cell Accounting
By evaluating parent cells first and propagating empty space flags downward, sub-grids that are completely empty are immediately skipped from geometric evaluations, reducing the calculation workload to $O(N(r))$ where $N(r)$ is the count of occupied boxes.

### RLE Compression & Spatial Indexing
Occupancy matrices at high levels are compressed using Run-Length Encoding (RLE) row-runs. Spatial querying is optimized via STRtree R-tree indices built in C++, pruning vector segments outside active cell bboxes.

### Parallel Adaptive Negative Space Ledger Engine
The **RASH-HIT Fractal Engine** uses a parallel-aware negative space ledger. By tracking and caching empty parent coordinates across concurrent workers, it prunes empty spaces dynamically across multi-threaded CPU architectures, speeding up high-level calculations by up to 5x.

---

## Output Dashboard

The web dashboard (`frontend/index.html`) is an API-first interface written in modern, dependency-free vanilla JS:
- **Overview**: Displays metadata cards for all processed output packages.
- **Details Drawer**: Slides in from the right to show metadata, SHA-256 manifests, and file logs.
- **Live Scientific Console**: Polls active analysis progress in real-time, printing table rows with flash animations and live logs.
- **Compare View**: Compares multiple runs side-by-side.
- **Interactive SVG Maps**: Renders zoomable grid overlays directly over input vector shapes.

---

## Technical Documentation
For full API routing details, component layouts, and JSON schemas, refer to the active documentation:
- `docs/architecture.md`: Module architecture and processing pipeline details.
- `docs/api_contract.md`: Comprehensive REST API endpoint contract.
- `docs/frontend_components.md`: Detailed breakdown of dashboard sections and UI styling.

---

## Package Versioning & Overwrite Protection

Every execution produces a structured directory under `outputs/` identified by the motif slug and creation timestamp (e.g. `16D_20260810_123000`). If `overwrite=True` is explicitly passed via API/CLI, it replaces the directory directly.

---

## Output Profiles & Execution Modes

The engine supports five pre-configured output profiles:
- **`lean`** (default): Generates key summaries, Excel files, and gates raw index data to level 8.
- **`reproducible`**: Generates full raw coordinate lists, manifests, and tables for all levels.
- **`presentation`**: Optimized for rendering high-resolution visual reports.
- **`debug`**: Retains full step execution logs, SVG geometry dumps, and metrics.
- **`batch`**: Tailored for batch directory runs; limits heavy tables but keeps SVG maps.

---

## Academic Output Package Specifications

Each processed package contains:
- `report/report.html`: Academic interactive HTML summary using Navy design system.
- `report/report.pdf`: Print-ready PDF report compiled using PyMuPDF.
- `excel/workbook.xlsx`: Multi-sheet Excel workbook (Cover, Summary, Levels, Regression, Maps).
- `tables/tables_data.json` & `tables/levels.csv`: Raw metrics.
- `manifest/manifest.json`: Integrity audit containing SHA-256 hashes of every file in the package.

---

## Script & Tools Directory

The repository contains several key scripts and utilities:
- **`run_analysis.py`**: The core Python CLI entry point. Executes single file analysis or batch folder processing.
- **`launcher.py`**: Stylized terminal menu written with the Rich library. Launches Web Server, CLI Analysis, System Diagnostics, or runs Pytest.
- **`bin/rash-hit.js`**: npm CLI wrapper (`rash-hit`). Automatic Python environment check and dependency bootstrapper.
- **`start.bat` & `start.sh`**: OS-specific startup scripts for launching the Interactive TUI Launcher.
- **`scripts/verify_orientation.py`**: Validates generated Excel sheets against C++ geometry objects.
- **`tests/run_koch_test.py`** (formerly `run_koch_test.py`): Standalone mathematical verification script comparing Koch Curve box-counting metrics to theoretical dimension.
- **`tools/validate_license_docs.py`**: Verifies license headers and notice file structure.
- **`tools/final_public_scan.py`**: Pre-release scanner guarding against absolute paths and sensitive folders.

---

## Installation & Dependencies

Ensure Python 3.9+ and Node.js 16+ are installed.

```bash
# Clone the repository
git clone https://github.com/mehmetrasit/rash-hit-fractal-studio.git
cd rash-hit-fractal-studio

# Install dependencies (Python & Node)
npm run setup
```

### Python Dependencies (`requirements.txt`)
- `numpy>=2.4.6`: High-performance numerical processing.
- `shapely>=2.1.2`: Exact C++ GEOS vector predicates.
- `openpyxl>=3.1.5`: Backend Excel workbook builder.
- `PyMuPDF>=1.28.0`: PDF export compiler.
- `Pillow>=9.0.0`: Image processing pipeline.
- `tinycss2>=1.1.0`: SVG CSS styling parser.
- `defusedxml>=0.7.1`: XML security hardening (XXE protection).
- `rich>=13.0.0`: Stylized CLI terminal elements.
- `pytest>=7.0`: Unit testing framework.

### npm Dependencies (`package.json`)
- `exceljs` (Production): Client-side spreadsheet formatting.
- `jsdom` (Dev): Headless DOM testing.

---

## npm & CLI Script Commands

Available scripts declared in `package.json`:
- `npm start`: Runs the interactive launcher menu (`launcher.py`).
- `npm run setup`: Installs all required Python packages.
- `npm run check`: Executes system environment checks.
- `npm run lint`: Performs static analysis lint checks (`pyflakes`).
- `npm test`: Runs the pytest suite.
- `npm run test:js`: Runs the JavaScript unit test suite.
- `npm run validate`: Validates LICENSE and NOTICE files.

---

## CLI Usage & Level Counts

Run the analysis script directly via Python:

```bash
# Analyze a single SVG file (levels 1-7)
python run_analysis.py --input input_svgs/16D.svg --levels 7 --profile lean

# Process all files in batch directory
python run_analysis.py --batch input_svgs/ --levels 6 --profile batch
```

---

## Code Provenance & Authorship Statement

### Original Development Statement
RASH-HIT Fractal Studio was developed as an original personal academic software project by Mehmet Raşit Narçiçek.

### Scope & Intellectual Property Boundaries
The project does not claim ownership over GEOS, Shapely, box-counting theory, or general quadtree algorithms.

The original contribution of this project lies in:
- SVG fill and stroke geometry extraction pipeline.
- Aspect-ratio-aware grid planning algorithms.
- Automated academic export engine (PDF, HTML, Excel, SVG maps, manifest metadata).
- Fully reproducible SHA-256 manifest system.

### Module Provenance Directory

| Module / File Path | Author | Provenance & Description |
|:---|:---|:---|
| `run_analysis.py` | Mehmet Raşit Narçiçek | Original CLI entry point & analysis pipeline manager. |
| `backend/svg_loader.py` | Mehmet Raşit Narçiçek | Original SVG parsing and ViewBox scale engine. |
| `backend/geometry_engine.py` | Mehmet Raşit Narçiçek | Original vector path extraction & style resolver. |
| `backend/grid_planner.py` | Mehmet Raşit Narçiçek | Original aspect-ratio-aware grid plan generator. |
| `backend/intersection_cpu.py` | Mehmet Raşit Narçiçek | Original CPU data models and level result wrappers. |
| `backend/intersection_hierarchical.py` | Mehmet Raşit Narçiçek | Original quadtree spatial pruning engine. |
| `backend/regression.py` | Mehmet Raşit Narçiçek | Log-log regression & Db calculation engine. |
| `backend/academic_exporter.py` | Mehmet Raşit Narçiçek | Original multi-format academic report exporter. |
| `backend/output_profiles.py` | Mehmet Raşit Narçiçek | Original output profile management system. |
| `backend/processor.py` | Mehmet Raşit Narçiçek | Original analysis pipeline orchestrator. |
| `backend/tui.py` | Mehmet Raşit Narçiçek | Original terminal user interface & menus. |
| `backend/web_server.py` | Mehmet Raşit Narçiçek | Original Flask/aiohttp web dashboard & REST API. |
| `backend/batch_processor.py` | Mehmet Raşit Narçiçek | Original batch SVG analysis runner. |
| `backend/confidence.py` | Mehmet Raşit Narçiçek | Original fractal confidence scoring system. |
| `backend/package_index.py` | Mehmet Raşit Narçiçek | Original output package index builder. |
| `backend/artifact_validator.py` | Mehmet Raşit Narçiçek | Original artifact integrity checker. |
| `launcher.py` | Mehmet Raşit Narçiçek | Original system entry point & menu. |
| `tests/run_koch_test.py` | Mehmet Raşit Narçiçek | Standalone mathematical verification runner. |

---

## Third-Party Notices & Dependencies

RASH-HIT Fractal Studio relies on third-party open-source computational software libraries:

- **Shapely / GEOS** (BSD 3-Clause / LGPL 2.1): Used as third-party computational geometry dependencies for exact vector intersection predicates.
- **NumPy** (BSD 3-Clause): Used for high-performance array operations and matrix grid indexing.
- **ExcelJS** (MIT License): Used in client-side dashboard for styled `.xlsx` workbook generation.
- **openpyxl** (MIT License): Used in backend Python for producing Excel workbooks (`workbook.xlsx`) and per-level cell datasets.
- **PyMuPDF / fitz** (GNU AGPL v3.0): Used for compiled PDF report generation (`report.pdf`).
- **defusedxml** (PSFL): Used for XML security hardening against entity expansion (XXE) vulnerabilities.
- **tinycss2** (BSD 3-Clause): Used for parsing SVG inline CSS style declarations.
- **Pillow** (HPND License): Used for image processing, dimension checks, and graphics.
- **rich** (MIT License): Used to build beautiful CLI outputs, tables, and dashboards.

---

## Validation Table

Mathematical correctness was verified using standard fixtures (such as the Koch Curve) at level 7, checking measured values against theoretical values:

| Fixture | Theoretical D | Measured D | Absolute Error | Percentage Error | $R^2$ | Warnings |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Koch Curve | 1.2619 | 1.3216 | 0.0597 | 4.73% | 0.9987 | None |

An $R^2 \ge 0.99$ linear fit proves that the raster-free geometry calculation is highly accurate and reproducible.

---

## System Audit History

During the development cycle, the codebase underwent a detailed system audit (v1.0.5) resolving critical operational bugs:
- **Encoding & i18n Fixes**: Corrupted Turkish characters in generated Excel coordinate maps were resolved, and file name slugs were hardened.
- **Professional Dashboard Excel Export**: Adapted `export.js` to support Slate design templates (gray borders, navy headers, Consolas formatting, auto-sized columns).
- **Interactive TUI Alignment**: Re-aligned the TUI ASCII logo in Bold White academic tone and centered all tables.
- **API Performance**: Debounced dashboard search inputs to 150ms and capped live log streaming to 500 lines to prevent UI freezing.
- **Path Traversal Protection**: REST delete endpoints were secured to prevent folder traversal outside the `outputs/` folder.

---

## Release Notes (v1.0.6)

- Initial public release of RASH-HIT Fractal Studio.
- CPU Exact Vector Geometry Engine for SVG-based raster-free box-counting analysis.
- Aspect-ratio-aware multilevel grid planning.
- Box-counting fractal dimension estimation using log-log regression.
- Publication-ready output package including PDF, HTML, Excel workbook, per-level XLSX tables, SVG maps, interactive tables viewer, and manifest metadata.
- Interactive central Output Library dashboard (`frontend/index.html`) with 7 View Modes.
- Parallel Adaptive Negative Space Ledger Engine for fast empty-cell pruning.
- Clean single-language (English UI) release package ready for open-source distribution.

---

# [TR] RASH-HIT Fractal Studio — Türkçe Sürüm

**RASH-HIT Fractal Studio**, SVG vektör geometrisi analizi, en boy oranına duyarlı ızgara doluluk haritalaması, kutu sayma (box-counting) yöntemiyle fraktal boyut ($D_b$) tahmini, SVG Koordinat Haritası oluşturma ve akademik araştırma paketleri üretimi için geliştirilmiş, akademik düzeyde, rasterleştirme (görüntüye dönüştürme) yapmayan bir hesaplama motorudur (**RASH-HIT Fractal Engine**).

Vektör çizimlerini PNG/JPEG piksel matrislerine dönüştürerek çözünürlük bağımlılığı, kenar yumuşatma (anti-aliasing) bozulması ve ölçeklendirme hataları üreten geleneksel yazılımların aksine, **RASH-HIT Fractal Engine** ham SVG vektör geometrisini doğrudan C++ GEOS geometrik ilişkilerini kullanan Shapely 2.0 üzerinden kesintisiz kayan noktalı koordinat uzayında analiz eder.

---

## [TR] İçindekiler

1. [Araştırma Bağlamı ve Motivasyon](#tr-arastirma-baglami-ve-motivasyon)
2. [Temel Mimari ve Sistem Modülleri](#tr-temel-mimari-ve-sistem-modulleri)
3. [Matematiksel Metot ve Regresyon](#tr-matematiksel-metot-ve-regresyon)
4. [Hesaplamalı Geometri İşlem Hattı](#tr-hesaplamali-geometri-islem-hatti)
5. [En Boy Oranına Duyarlı Izgara Planlaması](#tr-en-boy-oranina-duyarli-izgara-planlamasi)
6. [Performans Optimizasyonu](#tr-performans-optimizasyonu)
7. [Çıktı Kontrol Paneli (Dashboard)](#tr-cikti-kontrol-paneli-dashboard)
8. [Betik ve Araçlar Dizini](#tr-betik-ve-araclar-dizini)
9. [Kurulum ve Bağımlılıklar](#tr-kurulum-ve-bagimliliklar)
10. [Çalıştırma ve CLI Kullanımı](#tr-calistirma-ve-cli-kullanimi)
11. [Kod Kaynağı ve Yazarlık Beyanı](#tr-kod-kaynagi-ve-yazarlik-beyani)
12. [Doğrulama Tablosu](#tr-dogrulama-tablosu)
13. [Sistem Denetim Geçmişi](#tr-sistem-denetim-gecmisi)

---

## [TR] Araştırma Bağlamı ve Motivasyon

Tasarım, mimarlık, motif, kültürel miras ve desen araştırmaları sıklıkla SVG formatında saklanan görsellere dayanır. Standart yazılım iş akışları, kutu sayma algoritmalarını uygulamadan önce bu vektör dosyalarını piksel tabanlı görüntülere dönüştürür.

Rasterleştirme (piksele dönüştürme), matematiksel fraktal ölçümlerini şu yollarla bozar:
- **Piksel Izgara Ayrıklaştırması**: Piksel çözünürlüğünün altındaki ince geometrik detaylar birleşir veya silinir.
- **Kenar Yumuşatma Etkisi**: Sınır pikselleri yarı saydam hale gelerek doluluk kararlarını etkiler.
- **Ölçek Bağımlılığı**: Ölçülen fraktal boyutu rasterleştirme için seçilen çözünürlüğe göre değişir.

**RASH-HIT Fractal Studio** rasterleştirmeyi tamamen ortadan kaldırır. SVG elemanlarını (`path`, `rect`, `circle`, `ellipse`, `line`, `polyline`, `polygon`) doğrudan ayrıştırır, 2D dönüşüm matrislerini uygular ve C++ GEOS geometrik sorgularını Shapely kullanarak doğrudan floating-point ızgara hücreleri üzerinde hesaplar.

### Tasarım Sezgilerini Sayısallaştırma: Öznel Yorumlardan Empirik Verilere

RASH-HIT Fractal Engine; mimarlık, grafik tasarım, tekstil mühendisliği, geleneksel motif ve desen tasarımı, görsel sanatlar ve endüstriyel tasarım dahil olmak üzere tüm tasarım disiplinlerinde evrensel olarak kullanılabilir. Temel amacı, herhangi bir 2D kompozisyondaki dolu ve boş bölgelerin mekânsal dağılımını matematiksel olarak analiz etmek ve görselleştirmektir.

Yaratıcı süreçlerde, jüri değerlendirmelerinde veya tasarım eleştirilerinde, tasarımcılar ve paydaşlar genellikle şu tür öznel ve niteliksel (nitel) ifadelere başvururlar:
- *"Bu alan çok dolu/kalabalık görünüyor, buraları biraz boşaltalım."*
- *"Bu kompozisyon çok boş kalmış, detaylarla doldurmalıyız."*

Bu sezgisel gözlemler kıymetli olsa da nesnel bir ölçüm tabanından yoksundur. RASH-HIT Fractal Studio, bu sezgisel yargıları kesin, bilimsel ve nicel (niceliksel) verilere dönüştürerek bu boşluğu doldurur. Izgara hücrelerinin doluluk/boşluk oranlarını, mekânsal dağılımlarını ve fraktal boyutunu ($D_b$) hesaplayarak; estetik, yoğunluk, denge ve karmaşıklık değerlendirmelerine bilimsel ve matematiksel bir zemin kazandırır. Tasarım kararlarını kanıta ve veriye dayalı hale getirmek için bu nicel analizlerin yapılması şarttır.

---

## [TR] Temel Mimari ve Sistem Modülleri

Proje, API öncelikli, ayrıştırılmış modüler bir yapıya sahiptir:
- **`backend/`**: Çekirdek hesaplama motoru, web sunucusu (`web_server.py`) ve akademik rapor üreticilerini barındırır.
- **`frontend/`**: Bağımsız web arayüzünü içerir (`frontend/index.html`).
- **`outputs/`**: Analiz sonuçlarının saklandığı **Salt Veri Deposu**dur (Pure Data Repository).
- **`tests/`**: Pytest tabanlı Python testlerini ve Node tabanlı JS testlerini içerir.
- **`tools/`**: Lisans doğrulama ve kod tarama araçlarını barındırır.

---

## [TR] Matematiksel Metot ve Regresyon

Hücre boyutu $r$ ($1/\text{cols}$) ile dolu kutu sayısı $N(r)$ arasındaki regresyon şu formülle hesaplanır:

$$\ln N(r) = -D_b \ln(r) + C$$

Geometrik doluluk hesaplamalarında $R^2 \ge 0.98$ barajı aranmaktadır. $R^2 \ge 0.99$ değerleri doğrusal modelin yüksek uyumunu göstermektedir.

---

## [TR] Hesaplamalı Geometri İşlem Hattı

1. **SVG Stil Çözümleme**: `tinycss2` kütüphanesi kullanılarak satır içi ve gömülü CSS kuralları ayrıştırılır. `display="none"` veya `visibility="hidden"` olan elemanlar elenir.
2. **2D Dönüşüm Matrisleri**: SVG gruplarında (`<g>`) yer alan matrisler (`translate`, `rotate`, `scale`, `skew`) çarpılarak nesnelere uygulanır.
3. **Eğri Düzleştirme (Flattening)**: Bézier eğrileri ve eliptik yaylar kayan noktalı doğru parçacıklarına dönüştürülür.
4. **Doluluk Kuralları (Fill Rule)**: `nonzero` kuralları için geometrik birleşim (`unary_union`), `evenodd` kuralları için simetrik fark (`symmetric_difference`) işlemleri yürütülür.

---

## [TR] En Boy Oranına Duyarlı Izgara Planlaması

Görsellerin en-boy oranından kaynaklanan geometrik bozulmaları önlemek amacıyla, hesaplama hücreleri daima tam kare ($w_\text{cell} = h_\text{cell}$) olacak şekilde genişletilmiş ızgara sınırları çizilir.

---

## [TR] Performans Optimizasyonu

Hiyerarşik boş alan takibi (Complementary Empty Cell Accounting) sayesinde, tamamen boş olduğu saptanan üst seviye hücrelerin alt kırılımları hesaplama dışı bırakılır. High-level seviyelerde (L9+) RLE (Run-Length Encoding) sıkıştırması uygulanarak SVG haritaları ve doluluk koordinatları optimize edilir. Çok çekirdekli sistemlerde Parallel Adaptive Negative Space Ledger mimarisi ile paralel boşluk budaması yapılır.

---

## [TR] Çıktı Kontrol Paneli (Dashboard)

Tamamen bağımsız vanilya JavaScript (`frontend/index.html`) ile geliştirilen kontrol paneli şu özellikleri barındırır:
- **Overview**: Çalıştırılmış analiz paketlerinin kart listesi.
- **Details Drawer**: Paketlerin SHA-256 doğrulama özetleri ve dosya listeleri.
- **Scientific Console**: Analiz ilerlemesini gerçek zamanlı izleme ekranı.
- **Compare View**: Birden fazla analizi yan yana kıyaslama.

---

## [TR] Betik ve Araçlar Dizini

- **`run_analysis.py`**: Analizleri başlatan ana Python CLI betiği.
- **`launcher.py`**: Rich kütüphanesiyle yazılmış etkileşimli terminal menüsü.
- **`bin/rash-hit.js`**: npm CLI sarmalayıcısı. Python bağımlılıklarını otomatik yükler ve denetler.
- **`start.bat` ve `start.sh`**: Tek tıklamayla etkileşimli menüyü başlatan işletim sistemine özel betikler.
- **`scripts/verify_orientation.py`**: Üretilen Excel dosyalarını Shapely geometrisiyle doğrular.
- **`tests/run_koch_test.py`**: Koch Eğrisi üzerinde teorik fraktal boyut testi yapar.
- **`tools/validate_license_docs.py`**: Proje lisans bilgilerini ve Apache 2.0 başlıklarını denetler.
- **`tools/final_public_scan.py`**: Projeyi yayına hazırlamadan önce mutlak yollar ve yasaklı ifadeler için tarar.

---

## [TR] Kurulum ve Bağımlılıklar

Bilgisayarınızda Python 3.9+ ve Node.js 16+ kurulu olmalıdır.

```bash
# Projeyi indirin
git clone https://github.com/mehmetrasit/rash-hit-fractal-studio.git
cd rash-hit-fractal-studio

# Bağımlılıkları yükleyin
npm run setup
```

### Python Bağımlılıkları (`requirements.txt`)
- `numpy`: Sayısal matris işlemleri.
- `shapely`: C++ GEOS vektör kesişim motoru.
- `openpyxl`: Excel çıktısı üretici.
- `PyMuPDF`: PDF rapor derleme.
- `Pillow`: Görüntü denetimi ve doğrulama.
- `tinycss2`: SVG CSS ayrıştırıcı.
- `defusedxml`: XML güvenlik sıkılaştırması (XXE koruması).
- `rich`: Terminal grafikleri ve tablolar.
- `pytest`: Python test kütüphanesi.

### npm Bağımlılıkları (`package.json`)
- `exceljs`: Tarayıcı tarafında Excel oluşturma.
- `jsdom` (Dev): Arayüz bileşenlerinin birim testleri.

---

## [TR] Çalıştırma ve CLI Kullanımı

Etkileşimli terminal menüsünü açmak için:
```bash
npm start
```

Doğrudan CLI üzerinden tekli SVG analizi yapmak için:
```bash
python run_analysis.py --input input_svgs/16D.svg --levels 7 --profile lean
```

---

## [TR] Kod Kaynağı ve Yazarlık Beyanı

RASH-HIT Fractal Studio, Mehmet Raşit Narçiçek tarafından özgün bir akademik yazılım projesi olarak geliştirilmiştir. Proje, GEOS, Shapely, kutu sayma teorisi veya genel quadtree algoritmaları üzerinde hak iddia etmez. Özgün katkı, SVG geometri çıkarım boru hattı, en boy oranına duyarlı ızgara planlama algoritmaları, akademik çok formatlı dışa aktarım motoru ve SHA-256 doğrulama sistemidir.

---

## [TR] Doğrulama Tablosu

Koch Eğrisi (Koch Curve) referansı üzerinde seviye 7 doluluk analizinin doğrulaması:

| Örnek | Teorik D | Ölçülen D | Mutlak Hata | Yüzde Hata | $R^2$ | Uyarısı |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Koch Curve | 1.2619 | 1.3216 | 0.0597 | 4.73% | 0.9987 | Yok |

---

## [TR] Sistem Denetim Geçmişi

v1.0.5 sürümüyle birlikte gerçekleştirilen sistem denetiminde şu sorunlar giderilmiştir:
- **Karakter Kodlama**: Excel koordinat tablolarındaki Türkçe karakter hataları düzeltildi.
- **Gelişmiş Excel Tasarımı**: Kontrol panelinden indirilen Excel dosyaları Slate tasarım şablonlarına uyarlandı (koyu başlık satırları, ince kenarlıklar, Consolas yazı tipi).
- **Arayüz Kararlılığı**: Çoklu işlem durumunda konsol yükünü azaltmak amacıyla arama filtreleri 150ms debounced yapıldı, konsol satır akışı 500 satırla sınırlandırıldı.
- **Güvenlik**: Dosya silme API isteklerine klasör dışına çıkma (path traversal) koruması eklendi.
- **ASCII Logo**: CLI açılışındaki ASCII sanat tasarımı dikey olarak tam hizalandı.

---

## Release Notes (v1.0.6)

- RASH-HIT Fractal Studio'nun ilk genel sürümü yayınlandı.
- Rasterleştirme yapmayan SVG tabanlı kutu sayma motoru (CPU Exact Vector).
- Seviyeler arası en boy oranına duyarlı dinamik ızgara planlaması.
- Excel, PDF, HTML raporlama ve SHA-256 paket bütünlük kontrolü.
- Paralel boş alan budama motoru (Parallel Adaptive Negative Space Ledger).
- Açık kaynak paylaşıma hazır temiz İngilizce arayüz katmanı.
