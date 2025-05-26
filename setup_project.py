#!/usr/bin/env python3
import os
import subprocess
import sys
from datetime import datetime

"""
Module: setup_project.py
Provides a `scaffold_project()` function to programmatically generate new Python
desktop-app projects, plus a CLI entry point for interactive use.
"""

def run(cmd, cwd=None):
    """Run a shell command and print it."""
    print(f"> {' '.join(cmd)}")
    subprocess.check_call(cmd, cwd=cwd)

def get_mit_license(author: str, year: int) -> str:
    """Return the text of an MIT license."""
    return f"""MIT License

Copyright (c) {year} {author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

def scaffold_project(
    project_name: str,
    description: str,
    author: str,
    license_type: str,
    gui_lib: str,
    use_git: bool,
    include_tests: bool,
    include_ci: bool,
    include_docs: bool,
    include_precommit: bool,
    include_editorconfig: bool,
    use_src: bool,
    output_dir: str = None
) -> str:
    """
    Generate a new Python desktop-app project with the given options.
    Returns the absolute path of the created project.
    """
    # 1) change to output dir if given
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        os.chdir(output_dir)
    # 2) create project folder if not '.'
    if project_name != '.':
        os.makedirs(project_name, exist_ok=True)
        os.chdir(project_name)
    project_dir = os.getcwd()

    # 3) create virtualenv
    run([sys.executable, '-m', 'venv', 'venv'])

    # 4) write README.md
    with open('README.md', 'w') as f:
        f.write(f"# {project_name}\n\n{description}\n")

    # 5) write LICENSE if MIT
    if license_type.upper() == 'MIT' and author:
        year = datetime.now().year
        with open('LICENSE', 'w') as f:
            f.write(get_mit_license(author, year))

    # 6) set up source package
    pkg_name = project_name.lower().replace(' ', '_')
    src_root = 'src' if use_src else '.'
    os.makedirs(os.path.join(src_root, pkg_name), exist_ok=True)
    open(os.path.join(src_root, pkg_name, '__init__.py'), 'w').close()

    # 7) optional docs
    if include_docs:
        os.makedirs('docs', exist_ok=True)
        with open(os.path.join('docs', 'index.md'), 'w') as f:
            f.write(f"# Documentation for {project_name}\n")

    # 8) write starter main.py
    if gui_lib.lower() == 'pyqt5':
        main_code = f"""import sys
from PyQt5.QtWidgets import QApplication, QLabel

def main():
    app = QApplication(sys.argv)
    win = QLabel('Hello, PyQt5!')
    win.setWindowTitle('{project_name}')
    win.resize(400, 250)
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()"""
    else:
        main_code = f"""import tkinter as tk
from tkinter import messagebox

def main():
    app = tk.Tk()
    app.title('{project_name}')
    app.geometry('450x280')
    tk.Label(app, text='📦 {project_name}', font=('Helvetica',16,'bold')).pack(pady=10)
    tk.Button(app, text='What does this do?',
              command=lambda: messagebox.showinfo('Scaffolder','This will scaffold a new project!')).pack(pady=5)
    tk.Entry(app, width=35, font=('Helvetica',12)).pack(pady=10)
    tk.Button(app, text='Scaffold!', command=lambda: messagebox.showinfo('Info','Replace with scaffolder call')).pack(pady=5)
    tk.Label(app, text='Designed by Darrin A. Rapoport',
             font=('Helvetica',8,'italic'), fg='gray').pack(side='bottom', pady=10)
    app.mainloop()

if __name__ == '__main__':
    main()"""

    with open('main.py', 'w') as f:
        f.write(main_code)

    # 9) optional tests
    if include_tests:
        os.makedirs('tests', exist_ok=True)
        with open(os.path.join('tests','test_placeholder.py'),'w') as f:
            f.write(f"import {pkg_name}\n\ndef test_placeholder():\n    assert True\n")

    # 10) requirements.txt
    reqs = []
    if gui_lib.lower() == 'pyqt5': reqs.append('PyQt5')
    if include_tests:     reqs.append('pytest')
    if include_precommit:  reqs.append('pre-commit')
    with open('requirements.txt','w') as f:
        f.write('\n'.join(reqs))

    # 11) .gitignore
    with open('.gitignore','w') as f:
        f.write("venv/\n__pycache__/\n*.pyc\n.venv*\n")

    # 12) .editorconfig
    if include_editorconfig:
        with open('.editorconfig','w') as f:
            f.write("""root = true
[*]
indent_style = space
indent_size = 4
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true
""")

    # 13) pre-commit config
    if include_precommit:
        with open('.pre-commit-config.yaml','w') as f:
            f.write("""repos:
- repo: https://github.com/psf/black
  rev: stable
  hooks:
  - id: black
""")

    # 14) CI workflow
    if include_ci:
        os.makedirs('.github/workflows', exist_ok=True)
        with open('.github/workflows/ci.yml','w') as f:
            f.write("""name: CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install
        run: pip install -r requirements.txt
      - name: Test
        run: pytest
""")

    # 15) initialize Git
    if use_git:
        run(['git','init'])
        run(['git','add','.'])
        run(['git','commit','-m','Initial scaffold'])

    print(f"Project created at: {project_dir}")
    return project_dir

def ask(prompt, default):
    resp = input(f"{prompt} [{default}]: ").strip()
    return resp or default

def main():
    # CLI entry point
    print("🛠️ Full-Featured Python Project Scaffolder 🛠️\n")
    name       = ask("Project name",       "MyApp")
    desc       = ask("Description",        "A Python desktop application.")
    auth       = ask("Author",             "Darrin A. Rapoport")
    lic        = ask("License (MIT/None)", "MIT")
    gui        = ask("GUI toolkit (tkinter/pyqt5)", "tkinter").lower()
    git_flag   = ask("Initialize a git repo? (y/n)", "y").lower().startswith('y')
    tests_flag = ask("Include pytest tests? (y/n)", "y").lower().startswith('y')
    ci_flag    = ask("Add GitHub Actions CI? (y/n)", "y").lower().startswith('y')
    docs_flag  = ask("Include docs folder? (y/n)", "n").lower().startswith('y')
    pre_flag   = ask("Include pre-commit config? (y/n)", "n").lower().startswith('y')
    ec_flag    = ask("Include .editorconfig? (y/n)", "n").lower().startswith('y')
    src_flag   = ask("Use src/ layout? (y/n)", "y").lower().startswith('y')
    scaffold_project(name, desc, auth, lic, gui, git_flag,
                     tests_flag, ci_flag, docs_flag,
                     pre_flag, ec_flag, src_flag)

if __name__ == '__main__':
    main()
