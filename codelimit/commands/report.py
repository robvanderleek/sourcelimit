from pathlib import Path

import typer
from rich import print
from rich.console import Console

from codelimit.common.report.Report import Report
from codelimit.common.utils import format_measurement
from codelimit.utils import read_cached_report

REPORT_LENGTH = 10


def report_command(path: Path, full: bool, totals: bool):
    report = read_report(path)
    if totals:
        _report_totals(report)
    else:
        _report_units(report, path, full)

def _report_totals(report: Report):
    pass

def _report_units(report: Report, path: Path, full: bool):
    units = report.all_report_units_sorted_by_length_asc(30)
    if len(units) == 0:
        print(
            "[bold]Refactoring not necessary, :sparkles: happy coding! :sparkles:[/bold]"
        )
        return
    if full:
        report_units = units
    else:
        report_units = units[0:REPORT_LENGTH]
    root = get_root(path)
    _print_functions(root, units, report_units, full)


def get_root(path: Path) -> Path | None:
    cwd = Path().resolve()
    if str(cwd) == str(path.absolute()):
        return None
    elif path.absolute().is_relative_to(cwd):
        return path
    else:
        return path.absolute()


def read_report(path: Path) -> Report:
    report = read_cached_report(path)
    if not report:
        print("[red]No cached report found in current folder[/red]")
        raise typer.Exit(code=1)
    return report


def _print_functions(root, units, report_units, full):
    stdout = Console()
    for unit in report_units:
        file_path = unit.file if root is None else root.joinpath(unit.file)
        stdout.print(
            format_measurement(str(file_path), unit.measurement), soft_wrap=True
        )
    if not full and len(units) > REPORT_LENGTH:
        print(
            f"[bold]{len(units) - REPORT_LENGTH} more rows, use --full option to get all rows[/bold]"
        )
