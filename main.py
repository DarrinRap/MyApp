import sys
import os
import json
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from functools import partial
from setup_project import scaffold_project

# Configuration file to store window size\CONFIG_PATH = os.path.expanduser("~/.scaffolder_config.json")

# Application metadata
APP_TITLE = "Python Project Scaffolder"
VERSION = "2.0"
AUTHOR = "Darrin A. Rapoport"

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
- Add GitHub Actions CI: Generates a simple GitHub Actions workflow to install dependencies and run pytest.
- Create docs folder: Adds a docs/ directory with an index.md stub for your project documentation.
- Add pre-commit config: Creates a .pre-commit-config.yaml file configured to run Black formatting.
- Add .editorconfig file: Provides an .editorconfig file to ensure consistent indentation and line endings.
- Use src/ directory layout: Organizes your Python package under a src/ directory.

Buttons:
- Start Scaffolding: Generates your project structure and files based on the above settings.
- Update pip: Upgrades pip itself to the latest version and logs the updated version.
- Update All Packages: Finds and upgrades any outdated packages, logging current vs. latest versions.
- Package Executable: Bundles the scaffolded app into a single executable using PyInstaller.
- Open in Editor: Launches VS Code in the scaffolded project folder.
- Open Terminal: Opens a system terminal in the scaffolded project folder.
- Clear Log: Clears both Log and Terminal tabs.

