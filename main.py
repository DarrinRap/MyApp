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

# Usage guide text for beginners
USAGE_TEXT = '''
Welcome to the Python Project Scaffolder!

This tool helps you quickly generate a boilerplate Python desktop app.

Fields:

- Project Name: The name of your new project; this will also be the root folder and Python package name.
- Destination Folder: The directory where your project folder will be created (defaults to current directory).
- Framework: Choose between "tkinter", "pyqt5", or "pyqt6" for your GUI library.
- License: Select the MIT license template or "None" to skip adding a license file.

Options:

- Initialize Git repository: Creates a new Git repo inside your project and makes an initial commit.
- Include pytest tests: Sets up a basic tests/ folder with a placeholder test file.
- Add GitHub Actions CI: Generates a simple GitHub Actions workflow to install dependencies and run pytest on push and pull requests.
- Create docs folder: Adds a docs/ directory with an index.md stub for your project documentation.
- Add pre-commit config: Creates a .pre-commit-config.yaml file configured to run Black formatting.
- Add .editorconfig file: Provides an .editorconfig file to ensure consistent indentation and line endings.
- Use src/ directory layout: Organizes your Python package under a src/ directory (recommended for modern Python projects).

Buttons:

- Start Scaffolding: Generates your project structure and files based on the above settings.
- Update pip: Upgrades pip itself to the latest version.
- Update All Packages: Finds and upgrades any outdated packages in the current virtual environment.
- Package Executable: Bundles the scaffolded app into a single executable using PyInstaller; you can locate scripts and executables via file dialogs if they aren’t in default locations.

Use File → New Project to clear all fields and start over at any time.
'''

