# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
import os
import sys

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
        ".gemini", ".antigravity", "scratch", "docs/internal/experiments", "docs/internal/gpu_experiments"
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
                    if "mehmet raşit narçiçek" in line.lower() or "https://orcid.org" in line.lower():
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
