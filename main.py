import tkinter as tk
from tkinter import filedialog, messagebox
from setup_project import scaffold_project

def choose_dir(entry):
    d = filedialog.askdirectory(title="Select Output Folder")
    if d:
        entry.delete(0, tk.END)
        entry.insert(0, d)

def on_scaffold(name_entry, out_entry, gui_var, git_var, test_var,
                ci_var, docs_var, pre_var, ec_var, src_var):
    name = name_entry.get().strip()
    out  = out_entry.get().strip() or None
    if not name:
        messagebox.showerror("Error", "Project name cannot be empty.")
        return
    try:
        path = scaffold_project(
            project_name=name,
            description=f"A Python desktop app named {name}",
            author="Darrin A. Rapoport",
            license_type="MIT",
            gui_lib=gui_var.get(),
            use_git=bool(git_var.get()),
            include_tests=bool(test_var.get()),
            include_ci=bool(ci_var.get()),
            include_docs=bool(docs_var.get()),
            include_precommit=bool(pre_var.get()),
            include_editorconfig=bool(ec_var.get()),
            use_src=bool(src_var.get()),
            output_dir=out
        )
        messagebox.showinfo("Done", f"Project created at:\n{path}")
    except Exception as e:
        messagebox.showerror("Failed", str(e))

def build_gui():
    app = tk.Tk()
    app.title("Python Project Scaffolder")
    app.geometry("500x480")

    tk.Label(app, text="Project Name:").pack(anchor="w", padx=10, pady=(10,0))
    name_entry = tk.Entry(app, width=40)
    name_entry.insert(0, "MyApp")
    name_entry.pack(padx=10, pady=5)

    tk.Label(app, text="Output Folder (blank for current):").pack(anchor="w", padx=10)
    out_frame = tk.Frame(app)
    out_frame.pack(fill="x", padx=10, pady=5)
    out_entry = tk.Entry(out_frame, width=30)
    out_entry.pack(side="left", fill="x", expand=True)
    tk.Button(out_frame, text="Browse…", command=lambda: choose_dir(out_entry)).pack(side="right")

    gui_var = tk.StringVar(value="tkinter")
    tk.Label(app, text="GUI Toolkit:").pack(anchor="w", padx=10, pady=(10,0))
    tk.OptionMenu(app, gui_var, "tkinter", "pyqt5").pack(fill="x", padx=10)

    opts = [
        ("Initialize Git repo",      "git_var"),
        ("Include pytest tests",     "test_var"),
        ("Add GitHub Actions CI",    "ci_var"),
        ("Include docs folder",      "docs_var"),
        ("Include pre-commit config","pre_var"),
        ("Include .editorconfig",    "ec_var"),
        ("Use src/ layout",          "src_var"),
    ]
    vars_map = {}
    tk.Label(app, text="Options:").pack(anchor="w", padx=10, pady=(10,0))
    for text, var in opts:
        v = tk.IntVar(value=1)
        cb = tk.Checkbutton(app, text=text, variable=v)
        cb.pack(anchor="w", padx=20)
        vars_map[var] = v

    tk.Button(
        app,
        text="Scaffold!",
        font=("Helvetica", 12, "bold"),
        command=lambda: on_scaffold(
            name_entry, out_entry, gui_var,
            vars_map["git_var"], vars_map["test_var"], vars_map["ci_var"],
            vars_map["docs_var"], vars_map["pre_var"], vars_map["ec_var"], vars_map["src_var"],
        )
    ).pack(pady=20)

    tk.Label(
        app,
        text="Designed by Darrin A. Rapoport",
        font=("Helvetica", 8, "italic"),
        fg="gray"
    ).pack(side="bottom", pady=5)

    app.mainloop()

if __name__ == '__main__':
    build_gui()