class ScaffoldApp(tk.Tk):
    """Main GUI application for scaffolding and packaging Python desktop apps."""
    def __init__(self):
        super().__init__()
        # Restore window size
        w, h = self._load_window_size()
        self.title(f"{APP_TITLE} v{VERSION}")
        self.geometry(f"{w}x{h}")
        self.minsize(500, 400)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.last_path = None
        self._init_variables()
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
            with open(CONFIG_PATH, 'w') as f:
                json.dump({'width': int(w), 'height': int(h)}, f)
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
        self.options = {flag: tk.BooleanVar(value=True) for flag in flags}

    def _create_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="New Project", command=self._clear_form)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_close)
        menubar.add_cascade(label="File", menu=file_menu)
        help_menu = tk.Menu(menubar, tearoff=False)
        help_menu.add_command(label="Usage Guide", command=self._show_usage)
        help_menu.add_command(label="About", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menubar)

    def _create_form(self):
        frame = tk.Frame(self)
        frame.pack(fill='x', padx=15, pady=10)
        frame.columnconfigure(1, weight=1)
        labels = ["Project Name:", "Destination Folder:", "Framework:", "License:"]
        for i, txt in enumerate(labels):
            tk.Label(frame, text=txt).grid(row=i, column=0, sticky='w', pady=5)
        tk.Entry(frame, textvariable=self.project_name).grid(row=0, column=1, columnspan=2, sticky='ew')
        tk.Entry(frame, textvariable=self.output_folder).grid(row=1, column=1, sticky='ew')
        tk.Button(frame, text="Browse…", command=partial(self._browse_folder, self.output_folder))\
            .grid(row=1, column=2, padx=5)
        tk.OptionMenu(frame, self.gui_lib, "tkinter", "pyqt5", "pyqt6").grid(row=2, column=1, columnspan=2, sticky='ew')
        tk.OptionMenu(frame, self.license_type, "MIT", "None").grid(row=3, column=1, columnspan=2, sticky='ew')
        options = [
            ("Initialize Git repository", 'git'),
            ("Include pytest tests", 'tests'),
            ("Add GitHub Actions CI", 'ci'),
            ("Create docs folder", 'docs'),
            ("Add pre-commit config", 'precommit'),
            ("Add .editorconfig file", 'editor'),
            ("Use src/ directory layout", 'src'),
        ]
        for idx, (lbl, key) in enumerate(options, start=4):
            tk.Checkbutton(frame, text=lbl, variable=self.options[key])\
                .grid(row=idx, column=0, columnspan=3, sticky='w')

    def _create_actions(self):
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Start Scaffolding", font=(None,12,'bold'), command=self._run_scaffold)\
            .pack(pady=5)
        tk.Button(btn_frame, text="Update pip", command=self._update_pip).pack(pady=2)
        tk.Button(btn_frame, text="Update All Packages", command=self._update_all).pack(pady=2)
        tk.Button(btn_frame, text="Package Executable", command=self._package_executable).pack(pady=2)

    def _create_log_pane(self):
        global log_pane
        log_pane = ScrolledText(self, state='disabled', height=8)
        log_pane.pack(fill='both', expand=True, padx=15, pady=(0,10))
        tk.Label(self, text=f"© {AUTHOR}", font=(None,8,'italic'), fg='gray').pack(side='bottom', pady=5)

    def _browse_folder(self, var):
        path = filedialog.askdirectory(title="Select a folder")
        if path:
            var.set(path)

    def _log(self, msg):
        log_pane.configure(state='normal')
        log_pane.insert('end', msg + '\n')
        log_pane.yview('end')
        log_pane.configure(state='disabled')

    def _clear_form(self):
        self.project_name.set("MyApp")
        self.output_folder.set("")
        self.gui_lib.set("tkinter")
        self.license_type.set("MIT")
        for v in self.options.values(): v.set(True)
        log_pane.configure(state='normal')
        log_pane.delete('1.0','end')
        log_pane.configure(state='disabled')

    def _show_about(self):
        messagebox.showinfo("About", f"{APP_TITLE} v{VERSION}\nCreated by {AUTHOR}\n\nPackage into EXE with:\npip install pyinstaller\npyinstaller --onefile --windowed main.py")

    def _show_usage(self):
        win = tk.Toplevel(self)
        win.title("Usage Guide")
        win.geometry("400x400")
        txt = ScrolledText(win, wrap='word')
        txt.pack(fill='both', expand=True, padx=10, pady=10)
        txt.insert('end', USAGE_TEXT)
        txt.configure(state='disabled')

    def _update_pip(self):
        self._log("Updating pip…")
        try:
            subprocess.check_call([sys.executable,'-m','pip','install','--upgrade','pip'])
            self._log("pip upgraded successfully")
            messagebox.showinfo("Success","pip has been upgraded.")
        except Exception as e:
            self._log(f"Error updating pip: {e}")
            messagebox.showerror("Error",str(e))

    def _update_all(self):
        self._log("Checking outdated packages…")
        try:
            data = subprocess.check_output([sys.executable,'-m','pip','list','--outdated','--format=json'])
            pkgs = [p['name'] for p in json.loads(data)]
            if not pkgs:
                self._log("All packages are up to date.")
                messagebox.showinfo("Up to date","All packages are current.")
                return
            for name in pkgs:
                self._log(f"Upgrading {name}…")
                subprocess.check_call([sys.executable,'-m','pip','install','--upgrade',name])
            self._log("All packages upgraded.")
            messagebox.showinfo("Success","All packages have been upgraded.")
        except Exception as e:
            self._log(f"Error upgrading packages: {e}")
            messagebox.showerror("Error",str(e))

    def _run_scaffold(self):
        name = self.project_name.get().strip()
        if not name:
            messagebox.showwarning("Input Required","Please enter a project name.")
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
            self.last_path = path
            self._log(f"Project created at: {path}")
            messagebox.showinfo("Done",f"Project scaffolded:\n{path}")
        except Exception as e:
            self._log(f"Error: {e}")
            messagebox.showerror("Scaffolding Error", str(e))

    def _package_executable(self):
        # Prompt for project folder if needed
        if not self.last_path:
            folder = filedialog.askdirectory(title="Select project folder to package")
            if not folder:
                return
            self.last_path = folder
        project_dir = self.last_path

        # Locate entry script
        entry_script = os.path.join(project_dir, 'main.py')
        if not os.path.isfile(entry_script):
            entry_script = filedialog.askopenfilename(
                title="Locate entry script",
                initialdir=project_dir,
                filetypes=[("Python files","*.py")]
            )
            if not entry_script:
                return

        self._log("Packaging executable…")
        # Ensure PyInstaller installed
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
        except Exception as e:
            self._log(f"Error installing PyInstaller: {e}")
            messagebox.showerror("Error", str(e))
            return

        cmd = [sys.executable, '-m', 'PyInstaller', '--onefile', '--windowed', entry_script]
        try:
            subprocess.check_call(cmd, cwd=project_dir)
            dist_dir = os.path.join(project_dir, 'dist')
            exe_files = []
            if os.path.isdir(dist_dir):
                exe_files = [f for f in os.listdir(dist_dir) if f.lower().endswith('.exe')]
            # If no .exe found, let user locate
            if not exe_files:
                exe_path = filedialog.askopenfilename(
                    title="Locate executable",
                    initialdir=dist_dir if os.path.isdir(dist_dir) else project_dir,
                    filetypes=[("Executable","*.exe"),("All files","*")]
                )
                if exe_path:
                    self._log(f"Executable found: {exe_path}")
                    messagebox.showinfo("Packaged", f"Executable located at:\n{exe_path}")
                else:
                    self._log("No executable found.")
                    messagebox.showwarning("No Executable", "No .exe found.")
            else:
                exe_path = os.path.join(dist_dir, exe_files[0])
                self._log(f"Executable created at: {exe_path}")
                messagebox.showinfo("Packaged", f"Executable created:\n{exe_path}")
        except Exception as e:
            self._log(f"Packaging failed: {e}")
            messagebox.showerror("Packaging Error", str(e))

if __name__ == '__main__':
    app = ScaffoldApp()
    app.mainloop()
