# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek

from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class OutputProfile:
    name: str
    generate_workbook: bool = True
    generate_xlsx_tables: bool = True
    generate_tables_html: bool = True
    generate_map_svgs: bool = True
    generate_map_svgs_legacy: bool = False
    generate_html_report: bool = True
    generate_pdf_report: bool = True
    generate_markdown_report: bool = True
    generate_manifest: bool = True
    generate_audit_report: bool = True
    generate_terminal_log: bool = True
    generate_ascii: bool = False
    generate_ascii_book: bool = False
    generate_masks: bool = False
    generate_rle: bool = False
    generate_raw_csv: bool = False
    generate_levels_csv: bool = False
    generate_levels_json: bool = False
    generate_summary_json: bool = False
    generate_terminal_txt: bool = False

PROFILES: Dict[str, OutputProfile] = {
    "lean": OutputProfile(
        name="lean", generate_workbook=True, generate_xlsx_tables=True, generate_tables_html=True,
        generate_map_svgs=True, generate_map_svgs_legacy=False, generate_html_report=True, generate_pdf_report=True,
        generate_markdown_report=True, generate_manifest=True, generate_audit_report=True, generate_terminal_log=True,
        generate_ascii=False, generate_ascii_book=False, generate_masks=False, generate_rle=False,
        generate_raw_csv=False, generate_levels_csv=False, generate_levels_json=False, generate_summary_json=False,
    ),
    "reproducible": OutputProfile(
        name="reproducible", generate_workbook=True, generate_xlsx_tables=True, generate_tables_html=True,
        generate_map_svgs=True, generate_map_svgs_legacy=False, generate_html_report=True, generate_pdf_report=True,
        generate_markdown_report=True, generate_manifest=True, generate_audit_report=True, generate_terminal_log=True,
        generate_ascii=False, generate_ascii_book=False, generate_masks=True, generate_rle=True,
        generate_raw_csv=False, generate_levels_csv=True, generate_levels_json=True, generate_summary_json=True,
    ),
    "debug": OutputProfile(
        name="debug", generate_workbook=True, generate_xlsx_tables=True, generate_tables_html=True,
        generate_map_svgs=True, generate_map_svgs_legacy=True, generate_html_report=True, generate_pdf_report=True,
        generate_markdown_report=True, generate_manifest=True, generate_audit_report=True, generate_terminal_log=True,
        generate_ascii=True, generate_ascii_book=True, generate_masks=True, generate_rle=True,
        generate_raw_csv=True, generate_levels_csv=True, generate_levels_json=True, generate_summary_json=True,
    ),
    "presentation": OutputProfile(
        name="presentation", generate_workbook=True, generate_xlsx_tables=True, generate_tables_html=True,
        generate_map_svgs=True, generate_map_svgs_legacy=True, generate_html_report=True, generate_pdf_report=True,
        generate_markdown_report=True, generate_manifest=True, generate_audit_report=True, generate_terminal_log=True,
        generate_ascii=False, generate_ascii_book=False, generate_masks=False, generate_rle=False,
        generate_raw_csv=False, generate_levels_csv=False, generate_levels_json=False, generate_summary_json=False,
    ),
}

def load_output_profile(name: Optional[str] = None) -> OutputProfile:
    if not name:
        return PROFILES["lean"]
    key = name.lower().strip()
    if key not in PROFILES:
        valid_keys = ", ".join(PROFILES.keys())
        raise ValueError(f"Unknown output profile '{name}'. Valid profiles: {valid_keys}")
    return PROFILES[key]