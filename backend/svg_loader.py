# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek

"""
svg_loader.py — SVG Loader & CSS Style Resolver module.
Parses SVG XML structure, resolves CSS style blocks (tag, class, and ID selectors using tinycss2 with regex fallback),
inline styles, presentation attributes, and <use> instances according to SVG priority rules. Filters out hidden/invisible elements.
Detects advanced features (clipPath, mask, fill-rule) and records warnings for report outputs.
"""

from __future__ import annotations
import re
# Use defusedxml for safe XML parsing; fall back to stdlib with a warning.
try:
    import defusedxml.ElementTree as ET  # type: ignore[import]
except ImportError:  # pragma: no cover
    import warnings as _warnings
    _warnings.warn(
        "defusedxml not installed. Falling back to stdlib xml.etree.ElementTree. "
        "Install defusedxml>=0.7.1 for XML attack protection.",
        ImportWarning, stacklevel=2,
    )
    import xml.etree.ElementTree as ET  # type: ignore[assignment]
from typing import Dict, List, Tuple, Optional, Set, Any

try:
    import tinycss2
    HAS_TINYCSS2 = True
except ImportError:
    HAS_TINYCSS2 = False


def safe_float(val: Any, default: float = 0.0) -> float:
    """Safely converts an arbitrary value to float with fallback on failure."""
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def parse_css_style_block(style_content: str) -> Dict[str, Dict[str, Dict[str, str]]]:
    """
    Parses CSS <style> block content and extracts rules grouped by selector type:
    - 'classes': .class-name
    - 'tags': tag-name (e.g. path, rect, circle)
    - 'ids': #id-name

    Uses tinycss2 if available, otherwise falls back to regex parser.
    """
    rules: Dict[str, Dict[str, Dict[str, str]]] = {
        'classes': {},
        'tags': {},
        'ids': {}
    }
    if not style_content:
        return rules

    def add_selector_rule(sel_str: str, declarations: Dict[str, str]):
        sel_clean = sel_str.strip()
        if not sel_clean:
            return
        if sel_clean.startswith('.'):
            cls_name = sel_clean[1:].strip()
            if cls_name:
                rules['classes'].setdefault(cls_name, {}).update(declarations)
        elif sel_clean.startswith('#'):
            id_name = sel_clean[1:].strip()
            if id_name:
                rules['ids'].setdefault(id_name, {}).update(declarations)
        else:
            tag_name = sel_clean.lower().strip()
            if tag_name:
                rules['tags'].setdefault(tag_name, {}).update(declarations)

    if HAS_TINYCSS2:
        try:
            rulesets = tinycss2.parse_stylesheet(style_content, skip_comments=True, skip_whitespace=True)
            for rule in rulesets:
                if rule.type == 'qualified-rule':
                    selector_str = "".join([token.serialize() for token in rule.prelude]).strip()
                    declarations = tinycss2.parse_declaration_list(rule.content, skip_comments=True, skip_whitespace=True)
                    props: Dict[str, str] = {}
                    for decl in declarations:
                        if decl.type == 'declaration':
                            prop_name = decl.name.lower().strip()
                            prop_val = "".join([token.serialize() for token in decl.value]).strip().lower()
                            props[prop_name] = prop_val

                    for sel in selector_str.split(','):
                        add_selector_rule(sel, props)
            if rules['classes'] or rules['tags'] or rules['ids']:
                return rules
        except Exception as e:
            import warnings as _warnings
            _warnings.warn(
                f"tinycss2 failed to parse CSS <style> block ({e!r}); falling back to regex CSS parser.",
                RuntimeWarning, stacklevel=2,
            )

    # Fallback Regex CSS Parser
    clean_css = re.sub(r'/\*.*?\*/', '', style_content, flags=re.DOTALL)
    blocks = re.findall(r'([^{]+)\{([^}]+)\}', clean_css)

    for selectors, props_raw in blocks:
        props: Dict[str, str] = {}
        for line in props_raw.split(';'):
            if ':' in line:
                key, val = line.split(':', 1)
                props[key.strip().lower()] = val.strip().lower()

        for sel in selectors.split(','):
            add_selector_rule(sel, props)

    return rules


def parse_style_attribute(style_str: str) -> Dict[str, str]:
    """Parses inline style="..." attribute string into a dictionary."""
    props: Dict[str, str] = {}
    if not style_str:
        return props
    for item in style_str.split(';'):
        if ':' in item:
            k, v = item.split(':', 1)
            props[k.strip().lower()] = v.strip().lower()
    return props


