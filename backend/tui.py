# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
"""
tui.py — Console Text User Interface (TUI) components for RASH-HIT Fractal Studio.
Flat, modern, academic terminal UI:
  - borderless flat layout (no ROUNDED Panel)
  - pure white RASH-HIT logo; single white accent for selections
  - thin separators, minimalist scientific styling
"""
from __future__ import annotations
import os
import sys
import math
from pathlib import Path
from typing import List, Any, Optional

try:
    import msvcrt
except ImportError:
    msvcrt = None

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.console import Group
from rich import box

console = Console()
try:
    from backend import __version__ as APP_VERSION
except Exception:
    APP_VERSION = "1.0.6"

ACCENT = "white"
ACCENT2 = "white"

LOGO_LINES = [
    "██████╗  █████╗ ███████╗██╗  ██╗      ██╗  ██╗██╗████████╗",
    "██╔══██╗██╔══██╗██╔════╝██║  ██║      ██║  ██║██║╚══██╔══╝",
    "██████╔╝███████║███████╗███████║█████╗███████║██║   ██║   ",
    "██╔══██╗██╔══██║╚════██║██╔══██║╚════╝██╔══██║██║   ██║   ",
    "██║  ██║██║  ██║███████║██║  ██║      ██║  ██║██║   ██║   ",
    "╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝      ╚═╝  ╚═╝╚═╝   ╚═╝   ",
    "                                                          ",
]

LOGO_ASCII = "\n".join(LOGO_LINES)


