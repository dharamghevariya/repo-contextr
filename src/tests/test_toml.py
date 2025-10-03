import tempfile
from pathlib import Path
from unittest.mock import patch
from contextr.cli import load_toml_config, merge_cli_with_config


def test_load_toml_config_file_not_found():
    """Test that empty dict is returned when no config file exists"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Mock the cwd function to return the temporary directory
        with patch('pathlib.Path.cwd', return_value=Path(tmpdir)):
            config = load_toml_config()
            assert config == {}


def test_load_toml_config_valid_file():
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
            config = load_toml_config()
            assert config == {
                "Flags": {
                    "include": "*.py",
                    "output": "test.txt",
                    "recent": True
                }
            }


def test_load_toml_config_invalid_syntax():
    """Test that invalid TOML syntax raises SystemExit"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create invalid TOML file
        config_path = Path(tmpdir) / ".contextr.toml"
        config_path.write_text("invalid toml [[[")

        with patch('pathlib.Path.cwd', return_value=Path(tmpdir)):
            try:
                load_toml_config()
                # typer.Exit(1) is a type of SystemExit 
                assert False, "Expected SystemExit to be raised"
            except SystemExit:
                # This is expected behavior
                pass


def test_merge_cli_with_config_cli_takes_precedence():
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
            paths, include, output, recent, version = merge_cli_with_config(
                paths=["/cli/path"],
                include="*.md",
                output="cli.txt",
                recent=True,
                version=False
            )

            assert paths == ["/cli/path"]
            assert include == "*.md"
            assert output == "cli.txt"
            assert recent is True


def test_merge_cli_with_config_uses_config_defaults():
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
            paths, include, output, recent, version = merge_cli_with_config(
                paths=None,
                include=None,
                output=None,
                recent=False,
                version=False
            )

            assert paths == ["/config/path"]
            assert include == "*.py"
            assert output == "config.txt"
            assert recent is True


def test_merge_cli_with_config_normalizes_string_path():
    """Test that string paths are normalized to lists"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test.contextr.toml"
        config_path.write_text("""
[Flags]
paths = "/single/path"
""")

        with patch('pathlib.Path.cwd', return_value=Path(tmpdir)):
            paths, _, _, _, _ = merge_cli_with_config(
                paths=None,
                include=None,
                output=None,
                recent=False,
                version=False
            )

            assert paths == ["/single/path"]
            assert isinstance(paths, list)


def test_merge_cli_with_config_default_path():
    """Test that default path ['.'] is used when no paths provided"""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch('pathlib.Path.cwd', return_value=Path(tmpdir)):
            paths, _, _, _, _ = merge_cli_with_config(
                paths=None,
                include=None,
                output=None,
                recent=False,
                version=False
            )

            assert paths == ["."]


if __name__ == "__main__":
    # Run all tests
    test_load_toml_config_file_not_found()
    test_load_toml_config_valid_file()
    test_load_toml_config_invalid_syntax()
    test_merge_cli_with_config_cli_takes_precedence()
    test_merge_cli_with_config_uses_config_defaults()
    test_merge_cli_with_config_normalizes_string_path()
    test_merge_cli_with_config_default_path()
    print("✅ All tests passed!")
