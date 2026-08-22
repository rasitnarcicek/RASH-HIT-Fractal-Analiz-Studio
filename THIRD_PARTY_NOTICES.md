# Third-Party Notices & Dependencies

RASH-HIT Fractal Studio CLI relies on third-party open-source computational software libraries. This document lists all dependencies, their licenses, and usage context.

---

## 1. Computational Geometry & Vector Processing

### Shapely / GEOS
- **Project**: Shapely
- **License**: BSD 3-Clause License
- **Upstream Engine**: GEOS (Geometry Engine - Open Source) - LGPL 2.1
- **Notice**: Shapely/GEOS are used for exact vector intersection predicates.

### NumPy
- **Project**: NumPy
- **License**: BSD 3-Clause License
- **Usage**: Used for array operations, matrix grid indexing, and least-squares regression fitting.

---

## 2. SVG Parsing & Security

### tinycss2
- **Project**: tinycss2
- **License**: BSD 3-Clause License
- **Usage**: Used for parsing SVG inline and block CSS style declarations.

### defusedxml
- **Project**: defusedxml
- **License**: Python Software Foundation License (PSFL)
- **Usage**: Used for secure XML parsing hardened against XML entity expansion (XXE) vulnerabilities.
