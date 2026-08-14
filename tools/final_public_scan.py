# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
import os
import sys
from urllib.parse import urlparse


def _line_is_author_attribution(line: str) -> bool:
    """Return True if the line is an author-attribution line that should be skipped.

    Uses an explicit author-name check and a proper URL netloc check for ORCID
    links, rather than a bare substring search (``"https://orcid.org" in text``)
    which could be fooled by crafted URLs such as
    ``https://evil.com?ref=https://orcid.org``.
    """
    line_low = line.lower()

    # Skip lines that mention the project author name directly.
    if "mehmet raşit narçiçek" in line_low:
        return True

    # Skip lines that contain a URL whose netloc is exactly orcid.org or a
    # subdomain (e.g. pub.orcid.org).  We check every whitespace-separated
    # token so that the scheme+host must be structurally correct.
    for token in line_low.split():
        # Strip common surrounding punctuation from markdown / YAML values.
        token = token.strip("\"'()[]<>,")
        if not token.startswith("http"):
            continue
        try:
            netloc = urlparse(token).netloc  # e.g. "orcid.org" or "pub.orcid.org"
        except Exception:
            continue
        # Accept only if netloc IS orcid.org or ends with .orcid.org.
        if netloc == "orcid.org" or netloc.endswith(".orcid.org"):
            return True

    return False


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    banned_global = [
        "c:\\users\\", "raşitnarçiçek\\desktop",
        "gpu", "cuda", "hybrid", "gpu-area", "gpu-sparse", "zero error",
        "%100", "perfectly", "gold standard", "altın standart", "mükemmel", "kusursuz",
        "darboğaz sıfırlandı", "100 kat", "terminal_ansi", "main_card", "main_map"
    ]

    banned_doc_html = [
        "<" + "br" + ">", "</a>", "target=", "rel=", "fai-chatinput", "[http", "[https"
    ]

    ignore_dirs = [
        ".git", ".venv", "venv", "__pycache__", "outputs", "output_reports",
        ".gemini", ".antigravity", "scratch", "docs",
        "node_modules"
    ]
    ignore_files = [
        "PROJE_MIMARI_VE_KOD_HARITASI.md", "RASH_HIT_FRACTAL_STUDIO_MASTER_HARITA.md",
        "PROJE_TUM_MIMARI_VE_KOD_HARITASI.md", "final_public_scan.py"
    ]

    issues = 0
    for r, d, files in os.walk(root):
        rel_r = os.path.relpath(r, root).replace("\\", "/")
        d[:] = [dirname for dirname in d if not any(ig in (rel_r + "/" + dirname).strip("./") for ig in ignore_dirs)]
        if any(ig in rel_r for ig in ignore_dirs):
            continue
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in [".py", ".md", ".txt", ".json", ".yml", ".yaml", ".toml", ".ini", ".cfg", ".cff"] or f in ["LICENSE", "NOTICE", "requirements.txt", ".gitignore"]:
                if f in ignore_files:
                    continue
                fpath = os.path.join(r, f)
                rel_fpath = os.path.relpath(fpath, root)
                with open(fpath, encoding="utf-8", errors="ignore") as fo:
                    lines_f = fo.readlines()

                is_doc_file = ext in [".md", ".txt", ".cff"] or f in ["LICENSE", "NOTICE", "requirements.txt"]
                is_gitignore = (f == ".gitignore")

                for idx, line in enumerate(lines_f, start=1):
                    if _line_is_author_attribution(line):
                        continue
                    if is_gitignore:
                        continue

                    line_low = line.lower()

                    for b in banned_global:
                        if b in line_low:
                            print(f"[!] Forbidden term '{b}' in {rel_fpath}:{idx}: {line.strip()[:80]}")
                            issues += 1

                    if is_doc_file:
                        for b in banned_doc_html:
                            if b in line_low:
                                print(f"[!] Forbidden doc HTML/link term '{b}' in {rel_fpath}:{idx}: {line.strip()[:80]}")
                                issues += 1

    if issues > 0:
        print(f"[!] Final public scan failed with {issues} issues.")
        sys.exit(1)
    print("[OK] Final public scan passed clean.")


if __name__ == "__main__":
    main()
