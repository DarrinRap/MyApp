import sys
import os
import json
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from functools import partial
from setup_project import scaffold_project

# Configuration file to store window size
CONFIG_PATH = os.path.expanduser("~/.scaffolder_config.json")

# Application metadata
APP_TITLE = "Python Project Scaffolder"
VERSION   = "2.0"
AUTHOR    = "Darrin A. Rapoport"

class ScaffoldApp(tk.Tk):
    """A GUI for scaffolding new Python desktop-app projects."""
    def __init__(self):
        super().__init__()
        # Load window size from config or use defaults
        width, height = self._load_window_size()
        self.title(f"{APP_TITLE} v{VERSION}")
        self.geometry(f"{width}x{height}")
        self.minsize(500, 400)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        # Initialize state
        self._init_variables()
        # Build UI
        self._create_menu()
        self._create_form()
        self._create_actions()
        self._create_log_pane()

    def _load_window_size(self):
        try:
            cfg = json.load(open(CONFIG_PATH))
            return cfg.get('width', 600), cfg.get('height', 700)
        except Exception:
            return 600, 700

    def _save_window_size(self):
        try:
            geom = self.geometry().split('+')[0]
            w, h = geom.split('x')
            cfg = {'width': int(w), 'height': int(h)}
            with open(CONFIG_PATH, 'w') as f:
                json.dump(cfg, f)
        except Exception:
            pass

    def _on_close(self):
        self._save_window_size()
        self.destroy()

    def _init_variables(self):
        self.project_name  = tk.StringVar(value="MyApp")
        self.output_folder = tk.StringVar()
        self.gui_lib       = tk.StringVar(value="tkinter")
        self.license_type  = tk.StringVar(value="MIT")
        flags = ['git', 'tests', 'ci', 'docs', 'precommit', 'editor', 'src']
        self.options = {f: tk.BooleanVar(value=True) for f in flags}

    def _create_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="New Project", command=self._clear_form)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_close)
        menubar.add_cascade(label="File", menu=file_menu)
        help_menu = tk.Menu(menubar, tearoff=False)
        help_menu.add_command(label="About", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menubar)

    def _create_form(self):
        frame = tk.Frame(self)
        frame.pack(fill='x', padx=15, pady=10)
        frame.columnconfigure(1, weight=1)

        # Project name
        tk.Label(frame, text="Project Name:").grid(row=0, column=0, sticky='w')
        tk.Entry(frame, textvariable=self.project_name).grid(row=0, column=1, columnspan=2, sticky='ew')

        # Output folder
        tk.Label(frame, text="Destination Folder:").grid(row=1, column=0, sticky='w', pady=5)
        tk.Entry(frame, textvariable=self.output_folder).grid(row=1, column=1, sticky='ew')
        tk.Button(frame, text="Browse…", command=partial(self._browse_folder, self.output_folder))\
            .grid(row=1, column=2, padx=5)

        # GUI toolkit
        tk.Label(frame, text="Framework:").grid(row=2, column=0, sticky='w')
        tk.OptionMenu(frame, self.gui_lib, "tkinter", "pyqt5", "pyqt6").grid(row=2, column=1, columnspan=2, sticky='ew')

        # License
        tk.Label(frame, text="License:").grid(row=3, column=0, sticky='w', pady=5)
        tk.OptionMenu(frame, self.license_type, "MIT", "None").grid(row=3, column=1, columnspan=2, sticky='ew')

        # Features checkboxes
        features = [
            ("Initialize Git repository", 'git'),
            ("Include pytest tests", 'tests'),
            ("Add GitHub Actions CI", 'ci'),
            ("Create docs folder", 'docs'),
            ("Add pre-commit config", 'precommit'),
            ("Add .editorconfig file", 'editor'),
            ("Use src/ directory layout", 'src'),
        ]
        for i, (label, key) in enumerate(features, start=4):
            tk.Checkbutton(frame, text=label, variable=self.options[key])\
                .grid(row=i, column=0, columnspan=3, sticky='w')

    def _create_actions(self):
        act = tk.Frame(self)
        act.pack(pady=10)
        tk.Button(act, text="Start Scaffolding", font=(None, 12, 'bold'), command=self._run_scaffold)\
            .pack(pady=5)
        tk.Button(act, text="Update pip", command=self._update_pip).pack(pady=2)
        tk.Button(act, text="Update All Packages", command=self._update_all).pack(pady=2)

    def _create_log_pane(self):
        global log_pane
        log_pane = ScrolledText(self, state='disabled', height=8)
        log_pane.pack(fill='both', expand=True, padx=15, pady=(0,10))
        tk.Label(self, text=f"© {AUTHOR}", font=(None,8,'italic'), fg='gray')\
            .pack(side='bottom', pady=5)

    def _browse_folder(self, var):
        path = filedialog.askdirectory(title="Select a folder")
        if path:
            var.set(path)

    def _log(self, message):
        log_pane.configure(state='normal')
        log_pane.insert('end', message + '\n')
        log_pane.yview('end')
        log_pane.configure(state='disabled')

    def _clear_form(self):
        self.project_name.set("MyApp")
        self.output_folder.set("")
        self.gui_lib.set("tkinter")
        self.license_type.set("MIT")
        for var in self.options.values():
            var.set(True)
        log_pane.configure(state='normal')
        log_pane.delete('1.0', 'end')
        log_pane.configure(state='disabled')

    def _show_about(self):
        messagebox.showinfo("About",
            f"{APP_TITLE} v{VERSION}\nCreated by {AUTHOR}\n\n"
            "Pack into EXE with:\n"
            "pip install pyinstaller\n"
            "pyinstaller --onefile --windowed main.py"
        )

    def _update_pip(self):
        self._log("Updating pip…")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
            self._log("pip upgraded successfully")
            messagebox.showinfo("Success", "pip has been upgraded.")
        except Exception as e:
            self._log(f"Error updating pip: {e}")
            messagebox.showerror("Error", str(e))

    def _update_all(self):
        self._log("Checking outdated packages…")
        try:
            data = subprocess.check_output([sys.executable, '-m', 'pip', 'list', '--outdated', '--format=json'])
            pkgs = [p['name'] for p in json.loads(data)]
            if not pkgs:
                self._log("All packages are up to date.")
                messagebox.showinfo("Up to date", "All packages are current.")
                return
            for name in pkgs:
                self._log(f"Upgrading {name}…")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', name])
            self._log("All packages upgraded.")
            messagebox.showinfo("Success", "All packages have been upgraded.")
        except Exception as e:
            self._log(f"Error upgrading packages: {e}")
            messagebox.showerror("Error", str(e))

    def _run_scaffold(self):
        name = self.project_name.get().strip()
        if not name:
            messagebox.showwarning("Input Required", "Please enter a project name.")
            return
        self._log(f"Scaffolding '{name}'…")
        try:
            path = scaffold_project(
                project_name=name,
                description=f"Python desktop app: {name}",
                author=AUTHOR,
                license_type=self.license_type.get(),
                gui_lib=self.gui_lib.get(),
                use_git=self.options['git'].get(),
                include_tests=self.options['tests'].get(),
                include_ci=self.options['ci'].get(),
                include_docs=self.options['docs'].get(),
                include_precommit=self.options['precommit'].get(),
                include_editorconfig=self.options['editor'].get(),
                use_src=self.options['src'].get(),
                output_dir=self.output_folder.get() or None
            )
            self._log(f"Project created at: {path}")
            messagebox.showinfo("Done", f"Project scaffolded:\n{path}")
        except Exception as e:
            self._log(f"Error: {e}")
            messagebox.showerror("Scaffolding Error", str(e))

if __name__ == '__main__':
    ScaffoldApp().mainloop()