def parse_length(val_str: Any, default: float = 0.0) -> float:
    """
    Parses standard SVG length values with full unit conversion to float pixels:
    - px: 1:1 pixel
    - pt: 1.333333 px (96 / 72)
    - pc: 16.0 px (1 pica = 12 pt)
    - in: 96.0 px (1 inch = 96 px)
    - mm: 3.779527559 px (96 / 25.4)
    - cm: 37.79527559 px (96 / 2.54)
    - em / rem: 16.0 px standard baseline
    """
    if val_str is None:
        return default
    s = str(val_str).strip().lower()
    if not s:
        return default

    # Standard conversion factors to CSS / SVG pixels (96 DPI baseline)
    unit_map = {
        'px': 1.0,
        'pt': 96.0 / 72.0,           # ~1.333333
        'pc': 16.0,                  # 12 pt = 16 px
        'in': 96.0,                  # 1 in = 96 px
        'mm': 96.0 / 25.4,           # ~3.779528 px
        'cm': 960.0 / 25.4,          # ~37.795276 px
        'em': 16.0,
        'rem': 16.0,
    }

    for unit, factor in unit_map.items():
        if s.endswith(unit):
            num_part = s[:-len(unit)].strip()
            try:
                return float(num_part) * factor
            except ValueError:
                return default

    if s.endswith('%'):
        num_part = s[:-1].strip()
        try:
            return float(num_part)
        except ValueError:
            return default

    try:
        return float(s)
    except ValueError:
        return default


class SVGNode:
    """Represents a resolved SVG element with effective styles and geometry attributes."""
    def __init__(self, tag: str, attribs: Dict[str, str], styles: Dict[str, str], transform_str: str):
        self.tag = tag.split('}')[-1]  # Strip XML namespace if present
        self.attribs = attribs
        self.styles = styles
        self.transform_str = transform_str

        # Resolved properties
        self.fill = styles.get('fill', 'black')
        self.stroke = styles.get('stroke', 'none')
        self.stroke_width = parse_length(styles.get('stroke-width', '1'), default=1.0)
        self.opacity = safe_float(styles.get('opacity', '1.0'), default=1.0)
        self.display = styles.get('display', 'inline')
        self.visibility = styles.get('visibility', 'visible')

        # Per-channel alpha: effective alpha = opacity * channel_opacity (SVG spec)
        _fill_opacity = safe_float(styles.get('fill-opacity', '1.0'), default=1.0)
        _stroke_opacity = safe_float(styles.get('stroke-opacity', '1.0'), default=1.0)
        self.effective_fill_alpha = max(0.0, min(1.0, self.opacity * _fill_opacity))
        self.effective_stroke_alpha = max(0.0, min(1.0, self.opacity * _stroke_opacity))

        # Flags: use per-channel alpha so fill-opacity:0 correctly marks fill invisible.
        self.has_fill = (
            self.fill not in ('none', 'transparent', '')
            and self.effective_fill_alpha > 0
        )
        self.has_stroke = (
            self.stroke not in ('none', 'transparent', '')
            and self.stroke_width > 0
            and self.effective_stroke_alpha > 0
        )
        self.is_visible = (
            self.display != 'none'
            and self.visibility != 'hidden'
            and (self.has_fill or self.has_stroke)
        )


