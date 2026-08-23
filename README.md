# RASH-HIT Fractal Studio CLI

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-green.svg)](https://www.python.org/)
[![Concept DOI](https://img.shields.io/badge/Concept_DOI-10.5281%2Fzenodo.21693694-blue.svg)](https://doi.org/10.5281/zenodo.21693694)
[![Version DOI](https://img.shields.io/badge/Version_DOI-10.5281%2Fzenodo.22063154-blue.svg)](https://doi.org/10.5281/zenodo.22063154)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0005--3423--255X-green.svg)](https://orcid.org/0009-0005-3423-255X)

**RASH-HIT Fractal Studio CLI** is a research-grade, raster-free computational software engine designed for **exact vector geometry box-counting** and **fractal dimension ($D_B$)** analysis directly from Scalable Vector Graphics (SVG) vector motifs and architectural patterns.

Unlike conventional image-processing tools that convert vector artwork into PNG/JPEG pixel rasters—introducing resolution dependency, anti-aliasing distortion, edge blurring, and scaling artifacts—**RASH-HIT Fractal Studio** evaluates raw SVG vector geometry directly in continuous floating-point coordinate space using C++ GEOS spatial predicates via Shapely 2.0.

---

## 🏛️ Research Context & Application Domains

### 1. Architectural & Spatial Design
Architectural facades, floor plans, spatial layouts, and parametric structures frequently incorporate self-similar geometric patterns. RASH-HIT Fractal Studio enables architectural researchers to quantify visual complexity, scale-hierarchy depth, and fractal density without rasterization error.

### 2. Traditional Motifs, Visual Heritage & Pattern Research
Historical ornaments, traditional motifs (e.g., Islamic geometric patterns, Anatolian carpets, Celtic knotwork, fractal textiles), and archaeological visual heritage forms are natively drawn as vector curves. This engine counts filled and empty spatial cells with mathematical rigor, enabling precise comparative morphological studies across cultures and design eras.

### 3. Graphic Design & Fractal Aesthetics
Designers and aesthetic complexity researchers can evaluate visual balance, pattern density, and structural scale invariance across multiple zoom levels ($L_1 \dots L_N$).

### 4. Why Exact Vector Geometry Over Raster Box-Counting?
Standard raster-based box-counting tools convert vector artworks into fixed pixel grids, leading to three critical sources of mathematical error:
- **Pixel Grid Discretization:** Fine geometric details and sharp corners smaller than pixel size are merged or lost.
- **Anti-Aliasing Fringing:** Boundary pixels become semi-transparent gray values, causing arbitrary thresholding errors during binary occupancy decisions.
- **Scale & Resolution Dependency:** The measured fractal dimension shifts artificially depending on the arbitrary DPI / resolution chosen during raster export.

**RASH-HIT Fractal Studio solves this completely:** It computes exact point-set intersections between continuous polygon fills, buffered stroke lines, and grid cell bounding boxes using IEEE 754 double-precision floating-point arithmetic.

---

## ⚡ Key Architecture & Features

- **Exact Vector Intersection:** Uses C++ GEOS / Shapely 2.0 spatial predicates (`intersects`, `contains`, `STRtree`) for exact geometric contact testing.
- **Hierarchical Quadtree Pruning:** Fast spatial tree acceleration skips empty child cells automatically, enabling multi-level deep analysis ($L_1 \dots L_N$) in milliseconds.
- **Aspect-Ratio-Aware Grid Planning:** Base grid planning adapts to arbitrary canvas aspect ratios ($AR = W/H$) with strict power-of-two resolution doubling.
- **Comprehensive SVG Element Support:** Full support for `path` (Bézier curves, elliptical arcs), `rect`, `circle`, `ellipse`, `line`, `polyline`, `polygon`, and 2D affine transformation matrices (`matrix`, `translate`, `scale`, `rotate`, `skewX`, `skewY`).
- **Statistical Regression:** Ordinary Least Squares (OLS) log-log regression for Box-Counting Dimension ($D_B$) and goodness-of-fit ($R^2$).
- **Pure Terminal Interface:** Clean, monospaced ASCII table reports printed directly to terminal with zero disk footprint.
- **Batch Processing:** Single file and whole directory analysis modes with comparative summary matrices.

---

## 📦 Installation & Dependencies

Ensure you have Python 3.9+ installed (Python 3.11 / 3.12 recommended).

```bash
# Clone the repository
git clone https://github.com/rasitnarcicek/RASH-HIT-Fractal-Studio.git
cd RASH-HIT-Fractal-Studio

# Install lightweight dependencies
pip install -r requirements.txt
```

### Core Dependency Stack
- `numpy` ($\ge 1.24.0$): Vectorized grid coordinates and numerical regression fitting (BSD 3-Clause).
- `shapely` ($\ge 2.0.0$): Continuous vector geometry objects and C++ GEOS spatial index (BSD 3-Clause).
- `defusedxml` ($\ge 0.7.1$): Secure XML parsing protecting against XXE entity expansion attacks (PSFL).
- `tinycss2` ($\ge 1.2.0$): CSS style block and inline style parser (BSD 3-Clause).

---

## 🚀 CLI Usage & Examples

### 1. Analyze a Single SVG Motif
```bash
python run_analysis.py --input input_svgs/16D.svg --levels 7
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
|  L01  | 4x8      |          32 |           32 |           0 |     100.00% |     0.21 |
|  L02  | 8x16     |         128 |          128 |           0 |     100.00% |     0.17 |
|  L03  | 16x32    |         512 |          420 |          92 |      82.03% |     0.48 |
|  L04  | 32x64    |       2,048 |        1,508 |         540 |      73.63% |     1.39 |
|  L05  | 64x128   |       8,192 |        6,032 |       2,160 |      73.63% |     5.28 |
|  L06  | 128x256  |      32,768 |       24,128 |       8,640 |      73.63% |    23.12 |
|  L07  | 256x512  |     131,072 |       95,172 |      35,900 |      72.61% |    99.55 |
+-------+----------+-------------+--------------+-------------+-------------+----------+
  [RESULT] Box-Counting Fractal Dimension Db = 1.9134
  [RESULT] Linear Regression Fit R2           = 0.9994
  [RESULT] Total Execution Time               = 131.86 ms
+------------------------------------------------------------------------------+
```

### 2. Batch Processing a Directory of SVGs
```bash
python run_analysis.py --dir input_svgs/ --levels 5
```

### 3. Command-Line Options
| Option | Short | Default | Description |
|:---|:---|:---|:---|
| `--input <path>` | `-i` | `None` | Path to a single input SVG file. Mutually exclusive with `--dir`. |
| `--dir <path>` | `-d` | `None` | Path to directory for batch processing all SVGs. Mutually exclusive with `--input`. |
| `--levels <int>` | `-l` | `7` | Number of grid scaling levels to evaluate ($N \ge 1$). |
| `--version` | `-v` | - | Displays application version and exit. |

---

## 🧪 Unit Testing

The test suite validates SVG parsing, CSS style cascades, affine transformation matrices, spatial quadtree subdivisions, and linear regression:

```bash
pytest
```

---

## 📄 Mathematical Methodology

The box-counting dimension $D_B$ is computed by dividing the 2D SVG canvas into a series of spatial grids with cell scale $\varepsilon$. The relationship between scale $\varepsilon$ and occupied box count $N(\varepsilon)$ follows a power law:

$$N(\varepsilon) \propto \left(\frac{1}{\varepsilon}\right)^{D_B}$$

Taking the natural logarithm yields the linear regression model:

$$\log N(\varepsilon) = D_B \cdot \log\left(\frac{1}{\varepsilon}\right) + C$$

Where:
- $N(\varepsilon)$ = Number of filled (occupied) grid cells at scale $\varepsilon$.
- $\varepsilon = \frac{\max(W_{\text{cell}}, H_{\text{cell}})}{\max(W_{\text{canvas}}, H_{\text{canvas}})}$ = Normalized grid scale parameter.
- $D_B$ = Box-counting fractal dimension (Ordinary Least Squares regression slope).
- $R^2 = 1 - \frac{SS_{\text{res}}}{SS_{\text{tot}}}$ = Coefficient of determination (goodness of fit).

---

## 🎓 Academic Citation

If you use RASH-HIT Fractal Studio in your research, publications, or thesis, please cite the software using the DOIs below:

- **Concept DOI:** [10.5281/zenodo.21693694](https://doi.org/10.5281/zenodo.21693694)
- **Version DOI (v1.0.0):** [10.5281/zenodo.22063154](https://doi.org/10.5281/zenodo.22063154)
- **ORCID:** [0009-0005-3423-255X](https://orcid.org/0009-0005-3423-255X)

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
