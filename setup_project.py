import os
import subprocess
import textwrap
import sys

def scaffold_project(
    project_name,
    description,
    author,
    license_type,
    gui_lib,
    use_git,
    include_tests,
    include_ci,
    include_docs,
    include_precommit,
    include_editorconfig,
    use_src,
    output_dir=None
):
    """
    Create a new Python project scaffold.
    Returns the path to the created project.
    """
    base_dir = output_dir or os.getcwd()
    project_dir = os.path.join(base_dir, project_name)
    os.makedirs(project_dir, exist_ok=True)
    # create a virtual environment automatically
    venv_dir = os.path.join(project_dir, 'venv')
    subprocess.check_call([sys.executable, '-m', 'venv', venv_dir])

    # 1. Create src/ layout or root package
    if use_src:
        pkg_dir = os.path.join(project_dir, 'src', project_name)
    else:
        pkg_dir = os.path.join(project_dir, project_name)
    os.makedirs(pkg_dir, exist_ok=True)
    open(os.path.join(pkg_dir, '__init__.py'), 'w').close()
    open(os.path.join(pkg_dir, '__init__.py'), 'w').close()

    # 2. Generate main.py stub
    main_path = os.path.join(project_dir, 'main.py')
    with open(main_path, 'w') as f:
        if gui_lib == 'tkinter':
            f.write(textwrap.dedent(f"""
                import tkinter as tk

                def main():
                    root = tk.Tk()
                    root.title("{project_name}")
                    label = tk.Label(root, text="Welcome to {project_name}!")
                    label.pack(padx=20, pady=20)
                    root.mainloop()

                if __name__ == '__main__':
                    main()
            """))
        elif gui_lib == 'pyqt5':
            f.write(textwrap.dedent(f"""
                from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
                import sys

                def main():
                    app = QApplication(sys.argv)
                    window = QWidget()
                    window.setWindowTitle("{project_name}")
                    layout = QVBoxLayout()
                    label = QLabel("Welcome to {project_name}!")
                    layout.addWidget(label)
                    window.setLayout(layout)
                    window.show()
                    sys.exit(app.exec_())

                if __name__ == '__main__':
                    main()
            """))
        else:  # pyqt6
            f.write(textwrap.dedent(f"""
                from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
                import sys

                def main():
                    app = QApplication(sys.argv)
                    window = QWidget()
                    window.setWindowTitle("{project_name}")
                    layout = QVBoxLayout()
                    label = QLabel("Welcome to {project_name}!")
                    layout.addWidget(label)
                    window.setLayout(layout)
                    window.show()
                    sys.exit(app.exec())

                if __name__ == '__main__':
                    main()
            """))

    # 3. Generate README.md
    readme_path = os.path.join(project_dir, 'README.md')
    with open(readme_path, 'w') as f:
        f.write(f"# {project_name}\n")
        f.write(f"{description}\n\n")
        f.write(f"Created by {author}\n\n")
        if include_ci:
            f.write(f"![CI](https://github.com/{author}/{project_name}/actions/workflows/ci.yml/badge.svg)\n\n")
        f.write("## Quick Start\n")
        f.write(textwrap.dedent(f"""
            ```bash
            cd {project_name}
            python -m venv venv
            # Windows: .\\venv\\Scripts\\activate
            source venv/bin/activate
            pip install -r requirements.txt
            python main.py
            ```
        """))

    # 4. Generate .gitignore
    gitignore_path = os.path.join(project_dir, '.gitignore')
    gitignore_contents = textwrap.dedent("""
        # Byte-compiled / optimized / DLL files
        __pycache__/
        *.py[cod]
        *$py.class

        # Virtual environment
        venv/

        # Distribution / packaging
        build/
        dist/
        *.egg-info/

        # IDE and OS files
        .vscode/
        .DS_Store
        Thumbs.db
    """
    )
    with open(gitignore_path, 'w') as f:
        f.write(gitignore_contents)

    # 5. Create requirements.txt stub
    reqs_path = os.path.join(project_dir, 'requirements.txt')
    with open(reqs_path, 'w') as f:
        f.write("# Add your project dependencies here\n")

    # 6. Optional: include pytest tests
    if include_tests:
        tests_dir = os.path.join(project_dir, 'tests')
        os.makedirs(tests_dir, exist_ok=True)
        test_file = os.path.join(tests_dir, 'test_sample.py')
        with open(test_file, 'w') as f:
            f.write(textwrap.dedent("""
                def test_placeholder():
                    assert True  # Replace with real tests
            """))

    # 7. Optional: include docs folder
    if include_docs:
        docs_dir = os.path.join(project_dir, 'docs')
        os.makedirs(docs_dir, exist_ok=True)
        with open(os.path.join(docs_dir, 'index.md'), 'w') as f:
            f.write(f"# {project_name} Documentation\n\nWrite your docs here.")

    # 8. Optional: include pre-commit config
    if include_precommit:
        precommit_path = os.path.join(project_dir, '.pre-commit-config.yaml')
        with open(precommit_path, 'w') as f:
            f.write(textwrap.dedent("""
                repos:
                - repo: https://github.com/psf/black
                  rev: stable
                  hooks:
                    - id: black
            """))

    # 9. Optional: include .editorconfig
    if include_editorconfig:
        editor_path = os.path.join(project_dir, '.editorconfig')
        with open(editor_path, 'w') as f:
            f.write(textwrap.dedent("""
                root = true

                [*]
                indent_style = space
                indent_size = 4
                end_of_line = lf
                charset = utf-8
                trim_trailing_whitespace = true
                insert_final_newline = true
            """))

    # 10. Optional: generate GitHub Actions workflow
    if include_ci:
        ci_dir = os.path.join(project_dir, '.github', 'workflows')
        os.makedirs(ci_dir, exist_ok=True)
        ci_path = os.path.join(ci_dir, 'ci.yml')
        with open(ci_path, 'w') as f:
            f.write(textwrap.dedent(f"""
                name: CI

                on:
                  push:
                    branches: [ main ]
                  pull_request:
                    branches: [ main ]

                jobs:
                  test:
                    runs-on: ubuntu-latest
                    steps:
                      - uses: actions/checkout@v3
                      - name: Set up Python
                        uses: actions/setup-python@v4
                        with:
                          python-version: '3.x'
                      - name: Install dependencies
                        run: |
                          python -m pip install --upgrade pip
                          pip install -r requirements.txt
                          pip install pytest
                      - name: Run tests
                        run: pytest --maxfail=1 --disable-warnings -q
            """))

    # 11. License file
    if license_type.upper() == 'MIT':
        year = str(subprocess.check_output(['date', '+%Y']).decode().strip()) if os.name != 'nt' else str(os.popen('echo %date:~-4%').read().strip())
        with open(os.path.join(project_dir, 'LICENSE'), 'w') as f:
            f.write(textwrap.dedent(f"""
                MIT License

                Copyright (c) {year} {author}

                Permission is hereby granted, free of charge, to any person obtaining a copy
                of this software and associated documentation files (the "Software"), to deal
                in the Software without restriction, including without limitation the rights
                to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
                copies of the Software, and to permit persons to whom the Software is
                furnished to do so, subject to the following conditions:

                THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
                IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
                FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
                AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
                LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
                OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
                SOFTWARE.
            """))

    # 12. Initialize Git repository
    if use_git:
        subprocess.check_call(['git', 'init'], cwd=project_dir)
        subprocess.check_call(['git', 'add', '.'], cwd=project_dir)
        subprocess.check_call(['git', 'commit', '-m', 'Initial commit'], cwd=project_dir)

    return project_dir
