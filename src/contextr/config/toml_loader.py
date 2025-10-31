"""
TOML configuration file loading and processing
"""

import tomllib
from pathlib import Path

import typer
from rich.console import Console

from .settings import DEFAULT_CONFIG_FILE, DEFAULT_PATHS

console = Console()


class ContextrConfig:
    """Configuration class for contextr"""

    def __init__(
        self,
        paths: list[str],
        include: str | None = None,
        output: str | None = None,
        recent: bool = False,
    ):
        self.paths = paths
        self.include = include
        self.output = output
        self.recent = recent

    @classmethod
    def from_toml(cls, config_path: Path | None = None) -> "ContextrConfig":
        """
        Load configuration from TOML file.

        Args:
            config_path: Path to config file. If None, looks for .contextr.toml in cwd

        Returns:
            ContextrConfig instance with loaded settings
        """
        if config_path is None:
            config_path = Path.cwd() / DEFAULT_CONFIG_FILE

        if not config_path.exists():
            return cls(paths=DEFAULT_PATHS.copy())

        try:
            with open(config_path, "rb") as f:
                data = tomllib.load(f)

            flags = data.get("Flags", {})

            # Normalize paths - handle both string and list formats
            paths = flags.get("paths", DEFAULT_PATHS.copy())
            if isinstance(paths, str):
                paths = [paths]

            return cls(
                paths=paths,
                include=flags.get("include"),
                output=flags.get("output"),
                recent=flags.get("recent", False),
            )

        except tomllib.TOMLDecodeError as e:
            console.print(
                f"Invalid TOML syntax in {config_path}: {e}", style="bold red"
            )
            raise typer.Exit(1) from e
        except Exception as e:
            console.print(
                f"Error reading config file {config_path}: {e}", style="bold red"
            )
            raise typer.Exit(1) from e

    def merge_with_cli(
        self,
        cli_paths: list[str] | None = None,
        cli_include: str | None = None,
        cli_output: str | None = None,
        cli_recent: bool = False,
    ) -> "ContextrConfig":
        """
        Merge configuration with CLI arguments. CLI arguments take precedence.

        Args:
            cli_paths: CLI paths argument
            cli_include: CLI include pattern
            cli_output: CLI output file
            cli_recent: CLI recent flag

        Returns:
            New ContextrConfig instance with merged settings
        """
        return ContextrConfig(
            paths=cli_paths if cli_paths else self.paths,
            include=cli_include if cli_include is not None else self.include,
            output=cli_output if cli_output is not None else self.output,
            recent=cli_recent if cli_recent else self.recent,
        )


def get_effective_config(
    cli_paths: list[str] | None = None,
    cli_include: str | None = None,
    cli_output: str | None = None,
    cli_recent: bool = False,
    config_path: Path | None = None,
) -> ContextrConfig:
    """
    Get the effective configuration by merging TOML config with CLI arguments.

    Args:
        cli_paths: CLI paths argument
        cli_include: CLI include pattern
        cli_output: CLI output file
        cli_recent: CLI recent flag
        config_path: Path to config file

    Returns:
        ContextrConfig instance with final effective settings
    """
    # Load config from TOML file
    toml_config = ContextrConfig.from_toml(config_path)

    # Merge with CLI arguments
    final_config = toml_config.merge_with_cli(
        cli_paths=cli_paths,
        cli_include=cli_include,
        cli_output=cli_output,
        cli_recent=cli_recent,
    )

    return final_config
