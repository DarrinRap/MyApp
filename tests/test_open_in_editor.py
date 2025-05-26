import pytest
import tkinter.messagebox as messagebox
from main import ScaffoldApp

@pytest.fixture(autouse=True)
def prevent_display(monkeypatch):
    # Prevent actual window display
    monkeypatch.setenv('DISPLAY', ':0')
    yield

def test_open_in_editor_without_project(monkeypatch):
    # Capture showwarning calls
    calls = []
    monkeypatch.setattr(messagebox, 'showwarning',
                        lambda title, msg: calls.append((title, msg)))

    app = ScaffoldApp()
    app.last_path = None
    app._log = lambda msg: None  # Silence logs

    app._open_in_editor()

    assert calls == [("No Project", "Please scaffold a project first.")], \
        f"Expected one warning call, got {calls}"
    app.destroy()
