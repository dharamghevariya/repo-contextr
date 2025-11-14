from contextr.output.tree_formatter import _format_tree, generate_tree_structure


class TestGenerateTreeStructure:
    """Tests for generate_tree_structure function."""

    def test_basic_structures(self, temp_dir):
        """Test basic tree structures: single file, directory, and multiple files."""
        # Single file
        file1 = temp_dir / "test3.py"
        file1.write_text("content", encoding="utf-8")
        result = generate_tree_structure([file1], temp_dir)
        assert isinstance(result, str)
        assert "test.py" in result

        # Single directory with file
        subdir = temp_dir / "src"
        subdir.mkdir()
        file2 = subdir / "main.py"
        file2.write_text("content", encoding="utf-8")
        result = generate_tree_structure([file2], temp_dir)
        assert "src/" in result
        assert "main.py" in result

        # Multiple files in root
        file3 = temp_dir / "file1.py"
        file4 = temp_dir / "file2.py"
        file3.write_text("content", encoding="utf-8")
        file4.write_text("content", encoding="utf-8")
        result = generate_tree_structure([file1, file3, file4], temp_dir)
        assert all(f in result for f in ["test.py", "file1.py", "file2.py"])

    def test_nested_and_deep_directories(self, temp_dir):
        """Test nested and deeply nested directory structures."""
        # Nested directories
        nested_dir = temp_dir / "src" / "utils" / "helpers"
        nested_dir.mkdir(parents=True)
        file1 = nested_dir / "helper.py"
        file1.write_text("content", encoding="utf-8")
        result = generate_tree_structure([file1], temp_dir)
        assert all(d in result for d in ["src/", "utils/", "helpers/", "helper.py"])

        # Deeply nested (5+ levels)
        deep_dir = temp_dir / "a" / "b" / "c" / "d" / "e"
        deep_dir.mkdir(parents=True)
        deep_file = deep_dir / "deep.py"
        deep_file.write_text("content", encoding="utf-8")
        result = generate_tree_structure([deep_file], temp_dir)
        assert all(d in result for d in ["a/", "b/", "c/", "d/", "e/", "deep.py"])

    def test_formatting_and_display_rules(self, temp_dir):
        """Test tree formatting characters, directory slashes, and empty lists."""
        # Empty file list
        result = generate_tree_structure([], temp_dir)
        assert isinstance(result, str)
        assert result == ""

        # Tree characters
        subdir = temp_dir / "src"
        subdir.mkdir()
        file1 = subdir / "file1.py"
        file2 = subdir / "file2.py"
        file1.write_text("content", encoding="utf-8")
        file2.write_text("content", encoding="utf-8")
        result = generate_tree_structure([file1, file2], temp_dir)
        assert "├──" in result or "└──" in result
        assert "src/" in result  # Directories have trailing slash

    def test_sorting_and_filtering(self, temp_dir):
        """Test file sorting and filtering of files outside root."""
        # Files outside root are skipped
        other_dir = temp_dir.parent / "other"
        other_dir.mkdir(exist_ok=True)
        outside_file = other_dir / "outside.py"
        outside_file.write_text("content", encoding="utf-8")
        inside_file = temp_dir / "inside.py"
        inside_file.write_text("content", encoding="utf-8")
        result = generate_tree_structure([outside_file, inside_file], temp_dir)
        assert "inside.py" in result
        assert "outside.py" not in result
        outside_file.unlink()
        other_dir.rmdir()

        # Files are sorted alphabetically
        file_c = temp_dir / "c_file.py"
        file_a = temp_dir / "a_file.py"
        file_b = temp_dir / "b_file.py"
        for f in [file_c, file_a, file_b]:
            f.write_text("content", encoding="utf-8")
        result = generate_tree_structure([file_c, file_a, file_b], temp_dir)
        pos_a, pos_b, pos_c = (
            result.find("a_file.py"),
            result.find("b_file.py"),
            result.find("c_file.py"),
        )
        assert pos_a < pos_b < pos_c

    def test_complex_realistic_structures(self, temp_dir):
        """Test complex realistic project structures with mixed files and directories."""
        files = []

        # Root files
        readme = temp_dir / "README.md"
        readme.write_text("content", encoding="utf-8")
        files.append(readme)

        # src directory with nested structure
        src = temp_dir / "src"
        src.mkdir()
        main = src / "main.py"
        main.write_text("content", encoding="utf-8")
        files.append(main)

        # src/utils directory
        utils = src / "utils"
        utils.mkdir()
        helper = utils / "helper.py"
        helper.write_text("content", encoding="utf-8")
        files.append(helper)

        # tests directory
        tests = temp_dir / "tests"
        tests.mkdir()
        test_file = tests / "test_main.py"
        test_file.write_text("content", encoding="utf-8")
        files.append(test_file)

        result = generate_tree_structure(files, temp_dir)

        # Verify all components are present
        expected = [
            "README.md",
            "src/",
            "main.py",
            "utils/",
            "helper.py",
            "tests/",
            "test_main.py",
        ]
        assert all(item in result for item in expected)


