import os
import pytest

from setup_project import scaffold_project


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


@pytest.fixture
def tmp_project(tmp_path):
    """Provides an empty temporary directory."""
    return tmp_path


def test_minimal_scaffold(tmp_project):
    """
    Minimal scaffold: all optional features off, no src layout.
    """
    project_dir = scaffold_project(
        project_name="DemoApp",
        description="A minimal demo app",
        author="TestUser",
        license_type="None",
        gui_lib="tkinter",
        use_git=False,
        include_tests=False,
        include_ci=False,
        include_docs=False,
        include_precommit=False,
        include_editorconfig=False,
        use_src=False,
        output_dir=str(tmp_project)
    )

    # The project directory should exist
    assert os.path.isdir(project_dir)

    # No nested DemoApp folder inside project_dir
    assert not os.path.isdir(os.path.join(project_dir, "DemoApp"))

    # main.py stub is present
    assert os.path.isfile(os.path.join(project_dir, "main.py"))

    # README.md contains description and author
    readme = read(os.path.join(project_dir, "README.md"))
    assert "A minimal demo app" in readme
    assert "TestUser" in readme

    # No tests/ folder created
    assert not os.path.exists(os.path.join(project_dir, "tests"))


def test_full_scaffold(tmp_project):
    """
    Full scaffold: all optional features on, with src layout.
    """
    project_dir = scaffold_project(
        project_name="FullApp",
        description="A full-featured app",
        author="Tester",
        license_type="MIT",
        gui_lib="pyqt6",
        use_git=False,
        include_tests=True,
        include_ci=True,
        include_docs=True,
        include_precommit=True,
        include_editorconfig=True,
        use_src=True,
        output_dir=str(tmp_project)
    )

    # src directory should exist
    src_dir = os.path.join(project_dir, "src")
    assert os.path.isdir(src_dir)

    # tests/ directory and sample test file
    tests_dir = os.path.join(project_dir, "tests")
    assert os.path.isdir(tests_dir)
    assert os.path.isfile(os.path.join(tests_dir, "test_sample.py"))

    # docs/index.md should exist with correct header
    docs_index = os.path.join(project_dir, "docs", "index.md")
    assert os.path.isfile(docs_index)
    assert "# FullApp Documentation" in read(docs_index)

    # CI workflow file exists and references pytest
    ci_file = os.path.join(project_dir, ".github", "workflows", "ci.yml")
    assert os.path.isfile(ci_file)
    assert "pytest" in read(ci_file)

    # LICENSE file contains MIT license text
    license_text = read(os.path.join(project_dir, "LICENSE"))
    assert "MIT License" in license_text
    assert "Copyright" in license_text

    # pre-commit and editorconfig files
    assert os.path.isfile(os.path.join(project_dir, ".pre-commit-config.yaml"))
    assert os.path.isfile(os.path.join(project_dir, ".editorconfig"))

    # main.py stub uses PyQt6 import path
    main_py = read(os.path.join(project_dir, "main.py"))
    assert "from PyQt6.QtWidgets" in main_py.lower() or "from pyqt6" in main_py.lower()