Use File → New Project to clear all fields and start over at any time.
'''

class ScaffoldApp(tk.Tk):
    """Main GUI for scaffolding and packaging Python desktop apps."""
    def __init__(self):
        super().__init__()
        # Load and apply window size
        w, h = self._load_window_size()
        self.title(f"{APP_TITLE} v{VERSION}")
        self.geometry(f"{w}x{h}")
        self.minsize(600, 500)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # State
        self.last_path = None
        self._init_variables()

        # Build UI
        self._create_menu()
        self._create_form()
        self._create_actions()
        self._create_notebook()

    def _load_window_size(self):
        try:
            with open(CONFIG_PATH) as f:
                cfg = json.load(f)
            return cfg.get('width', 800), cfg.get('height', 600)
        except Exception:
            return 800, 600

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
        # Form fields
        self.project_name = tk.StringVar(value="MyApp")
        self.output_folder = tk.StringVar()
        self.gui_lib = tk.StringVar(value="tkinter")
        self.license_type = tk.StringVar(value="MIT")
        # Option flags
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
        # Project Settings
        ps_frame = ttk.LabelFrame(self, text="Project Settings")
        ps_frame.pack(fill='x', padx=15, pady=(10, 5))
        ps_frame.columnconfigure(1, weight=1)

        ttk.Label(ps_frame, text="Project Name:").grid(row=0, column=0, sticky='w', pady=2)
        ttk.Entry(ps_frame, textvariable=self.project_name).grid(row=0, column=1, columnspan=2, sticky='ew', pady=2)

        ttk.Label(ps_frame, text="Destination Folder:").grid(row=1, column=0, sticky='w', pady=2)
        ttk.Entry(ps_frame, textvariable=self.output_folder).grid(row=1, column=1, sticky='ew', pady=2)
        ttk.Button(ps_frame, text="Browse…", command=partial(self._browse_folder, self.output_folder))\
            .grid(row=1, column=2, padx=5, pady=2)

        ttk.Label(ps_frame, text="Framework:").grid(row=2, column=0, sticky='w', pady=2)
        ttk.OptionMenu(ps_frame, self.gui_lib, self.gui_lib.get(), "tkinter", "pyqt5", "pyqt6").grid(row=2, column=1, columnspan=2, sticky='ew', pady=2)

        ttk.Label(ps_frame, text="License:").grid(row=3, column=0, sticky='w', pady=2)
        ttk.OptionMenu(ps_frame, self.license_type, self.license_type.get(), "MIT", "None").grid(row=3, column=1, columnspan=2, sticky='ew', pady=2)

        # Options
        opt_frame = ttk.LabelFrame(self, text="Options")
        opt_frame.pack(fill='x', padx=15, pady=(0, 10))
        opts = [
            ("Initialize Git repository", 'git'),
            ("Include pytest tests", 'tests'),
            ("Add GitHub Actions CI", 'ci'),
            ("Create docs folder", 'docs'),
            ("Add pre-commit config", 'precommit'),
            ("Add .editorconfig file", 'editor'),
            ("Use src/ directory layout", 'src'),
        ]
        for i, (text, key) in enumerate(opts):
            ttk.Checkbutton(opt_frame, text=text, variable=self.options[key]).grid(row=i//2, column=i%2, sticky='w', padx=5, pady=2)

    def _create_actions(self):
        act_frame = ttk.Frame(self)
        act_frame.pack(fill='x', padx=15)
        btns = [
            ("Start Scaffolding", self._run_scaffold),
            ("Update pip", self._update_pip),
            ("Update All Packages", self._update_all),
            ("Package Executable", self._package_executable),
            ("Open in Editor", self._open_in_editor),
            ("Open Terminal", self._open_terminal),
            ("Clear Log", self._clear_log)
        ]
        for text, cmd in btns:
            ttk.Button(act_frame, text=text, command=cmd).pack(side='left', expand=True, fill='x', padx=3, pady=5)

    def _create_notebook(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=15, pady=5)

        # Log tab
        log_frame = ttk.Frame(self.notebook)
        self.log_pane = ScrolledText(log_frame, state='disabled', wrap='none', height=10)
        self.log_pane.pack(fill='both', expand=True)
        self.notebook.add(log_frame, text="Log")

        # Terminal tab
        term_frame = ttk.Frame(self.notebook)
        self.term_pane = ScrolledText(term_frame, state='disabled', wrap='none', height=10)
        self.term_pane.pack(fill='both', expand=True)
        self.notebook.add(term_frame, text="Terminal")

        ttk.Label(self, text=f"© {AUTHOR}", font=(None, 8, 'italic'), foreground='gray')\
            .pack(side='bottom', pady=(0, 5))

    def _browse_folder(self, var):
        path = filedialog.askdirectory(title="Select Output Folder")
        if path:
            var.set(path)

    def _clear_form(self):
        # Reset all form fields and clear logs
        self.project_name.set("MyApp")
        self.output_folder.set("")
        self.gui_lib.set("tkinter")
        self.license_type.set("MIT")
        for v in self.options.values():
            v.set(True)
        self._clear_log()

    def _log(self, message):
        self.log_pane.configure(state='normal')
        self.log_pane.insert('end', message + '\n')
        self.log_pane.see('end')
        self.log_pane.configure(state='disabled')

    def _term_log(self, message):
        self.term_pane.configure(state='normal')
        self.term_pane.insert('end', message + '\n')
        self.term_pane.see('end')
        self.term_pane.configure(state='disabled')

    def _clear_log(self):
        for pane in (self.log_pane, self.term_pane):
            pane.configure(state='normal')
            pane.delete('1.0', 'end')
            pane.configure(state='disabled')

    def _show_about(self):
        about = (
            f"{APP_TITLE} v{VERSION}\n"
            f"Created by {AUTHOR}\n\n"
            "Package into EXE with:\n"
            "pip install pyinstaller\n"
            "pyinstaller --onefile --windowed main.py"
        )
        messagebox.showinfo("About", about)

    def _show_usage(self):
        win = tk.Toplevel(self)
        win.title("Usage Guide")
        win.geometry("500x400")
        txt = ScrolledText(win, wrap='word')
        txt.pack(fill='both', expand=True, padx=10, pady=10)
        txt.insert('end', USAGE_TEXT)
        txt.configure(state='disabled')

    def _update_pip(self):
        self._log("Updating pip...")
        try:
            proc = subprocess.Popen([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'],
                                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in proc.stdout:
                self._term_log(line.rstrip())
            proc.wait()
            if proc.returncode == 0:
                self._log("pip upgraded successfully.")
                messagebox.showinfo("Success", "pip has been upgraded.")
            else:
                self._log(f"pip upgrade failed (code {proc.returncode}).")
                messagebox.showerror("Error", f"pip upgrade failed (code {proc.returncode})")
        except Exception as e:
            self._log(f"Error updating pip: {e}")
            messagebox.showerror("Error", str(e))

    def _update_all(self):
        self._log("Checking outdated packages...")
        try:
            data = subprocess.check_output([sys.executable, '-m', 'pip', 'list', '--outdated', '--format=json'])
            pkgs = json.loads(data)
            if not pkgs:
                self._log("All packages are up to date.")
                messagebox.showinfo("Up to date", "All packages are current.")
                return
            for pkg in pkgs:
                name = pkg['name']
                self._log(f"Upgrading {name}...")
                term = subprocess.Popen([sys.executable, '-m', 'pip', 'install', '--upgrade', name],
                                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                for line in term.stdout:
                    self._term_log(line.rstrip())
                term.wait()
                if term.returncode == 0:
                    self._log(f"{name} upgraded.")
                else:
                    self._log(f"{name} upgrade failed (code {term.returncode}).")
            messagebox.showinfo("Success", "Package upgrades completed.")
        except Exception as e:
            self._log(f"Error upgrading packages: {e}")
            messagebox.showerror("Error", str(e))

    def _package_executable(self):
        if not self.last_path:
            folder = filedialog.askdirectory(title="Select project folder to package")
            if not folder:
                return
            self.last_path = folder
        project_dir = self.last_path
        # Ensure PyInstaller
        self._log("Installing PyInstaller...")
        try:
            inst = subprocess.Popen([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pyinstaller'],
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in inst.stdout:
                self._term_log(line.rstrip())
            inst.wait()
            if inst.returncode != 0:
                raise RuntimeError("PyInstaller install failed")
        except Exception as e:
            self._log(f"Error installing PyInstaller: {e}")
            messagebox.showerror("Error", str(e))
            return
        # Package
        self._log("Packaging executable...")
        try:
            cmd = [sys.executable, '-m', 'PyInstaller', '--onefile', '--windowed', os.path.join(project_dir, 'main.py')]
            pkg = subprocess.Popen(cmd, cwd=project_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in pkg.stdout:
                self._term_log(line.rstrip())
            pkg.wait()
            if pkg.returncode == 0:
                self._log("Executable created successfully.")
                messagebox.showinfo("Packaged", "Executable has been created.")
            else:
                self._log(f"Packaging failed (code {pkg.returncode}).")
                messagebox.showerror("Error", f"Packaging failed (code {pkg.returncode})")
        except Exception as e:
            self._log(f"Error packaging executable: {e}")
            messagebox.showerror("Error", str(e))

    def _open_in_editor(self):
        if not self.last_path:
            messagebox.showwarning("No Project", "Please scaffold a project first.")
            return
        self._log(f"Opening editor at {self.last_path}")
        try:
            subprocess.Popen(["code", self.last_path])
        except Exception as e:
            self._log(f"Error opening editor: {e}")
            messagebox.showerror("Error", str(e))

    def _open_terminal(self):
        if not self.last_path:
            messagebox.showwarning("No Project", "Please scaffold a project first.")
            return
        self._log(f"Opening terminal at {self.last_path}")
        try:
            if sys.platform.startswith("win"):
                subprocess.Popen(["cmd.exe", "/K", f"cd /d {self.last_path}"])
            elif sys.platform.startswith("darwin"):
                subprocess.Popen(["open", "-a", "Terminal", self.last_path])
            else:
                terminal = os.environ.get("TERMINAL", "x-terminal-emulator")
                subprocess.Popen([terminal, "--working-directory", self.last_path])
        except Exception as e:
            self._log(f"Error opening terminal: {e}")
            messagebox.showerror("Error", str(e))

    def _run_scaffold(self):
        name = self.project_name.get().strip()
        if not name:
            messagebox.showwarning("Input Required", "Please enter a project name.")
            return
        self._log(f"Scaffolding '{name}'...")
        try:
            path = scaffold_project(
                project_name=name,
                description=f"A Python desktop app named {name}",
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
            self._log(f"Project created at {path}")
            # Create virtualenv
            self._log("Creating virtual environment...")
            venv = subprocess.Popen([sys.executable, '-m', 'venv', os.path.join(path, 'venv')],
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in venv.stdout:
                self._term_log(line.rstrip())
            venv.wait()
            self._log(f"Virtual environment created at {os.path.join(path, 'venv')}")
            # Ask to open terminal with venv
            if messagebox.askyesno("Open Terminal", "Open terminal with venv activated?"):
                if sys.platform.startswith("win"):
                    cmd = ["powershell", "-NoExit", "-Command", f"Set-Location -LiteralPath '{path}'; .\\venv\\Scripts\\Activate.ps1"]
                else:
                    cmd = ["bash", "-i", "-c", f"cd '{path}' && source venv/bin/activate; exec $SHELL"]
                subprocess.Popen(cmd)
            messagebox.showinfo("Done", f"Scaffolded at {path}\nVirtual environment created.")
        except Exception as e:
            self._log(f"Error during scaffolding: {e}")
            messagebox.showerror("Scaffolding Error", str(e))

if __name__ == '__main__':
    app = ScaffoldApp()
    app.mainloop()
