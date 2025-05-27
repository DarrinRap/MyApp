import os
import subprocess
import pytest


def find_executable():
    """
    Locate the first .exe in the dist/ directory under project root.
    """
    # project root is two levels up from this test file
    project_root = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            os.pardir,
            os.pardir
        )
    )
    dist_dir = os.path.join(project_root, 'dist')
    assert os.path.isdir(dist_dir), f"dist/ directory not found at {dist_dir}"
    exes = [f for f in os.listdir(dist_dir) if f.lower().endswith('.exe')]
    assert exes, f"No .exe files found in {dist_dir}"
    # Return full path to the first executable found
    return os.path.join(dist_dir, exes[0])


def test_executable_launch():
    """
    Test that the packaged executable launches without crashing.
    - If the process stays running for at least 2 seconds, we consider it a success and terminate it.
    - If it exits quickly, the exit code must be zero.
    """
    exe_path = find_executable()

    proc = subprocess.Popen([exe_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        # Wait up to 2 seconds for process to exit
        proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        # Process is still running: good sign. Terminate cleanly.
        proc.terminate()
        proc.wait(timeout=5)
    else:
        # Process exited quickly: ensure it exited cleanly
        stdout, stderr = proc.communicate()
        assert proc.returncode == 0, (
            f"Executable exited with return code {proc.returncode}\n"
            f"stdout: {stdout.decode(errors='ignore')}\n"
            f"stderr: {stderr.decode(errors='ignore')}"
        )
