import sys
import subprocess
import io
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from setup_project import scaffold_project

APP_TITLE = "Python Project Scaffolder"
VERSION   = "1.0"
AUTHOR    = "Darrin A. Rapoport"

def choose_dir(entry):
    d = filedialog.askdirectory(title="Select Output Folder")
    if d:
        entry.delete(0, tk.END)
        entry.insert(0, d)

def log(msg: str):
    log_pane.configure(state='normal')
    log_pane.insert(tk.END, msg + "\n")
    log_pane.see(tk.END)
    log_pane.configure(state='disabled')

def clear_all():
    name_entry.delete(0, tk.END)
    name_entry.insert(0, "MyApp")
    out_entry.delete(0, tk.END)
    gui_var.set("tkinter")
    for var in vars_map.values():
        var.set(1)
    log_pane.configure(state='normal')
    log_pane.delete('1.0', tk.END)
    log_pane.configure(state='disabled')

def show_about():
    message = (
        f"{APP_TITLE} v{VERSION}\n"
        f"Designed by {AUTHOR}\n\n"
        "To package this GUI into an executable:\n"
        "  1. Install PyInstaller: pip install pyinstaller\n"
        "  2. Run in project folder:\n"
        "       pyinstaller --onefile --windowed main.py\n"
    )
    messagebox.showinfo("About", message)

def update_pip():
    log("Updating pip...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
        log("✔ pip upgraded successfully")
        messagebox.showinfo("Updated", "pip has been upgraded!")
    except Exception as e:
        log(f"✖ pip update failed: {e}")
        messagebox.showerror("Error", f"Failed to update pip:\n{e}")

def update_all():
    log("Checking for outdated packages…")
    try:
        out = subprocess.check_output([sys.executable, '-m', 'pip', 'list', '--outdated', '--format=freeze'])
        pkgs = [line.split(b'==')[0] for line in out.splitlines()]
        if not pkgs:
            log("✔ All packages are up to date")
            messagebox.showinfo("Done", "All packages are already up to date!")
            return
        for pkg in pkgs:
            name = pkg.decode()
            log(f"Upgrading {name}…")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', name])
        log("✔ All packages upgraded")
        messagebox.showinfo("Done", "All packages have been upgraded!")
    except Exception as e:
        log(f"✖ update failed: {e}")
        messagebox.showerror("Error", f"Failed to update packages:\n{e}")

def on_scaffold():
    name = name_entry.get().strip()
    out  = out_entry.get().strip() or None
    if not name:
        messagebox.showerror("Error", "Project name cannot be empty.")
        return

    # capture stdout from scaffold_project
    buffer = io.StringIO()
    old, sys.stdout = sys.stdout, buffer
    try:
        log(f"Starting scaffolding of '{name}'…")
        path = scaffold_project(
            project_name       = name,
            description        = f"A Python desktop app named {name}",
            author             = AUTHOR,
            license_type       = lic_var.get(),
            gui_lib            = gui_var.get(),
            use_git            = bool(vars_map["git_var"].get()),
            include_tests      = bool(vars_map["test_var"].get()),
            include_ci         = bool(vars_map["ci_var"].get()),
            include_docs       = bool(vars_map["docs_var"].get()),
            include_precommit  = bool(vars_map["pre_var"].get()),
            include_editorconfig = bool(vars_map["ec_var"].get()),
            use_src            = bool(vars_map["src_var"].get()),
            output_dir         = out
        )
        sys.stdout = old
        logs = buffer.getvalue().splitlines()
        for line in logs:
            log(line)
        log("✔ Scaffolding complete")
        messagebox.showinfo("Done", f"Project created at:\n{path}")
    except Exception as e:
        sys.stdout = old
        log(f"✖ Scaffolding failed: {e}")
        messagebox.showerror("Failed", str(e))

# ─── Build the GUI ─────────────────────────────────────────────────────────────

app = tk.Tk()
app.title(APP_TITLE)
app.geometry("600x700")

# Menu bar
menubar = tk.Menu(app)
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="New",   command=clear_all)
filemenu.add_separator()
filemenu.add_command(label="Exit",  command=app.destroy)
menubar.add_cascade(label="File",   menu=filemenu)

helpmenu = tk.Menu(menubar, tearoff=0)
helpmenu.add_command(label="About", command=show_about)
menubar.add_cascade(label="Help",   menu=helpmenu)

app.config(menu=menubar)

# --- Form ---
frm = tk.Frame(app)
frm.pack(padx=10, pady=10, fill="x")

tk.Label(frm, text="Project Name:").grid(row=0, column=0, sticky="w")
name_entry = tk.Entry(frm, width=40); name_entry.insert(0, "MyApp")
name_entry.grid(row=0, column=1, sticky="ew", pady=5)

tk.Label(frm, text="Output Folder:").grid(row=1, column=0, sticky="w")
out_entry = tk.Entry(frm, width=30); out_entry.grid(row=1, column=1, sticky="ew")
tk.Button(frm, text="Browse…", command=lambda: choose_dir(out_entry))\
    .grid(row=1, column=2, padx=5)

tk.Label(frm, text="GUI Toolkit:").grid(row=2, column=0, sticky="w", pady=(10,0))
gui_var = tk.StringVar(value="tkinter")
tk.OptionMenu(frm, gui_var, "tkinter", "pyqt5", "pyqt6")\
    .grid(row=2, column=1, columnspan=2, sticky="ew", pady=(10,0))

lic_var = tk.StringVar(value="MIT")
tk.Label(frm, text="License:").grid(row=3, column=0, sticky="w")
tk.OptionMenu(frm, lic_var, "MIT", "None")\
    .grid(row=3, column=1, columnspan=2, sticky="ew")

# Feature checkboxes
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
for i, (txt, var) in enumerate(opts, start=4):
    v = tk.IntVar(value=1)
    tk.Checkbutton(frm, text=txt, variable=v)\
        .grid(row=i, column=0, columnspan=3, sticky="w")
    vars_map[var] = v

# Scaffold button
tk.Button(app, text="Scaffold!", font=("Helvetica", 12, "bold"), command=on_scaffold)\
    .pack(pady=10)

# Update buttons
tk.Button(app, text="Update pip",           command=update_pip).pack(pady=5)
tk.Button(app, text="Update All Packages",  command=update_all).pack(pady=5)

# Progress / log pane
log_pane = ScrolledText(app, height=10, state='disabled')
log_pane.pack(fill="both", expand=True, padx=10, pady=10)

# Footer
tk.Label(app, text=f"Designed by {AUTHOR}", font=("Helvetica", 8, "italic"), fg="gray")\
    .pack(side="bottom", pady=5)

app.mainloop()
