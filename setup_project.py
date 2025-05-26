#!/usr/bin/env python3
import os
import subprocess
import sys

def ask(prompt, default):
    resp = input(f"{prompt} [{default}]: ").strip()
    return resp or default

def run(cmd, **kwargs):
    print(f"> {' '.join(cmd)}")
    subprocess.check_call(cmd, **kwargs)

def main():
    print("🛠️  Python Windows Desktop App Scaffolder 🛠️\n")

    project_name = ask("Project name", "MyApp")
    gui_lib      = ask("GUI toolkit (tkinter / pyqt5)", "tkinter").lower()
    use_git      = ask("Initialize a git repo? (y/n)", "y").lower().startswith("y")

    os.makedirs(project_name, exist_ok=True)
    os.chdir(project_name)

    run([sys.executable, "-m", "venv", "venv"])

    if os.name == 'nt':
        activate = os.path.join("venv", "Scripts", "activate")
    else:
        activate = os.path.join("venv", "bin", "activate")
    print(f"\n▶ To activate, run: {activate}")

    with open("requirements.txt", "w") as f:
        libs = []
        if gui_lib == "pyqt5":
            libs.append("PyQt5")
        f.write("\n".join(libs))

    starter = """\
import sys
{import_line}

def main():
    app = {app_init}
    {show_window}
    sys.exit(app.exec_() if hasattr(app, 'exec_') else 0)

if __name__ == '__main__':
    main()
"""
    if gui_lib == "pyqt5":
        import_line = "from PyQt5.QtWidgets import QApplication, QLabel"
        app_init    = "QApplication(sys.argv)"
        show_window = "win = QLabel('Hello, PyQt5!')\n    win.show()"
    else:
        import_line = "import tkinter as tk"
        app_init    = "tk.Tk()"
        show_window = "app.title('Hello, Tkinter!')\n    app.geometry('300x100')\n    tk.Label(app, text='Hello, Tkinter!').pack(pady=20)\n    app.mainloop()"

    with open("main.py", "w") as f:
        f.write(starter.format(import_line=import_line,
                               app_init=app_init,
                               show_window=show_window))

    with open(".gitignore", "w") as f:
        f.write("venv/\n__pycache__/\n*.pyc\n")

    if use_git:
        run(["git", "init"])
        run(["git", "add", "."])
        run(["git", "commit", "-m", "Initial commit"])

    print(f"\n✅ Project '{project_name}' is ready!  ")
    print("  • `cd {0}`".format(project_name))
    print("  • Activate your venv")
    print("  • `pip install -r requirements.txt`")
    print("  • `python main.py` to launch your app")

if __name__ == "__main__":
    main()
