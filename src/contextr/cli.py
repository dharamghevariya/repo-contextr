from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console

from . import __version__
from .commands.package import package_repository
from .config import get_effective_config

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
        console.print(f"contextr version {__version__}", style="bold green")
        raise typer.Exit()
    
    # Get effective configuration by merging TOML config with CLI arguments
    config = get_effective_config(
        cli_paths=paths,
        cli_include=include,
        cli_output=output,
        cli_recent=recent
    )
    
    try:
        result = package_repository(
            config.paths, 
            include_pattern=config.include, 
            recent=config.recent
        )
        
        if config.output:
            output_path = Path(config.output)
            try:
                output_path.write_text(result, encoding='utf-8')
                console.print(f"✅ Context packaged and saved to: {config.output}", style="bold green")
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