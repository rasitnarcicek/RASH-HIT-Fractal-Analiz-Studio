# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
"""
run_analysis.py - Direct CLI Execution Command for RASH-HIT Fractal Studio.
Delegates directly to backend.processor.AnalysisProcessor to guarantee 100% engine parity.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.processor import AnalysisProcessor, StepProgress
from backend.batch_processor import run_batch_analysis


def main():
    parser = argparse.ArgumentParser(
        description="RASH-HIT Fractal Studio - Direct CLI Analysis Command\nExample: python run_analysis.py --input input_svgs/16A.svg --levels 7 --output outputs/"
    )
    parser.add_argument("--input", "-i", help="Path to input SVG file (for single analysis)")
    parser.add_argument("--output", "-o", default="outputs", help="Output root directory (default: outputs)")
    # Allow --batch to be a boolean flag OR take an optional folder path string
    parser.add_argument("--batch", "-b", nargs="?", const=True, help="Process an entire folder of SVG files. Can specify folder path directly (e.g. --batch input_svgs/) or combine with --input")
    parser.add_argument("--levels", "-l", type=int, default=7, help="Number of grid levels (>= 1, default: 7)")
    parser.add_argument("--measure", choices=["area"], default="area", help="Measurement mode")
    parser.add_argument("--profile", choices=["lean", "reproducible", "debug", "presentation", "batch"], default="lean", help="Output profile")
    parser.add_argument("--batch-profile", choices=["lean", "reproducible", "debug", "presentation", "batch"], default="batch", help="Batch run profile")
    parser.add_argument("--overwrite", action="store_true", help="Explicitly overwrite an existing package with the same motif (default: create a new versioned package folder)")
    parser.add_argument("--engine", "-e", choices=["cpu"], default="cpu", help="Computation engine")
    # --mode kept only for backwards compatibility; hidden from help and never surfaced in UI.
    parser.add_argument("--mode", "-m", choices=["fast", "balanced", "precise", "academic", "batch"], default="balanced", help=argparse.SUPPRESS)

    args = parser.parse_args()

    # Determine input path from either --batch argument or --input argument
    input_str = None
    is_batch = False

    if isinstance(args.batch, str):
        input_str = args.batch
        is_batch = True
    elif args.batch is True:
        is_batch = True
        input_str = args.input
    else:
        input_str = args.input

    if not input_str:
        print("[ERROR] Please specify at least one of --input <file> or --batch <folder>.")
        parser.print_help()
        sys.exit(1)

    if args.levels is not None and args.levels <= 0:
        print(f"[ERROR] --levels must be an integer >= 1 (given: {args.levels})")
        sys.exit(1)

    input_p = Path(input_str).resolve()
    if not input_p.exists():
        print(f"[ERROR] Input file or folder not found: '{input_str}'")
        sys.exit(1)

    if is_batch:
        if not input_p.is_dir():
            print(f"[ERROR] --batch requires a valid folder: '{input_str}'")
            sys.exit(1)
        print(f"Running BATCH processing on folder: {input_p.name}...")

        def _batch_cb(curr, total, fname, result):
            print(f"  [{curr}/{total}] {fname:25s} -> Status: {result.status} | Db: {result.fractal_dimension:.4f} | R2: {result.r_squared:.4f}")

        res = run_batch_analysis(
            folder_path=input_p,
            output_dir=args.output,
            mode=args.mode,
            levels=args.levels,
            progress_callback=_batch_cb,
            export_batch_summary=False,
            overwrite=args.overwrite,
            profile=args.profile,
            batch_profile=args.batch_profile,
        )

        print("============================================================")
        print(f"BATCH COMPLETE: {res.successful_count}/{res.total_files} Successful in {res.duration_seconds:.2f}s")
        print(f"Batch Report Output: {res.output_dir}")
        print("============================================================")
        sys.exit(0 if res.failed_count == 0 else 1)

    # Single SVG File Mode
    print("============================================================")
    print("RASH-HIT Fractal Studio v1.0.0 - Running Analysis")
    print("============================================================")
    print(f"Input File      : {input_p.name}")
    print(f"Target Levels   : {args.levels}")
    print(f"Engine          : {args.engine.upper()} Exact Vector Geometry Engine")
    print("------------------------------------------------------------")

    def _cli_cb(sp: StepProgress):
        if sp.status == "SUCCESS":
            print(f"  [OK] {sp.name:45s} ({sp.duration_sec:.2f} s)")
            if sp.message:
                print(f"       └─ {sp.message}")
        elif sp.status == "ERROR":
            print(f"  [FAIL] {sp.name:45s}")
            if sp.error_message:
                print(f"         └─ {sp.error_message}")

    proc = AnalysisProcessor(
        input_path=input_p,
        output_dir=args.output,
        mode=args.mode,
        levels=args.levels,
        engine=args.engine,
        overwrite=args.overwrite,
        progress_callback=_cli_cb,
        profile=args.profile,
    )

    exec_res = proc.run()

    if exec_res.status == "SUCCESS":
        print("------------------------------------------------------------")
        print("SUMMARY RESULTS")
        print("------------------------------------------------------------")
        print(f"Fractal Dimension (Db) : {exec_res.fractal_dimension:.4f}")
        print(f"Log-Log Fit (R2)       : {exec_res.r_squared:.4f}")
        print(f"Confidence Level       : {exec_res.confidence_label} ({exec_res.confidence_score:.1f}/100)")
        print(f"Complexity Class       : {exec_res.motif_profile.get('complexity_class', 'N/A')}")
        print(f"Total Time             : {exec_res.duration_seconds:.2f} s")
        print("------------------------------------------------------------")
        print(f"[OK] Package Folder       : {exec_res.package_id}")
        print(f"[OK] Package Generated at: {exec_res.output_dir}")
        sys.exit(0)
    else:
        print(f"[ERROR] Analysis failed: {'; '.join(exec_res.errors)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
