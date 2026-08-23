# RASH-HIT Fractal Studio CLI

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-green.svg)](https://www.python.org/)
[![PyPI version](https://img.shields.io/pypi/v/rash-hit-fractal-studio.svg)](https://pypi.org/project/rash-hit-fractal-studio/)
[![npm version](https://img.shields.io/npm/v/rash-hit-fractal-studio.svg)](https://www.npmjs.com/package/rash-hit-fractal-studio)
[![Concept DOI](https://img.shields.io/badge/Concept_DOI-10.5281%2Fzenodo.21693694-blue.svg)](https://doi.org/10.5281/zenodo.21693694)
[![Version DOI](https://img.shields.io/badge/Version_DOI-10.5281%2Fzenodo.22063154-blue.svg)](https://doi.org/10.5281/zenodo.22063154)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0005--3423--255X-green.svg)](https://orcid.org/0009-0005-3423-255X)

**RASH-HIT Fractal Studio CLI** is a research-grade, zero-rasterization computational geometry engine engineered for **exact vector box-counting**, **spatial occupancy profiling (fill vs. empty void ratio)**, and **fractal dimension ($D_B$)** analysis directly from Scalable Vector Graphics (SVG) vector motifs, architectural drawings, textile patterns, and graphic compositions.

---

## 🔬 Scientific Foundation & The Exact Vector Paradigm

For over three decades, computational fractal analysis in design and morphology has relied on **raster image-processing tools** (e.g., ImageJ FracLac, HarFA, Benoit). These conventional tools force vector artwork to be rasterized into fixed-resolution pixel grids (PNG/JPEG/TIFF), introducing three severe classes of mathematical error:

1. **Resolution & DPI Inconsistency:** Measured fractal dimensions vary artificially depending on the arbitrary export resolution, canvas size, or DPI chosen.
2. **Anti-Aliasing & Fringing Distortion:** Vector curves produce semi-transparent grayscale boundary pixels during rasterization, forcing arbitrary binarization thresholds that corrupt fine geometric boundaries.
3. **Discretization Corner Clipping:** Fine ornamental strokes, sharp corner vertices, and sub-pixel details smaller than pixel dimensions are merged, blurred, or obliterated.

### The RASH-HIT Solution
**RASH-HIT Fractal Studio completely eliminates rasterization artifacts.** It operates natively on continuous vector path geometry in floating-point coordinate space using the **C++ GEOS spatial engine via Shapely 2.0**. Grid cell occupancy is evaluated via continuous point-set topological intersection predicates ($E \cap B_{i,j} \neq \emptyset$), guaranteeing **100% mathematical determinism, zero discretization error, and publication-grade reproducibility**.

---

## 🏛️ Comprehensive Application Domains

RASH-HIT Fractal Studio serves as a bridge between pure computational geometry and creative design disciplines:

### 1. 🧵 Textile, Fashion & Pattern Design
- **Jacquard & Woven Structure Porosity:** Quantify the exact spatial density and void-to-fill distribution of woven structures, knitwear repeats, and lace filigree.
- **Carpet & Kilim Motif Analysis:** Mathematically profile traditional Anatolian, Persian, Caucasian, and Oriental carpet motifs, quantifying the transition of motif density from central medallions to borders.
- **Fashion Print Scaling & Repeat Balance:** Evaluate self-similarity across different scale factors in surface pattern design and all-over textile prints.

### 2. 🏺 Cultural Heritage, Islamic Geometry & Visual Ornamentation
- **Historic Ornament Morphology:** Analyze ornamental styles across cultural eras (Seljuk, Ottoman, Celtic, Gothic, Baroque, Islamic Geometric Star Patterns, Muqarnas, Tezhip, Ebru, Marbling).
- **Cultural Motif Classification:** Provide objective numerical metrics ($D_B$, $R^2$, level-by-level fill ratios) for digital humanities, archaeological pattern classification, and museum heritage preservation.
- **Geometric Complexity Indexing:** Distinguish between Euclidean symmetry and true fractal self-similarity in traditional craftsmanship.

### 3. 🎨 Graphic Design, Typography & Visual Branding
- **Logo Visual Weight & Balance:** Quantify positive vs. negative space distribution and visual occupancy ratios across branding assets.
- **Typographic Complexity:** Measure the structural complexity, stroke density, and spatial coverage of diverse typefaces and calligraphic scripts.
- **Generative & Algorithmic Vector Art:** Benchmark procedural vector patterns, cellular automata graphics, and L-system fractals.

### 4. 🏢 Architectural & Urban Morphology
- **Facade Articulation & Porosity:** Analyze architectural screens (e.g., Mashrabiya, Brise-soleil, perforated metal panels) for light filtration and structural complexity.
- **Floor Plan Spatial Hierarchy:** Quantify structural enclosure, wall-to-void density, and circulation complexity in architectural layouts.
- **Urban Footprint Scaling:** Evaluate the fractal scaling behavior of street networks, historical urban perimeters, and building layouts.

### 5. ⚙️ Industrial, Surface & Parametric Product Design
- **Laser-Cutting & CNC Path Optimization:** Assess vector distribution and material removal ratios prior to fabrication.
- **Biomimetic Textures & Metamaterials:** Measure geometric scale hierarchies in biologically-inspired lattice structures and textured functional surfaces.

---

## 📊 Analytical Comparison: Exact Vector vs. Raster Box-Counting

| Metric / Capability | Conventional Raster Tools (ImageJ/FracLac) | RASH-HIT Fractal Studio (Exact Vector) |
|:---|:---|:---|
| **Input Representation** | Discrete Bitmap Pixels (PNG/JPG/TIFF) | Continuous Double-Precision Floating Point (SVG) |
| **Geometry Evaluation** | Pixel counting (Binary 0/1 threshold) | C++ GEOS Topological Predicates (`intersects`) |
| **DPI / Resolution Dependency** | ⚠️ High (Results shift with image size/DPI) | 🟢 **Zero** (Scale-invariant exact geometry) |
| **Anti-Aliasing Artifacts** | ⚠️ Severe (Blurred edges distort boundary counts) | 🟢 **None** (Evaluated as true continuous boundaries) |
| **Stroke Width Accuracy** | ⚠️ Subject to pixel round-off error | 🟢 **Exact** (Converts strokes to precise buffer polygons) |
| **Aspect Ratio Handling** | Often square-padded, distorting non-square ratios | 🟢 **Adaptive** (Aspect-ratio-aware grid planning) |
| **Execution Performance** | Slower on large images (O(N*M) pixel scan) | 🟢 **Ultra-fast** (Hierarchical quadtree pruning) |
| **Reproducibility** | Depends on export settings and binarizer threshold | 🟢 **100% Deterministic & Scientifically Exact** |

---

## ⚡ Core Architecture & Engineering

- **Exact Vector Intersection Engine:** Powered by C++ GEOS / Shapely 2.0 with spatial indexing (`STRtree`) and strict point-set topological testing.
- **Aspect-Ratio-Aware Multi-Level Grid Planning:** Automatically adapts grid cell dimensions to arbitrary SVG viewbox dimensions ($AR = W/H$) with power-of-two resolution doubling across levels ($L_1 \dots L_N$).
- **Hierarchical Quadtree Pruning:** Automatically skips empty child cells based on parent occupancy, delivering sub-millisecond execution speeds even at deep resolution levels.
- **Comprehensive SVG Specification Support:**
  - Standard shapes: `<rect>`, `<circle>`, `<ellipse>`, `<line>`, `<polyline>`, `<polygon>`, and `<path>` (Cubic/Quadratic Bézier curves, elliptical arcs).
  - 2D affine transformation matrices: `matrix()`, `translate()`, `scale()`, `rotate()`, `skewX()`, `skewY()`.
  - CSS style hierarchy: Inline `style="..."`, presentation attributes, and `<style>` blocks (via `tinycss2`).
  - Per-channel alpha and visibility resolution: Filters non-rendered, hidden, or zero-opacity geometries.
- **Ordinary Least Squares (OLS) Regression:** Evaluates Box-Counting Fractal Dimension ($D_B$) and coefficient of determination ($R^2$) from:
  $$\log N(\epsilon) = D_B \cdot \log(1/\epsilon) + C$$
- **Zero Disk Footprint:** Generates clean, publication-ready ASCII framed summary tables directly to `stdout`.

---

## 📦 Installation & Setup

### Method 1: Instant Execution via NPX (Zero Setup)
```bash
# Run immediately without manual dependency installation
npx rash-hit-fractal-studio --input motif.svg --levels 7

# Or install globally
npm install -g rash-hit-fractal-studio
rash-hit-fractal --input motif.svg --levels 7
```
*(All required Python core libraries such as NumPy and Shapely are automatically detected and installed on first run).*

### Method 2: Install via PyPI
```bash
pip install rash-hit-fractal-studio
```

### Method 3: Install from Source
```bash
git clone https://github.com/rasitnarcicek/RASH-HIT-Fractal-Studio.git
cd RASH-HIT-Fractal-Studio
pip install -e .
```

---

## 🚀 CLI Usage & Examples

When installed via `pip` or `npm`, the `rash-hit-fractal` command is available system-wide:

### 1. Analyze a Single SVG Motif
```bash
rash-hit-fractal --input input_svgs/16D.svg --levels 7
```

**Terminal Output:**
```text
+------------------------------------------------------------------------------+
|               RASH-HIT FRACTAL STUDIO - ANALYSIS REPORT                      |
+------------------------------------------------------------------------------+
  Motif Loaded       : 16D (100.00 x 200.00)
  Geometries         : 2 vector elements
  Analysis Engine    : cpu
  Selected Engine    : CPU Exact Vector Geometry Engine (Shapely/GEOS)
+------------------------------------------------------------------------------+
| Level | Grid     | Total Cells | Filled Cells | Empty Cells | Occupancy % | Time ms  |
+-------+----------+-------------+--------------+-------------+-------------+----------+
|  L01  | 4x8      |          32 |           32 |           0 |     100.00% |     0.32 |
|  L02  | 8x16     |         128 |          128 |           0 |     100.00% |     0.24 |
|  L03  | 16x32    |         512 |          420 |          92 |      82.03% |     0.40 |
|  L04  | 32x64    |       2,048 |        1,508 |         540 |      73.63% |     1.65 |
|  L05  | 64x128   |       8,192 |        6,032 |       2,160 |      73.63% |     7.09 |
|  L06  | 128x256  |      32,768 |       23,744 |       9,024 |      72.46% |    25.14 |
|  L07  | 256x512  |     131,072 |       93,888 |      37,184 |      71.63% |    94.80 |
+-------+----------+-------------+--------------+-------------+-------------+----------+
  [RESULT] Box-Counting Fractal Dimension Db = 1.8675
  [RESULT] Linear Regression Fit R2           = 0.9993
  [RESULT] Total Execution Time               = 129.64 ms
+------------------------------------------------------------------------------+
```

### 2. Batch Process an Entire Directory of Motifs
```bash
rash-hit-fractal --dir ./input_svgs --levels 5
```

---

## 🎓 Academic Citation

If you use **RASH-HIT Fractal Studio** in your research, thesis, journal articles, or architectural/textile studies, please cite the software using the persistent DOIs below:

- **Concept DOI:** [10.5281/zenodo.21693694](https://doi.org/10.5281/zenodo.21693694)
- **Version DOI (v1.0.0):** [10.5281/zenodo.22063154](https://doi.org/10.5281/zenodo.22063154)
- **Author ORCID:** [0009-0005-3423-255X](https://orcid.org/0009-0005-3423-255X)

### BibTeX
```bibtex
@software{Narcicek_RASH_HIT_Fractal_Studio_CLI_2026,
  author    = {Nar{\c{c}}i{\c{c}}ek, Mehmet Ra{\s}it},
  title     = {RASH-HIT Fractal Studio CLI: Exact Vector Geometry Box-Counting and Fractal Dimension Engine},
  year      = {2026},
  version   = {1.0.0},
  publisher = {GitHub},
  doi       = {10.5281/zenodo.22063154},
  url       = {https://doi.org/10.5281/zenodo.22063154},
  orcid     = {https://orcid.org/0009-0005-3423-255X},
  license   = {Apache-2.0}
}
```

### APA
> Narçiçek, M. R. (2026). *RASH-HIT Fractal Studio CLI: Exact Vector Geometry Box-Counting and Fractal Dimension Engine* (Version 1.0.0) [Computer software]. GitHub. https://doi.org/10.5281/zenodo.22063154

### RIS
```ris
TY  - COMP
AU  - Narçiçek, Mehmet Raşit
TI  - RASH-HIT Fractal Studio CLI: Exact Vector Geometry Box-Counting and Fractal Dimension Engine
PY  - 2026
ET  - 1.0.0
PB  - GitHub
DO  - 10.5281/zenodo.22063154
UR  - https://doi.org/10.5281/zenodo.22063154
ER  - 
```

---

## 📜 License & Authorship

Licensed under the [Apache License, Version 2.0](LICENSE).  
Copyright (c) 2026 Mehmet Raşit Narçiçek. All rights reserved.
