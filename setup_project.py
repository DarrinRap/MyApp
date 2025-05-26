#!/usr/bin/env python3
import os, subprocess, sys
from datetime import datetime

def run(cmd, cwd=None):
    print(f"> {' '.join(cmd)}")
    subprocess.check_call(cmd, cwd=cwd)

def get_mit_license(author: str, year: int) -> str:
    return f"""MIT License

Copyright (c) {year} {author}

Permission is hereby granted, free of charge, to any person obtaining a copy...
... (full MIT text omitted for brevity)...
"""

def scaffold_project(
    project_name: str, description: str, author: str,
    license_type: str, gui_lib: str, use_git: bool,
    include_tests: bool, include_ci: bool, include_docs: bool,
    include_precommit: bool, include_editorconfig: bool,
    use_src: bool, output_dir: str = None
) -> str:
    # 1) cd into output_dir if set
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        os.chdir(output_dir)
    # 2) create or cd into project folder
    if project_name != '.':
        os.makedirs(project_name, exist_ok=True)
        os.chdir(project_name)
    project_dir = os.getcwd()

    # 3) venv
    run([sys.executable, '-m', 'venv', 'venv'])

    # 4) README
    with open('README.md','w') as f:
        f.write(f"# {project_name}\n\n{description}\n")

    # 5) LICENSE
    if license_type.upper()=='MIT' and author:
        year = datetime.now().year
        with open('LICENSE','w') as f:
            f.write(get_mit_license(author,year))

    # 6) Source package
    pkg = project_name.lower().replace(' ','_')
    src = 'src' if use_src else '.'
    os.makedirs(os.path.join(src,pkg),exist_ok=True)
    open(os.path.join(src,pkg,'__init__.py'),'w').close()

    # 7) docs
    if include_docs:
        os.makedirs('docs',exist_ok=True)
        with open(os.path.join('docs','index.md'),'w') as f:
            f.write(f"# Docs for {project_name}\n")

    # 8) starter main.py
    if gui_lib.lower()=='pyqt6':
        code = f"""import sys
from PyQt6.QtWidgets import QApplication,QLabel

def main():
    app=QApplication(sys.argv)
    lbl=QLabel('Hello, PyQt6!')
    lbl.setWindowTitle('{project_name}')
    lbl.resize(400,250)
    lbl.show()
    sys.exit(app.exec())

if __name__=='__main__':
    main()
"""
        reqs = ['PyQt6']
    elif gui_lib.lower()=='pyqt5':
        code = f"""import sys
from PyQt5.QtWidgets import QApplication,QLabel

def main():
    app=QApplication(sys.argv)
    lbl=QLabel('Hello, PyQt5!')
    lbl.setWindowTitle('{project_name}')
    lbl.resize(400,250)
    lbl.show()
    sys.exit(app.exec_())

if __name__=='__main__':
    main()
"""
        reqs = ['PyQt5']
    else:
        code = f"""import tkinter as tk
from tkinter import messagebox

def main():
    app=tk.Tk()
    app.title('{project_name}')
    app.geometry('450x280')
    tk.Label(app,text='📦 {project_name}',font=('Helvetica',16,'bold')).pack(pady=10)
    tk.Button(app,text='What does this do?',command=lambda: messagebox.showinfo('Scaffolder','Scaffolding now!')).pack(pady=5)
    tk.Entry(app,width=35,font=('Helvetica',12)).pack(pady=10)
    tk.Label(app,text='Designed by Darrin A. Rapoport',font=('Helvetica',8,'italic'),fg='gray').pack(side='bottom',pady=10)
    app.mainloop()

if __name__=='__main__':
    main()
"""
        reqs = []

    # write main.py
    with open('main.py','w') as f:
        f.write(code)

    # 9) tests
    if include_tests:
        os.makedirs('tests',exist_ok=True)
        with open(os.path.join('tests','test_placeholder.py'),'w') as f:
            f.write(f"import {pkg}\n\ndef test_placeholder():\n    assert True\n")
        reqs.append('pytest')

    # 10) add pre-commit if needed
    if include_precommit:
        reqs.append('pre-commit')
        with open('.pre-commit-config.yaml','w') as f:
            f.write("repos:\n- repo: https://github.com/psf/black\n  rev: stable\n  hooks:\n  - id: black\n")

    # 11) requirements.txt
    with open('requirements.txt','w') as f:
        f.write('\n'.join(reqs))

    # 12) .gitignore
    with open('.gitignore','w') as f:
        f.write("venv/\n__pycache__/\n*.pyc\n.venv*\n")

    # 13) CI
    if include_ci:
        os.makedirs('.github/workflows',exist_ok=True)
        with open('.github/workflows/ci.yml','w') as f:
            f.write("name: CI\non:[push,pull_request]\njobs:\n  build:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v2\n      - run: pip install -r requirements.txt\n      - run: pytest\n")

    # 14) editorconfig
    if include_editorconfig:
        with open('.editorconfig','w') as f:
            f.write("root=true\n[*]\nindent_style=space\nindent_size=4\n")

    # 15) git
    if use_git:
        run(['git','init'])
        run(['git','add','.'])
        run(['git','commit','-m','Initial scaffold'])

    print(f"Project created at: {project_dir}")
    return project_dir

def ask(prompt, default):
    r=input(f"{prompt} [{default}]: ").strip()
    return r or default

def main():
    print("🛠️ Python Project Scaffolder CLI 🛠️\n")
    name=ask("Project name","MyApp")
    desc=ask("Description","A Python desktop app")
    auth=ask("Author","Darrin A. Rapoport")
    lic=ask("License (MIT/None)","MIT")
    gui=ask("GUI toolkit (tkinter/pyqt5/pyqt6)","tkinter").lower()
    g=ask("Initialize git? (y/n)","y").lower().startswith('y')
    t=ask("Include pytest? (y/n)","y").lower().startswith('y')
    ci=ask("Include CI? (y/n)","y").lower().startswith('y')
    docs=ask("Include docs? (y/n)","n").lower().startswith('y')
    pre=ask("Include pre-commit? (y/n)","n").lower().startswith('y')
    ec=ask("Include editorconfig? (y/n)","n").lower().startswith('y')
    src=ask("Use src/ layout? (y/n)","y").lower().startswith('y')
    scaffold_project(name,desc,auth,lic,gui,g,t,ci,docs,pre,ec,src)

if __name__=='__main__':
    main()
