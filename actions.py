from tkinter import messagebox


def run_scaffold(app, scaffold_project):
    """Scaffold a new project using the provided app state and scaffold_project function."""
    name = app.project_name.get().strip()
    if not name:
        return messagebox.showwarning("Input Required", "Enter project name")

    app._log(f"Scaffolding '{name}'...")
    try:
        path = scaffold_project(
            project_name=name,
            description=f"A Python desktop app named {name}",
            author=app.author,
            license_type=app.license_type.get(),
            gui_lib=app.gui_lib.get(),
            use_git=app.options['git'].get(),
            include_tests=app.options['tests'].get(),
            include_ci=app.options['ci'].get(),
            include_docs=app.options['docs'].get(),
            include_precommit=app.options['precommit'].get(),
            include_editorconfig=app.options['editor'].get(),
            use_src=app.options['src'].get(),
            output_dir=app.output_folder.get() or None
        )
        app.last_path = path
        app._log(f"Project created at {path}")
    except Exception as e:
        app._log(f"Error scaffolding: {e}")
        messagebox.showerror("Error", str(e))

