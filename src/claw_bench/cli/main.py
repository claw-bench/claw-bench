"""Main Typer app entry point for claw-bench CLI."""

from typing import Optional

import typer

from claw_bench import __version__
from claw_bench.cli.analyze import analyze_app
from claw_bench.cli.doctor import doctor_cmd
from claw_bench.cli.init import init_cmd
from claw_bench.cli.list_cmd import list_app
from claw_bench.cli.moltbook import moltbook_app
from claw_bench.cli.oracle import oracle_cmd
from claw_bench.cli.report import report_cmd
from claw_bench.cli.submit import submit_cmd
from claw_bench.cli.validate import validate_cmd

app = typer.Typer(
    name="claw-bench",
    help="Claw Bench — AI Agent Framework Evaluation Benchmark",
    no_args_is_help=True,
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"claw-bench {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-V",
        help="Show the version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """Claw Bench — AI Agent Framework Evaluation Benchmark."""


app.command(name="submit")(submit_cmd)
app.command(name="validate")(validate_cmd)
app.command(name="doctor")(doctor_cmd)
app.command(name="init")(init_cmd)
app.command(name="oracle")(oracle_cmd)
app.command(name="report")(report_cmd)
app.add_typer(list_app, name="list")
app.add_typer(analyze_app, name="analyze")
app.add_typer(moltbook_app, name="moltbook")


if __name__ == "__main__":
    app()
