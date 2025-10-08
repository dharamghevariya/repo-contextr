import tempfile
from pathlib import Path
from unittest.mock import patch
import typer
from contextr.config import ContextrConfig, get_effective_config


def test_contextr_config_from_toml_file_not_found():
    """Test that default config is returned when no config file exists"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Mock the cwd function to return the temporary directory
        with patch('pathlib.Path.cwd', return_value=Path(tmpdir)):
            config = ContextrConfig.from_toml()
            assert config.paths == ["."]
            assert config.include is None
            assert config.output is None
            assert config.recent is False


def test_contextr_config_from_toml_valid_file():
    """Test loading a valid TOML config file"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a valid TOML file
        config_path = Path(tmpdir) / ".contextr.toml"
        config_path.write_text("""
[Flags]
include = "*.py"
output = "test.txt"
recent = true
""")

        with patch('pathlib.Path.cwd', return_value=Path(tmpdir)):
            config = ContextrConfig.from_toml()
            assert config.paths == ["."]  # Default value
            assert config.include == "*.py"
            assert config.output == "test.txt"
            assert config.recent is True


def test_contextr_config_from_toml_invalid_syntax():
    """Test that invalid TOML syntax raises SystemExit"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create invalid TOML file
        config_path = Path(tmpdir) / ".contextr.toml"
        config_path.write_text("invalid toml [[[")

        with patch('pathlib.Path.cwd', return_value=Path(tmpdir)):
            try:
                ContextrConfig.from_toml()
                assert False, "Expected typer.Exit to be raised"
            except typer.Exit:
                # This is expected behavior
                pass


def test_get_effective_config_cli_takes_precedence():
    """Test that CLI arguments override config values"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create config file
        config_path = Path(tmpdir) / ".contextr.toml"
        config_path.write_text("""
[Flags]
paths = ["/config/path"]
include = "*.py"
output = "config.txt"
recent = false
""")

        with patch('pathlib.Path.cwd', return_value=Path(tmpdir)):
            # CLI args should override config
            config = get_effective_config(
                cli_paths=["/cli/path"],
                cli_include="*.md",
                cli_output="cli.txt",
                cli_recent=True
            )

            assert config.paths == ["/cli/path"]
            assert config.include == "*.md"
            assert config.output == "cli.txt"
            assert config.recent is True


def test_get_effective_config_uses_config_defaults():
    """Test that config values are used when CLI args not provided"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create config file
        config_path = Path(tmpdir) / ".contextr.toml"
        config_path.write_text("""
[Flags]
paths = ["/config/path"]
include = "*.py"
output = "config.txt"
recent = true
""")

        with patch('pathlib.Path.cwd', return_value=Path(tmpdir)):
            # No CLI args provided (None/False)
            config = get_effective_config(
                cli_paths=None,
                cli_include=None,
                cli_output=None,
                cli_recent=False
            )

            assert config.paths == ["/config/path"]
            assert config.include == "*.py"
            assert config.output == "config.txt"
            assert config.recent is True


def test_get_effective_config_normalizes_string_path():
    """Test that string paths are normalized to lists"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / ".contextr.toml"
        config_path.write_text("""
[Flags]
paths = "/single/path"
""")

        with patch('pathlib.Path.cwd', return_value=Path(tmpdir)):
            config = get_effective_config(
                cli_paths=None,
                cli_include=None,
                cli_output=None,
                cli_recent=False
            )

            assert config.paths == ["/single/path"]
            assert isinstance(config.paths, list)


def test_get_effective_config_default_path():
    """Test that default path ['.'] is used when no paths provided"""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch('pathlib.Path.cwd', return_value=Path(tmpdir)):
            config = get_effective_config(
                cli_paths=None,
                cli_include=None,
                cli_output=None,
                cli_recent=False
            )

            assert config.paths == ["."]


def test_contextr_config_from_toml():
    """Test ContextrConfig.from_toml class method"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create config file
        config_path = Path(tmpdir) / ".contextr.toml"
        config_path.write_text("""
[Flags]
paths = ["/test/path"]
include = "*.js"
output = "output.md"
recent = true
""")

        config = ContextrConfig.from_toml(config_path)
        assert config.paths == ["/test/path"]
        assert config.include == "*.js"
        assert config.output == "output.md"
        assert config.recent is True


def test_contextr_config_merge_with_cli():
    """Test ContextrConfig.merge_with_cli method"""
    # Create base config
    base_config = ContextrConfig(
        paths=["/base/path"],
        include="*.py",
        output="base.txt",
        recent=False
    )
    
    # Merge with CLI args
    merged_config = base_config.merge_with_cli(
        cli_paths=["/cli/path"],
        cli_include="*.md",
        cli_output=None,  # Should keep base config value
        cli_recent=True
    )
    
    assert merged_config.paths == ["/cli/path"]  # CLI overrides
    assert merged_config.include == "*.md"      # CLI overrides
    assert merged_config.output == "base.txt"   # Base config preserved
    assert merged_config.recent is True         # CLI overrides


if __name__ == "__main__":
    # Run all tests
    test_contextr_config_from_toml_file_not_found()
    test_contextr_config_from_toml_valid_file()
    test_contextr_config_from_toml_invalid_syntax()
    test_get_effective_config_cli_takes_precedence()
    test_get_effective_config_uses_config_defaults()
    test_get_effective_config_normalizes_string_path()
    test_get_effective_config_default_path()
    test_contextr_config_from_toml()
    test_contextr_config_merge_with_cli()
    print("✅ All tests passed!")
