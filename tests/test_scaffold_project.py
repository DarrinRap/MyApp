import os
import subprocess
import pytest
from setup_project import scaffold_project

# Stub out any subprocess calls (e.g. git init)
def _noop(*args, **kwargs):
    return None

@pytest.fixture(autouse=True)
def no_subprocess(monkeypatch):
    monkeypatch.setattr(subprocess, 'check_call', _noop)
    yield

@pytest.mark.parametrize('flags, expected', [
    (
        # minimal scaffold
        dict(use_git=False, include_tests=False, include_ci=False,
             include_docs=False, include_precommit=False,
             include_editorconfig=False, use_src=False),
        ['main.py', 'README.md', '.gitignore', 'requirements.txt']
    ),
    (
        # full scaffold
        dict(use_git=False, include_tests=True, include_ci=True,
             include_docs=True, include_precommit=True,
             include_editorconfig=True, use_src=True),
        ['main.py', 'README.md', '.gitignore', 'requirements.txt',
         'tests/test_sample.py', 'docs/index.md',
         '.pre-commit-config.yaml', '.editorconfig',
         '.github/workflows/ci.yml', 'LICENSE']
    ),
])
def test_scaffold_creates_files(tmp_path, flags, expected):
    args = {
        'project_name': 'Proj',
        'description': 'Desc',
        'author': 'Tester',
        'license_type': 'MIT' if 'LICENSE' in expected else 'None',
        'gui_lib': 'tkinter',
        **flags,
        'output_dir': str(tmp_path)
    }
    proj_dir = scaffold_project(**args)
    assert os.path.isdir(proj_dir)
    for rel in expected:
        assert os.path.exists(os.path.join(proj_dir, rel)), f"Missing {rel}"
    # Verify src/ vs package dir
    if flags['use_src']:
        assert os.path.isdir(os.path.join(proj_dir, 'src'))
    else:
        assert os.path.isdir(os.path.join(proj_dir, 'Proj'))