class TestFormatTree:
    """Tests for _format_tree function (internal helper)."""

    def test_basic_tree_structures(self):
        """Test basic tree structures: empty, single file, single directory, multiple items."""
        # Empty tree
        assert _format_tree({}) == ""

        # Single file
        result = _format_tree({"file.py": None})
        assert "file.py" in result and "└──" in result

        # Single directory with file
        result = _format_tree({"src": {"main.py": None}})
        assert "src/" in result and "main.py" in result

        # Multiple files
        tree = {"file1.py": None, "file2.py": None, "file3.py": None}
        result = _format_tree(tree)
        assert all(f in result for f in ["file1.py", "file2.py", "file3.py"])

        # Multiple directories
        tree = {"src": {"main.py": None}, "tests": {"test.py": None}}
        result = _format_tree(tree)
        assert all(item in result for item in ["src/", "tests/", "main.py", "test.py"])

    def test_nested_structures(self):
        """Test nested and deeply nested directory structures."""
        # Simple nesting
        tree = {"src": {"utils": {"helper.py": None}}}
        result = _format_tree(tree)
        assert all(item in result for item in ["src/", "utils/", "helper.py"])

        # Deep nesting
        tree = {"a": {"b": {"c": {"d": {"e": {"deep.py": None}}}}}}
        result = _format_tree(tree)
        assert all(item in result for item in ["a/", "b/", "c/", "d/", "e/", "deep.py"])

    def test_formatting_characters_and_sorting(self):
        """Test tree characters, indentation, and sorting rules."""
        # Tree characters for last and middle items
        tree = {"file1.py": None, "file2.py": None, "file3.py": None}
        result = _format_tree(tree)
        assert "├──" in result and "└──" in result

        # Nested indentation
        tree = {"src": {"utils": {"helper.py": None}}}
        result = _format_tree(tree)
        assert len(result.split("\n")) >= 3

        # Sorting behavior: files come before directories, each sorted alphabetically within type
        tree = {"zfile.py": None, "adir": {"nested.py": None}, "bfile.py": None}
        result = _format_tree(tree)
        # Expected order: files first (bfile.py, zfile.py), then directories (adir/)
        assert result.index("bfile.py") < result.index("adir/")
        assert result.index("zfile.py") < result.index("adir/")
        assert result.index("bfile.py") < result.index(
            "zfile.py"
        )  # Files are alphabetically sorted

        # Alphabetical sorting within type
        tree = {"zebra.py": None, "alpha.py": None, "beta.py": None}
        result = _format_tree(tree)
        pos_alpha, pos_beta, pos_zebra = (
            result.find("alpha.py"),
            result.find("beta.py"),
            result.find("zebra.py"),
        )
        assert pos_alpha < pos_beta < pos_zebra

    def test_complex_and_mixed_structures(self):
        """Test complex realistic trees, prefix parameter, and mixed nesting."""
        # Complex realistic tree
        tree = {
            "README.md": None,
            "src": {"main.py": None, "utils": {"helper.py": None, "tools.py": None}},
            "tests": {"test_main.py": None},
            "LICENSE": None,
        }
        result = _format_tree(tree)
        expected = [
            "README.md",
            "src/",
            "main.py",
            "utils/",
            "helper.py",
            "tools.py",
            "tests/",
            "test_main.py",
            "LICENSE",
        ]
        assert all(item in result for item in expected)

        # Prefix parameter affects indentation
        tree = {"file.py": None}
        result_no_prefix = _format_tree(tree, prefix="")
        result_with_prefix = _format_tree(tree, prefix="    ")
        assert len(result_with_prefix) > len(result_no_prefix)

        # Mixed nested and root files
        tree = {
            "root.py": None,
            "dir1": {"nested1.py": None, "subdir": {"deep.py": None}},
            "root2.py": None,
        }
        result = _format_tree(tree)
        assert all(
            item in result
            for item in [
                "root.py",
                "dir1/",
                "nested1.py",
                "subdir/",
                "deep.py",
                "root2.py",
            ]
        )

    def test_file_handling_rules(self):
        """Test that None values are files (no slash) and directories have slashes."""
        tree = {"file.py": None, "dir": {"nested.py": None}}
        result = _format_tree(tree)

        assert isinstance(result, str)
        assert "file.py" in result
        assert "file.py/" not in result  # Files don't have trailing slash
        assert "dir/" in result  # Directories have trailing slash


