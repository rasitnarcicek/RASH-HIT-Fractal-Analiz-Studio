# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
"""
launcher.py - Modern Interactive CLI Terminal Launcher & System Entry Point for RASH-HIT Fractal Studio.
Provides a rich, interactive terminal menu interface for Web Dashboard, Interactive Terminal Mode,
System Diagnostics, and Test Execution.
"""
from __future__ import annotations

import sys
import subprocess
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.processor import AnalysisProcessor, StepProgress
from backend.batch_processor import run_batch_analysis
from backend.tui import (
    clear_screen,
    print_logo,
    select_from_menu,
    NAV_BACK,
    get_key,
    select_svg_file,
    prompt_custom_levels,
    LiveProgressViewer,
    print_result_summary,
    show_system_diagnostics,
    info_panel,
    console,
)
from rich.table import Table
from rich import box


def wait_for_enter() -> None:
    """Prompts user to press Enter or any key to return."""
    console.print("\n[dim white]Press ENTER to return to the main menu...[/dim white]")
    input()


def post_run_action_menu() -> int:
    """Offer two choices WITHOUT clearing the screen or drawing a box:

      1. Run a New Analysis   (returns 0)
      2. Back to Main Menu     (returns 1)

    The result table the user just read stays visible on screen. Navigation is
    in-place: only the two option lines are rewritten via ANSI cursor-up, so
    arrow keying never causes the menu to stack vertically.
    """
    import shutil as _sh
    term_w = _sh.get_terminal_size().columns
    sep = "─" * term_w
    lines = [sep, "  1. Run a New Analysis", "  2. Back to Main Menu", sep,
             "  ↑/↓ select · ENTER confirm · ESC/↩ Back to Main Menu"]
    idx = 0
    # Print the menu once below the preserved result table.
    for ln in lines:
        console.print(ln)

    def _paint():
        # Rewrite only the two option rows in place (cursor-up x2).
        for _ in range(2):
            print("\x1b[1A", end="")          # move up one line
        print("\x1b[2K", end="")              # clear current line
        print("  " + ("▸ " if idx == 0 else "  ") + "Run a New Analysis", end="")
        print("\x1b[1B", end="")              # down
        print("\x1b[2K", end="")              # clear current line
        print("  " + ("▸ " if idx == 1 else "  ") + "Back to Main Menu", end="")
        print("\x1b[1B", end="")              # back down to footer baseline
        sys.stdout.flush()

    while True:
        _paint()
        key = get_key()
        if key in ("up",):
            idx = 0
        elif key in ("down",):
            idx = 1
        elif key in ("enter", "space"):
            return idx
        elif key in ("escape", "q"):
            return 1

    return idx


