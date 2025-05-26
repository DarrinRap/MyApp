import os
import subprocess
import textwrap

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

    # 1. Create src/ layout or root package
    pkg_dir = os.path.join(project_dir, 'src' if use_src else project_name)
    os.makedirs(pkg_dir, exist_ok=True)
    open(os.path.join(pkg_dir, '__init__.py'), 'w').close()

    # 2. Generate README.md
    readme_path = os.path.join(project_dir, 'README.md')
    with open(readme_path, 'w') as f:
        f.write(f"# {project_name}\n")
        f.write(f"{description}\n\n")
        f.write(f"Created by {author}\n\n")
        f.write("## Quick Start\n")
        f.write(textwrap.dedent(f"""
            ```bash
            cd {project_name}
            python -m venv venv
            source venv/bin/activate  # or .\\venv\\Scripts\\activate on Windows
            pip install -r requirements.txt
            python main.py
            ```
        """))

    # 3. Generate .gitignore
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

    # 4. Create requirements.txt stub
    reqs_path = os.path.join(project_dir, 'requirements.txt')
    with open(reqs_path, 'w') as f:
        f.write("# Add your project dependencies here\n")

    # (The rest of your scaffold steps go here: main.py, tests/, CI, docs, pre-commit, editorconfig, license)
    # For brevity, ensure you integrate your existing scaffold_project logic below.

    # Initialize Git repository
    if use_git:
        subprocess.check_call(['git', 'init'], cwd=project_dir)
        subprocess.check_call(['git', 'add', '.'], cwd=project_dir)
        subprocess.check_call(['git', 'commit', '-m', 'Initial commit'], cwd=project_dir)

    return project_dir
