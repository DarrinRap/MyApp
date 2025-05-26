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

Use File → New Project to clear all fields and start over at any time.
'''

class ScaffoldApp(tk.Tk):
    """Main GUI for scaffolding and packaging Python desktop apps."""
    def __init__(self):
        super().__init__()
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
        for i, text in enumerate(labels):
            tk.Label(frame, text=text).grid(row=i, column=0, sticky='w', pady=5)
        tk.Entry(frame, textvariable=self.project_name).grid(row=0, column=1, columnspan=2, sticky='ew')
        tk.Entry(frame, textvariable=self.output_folder).grid(row=1, column=1, sticky='ew')
        tk.Button(frame, text="Browse…", command=partial(self._browse_folder, self.output_folder)).grid(row=1, column=2, padx=5)
        tk.OptionMenu(frame, self.gui_lib, "tkinter", "pyqt5", "pyqt6").grid(row=2, column=1, columnspan=2, sticky='ew')
        tk.OptionMenu(frame, self.license_type, "MIT", "None").grid(row=3, column=1, columnspan=2, sticky='ew')
        opts = [
            ("Initialize Git repository", 'git'),
            ("Include pytest tests", 'tests'),
            ("Add GitHub Actions CI", 'ci'),
            ("Create docs folder", 'docs'),
            ("Add pre-commit config", 'precommit'),
            ("Add .editorconfig file", 'editor'),
            ("Use src/ directory layout", 'src'),
        ]
        for idx, (label, key) in enumerate(opts, start=4):
            tk.Checkbutton(frame, text=label, variable=self.options[key]).grid(row=idx, column=0, columnspan=3, sticky='w')

    def _create_actions(self):
        frame = tk.Frame(self)
        frame.pack(pady=10)
        tk.Button(frame, text="Start Scaffolding", font=(None,12,'bold'), command=self._run_scaffold).pack(pady=5)
        tk.Button(frame, text="Update pip", command=self._update_pip).pack(pady=2)
        tk.Button(frame, text="Update All Packages", command=self._update_all).pack(pady=2)
        tk.Button(frame, text="Package Executable", command=self._package_executable).pack(pady=2)

    def _create_log_pane(self):
        global log_pane
        log_pane = ScrolledText(self, state='disabled', height=10)
        log_pane.pack(fill='both', expand=True, padx=15, pady=10)
        tk.Label(self, text=f"© {AUTHOR}", font=(None,8,'italic'), fg='gray').pack(side='bottom', pady=5)

    def _browse_folder(self, var):
        path = filedialog.askdirectory(title="Select Output Folder")
        if path:
            var.set(path)

    def _log(self, message):
        log_pane.configure(state='normal')
        log_pane.insert('end', message + '\n')
        log_pane.see('end')
        log_pane.configure(state='disabled')

    def _clear_form(self):
        self.project_name.set("MyApp")
        self.output_folder.set("")
        self.gui_lib.set("tkinter")
        self.license_type.set("MIT")
        for v in self.options.values():
            v.set(True)
        log_pane.configure(state='normal')
        log_pane.delete('1.0','end')
        log_pane.configure(state='disabled')

    def _show_about(self):
        about_text = (
            f"{APP_TITLE} v{VERSION}\n"
            f"Created by {AUTHOR}\n\n"
            "Package into EXE with:\n"
            "pip install pyinstaller\n"
            "pyinstaller --onefile --windowed main.py"
        )
        messagebox.showinfo("About", about_text)

    def _show_usage(self):
        usage_win = tk.Toplevel(self)
        usage_win.title("Usage Guide")
        usage_win.geometry("500x400")
        txt = ScrolledText(usage_win, wrap='word')
        txt.pack(fill='both', expand=True, padx=10, pady=10)
        txt.insert('end', USAGE_TEXT)
        txt.configure(state='disabled')

    def _update_pip(self):
        self._log("Updating pip…")
        try:
            subprocess.check_call([sys.executable,'-m','pip','install','--upgrade','pip'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            out = subprocess.check_output([sys.executable,'-m','pip','--version'])
            self._log(out.decode().strip())
            messagebox.showinfo("Success","pip has been upgraded.")
        except subprocess.CalledProcessError as e:
            err = e.output.decode(errors='ignore') if hasattr(e,'output') else str(e)
            self._log(f"Error updating pip: {err}")
            messagebox.showerror("Error", err)

    def _update_all(self):
        self._log("Checking outdated packages…")
        try:
            data = subprocess.check_output([sys.executable,'-m','pip','list','--outdated','--format=json'], stderr=subprocess.DEVNULL)
            pkgs = json.loads(data)
            if not pkgs:
                self._log("All packages are up to date.")
                messagebox.showinfo("Up to date","All packages are current.")
                return
            for pkg in pkgs:
                name,curr,latest = pkg['name'],pkg['version'],pkg['latest_version']
                self._log(f"Upgrading {name}: {curr} → {latest}")
                subprocess.check_call([sys.executable,'-m','pip','install','--upgrade',name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                info = subprocess.check_output([sys.executable,'-m','pip','show',name])
                for line in info.decode().splitlines():
                    if line.startswith("Version:"):
                        new_ver = line.split(": ")[1]
                        self._log(f"{name} now at version {new_ver}")
                        break
            messagebox.showinfo("Success","All packages have been upgraded.")
        except subprocess.CalledProcessError as e:
            err = e.output.decode(errors='ignore') if hasattr(e,'output') else str(e)
            self._log(f"Error upgrading packages: {err}")
            messagebox.showerror("Error", err)

    def _package_executable(self):
        if not self.last_path:
            folder = filedialog.askdirectory(title="Select project folder to package")
            if not folder:
                return
            self.last_path = folder
        project_dir = self.last_path

        entry_script = os.path.join(project_dir,'main.py')
        if not os.path.isfile(entry_script):
            entry_script = filedialog.askopenfilename(title="Locate entry script", initialdir=project_dir, filetypes=[("Python files","*.py")])
            if not entry_script:
                return

        self._log("Ensuring PyInstaller is installed…")
        try:
            subprocess.check_call([sys.executable,'-m','pip','install','--upgrade','pyinstaller'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            self._log(f"Error installing PyInstaller: {e}")
            messagebox.showerror("Error",str(e))
            return

        self._log("Installing compatible pefile version…")
        try:
            subprocess.check_call([sys.executable,'-m','pip','install','--upgrade','pefile!=2024.8.26,>=2022.5.30'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            self._log(f"Error installing pefile: {e}")
            messagebox.showerror("Error",str(e))
            return

        self._log("Packaging executable in real time…")
        try:
            proc = subprocess.Popen([sys.executable,'-m','PyInstaller','--onefile','--windowed',entry_script], cwd=project_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in proc.stdout:
                self._log(line.rstrip())
            proc.wait()
            if proc.returncode == 0:
                self._log("Packaging completed successfully.")
                messagebox.showinfo("Packaged","Executable has been created.")
            else:
                self._log(f"Packaging failed with exit code {proc.returncode}.")
                messagebox.showerror("Packaging Error",f"Exit code {proc.returncode}")
        except Exception as e:
            self._log(f"Packaging error: {e}")
            messagebox.showerror("Error",str(e))

    def _run_scaffold(self):
        name = self.project_name.get().strip()
        if not name:
            messagebox.showwarning("Input Required","Please enter a project name.")
            return
        self._log(f"Scaffolding '{name}'…")
        try:
            # Scaffold project
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
            self._log(f"Project created at: {path}")
            # Create virtual environment
            venv_dir = os.path.join(path,'venv')
            self._log("Creating virtual environment…")
            subprocess.check_call([sys.executable,'-m','venv',venv_dir])
            self._log(f"Virtual environment created at: {venv_dir}")
            # Offer terminal
            if messagebox.askyesno("Open Terminal","Open PowerShell with venv activated?"):
                cmd=["powershell","-NoExit","-Command",f"Set-Location -LiteralPath '{path}'; .\\venv\\Scripts\\Activate.ps1"]
                subprocess.Popen(cmd)
            messagebox.showinfo("Done", f"Project scaffolded at:\n{path}\n\nVirtual environment created at:\n{venv_dir}")
        except Exception as e:
            self._log(f"Error: {e}")
            messagebox.showerror("Scaffolding Error",str(e))

if __name__ == '__main__':
    app=ScaffoldApp()
    app.mainloop()
