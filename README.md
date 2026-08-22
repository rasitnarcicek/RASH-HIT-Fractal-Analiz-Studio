# RASH-HIT Fractal Studio CLI

[![Python Application CI](https://github.com/rasitnarcicek/RASH-HIT-Fractal-Studio/actions/workflows/python-app.yml/badge.svg)](https://github.com/rasitnarcicek/RASH-HIT-Fractal-Studio/actions)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)

**RASH-HIT Fractal Studio CLI** is a high-performance, lightweight command-line tool designed for **exact vector geometry box-counting** and **fractal dimension ($D_B$)** analysis directly from SVG vector motifs.

---

## ⚡ Key Features

- **Exact Vector Intersection:** Uses CPU-accelerated exact Shapely/GEOS vector geometry intersection tests (no rasterization or pixel loss).
- **Hierarchical Box-Counting:** Fast quadtree-based spatial decomposition for multi-scale grid hierarchies ($L_1 \dots L_N$).
- **Statistical Regression:** Calculates Box-Counting Fractal Dimension ($D_B$) and goodness-of-fit ($R^2$) using least-squares log-log regression.
- **Pure Terminal Interface:** Instant tabular results printed directly to your terminal with zero disk footprint.
- **Batch Processing:** Analyze single SVG motifs or entire folders with comparative summary tables.

---

## 📦 Installation

Ensure you have Python 3.9+ installed.

```bash
# Clone the repository
git clone https://github.com/rasitnarcicek/RASH-HIT-Fractal-Studio.git
cd RASH-HIT-Fractal-Studio

# Install lightweight dependencies
pip install -r requirements.txt
```

### Dependencies
- `numpy` (>=1.24.0)
- `shapely` (>=2.0.0)
- `defusedxml` (>=0.7.1)
- `tinycss2` (>=1.2.0)

---

## 🚀 Usage

### 1. Analyze a Single SVG File
```bash
python run_analysis.py --input input_svgs/16D.svg --levels 7
```

**Sample Terminal Output:**
```text
=================================================================
 RASH-HIT Fractal Studio CLI - v1.0.0
 Vector Geometry Box-Counting & Fractal Dimension Engine
=================================================================

[+] Processing: 16D.svg
-----------------------------------------------------------------
  * ViewBox       : 100.00 x 200.00 (Aspect: 0.50)
  * Geometries    : 2 vector elements (parsed in 0.68 ms)
  * Grid Levels   : L01 .. L07
  * Analysis Mode : Exact Vector Geometry (CPU Area)
-----------------------------------------------------------------
Level  Grid          Total Cells  Filled Cells  Empty Cells    Fill %   Time ms
-----------------------------------------------------------------------------
L01    4x8                    32            32            0   100.00%      0.20
L02    8x16                  128           128            0   100.00%      0.19
L03    16x32                 512           420           92    82.03%      0.54
L04    32x64               2,048         1,508          540    73.63%      1.43
L05    64x128              8,192         6,032        2,160    73.63%      5.48
L06    128x256            32,768        24,128        8,640    73.63%     23.45
L07    256x512           131,072        95,172       35,900    72.61%    103.61
-----------------------------------------------------------------------------
  >> Fractal Dimension (Db) : 1.9134
  >> Goodness of Fit (R^2)   : 0.9994
  >> Total Computation Time : 136.98 ms
=================================================================
```

### 2. Batch Processing a Directory
```bash
python run_analysis.py --dir input_svgs/ --levels 5
```

### 3. Command-Line Options
| Option | Short | Default | Description |
|---|---|---|---|
| `--input <path>` | `-i` | `None` | Path to a single input SVG file |
| `--dir <path>` | `-d` | `None` | Path to directory for batch processing |
| `--levels <int>` | `-l` | `7` | Number of grid scaling levels |
| `--quiet` | `-q` | `False` | Quiet mode (suppresses per-level steps) |
| `--version` | `-v` | - | Displays application version |

---

## 🧪 Running Tests

The test suite validates SVG parsing, geometric transformation matrices, hierarchical spatial subdivision, and regression fitting:

```bash
pytest
```

---

## 📄 Mathematical Background

The box-counting dimension $D_B$ is computed by dividing the 2D plane into a grid of boxes with side length $\epsilon$. The number of occupied boxes $N(\epsilon)$ is counted at various grid resolutions:

$$D_B = \lim_{\epsilon \to 0} \frac{\log N(\epsilon)}{\log(1/\epsilon)}$$

Linear least-squares regression is performed on $(\log(1/\epsilon), \log N(\epsilon))$ across grid levels $L_1 \dots L_N$, yielding the slope $D_B$ and coefficient of determination $R^2$.

---

## 📜 License

Licensed under the [Apache License, Version 2.0](LICENSE).
Copyright (c) 2026 Mehmet Raşit Narçiçek.
