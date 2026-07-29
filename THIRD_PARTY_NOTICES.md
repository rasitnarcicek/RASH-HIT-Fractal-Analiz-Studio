# Third-Party Notices & Dependencies

RASH-HIT Fractal Studio relies on third-party open-source computational software libraries to provide core functionality. This document lists all third-party dependencies, their licenses, and usage context.

---

## 1. Computational Geometry & Vector Processing

### Shapely / GEOS
- **Project**: Shapely
- **License**: BSD 3-Clause License
- **Upstream Engine**: GEOS (Geometry Engine - Open Source) - LGPL 2.1
- **Notice**: Shapely/GEOS are used as third-party computational geometry dependencies for exact vector intersection predicates.

### NumPy
- **Project**: NumPy
- **License**: BSD 3-Clause License
- **Usage**: Used for high-performance array operations, matrix grid indexing, and quadtree spatial decomposition.

---

## 2. Academic Output Generation & Reporting

### openpyxl
- **Project**: openpyxl
- **License**: MIT License
- **Usage**: Used to produce publication-ready Excel workbooks (`workbook.xlsx`) and per-level cell datasets (`tables/*.xlsx`).

### PyMuPDF (fitz)
- **Project**: PyMuPDF
- **License**: GNU AGPL v3.0 / Commercial
- **Notice**: PDF export uses PyMuPDF. Review PyMuPDF licensing requirements for redistribution.

### PyYAML
- **Project**: PyYAML
- **License**: MIT License
- **Usage**: Used for metadata and configuration serialization.

### Pillow (PIL)
- **Project**: Pillow
- **License**: HPND License
- **Usage**: Optional dependency for image validation and rendering pipeline.

### tinycss2
- **Project**: tinycss2
- **License**: BSD 3-Clause License
- **Usage**: Used for parsing SVG inline CSS style declarations.

---

## 3. Testing & Quality Assurance

### pytest
- **Project**: pytest
- **License**: MIT License
- **Usage**: Test runner framework for unit and integration testing.
