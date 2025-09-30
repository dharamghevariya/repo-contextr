from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console

from . import __version__
from .commands.package import package_repository

import tomllib

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
    # Merge CLI flags with config file
    paths, include, output, recent, version = merge_cli_with_config(
        paths, include, output, recent, version
    )

    if version:
        console.print(f"contextr version {__version__}", style="bold green")
        raise typer.Exit()
    
    # Default paths has been handled by merge_cli_with_config()
    
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

def merge_cli_with_config(
    paths: Optional[List[str]],
    include: Optional[str],
    output: Optional[str],
    recent: bool,
    version: bool
) -> tuple:
    """
    Merge CLI arguments with config file values.
    CLI arguments take precedence over config file.

    Returns:
        Tuple of (paths, include, output, recent, version)
    """
    toml_flags = load_toml_config().get("Flags", {})

    # CLI flags override config values if provided
    final_paths = paths if paths else toml_flags.get("paths", ["."])
    final_include = include if include else toml_flags.get("include")
    final_output = output if output else toml_flags.get("output")
    final_recent = recent if recent else toml_flags.get("recent", False)
    final_version = version if version else toml_flags.get("version", False)

    # Ensure paths to always be a list
    if isinstance(final_paths, str):
        final_paths = [final_paths]
    elif not final_paths:
        final_paths = ["."]

    return final_paths, final_include, final_output, final_recent, final_version


def load_toml_config() -> dict:
    """
    Load configuration from *.contextr.toml file in current directory.
    If multiple files match, uses the first one found.

    Returns:
        Dictionary containing the parsed TOML configuration, or empty dict if:
        - No config file found
        - File has invalid TOML syntax
        - Error occurs during file reading
    """
    config_path = list(Path.cwd().glob("*.contextr.toml"))
    if not config_path:
        return {}

    first_matched_config = config_path[0]
    try:
        with open(first_matched_config, "rb") as f:
            return tomllib.load(f)
    except tomllib.TOMLDecodeError:
        console.print("❌ Invalid toml config, ignored", style="bold yellow")
        return {}
    except Exception:
        console.print("❌ Error loading toml config, ignored", style="bold yellow")
        return {}

if __name__ == "__main__":
    app()