from typing import List, Optional

import typer

app = typer.Typer(
    name="contextr",
    help="Analyze git repositories and package their content for sharing with LLMs",
    add_completion=False
)

@app.command()
def main(
    paths: Optional[List[str]] = typer.Argument(
        None,
        help="One or more file or directory paths to analyze"
    ),
    output: Optional[str] = typer.Option(
        None,
        "-o",
        "--output",
        help="Output file path (default: stdout)"
    ),
    include: Optional[str] = typer.Option(
        None,
        "--include",
        help="Pattern to include files (e.g., '*.py', '*.js')"
    ),
    version: bool = typer.Option(
        False,
        "-v",
        "--version",
        help="Show version and exit"
    ),
):
    if version:
        # TODO: version should be dynamic, take from the pyproject.toml
        typer.echo("contextr version 0.1.0")
        raise typer.Exit()
    
    # Set default path if none provided
    if not paths:
        paths = ["."]
    
    # TODO: impelemnt the program logic

if __name__ == "__main__":
    app()