class SVGLoader:
    """Loads and parses SVG files into structured nodes with fully resolved styles and warning detection."""
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.tree = ET.parse(filepath)
        self.root = self.tree.getroot()
        self.css_classes: Dict[str, Dict[str, str]] = {}
        self.css_tags: Dict[str, Dict[str, str]] = {}
        self.css_ids: Dict[str, Dict[str, str]] = {}
        self.id_map: Dict[str, ET.Element] = {}
        self.viewbox: Optional[Tuple[float, float, float, float]] = None
        self.width: float = 0.0
        self.height: float = 0.0
        self.warnings: List[str] = []

        self._index_element_ids(self.root)
        self._parse_metadata()
        self._collect_css_styles()

    def _index_element_ids(self, elem: ET.Element):
        """Indexes all elements with an 'id' attribute for <use> element referencing."""
        elem_id = elem.attrib.get('id')
        if elem_id:
            self.id_map[elem_id] = elem
        for child in elem:
            self._index_element_ids(child)

    def _parse_metadata(self):
        """Extracts viewBox, width, and height from root <svg> tag."""
        root_attribs = self.root.attrib
        attr_map = {k.lower(): v for k, v in root_attribs.items()}

        # viewBox: "minX minY width height"
        if 'viewbox' in attr_map:
            parts = [safe_float(p, 0.0) for p in re.split(r'[\s,]+', attr_map['viewbox'].strip()) if p]
            if len(parts) == 4 and parts[2] > 0 and parts[3] > 0:
                self.viewbox = (parts[0], parts[1], parts[2], parts[3])

        w_str = attr_map.get('width', '')
        h_str = attr_map.get('height', '')
        self.width = parse_length(w_str, default=0.0)
        self.height = parse_length(h_str, default=0.0)

        if not self.viewbox and self.width > 0 and self.height > 0:
            self.viewbox = (0.0, 0.0, self.width, self.height)
            self.warnings.append(f"viewBox attribute missing. Defaulted to (0, 0, {self.width}, {self.height}) from width/height.")
        elif self.viewbox and (self.width == 0 or self.height == 0):
            self.width = self.viewbox[2]
            self.height = self.viewbox[3]
        elif not self.viewbox:
            self.viewbox = (0.0, 0.0, 100.0, 100.0)
            self.width = 100.0
            self.height = 100.0
            self.warnings.append("viewBox and width/height missing. Defaulted to (0, 0, 100, 100).")

    def _collect_css_styles(self):
        """Extracts all <style> tag contents from SVG and populates class, tag, and ID rule dictionaries."""
        for elem in self.root.iter():
            tag = elem.tag.split('}')[-1]
            if tag == 'style' and elem.text:
                parsed = parse_css_style_block(elem.text)
                for cls_name, props in parsed.get('classes', {}).items():
                    self.css_classes.setdefault(cls_name, {}).update(props)
                for tag_name, props in parsed.get('tags', {}).items():
                    self.css_tags.setdefault(tag_name, {}).update(props)
                for id_name, props in parsed.get('ids', {}).items():
                    self.css_ids.setdefault(id_name, {}).update(props)

    def get_elements(self) -> List[Tuple[SVGNode, List[str]]]:
        """
        Traverses SVG tree and returns a list of (SVGNode, transform_stack).
        Applies SVG standard style priority:
        1. Inherited parent styles
        2. CSS Tag rules (path { ... })
        3. CSS Class rules (.st0 { ... })
        4. CSS ID rules (#my-id { ... })
        5. Presentation attributes (fill="...", stroke="...")
        6. Inline styles (style="fill: ...")
        """
        elements: List[Tuple[SVGNode, List[str]]] = []
        self._traverse_node(self.root, parent_styles={}, transform_stack=[], results=elements, visited_use_ids=set())
        return elements

    def _traverse_node(
        self,
        elem: ET.Element,
        parent_styles: Dict[str, str],
        transform_stack: List[str],
        results: List[Tuple[SVGNode, List[str]]],
        visited_use_ids: Set[str]
    ):
        raw_tag = elem.tag
        tag = raw_tag.split('}')[-1]

        # Feature detection warnings
        if tag == 'clipPath':
            self.warnings.append("clipPath element detected. Clipping geometry bounds are ignored in core v1.0.")
            return
        if tag == 'mask' or 'mask' in elem.attrib:
            self.warnings.append("mask attribute/element detected. Alpha masking is ignored in core v1.0.")
            return
        if elem.attrib.get('fill-rule') == 'evenodd':
            self.warnings.append("fill-rule='evenodd' detected.")

        if tag in ('defs', 'symbol'):
            return  # Skip definitions and non-rendered templates directly

        # Resolve CSS hierarchy
        effective_styles = parent_styles.copy()

        # 1. Tag-level CSS rules (e.g. path { fill: black; })
        if tag in self.css_tags:
            effective_styles.update(self.css_tags[tag])

        # 2. Class-level CSS rules (e.g. .cls-1 { fill: red; })
        class_attr = elem.attrib.get('class', '')
        if class_attr:
            for cls_name in class_attr.split():
                if cls_name in self.css_classes:
                    effective_styles.update(self.css_classes[cls_name])

        # 3. ID-level CSS rules (e.g. #star1 { fill: blue; })
        elem_id = elem.attrib.get('id', '')
        if elem_id and elem_id in self.css_ids:
            effective_styles.update(self.css_ids[elem_id])

        # 4. Presentation Attributes
        for attr_key, attr_val in elem.attrib.items():
            k_clean = attr_key.lower().strip()
            if k_clean in ('fill', 'stroke', 'stroke-width', 'opacity', 'display', 'visibility', 'fill-opacity', 'stroke-opacity'):
                effective_styles[k_clean] = attr_val.strip().lower()

        # 5. Inline style attribute (highest priority)
        inline_style_str = elem.attrib.get('style', '')
        if inline_style_str:
            effective_styles.update(parse_style_attribute(inline_style_str))

        # Transform stack
        current_transform_stack = list(transform_stack)
        node_transform = elem.attrib.get('transform', '')
        if node_transform:
            current_transform_stack.append(node_transform)

        # Handle <use> element instantiation
        if tag == 'use':
            # Resolve target href (#id or xlink:href)
            href = elem.attrib.get('href') or elem.attrib.get('{http://www.w3.org/1999/xlink}href') or elem.attrib.get('xlink:href', '')
            if href.startswith('#'):
                target_id = href[1:].strip()
                if target_id in self.id_map and target_id not in visited_use_ids:
                    target_elem = self.id_map[target_id]
                    use_transforms = list(current_transform_stack)
                    # Apply x, y translation if specified on <use>
                    use_x = parse_length(elem.attrib.get('x', '0'), 0.0)
                    use_y = parse_length(elem.attrib.get('y', '0'), 0.0)
                    if use_x != 0.0 or use_y != 0.0:
                        use_transforms.append(f"translate({use_x}, {use_y})")

                    new_visited = visited_use_ids.copy()
                    new_visited.add(target_id)
                    self._traverse_node(target_elem, effective_styles, use_transforms, results, new_visited)
            return

        # Check if renderable shape element
        render_tags = {'path', 'rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon'}
        if tag in render_tags:
            node = SVGNode(tag, elem.attrib, effective_styles, node_transform)
            if node.is_visible:
                results.append((node, current_transform_stack))

        # Recurse into child elements (e.g. <g> containers)
        for child in elem:
            self._traverse_node(child, effective_styles, current_transform_stack, results, visited_use_ids)