class TestTreeFormatterEdgeCases:
    """Edge cases and boundary conditions for tree formatter."""

    def test_special_filenames(self, temp_dir):
        """Test files with special characters, no extensions, and hidden files."""
        # Special characters
        files = [
            temp_dir / "file-with-dash.py",
            temp_dir / "file_with_underscore.py",
            temp_dir / "file.with.dots.py",
            temp_dir / "README",  # No extension
            temp_dir / "LICENSE",
            temp_dir / "Makefile",
        ]
        for f in files:
            f.write_text("content", encoding="utf-8")
        result = generate_tree_structure(files, temp_dir)
        expected = [
            "file-with-dash.py",
            "file_with_underscore.py",
            "file.with.dots.py",
            "README",
            "LICENSE",
            "Makefile",
        ]
        assert all(name in result for name in expected)

        # Hidden files and directories
        hidden_file = temp_dir / ".gitignore"
        hidden_dir = temp_dir / ".github"
        hidden_dir.mkdir()
        workflows = hidden_dir / "workflows"
        workflows.mkdir()
        workflow_file = workflows / "ci.yml"
        hidden_file.write_text("content", encoding="utf-8")
        workflow_file.write_text("content", encoding="utf-8")
        result = generate_tree_structure([hidden_file, workflow_file], temp_dir)
        assert all(
            item in result
            for item in [".gitignore", ".github/", "workflows/", "ci.yml"]
        )

    def test_large_and_duplicate_structures(self, temp_dir):
        """Test many files in directory, duplicate directory names, and Unicode filenames."""
        # Many files (25+)
        subdir = temp_dir / "src"
        subdir.mkdir()
        files = []
        for i in range(25):
            file = subdir / f"file{i:02d}.py"
            file.write_text("content", encoding="utf-8")
            files.append(file)
        result = generate_tree_structure(files, temp_dir)
        assert all(f"file{i:02d}.py" in result for i in range(25))

        # Same directory name at different levels
        utils1 = temp_dir / "src" / "utils"
        utils1.mkdir(parents=True)
        file1 = utils1 / "helper.py"
        file1.write_text("content", encoding="utf-8")
        utils2 = temp_dir / "tests" / "utils"
        utils2.mkdir(parents=True)
        file2 = utils2 / "test_helper.py"
        file2.write_text("content", encoding="utf-8")
        result = generate_tree_structure([file1, file2], temp_dir)
        assert "src/" in result and "tests/" in result
        assert result.count("utils/") == 2
        assert "helper.py" in result and "test_helper.py" in result

        # Unicode filenames
        unicode_files = [
            temp_dir / "文件.py",
            temp_dir / "файл.py",
            temp_dir / "αρχείο.py",
        ]
        for f in unicode_files:
            f.write_text("content", encoding="utf-8")
        result = generate_tree_structure(unicode_files, temp_dir)
        assert all(f.name in result for f in unicode_files)