def run_interactive_terminal_mode() -> None:
    """Interactive mode for analyzing single SVG files or batch directory analysis.

    After every completed operation the user is offered "Run a New Analysis"
    or "Back to Main Menu" so the workflow can continue without re-launching.
    """
    while True:
        target_options = [
            "1. Single SVG File Analysis",
            "2. Batch Directory Analysis",
            "Back to Main Menu"
        ]
        target_idx = select_from_menu("Terminal Interactive Analysis Mode", target_options)

        if target_idx in (-1, 2):
            return

        if target_idx == 0:
            # Single SVG Analysis: file -> custom levels -> straight to counting.
            svg_file = select_svg_file()
            if not svg_file:
                continue

            levels = prompt_custom_levels()
            if levels <= 0:
                continue
            profile = "lean"

            file_p = Path(svg_file)
            clear_screen()
            print_logo()

            console.print("[bold white]Starting Analysis:[/bold white] [bold white]" + file_p.name + "[/bold white]")
            console.print("[dim white]Levels: " + str(levels) + " | Profile: " + profile + " | Engine: CPU Exact Vector[/dim white]\n")

            with LiveProgressViewer(
                title="Fractal Analysis Progress: " + file_p.name,
                total_levels=levels,
                show_technical=False,
            ) as viewer:
                def _tui_cb(sp: StepProgress):
                    viewer.update_step(sp)

                def _tui_level_cb(lm):
                    viewer.update_level(lm)

                processor = AnalysisProcessor(
                    input_path=file_p,
                    levels=levels,
                    profile=profile,
                    progress_callback=_tui_cb
                )
                exec_res = processor.run(level_callback=_tui_level_cb)

            print_result_summary(exec_res)

        elif target_idx == 1:
            # Batch Directory Analysis
            input_dir = Path("input_svgs")
            if not input_dir.exists() or not input_dir.is_dir():
                console.print("[bold white]Error: 'input_svgs' folder not found![/bold white]")
                wait_for_enter()
                continue

            svg_files = list(input_dir.glob("*.svg"))
            if not svg_files:
                console.print("[bold white]Warning: no SVG files found in 'input_svgs' folder![/bold white]")
                wait_for_enter()
                continue

            levels = prompt_custom_levels()
            if levels <= 0:
                continue
            profile = "lean"

            clear_screen()
            print_logo()
            console.print("[bold white]Starting Batch Folder Analysis:[/bold white] [bold white]" + input_dir.name + "[/bold white] (" + str(len(svg_files)) + " files)")
            console.print("[dim white]Levels: " + str(levels) + " | Profile: " + profile + " | Engine: CPU Exact Vector[/dim white]\n")

            table = Table(title="[bold white]Batch Process Progress[/bold white]", box=box.SQUARE,
                          safe_box=True, border_style="white", header_style="bold white on black")
            table.add_column("No", justify="right", style="dim", width=6)
            table.add_column("File", style="bold white", width=25)
            table.add_column("Status", style="bold", width=12)
            table.add_column("Db (Dimension)", justify="right", style="bold white", width=12)
            table.add_column("R2 (Fit)", justify="right", style="bold white", width=12)

            def _batch_cb(curr: int, total: int, fname: str, result):
                table.add_row(
                    "[" + str(curr) + "/" + str(total) + "]",
                    fname,
                    result.status,
                    str(round(result.fractal_dimension, 4)),
                    str(round(result.r_squared, 4))
                )

            res = run_batch_analysis(
                folder_path=input_dir,
                levels=levels,
                profile=profile,
                progress_callback=_batch_cb,
                export_batch_summary=False
            )

            console.print(table)
            console.print("")
            summary_text = (
                "[bold white]Batch Analysis Completed Successfully![/bold white]\n\n"
                "  Successful: " + str(res.successful_count) + "/" + str(res.total_files) + "\n"
                "  Total Time: " + str(round(res.duration_seconds, 2)) + " seconds\n"
                "  Report Directory: [dim]" + str(res.output_dir) + "[/dim]"
            )
            info_panel(" Batch Process Summary ", summary_text, accent="white")

        # After every operation: New Analysis or Back to Main Menu.
        choice = post_run_action_menu()
        if choice == 1:
            return
        clear_screen()


def run_system_diagnostics_menu() -> None:
    """Displays system diagnostics information in a stylized table."""
    clear_screen()
    print_logo()
    show_system_diagnostics()
    wait_for_enter()


def run_tests_menu() -> None:
    """Executes the test suite with rich status display."""
    clear_screen()
    print_logo()
    console.print("[bold white]Running Unit Test Suite (pytest)...[/bold white]\n")
    try:
        subprocess.run([sys.executable, "-m", "pytest", "tests/"], check=False)
    except Exception as e:
        console.print("[bold white]Test run error: " + str(e) + "[/bold white]")
    wait_for_enter()


def show_direct_cli_help() -> None:
    """Shows direct CLI command options and examples."""
    clear_screen()
    print_logo()
    help_text = (
        "[bold white]Direct Command Line Usage Examples:[/bold white]\n\n"
        "  Single SVG File Analysis:\n"
        "    python run_analysis.py --input input_svgs/16D.svg --levels 7 --profile lean\n\n"
        "  Batch Folder Analysis:\n"
        "    python run_analysis.py --batch input_svgs/ --levels 7 --profile lean\n\n"
        "  Starting the Web Server:\n"
        "    python launcher.py  (or choose option 1 from the menu)"
    )
    info_panel(" CLI Info ", help_text, accent="white")
    wait_for_enter()


def main_menu() -> None:
    """Main interactive launcher entry point."""
    while True:
        options = [
            "1. Launch Web Dashboard Server",
            "2. Interactive CLI Analysis",
            "3. Direct Command Mode Info",
            "4. System Diagnostics",
            "5. Run Test Suite",
            "6. Exit"
        ]

        choice = select_from_menu("Main Menu - Make a Selection", options)

        if choice == 0:
            from backend.web_server import start_server
            start_server(8000, open_browser=True)
        elif choice == 1:
            run_interactive_terminal_mode()
        elif choice == 2:
            show_direct_cli_help()
        elif choice == 3:
            run_system_diagnostics_menu()
        elif choice == 4:
            run_tests_menu()
        elif choice in (-1, 5):
            clear_screen()
            console.print("[bold white]RASH-HIT Fractal Studio closed. Goodbye![/bold white]\n")
            sys.exit(0)


if __name__ == "__main__":
    main_menu()
