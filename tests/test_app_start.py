import os
import sys
import pytest

# Ensure project root is on sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import ScaffoldApp

@pytest.fixture(autouse=True)
def no_gui_display(monkeypatch):
    # Prevent actual window from opening in CI
    monkeypatch.setenv('DISPLAY', ':0')
    yield

def test_app_starts_and_stops():
    """ScaffoldApp should initialize and be destroyable without errors."""
    app = ScaffoldApp()
    app.destroy()
