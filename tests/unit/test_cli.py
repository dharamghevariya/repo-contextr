from unittest.mock import Mock, patch

from typer.testing import CliRunner

from contextr.cli import app


class TestCLI:
    """Test the CLI application."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    def test_version_flag(self):
        """Test --version flag displays version and exits."""
        result = self.runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "contextr version" in result.stdout

    def test_version_short_flag(self):
        """Test -v flag displays version and exits."""
        result = self.runner.invoke(app, ["-v"])
        assert result.exit_code == 0
        assert "contextr version" in result.stdout

    def test_help_flag(self):
        """Test --help flag displays help."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.stdout

    def test_help_short_flag(self):
        """Test -h flag displays help."""
        result = self.runner.invoke(app, ["-h"])
        assert result.exit_code == 0
        assert "Usage:" in result.stdout

    @patch("contextr.cli.package_repository")
    @patch("contextr.cli.get_effective_config")
    def test_basic_execution(self, mock_config, mock_package):
        """Test basic CLI execution without errors."""
        # Mock configuration
        mock_config_obj = Mock()
        mock_config_obj.paths = ["."]
        mock_config_obj.include = None
        mock_config_obj.recent = False
        mock_config_obj.output = None
        mock_config.return_value = mock_config_obj

        # Mock package_repository to return simple result
        mock_package.return_value = "# Test Output"

        result = self.runner.invoke(app, ["."])
        assert result.exit_code == 0
        assert mock_package.called

    @patch("contextr.cli.package_repository")
    @patch("contextr.cli.get_effective_config")
    def test_output_to_file(self, mock_config, mock_package, temp_dir):
        """Test CLI output to file."""
        output_file = temp_dir / "output.txt"

        # Mock configuration
        mock_config_obj = Mock()
        mock_config_obj.paths = ["."]
        mock_config_obj.include = None
        mock_config_obj.recent = False
        mock_config_obj.output = str(output_file)
        mock_config.return_value = mock_config_obj

        # Mock package_repository
        mock_package.return_value = "# Test Output"

        result = self.runner.invoke(app, [".", "-o", str(output_file)])
        assert result.exit_code == 0
        assert "Context packaged and saved" in result.stdout

    @patch("contextr.cli.package_repository")
    @patch("contextr.cli.get_effective_config")
    def test_package_repository_exception(self, mock_config, mock_package):
        """Test handling of package_repository exceptions."""
        # Mock configuration
        mock_config_obj = Mock()
        mock_config_obj.paths = ["."]
        mock_config_obj.include = None
        mock_config_obj.recent = False
        mock_config_obj.output = None
        mock_config.return_value = mock_config_obj

        # Mock package_repository to raise exception
        mock_package.side_effect = Exception("Test error")

        result = self.runner.invoke(app, ["."])
        assert result.exit_code == 1
        assert "Error:" in result.stdout

    @patch("contextr.cli.package_repository")
    @patch("contextr.cli.get_effective_config")
    def test_file_write_error(self, mock_config, mock_package, temp_dir):
        """Test handling of file write errors."""
        # Use a directory as output file to cause write error
        output_dir = temp_dir / "subdir"
        output_dir.mkdir()

        # Mock configuration
        mock_config_obj = Mock()
        mock_config_obj.paths = ["."]
        mock_config_obj.include = None
        mock_config_obj.recent = False
        mock_config_obj.output = str(output_dir)  # This will cause write error
        mock_config.return_value = mock_config_obj

        # Mock package_repository
        mock_package.return_value = "# Test Output"

        result = self.runner.invoke(app, [".", "-o", str(output_dir)])
        assert result.exit_code == 0
        assert "Error writing to file" in result.stdout

    @patch("contextr.cli.get_effective_config")
    def test_cli_flags_passed_to_config(self, mock_config):
        """Test that CLI flags are passed to get_effective_config."""
        mock_config_obj = Mock()
        mock_config_obj.paths = ["."]
        mock_config_obj.include = "*.py"
        mock_config_obj.recent = True
        mock_config_obj.output = "output.txt"
        mock_config.return_value = mock_config_obj

        with patch("contextr.cli.package_repository", return_value="test"):
            self.runner.invoke(
                app, [".", "--include", "*.py", "--recent", "-o", "output.txt"]
            )

            # Verify get_effective_config was called with correct arguments
            mock_config.assert_called_once_with(
                cli_paths=["."],
                cli_include="*.py",
                cli_output="output.txt",
                cli_recent=True,
            )
