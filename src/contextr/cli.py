from pathlib import Path
from typing import List, Optional

import typer

from .commands.package import package_repository

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
        typer.echo("contextr version 0.1.0")
        raise typer.Exit()
    
    # Set default path if none provided
    if not paths:
        paths = ["."]
    
    try:
        result = package_repository(paths, include_pattern=include)
        
        if output:
            output_path = Path(output)
            try:
                output_path.write_text(result, encoding='utf-8')
                typer.echo(f"Context packaged and saved to: {output}", err=True)
            except Exception as write_error:
                typer.echo(f"Error writing to file: {write_error}", err=True)
                typer.echo(result)  # Fall back to stdout
        else:
            # Write to stdout
            typer.echo(result)
            
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        raise typer.Exit(1)


if __name__ == "__main__":
    app()