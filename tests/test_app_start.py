import os
import sys

# Make sure the project root (where main.py lives) is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from main import ScaffoldApp

@pytest.fixture(autouse=True)
def no_gui_display(monkeypatch):
    # Prevent actual window pops in CI
    monkeypatch.setenv('DISPLAY', ':0')
    yield

def test_app_starts_and_stops():
    """ScaffoldApp should initialize and be destroyable without errors."""
    app = ScaffoldApp()
    app.destroy()
