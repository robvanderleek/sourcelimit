import importlib.metadata
from pathlib import Path
from typing import List, Annotated, Optional

import typer
from rich import print
from typer import Context
from typer.core import TyperGroup

from codelimit.commands import github
from codelimit.commands.check import check_command
from codelimit.commands.report import report_command
from codelimit.commands.scan import scan_command
from codelimit.commands.upload import upload_command
from codelimit.common.Configuration import Configuration


class OrderCommands(TyperGroup):
    def list_commands(self, ctx: Context):
        return list(self.commands)


cli = typer.Typer(cls=OrderCommands, no_args_is_help=True, add_completion=False)
cli.add_typer(github.app, name="github", help="Code Limit GitHub App commands")


@cli.command(help="Check file(s)")
def check(
    paths: Annotated[List[Path], typer.Argument(exists=True)],
    quiet: Annotated[
        bool, typer.Option("--quiet", help="No output when successful")
    ] = False,
):
    check_command(paths, quiet)


@cli.command(help="Scan a codebase")
def scan(
    path: Annotated[
        Path, typer.Argument(exists=True, file_okay=False, help="Codebase root")
    ]
):
    scan_command(path)


@cli.command(help="Show report for codebase")
def report(
    path: Annotated[
        Path, typer.Argument(exists=True, file_okay=False, help="Codebase root")
    ],
    full: Annotated[bool, typer.Option("--full", help="Show full report")] = False,
):
    report_command(path, full)


@cli.command(help="Upload report to Code Limit GitHub App")
def upload(
    repository: Annotated[
        str,
        typer.Argument(
            envvar="GITHUB_REPOSITORY", show_default=False, help="GitHub repository"
        ),
    ],
    branch: Annotated[
        str,
        typer.Argument(envvar="GITHUB_REF", show_default=False, help="GitHub branch"),
    ],
    report_file: Path = typer.Option(
        None,
        "--report",
        exists=True,
        dir_okay=False,
        file_okay=True,
        help="JSON report file",
    ),
    token: str = typer.Option(None, "--token", help="GitHub access token"),
    url: str = typer.Option(
        "https://codelimit.vercel.app/api/upload",
        "--url",
        help="Upload JSON report to this URL.",
    ),
):
    upload_command(repository, branch, report_file, token, url)


def _version_callback(show: bool):
    if show:
        version = importlib.metadata.version("codelimit")
        print(f"Code Limit version: {version}")
        raise typer.Exit()


@cli.callback()
def main(
    verbose: Annotated[
        Optional[bool], typer.Option("--verbose", "-v", help="Verbose output")
    ] = False,
    exclude: Annotated[
        Optional[list[str]], typer.Option(help="Glob patterns for exclusion")
    ] = None,
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version", "-V", help="Show version", callback=_version_callback
        ),
    ] = None,
):
    """CodeLimit: Your refactoring alarm."""
    if verbose:
        Configuration.verbose = True
    if version:
        raise typer.Exit()
    if exclude:
        Configuration.excludes.extend(exclude)


if __name__ == "__main__":
    cli()