def _sep(width: int = 56) -> None:
    w = min(width, max(20, console.width - 4))
    pad = max(0, (console.width - w) // 2)
    console.print(" " * pad + f"[dim {ACCENT2}]{'─' * w}[/dim {ACCENT2}]")


def print_logo() -> None:
    """Renders the RASH-HIT ASCII logo in pure white (modern academic style)."""
    max_w = max((len(ln) for ln in LOGO_LINES), default=0)
    pad = max(0, (console.width - max_w) // 2)
    for line in LOGO_LINES:
        console.print(" " * pad + f"[bold white]{line}[/bold white]")
    console.print(f"[bold white]F R A C T A L   S T U D I O   v{APP_VERSION}[/bold white]", justify="center")
    console.print("[dim white]Fractal Dimension Analysis with Exact Vector Geometry[/dim white]", justify="center")
    console.print("")


def _enable_ansi() -> bool:
    """Best-effort enable of ANSI/Virtual Terminal processing on Windows 10+.

    Only affects COLORS / box-drawing rendering — screen clearing is handled
    separately by ``clear_screen`` and must NOT depend on this succeeding
    (VT can be unavailable while the console still works fine).
    """
    if os.name != 'nt':
        return True
    try:
        import ctypes
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        ENABLE_VIRTUAL_TERMINAL_INPUT = 0x0200
        ok = True
        for handle in (-11, -10):  # STD_OUTPUT_HANDLE, STD_INPUT_HANDLE
            h = kernel32.GetStdHandle(handle)
            if not h or h == ctypes.c_void_p(-1).value:
                ok = False
                continue
            mode = ctypes.c_uint32(0)
            if not kernel32.GetConsoleMode(h, ctypes.byref(mode)):
                ok = False
                continue
            if not kernel32.SetConsoleMode(
                h, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING
                | (ENABLE_VIRTUAL_TERMINAL_INPUT if handle == -10 else 0)
            ):
                ok = False
        return ok
    except Exception:
        return False


def clear_screen() -> None:
    """Clears the terminal reliably.

    Windows: always use ``cls`` (works on a real console regardless of Virtual
    Terminal support). We deliberately do NOT rely on ANSI ``\\x1b[2J`` because
    when VT is unavailable the escape is silently ignored and the menu stacks
    instead of repainting. On POSIX we use ``clear``. A final ANSI fallback is
    kept only for odd non-console environments.
    """
    _enable_ansi()  # best-effort: enable colors; clearing does not depend on it
    cleared = False
    try:
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')
        cleared = True
    except Exception:
        pass
    if not cleared:
        try:
            sys.stdout.write("\x1b[2J\x1b[H")
            sys.stdout.flush()
        except Exception:
            pass


def get_key() -> str:
    """Reads a single key press interactively (Cross-platform)."""
    if os.name == 'nt':
        if not msvcrt:
            return sys.stdin.read(1)
        # Flush any queued keystrokes so fast key-chords at a menu transition
        # don't carry over into the NEXT menu (a common cause of the selection
        # "jumping back" to a previous item).
        try:
            while msvcrt.kbhit():
                msvcrt.getch()
        except Exception:
            pass
        try:
            ch = msvcrt.getch()
        except Exception:
            return sys.stdin.read(1)
        if ch in (b'\x00', b'\xe0'):  # Arrow keys prefix
            ch2 = msvcrt.getch()
            if ch2 == b'H': return "up"
            if ch2 == b'P': return "down"
            if ch2 == b'K': return "left"
            if ch2 == b'M': return "right"
        if ch == b'\r':  # Enter key
            return "enter"
        if ch == b'\x1b':  # ESC key
            return "escape"
        if ch == b' ':
            return "space"
        try:
            return ch.decode('utf-8', errors='ignore').lower()
        except Exception:
            return ""
    else:
        import tty
        import termios
        fd = sys.stdin.fileno()
        try:
            old_settings = termios.tcgetattr(fd)
        except Exception:
            return sys.stdin.read(1)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    return {'A': 'up', 'B': 'down', 'C': 'right', 'D': 'left'}.get(ch3, ch3)
                return 'escape'
            elif ch in ('\r', '\n'):
                return 'enter'
            elif ch == ' ':
                return 'space'
            return ch.lower()
        finally:
            try:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            except Exception:
                pass


NAV_BACK = -2


def select_from_menu(title: str, options: List[str], preselected_idx: int = 0,
                     add_back: bool = False, escape_action: str = "exit",
                     clear: bool = True) -> int:
    """Displays an interactive menu whose options live inside a clean bordered box.

    clear=False renders the menu box WITHOUT wiping the screen (logo + prior
    content stays visible) — used by post-run action menus that must preserve
    the result table above.

    add_back: appends '↩ Back'; selecting it (or pressing ESC when escape_action=='back')
              returns NAV_BACK instead of an index.
    escape_action: 'exit' -> ESC hard-exits the app (top-level menus)
                   'back' -> ESC returns NAV_BACK (sub-menus)
    """
    opts = list(options)
    if add_back:
        opts.append("↩ Back")
    idx = preselected_idx if 0 <= preselected_idx < len(opts) else 0

    def _render() -> None:
        if clear:
            clear_screen()
            print_logo()
        table = Table(box=box.SIMPLE, show_header=False, show_footer=False,
                      padding=(0, 1), expand=False, border_style="white")
        table.add_column("opt", justify="left", no_wrap=True)
        for i, opt in enumerate(opts):
            if i == idx:
                table.add_row(Text(f"▸ {opt}", style="bold reverse"))
            elif i == len(opts) - 1 and add_back:
                table.add_row(Text(f"  {opt}", style="dim"))
            else:
                table.add_row(Text(f"  {opt}", style="white"))
        panel = Panel(
            table,
            border_style=ACCENT,
            padding=(0, 1),
            title=f"[bold {ACCENT}]{title}[/bold {ACCENT}]",
            subtitle="[dim]↑/↓ select · ENTER confirm · ESC exit[/dim]",
        )
        console.print(panel)

    _render()

    while True:
        key = get_key()
        if key == "up":
            idx = (idx - 1) % len(opts)
        elif key == "down":
            idx = (idx + 1) % len(opts)
        elif key in ("enter", "space"):
            if add_back and idx == len(opts) - 1:
                return NAV_BACK
            return idx
        elif key in ("escape", "q"):
            if escape_action == "back":
                return NAV_BACK
            sys.exit(0)
        else:
            continue
        # Robust full redraw: avoids fragile cursor-line math that previously
        # left ghost rows / garbled boxes when the Panel height shifted.
        if clear:
            clear_screen()
        _render()


def prompt_custom_file() -> List[Path]:
    clear_screen()
    print_logo()
    while True:
        console.print("[bold white]Please enter the path to the SVG file:[/bold white]")
        console.print("[dim]Type 'q', 'exit' or '0' to cancel.[/dim]")
        path_str = input("File Path: ").strip().strip('"\'')
        if not path_str:
            continue
        if path_str.lower() in ("q", "exit", "back", "cancel", "esc", "0"):
            return []
        p = Path(path_str)
        if p.exists() and p.is_file() and p.suffix.lower() == ".svg":
            return [p]
        console.print(f"[bold white]Error: Invalid file path or not an SVG: {path_str}[/bold white]\n")


def prompt_custom_folder() -> List[Path]:
    clear_screen()
    print_logo()
    while True:
        console.print("[bold white]Please enter the folder path containing SVG files:[/bold white]")
        console.print("[dim]Type 'q', 'exit' or '0' to cancel.[/dim]")
        path_str = input("Folder Path: ").strip().strip('"\'')
        if not path_str:
            continue
        if path_str.lower() in ("q", "exit", "back", "cancel", "esc", "0"):
            return []
        p = Path(path_str)
        if p.exists() and p.is_dir():
            svg_files = sorted(list(p.glob("*.svg")))
            if svg_files:
                return svg_files
            else:
                console.print(f"[bold white]Warning: No SVG files found in this folder: {path_str}[/bold white]\n")
        else:
            console.print(f"[bold white]Error: Invalid folder path: {path_str}[/bold white]\n")


def render_live_progress_table(filename: str, current_step: str, steps_progress: List[Any],
                               level_reports: List[Any], total_levels: int = 7,
                               show_technical: bool = False) -> Table:
    """Generates the live styled table showing per-level computation progress.

    Columns mirror the web Scientific Console's Live Scale Computation Table
    (Level, Grid, Total, Filled, Empty, Occupancy %, Cell Size, Time, Fit,
    Status). Extra technical regression columns are appended only when
    ``show_technical`` is True so no unnecessary columns are shown by default.
    """
    table = Table(
        title=f"[bold white]Fractal Analysis Progress: {filename} - {current_step}[/bold white]",
        box=box.SQUARE,
        safe_box=True,  # SIMPLE_HEAVY's legacy fallback drops the verticals; SQUARE keeps the full grid
        border_style="white",
        header_style="bold white on black",
        title_style="bold white",
        padding=(0, 1),
    )
    table.add_column("Level", justify="center", style="bold white")
    table.add_column("Grid", justify="center", style="white")
    table.add_column("Total", justify="right", style="white")
    table.add_column("Filled", justify="right", style="bold white")
    table.add_column("Empty", justify="right", style="white")
    table.add_column("Occ %", justify="right", style="white")
    table.add_column("Cell Size", justify="center", style="white")
    table.add_column("Time", justify="right", style="white")
    table.add_column("Fit", justify="center", style="white")
    table.add_column("Status", justify="center", style="white")

    if show_technical:
        table.add_column("1/r", justify="right", style="white")
        table.add_column("log(1/r)", justify="right", style="white")
        table.add_column("log(N(r))", justify="right", style="white")
        table.add_column("NegSpace", justify="right", style="white")

    report_map = {int(getattr(lm, 'level', 0)): lm for lm in level_reports}

    completed_max = max(report_map.keys()) if report_map else 0
    computing_level = None
    is_step5_running = any(getattr(sp, 'step_index', None) == 5 and getattr(sp, 'status', None) == "RUNNING" for sp in steps_progress)
    if is_step5_running and completed_max < total_levels:
        computing_level = completed_max + 1

    for i in range(1, total_levels + 1):
        lvl_code = f"L{i:02d}"
        if i in report_map:
            lm = report_map[i]
            pct = getattr(lm, 'occupancy_percent', 0.0)
            label = getattr(lm, 'grid_label', '-')
            filled = getattr(lm, 'filled_cells', 0)
            total = getattr(lm, 'total_cells', 0)
            empty = total - filled
            cell_w = getattr(lm, 'cell_w', 0.0)
            cell_h = getattr(lm, 'cell_h', 0.0)
            cell_size = f"{cell_w:.2f} x {cell_h:.2f}"
            exec_ms = getattr(lm, 'execution_time_ms', 0.0)
            fit = "Fit" if getattr(lm, 'included_in_fit', True) else "Excluded"

            row_data = [
                lvl_code,
                label,
                f"{total:,}",
                f"{filled:,}",
                f"{empty:,}",
                f"{pct:.2f}%",
                cell_size,
                f"{exec_ms:.0f} ms",
                fit,
                "DONE",
            ]
            if show_technical:
                avg_size = (cell_w + cell_h) / 2.0
                inv_r = 1.0 / avg_size if avg_size > 0 else 1.0
                log_inv_r = math.log10(inv_r) if inv_r > 0 else 0.0
                log_nr = math.log10(filled) if filled > 0 else 0.0
                neg_cache = int(getattr(lm, "negative_space_cached_cells", 0) or 0)
                row_data.extend([
                    f"{inv_r:.4f}",
                    f"{log_inv_r:.4f}",
                    f"{log_nr:.4f}",
                    f"{neg_cache:,}" if neg_cache > 0 else "-",
                ])
            table.add_row(*row_data)
        elif i == computing_level:
            row_data = [lvl_code, "[bold white]Computing...[/bold white]", "-", "-", "-", "-", "-", "-", "-", "-"]
            if show_technical:
                row_data.extend(["-", "-", "-", "-"])
            table.add_row(*row_data)
        else:
            row_data = [lvl_code, "-", "-", "-", "-", "-", "-", "-", "-", "-"]
            if show_technical:
                row_data.extend(["-", "-", "-", "-"])
            table.add_row(*row_data)

    return table


def print_result_summary(exec_res) -> None:
    """Renders the summary table of the analysis results (modern academic)."""
    table = Table(box=box.SQUARE, safe_box=True, padding=(0, 2), header_style="bold white on black",
                  border_style="white")
    table.add_column("Metric", style=f"{ACCENT} bold")
    table.add_column("Value", style="white bold")

    status_color = "white" if exec_res.status == "SUCCESS" else "white"

    table.add_row("Status", f"[{status_color}]{exec_res.status}[/{status_color}]")
    table.add_row("Fractal Dimension (Db)", f"[bold white]{exec_res.fractal_dimension:.4f}[/bold white]")
    table.add_row("Regression Fit (R²)", f"[bold white]{exec_res.r_squared:.4f}[/bold white]")
    table.add_row("Confidence Level", f"[bold white]{exec_res.confidence_label} ({exec_res.confidence_score:.1f}/100)[/bold white]")
    table.add_row("Complexity Class", f"[bold white]{exec_res.motif_profile.get('complexity_class', 'N/A')}[/bold white]")
    table.add_row("Total Analysis Time", f"{exec_res.duration_seconds:.2f} seconds")
    table.add_row("Output Directory", f"[dim]{exec_res.output_dir}[/dim]")

    console.print("")
    console.print("[bold white] 📊  Analysis Result Summary [/bold white]")
    console.print(table)
    console.print("")


def show_system_diagnostics() -> None:
    """Gathers and prints comprehensive environment details in a clean table."""
    import shapely
    import openpyxl

    table = Table(title=f"[bold {ACCENT}]System Diagnostics & Environment Audit[/bold {ACCENT}]",
                  box=box.SQUARE, safe_box=True, padding=(0, 2), header_style="bold white on black",
                  border_style="white")
    table.add_column("Component", style=f"{ACCENT} bold")
    table.add_column("Status / Version", style="white bold")

    table.add_row("Python Version", sys.version.split()[0])
    table.add_row("Operating System", f"{sys.platform} ({os.name})")
    table.add_row("Shapely (GEOS)", shapely.__version__)
    table.add_row("OpenPyXL", openpyxl.__version__)

    input_dir = Path("input_svgs")
    if input_dir.exists():
        svg_cnt = len(list(input_dir.glob("*.svg")))
        table.add_row("input_svgs/ Folder", f"[white]Present[/white] ({svg_cnt} SVG files)")
    else:
        table.add_row("input_svgs/ Folder", "[white]ERROR: Not Found[/white]")

    console.print("")
    console.print(table)
    console.print("")


def info_panel(title: str, body: str, accent: str = ACCENT) -> None:
    """Flat (box-free) information block used by launcher.py screens."""
    console.print("")
    _sep()
    console.print(f"[bold {accent}]{title}[/bold {accent}]")
    console.print("")
    console.print(body)
    _sep()
    console.print("")


# ---------------------------------------------------------------------------
# New CLI API (compatible with launcher.py): single selectors + live progress
# ---------------------------------------------------------------------------

def select_svg_file() -> Optional[Path]:
    """Single SVG file picker (for interactive terminal mode). None -> cancelled."""
    svg_dir = Path("input_svgs")
    files = sorted(list(svg_dir.glob("*.svg"))) if svg_dir.exists() else []
    if not files:
        console.print("[bold white]No SVGs found in the input_svgs/ folder![/bold white]")
        custom = prompt_custom_file()
        return custom[0] if custom else None

    options = [f.name for f in files] + ["Specify custom SVG file path"]
    idx = select_from_menu("Select SVG File", options, add_back=True, escape_action="back")
    if idx == NAV_BACK or idx == -1:
        return None
    if idx == len(files):
        custom = prompt_custom_file()
        return custom[0] if custom else None
    return files[idx]


def prompt_custom_levels() -> int:
    """Direct custom level input (the user types any level count 1-50).

    Returns the chosen integer level count, or 0 when the user cancels.
    Defaults to 7 when the input is empty.
    """
    clear_screen()
    print_logo()
    while True:
        console.print("[bold white]Enter the number of analysis levels (1-50):[/bold white]")
        console.print("[dim]Default: 7 | Type 'q' or '0' to cancel.[/dim]")
        raw = input("Levels: ").strip()
        if not raw:
            return 7
        low = raw.lower()
        if low in ("q", "exit", "back", "cancel", "esc", "0"):
            return 0
        try:
            val = int(raw)
        except ValueError:
            console.print(f"[bold white]Invalid input: {raw} — enter an integer between 1 and 50.[/bold white]\n")
            continue
        if 1 <= val <= 50:
            return val
        console.print(f"[bold white]Level count must be between 1 and 50 (got {val}).[/bold white]\n")


class LiveProgressViewer:
    """Live progress viewer: used with the AnalysisProcessor progress_callback.

    Displays the 7-step pipeline progress as a checklist and, once box-counting
    levels start completing, renders the real per-level Scale Table (the same
    table the web Scientific Console shows) via ``render_live_progress_table``.
    """

    _SYM = {"RUNNING": "▶", "SUCCESS": "✔", "ERROR": "✘", "PENDING": "•"}
    _COL = {"RUNNING": "white", "SUCCESS": "white", "ERROR": "white", "PENDING": "dim"}

    def __init__(self, title: str = "", total_levels: int = 7, show_technical: bool = True):
        self.title = title
        self.total_levels = max(1, total_levels)
        self.show_technical = show_technical
        self.step_states: dict = {}
        self.level_reports: List[Any] = []

    def __enter__(self):
        self._render()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def update_step(self, sp) -> None:
        idx = getattr(sp, "step_index", 0)
        status = getattr(sp, "status", "")
        msg = getattr(sp, "message", "")
        self.step_states[idx] = (status, msg)
        self._render()

    def update_level(self, lm) -> None:
        """Register a completed box-counting level and refresh the live table."""
        lvl = int(getattr(lm, "level", 0) or 0)
        if lvl <= 0:
            return
        # Keep only the latest report per level (in case of re-runs).
        self.level_reports = [r for r in self.level_reports if int(getattr(r, "level", 0) or 0) != lvl]
        self.level_reports.append(lm)
        self.level_reports.sort(key=lambda r: int(getattr(r, "level", 0) or 0))
        self._render()

    def _render(self) -> None:
        clear_screen()
        print_logo()
        console.print(f"[bold {ACCENT}]{self.title}[/bold {ACCENT}]\n")

        if not self.step_states:
            console.print("[dim]Starting...[/dim]")
            return

        for idx in sorted(self.step_states):
            status, msg = self.step_states[idx]
            sym = self._SYM.get(status, "•")
            color = self._COL.get(status, "white")
            console.print(f"  [{color}]{sym} Step {idx}: {msg}[/{color}]")
        console.print("")

        # Render the live Scale Table as soon as box-counting begins (step 5
        # RUNNING) or once at least one level has completed. Every requested
        # level row appears immediately and fills in one-by-one as each level
        # finishes -- never waiting for the whole run to complete in bulk.
        counting_started = any(
            idx == 5 and status == "RUNNING"
            for idx, (status, _msg) in self.step_states.items()
        ) or bool(self.level_reports)

        if counting_started:
            # The table builds its own "Fractal Analysis Progress: <file> - <step>"
            # title, so strip any duplicate prefix already stored in self.title.
            table_filename = self.title.replace("Fractal Analysis Progress: ", "").strip()
            current_step = next((msg for s, msg in self.step_states.values() if s == "RUNNING"), "Computing...")
            # Render the in-progress level as "Computing…" by presenting step 5
            # as RUNNING whenever box-counting is still under way.
            steps_progress = []
            completed_max = max((int(getattr(r, "level", 0) or 0) for r in self.level_reports), default=0)
            if completed_max < self.total_levels:
                from types import SimpleNamespace
                steps_progress = [SimpleNamespace(step_index=5, status="RUNNING")]
            table = render_live_progress_table(
                table_filename,
                current_step,
                steps_progress,
                self.level_reports,
                total_levels=self.total_levels,
                show_technical=self.show_technical,
            )
            console.print(table)
            console.print("")
