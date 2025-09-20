from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console

from .commands.package import package_repository

console = Console()

app = typer.Typer(
    name="contextr",
    help="Analyze git repositories and package their content for sharing with LLMs",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]}
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
    recent: bool = typer.Option(
        False,
        "-r",
        "--recent",
        help="Only include files modified in the last 7 days"
    ),
):
    if version:
        console.print("contextr version 0.1.0", style="bold green")
        raise typer.Exit()
    
    # Set default path if none provided
    if not paths:
        paths = ["."]
    
    try:
        result = package_repository(paths, include_pattern=include, recent=recent)
        
        if output:
            output_path = Path(output)
            try:
                output_path.write_text(result, encoding='utf-8')
                console.print(f"✅ Context packaged and saved to: {output}", style="bold green")
            except Exception as write_error:
                console.print(f"❌ Error writing to file: {write_error}", style="bold red")
                typer.echo(result)  # Fall back to stdout
        else:
            # Write to stdout
            typer.echo(result)
            
    except Exception as e:
        console.print(f"❌ Error: {e}", style="bold red")
        import traceback
        traceback.print_exc()
        raise typer.Exit(1)


if __name__ == "__main__":
    app()