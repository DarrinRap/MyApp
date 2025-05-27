import sys
import os
import json
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from functools import partial
from setup_project import scaffold_project

# Configuration file to store window size
CONFIG_PATH = os.path.expanduser("~/.scaffolder_config.json")

# Application metadata
APP_TITLE = "Python Project Scaffolder"
VERSION = "2.0"
AUTHOR = "Darrin A. Rapoport"

# Usage guide text
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
- Package Executable: Bundles a selected script into a single executable using PyInstaller.
- Open in Editor: Launches VS Code or system file explorer in the project folder.
- Open Terminal: Opens a system terminal in the scaffolded project folder.
- Clear Log: Clears both Log and Terminal tabs.

Use File → New Project to clear all fields and start over at any time.
'''

class ScaffoldApp(tk.Tk):
    def __init__(self):
        super().__init__()
        w, h = self._load_window_size()
        self.title(f"{APP_TITLE} v{VERSION}")
        self.geometry(f"{w}x{h}")
        self.minsize(600, 500)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._init_variables()
        self._create_menu()
        self._create_form()
        self._create_actions()
        self._create_notebook()

    def _init_variables(self):
        self.project_name = tk.StringVar(value="MyApp")
        self.output_folder = tk.StringVar()
        self.gui_lib = tk.StringVar(value="tkinter")
        self.license_type = tk.StringVar(value="MIT")
        flags = ['git','tests','ci','docs','precommit','editor','src']
        self.options = {f: tk.BooleanVar(value=True) for f in flags}
        self.last_path = None

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
        frm = ttk.LabelFrame(self, text="Project Settings")
        frm.pack(fill='x', padx=15, pady=(10,5))
        frm.columnconfigure(1, weight=1)

        ttk.Label(frm, text="Project Name:").grid(row=0,column=0,sticky='w')
        ttk.Entry(frm, textvariable=self.project_name).grid(row=0,column=1,columnspan=2,sticky='ew')

        ttk.Label(frm, text="Destination Folder:").grid(row=1,column=0,sticky='w')
        ttk.Entry(frm, textvariable=self.output_folder).grid(row=1,column=1,sticky='ew')
        ttk.Button(frm,text="Browse…",command=partial(self._browse_folder,self.output_folder)).grid(row=1,column=2)

        ttk.Label(frm, text="Framework:").grid(row=2,column=0,sticky='w')
        ttk.OptionMenu(frm,self.gui_lib,self.gui_lib.get(),"tkinter","pyqt5","pyqt6").grid(row=2,column=1,columnspan=2,sticky='ew')

        ttk.Label(frm, text="License:").grid(row=3,column=0,sticky='w')
        ttk.OptionMenu(frm,self.license_type,self.license_type.get(),"MIT","None").grid(row=3,column=1,columnspan=2,sticky='ew')

        opts_frame = ttk.LabelFrame(self, text="Options")
        opts_frame.pack(fill='x', padx=15, pady=(0,10))
        opts = [("Initialize Git repository",'git'),("Include pytest tests",'tests'),
                ("Add GitHub Actions CI",'ci'),("Create docs folder",'docs'),
                ("Add pre-commit config",'precommit'),("Add .editorconfig file",'editor'),
                ("Use src/ layout",'src')]
        for i,(text,key) in enumerate(opts):
            ttk.Checkbutton(opts_frame,text=text,variable=self.options[key]).grid(row=i//2,column=i%2,sticky='w',padx=5,pady=2)

    def _create_actions(self):
        frame = ttk.Frame(self)
        frame.pack(fill='x', padx=15)
        actions = [
            ("Start Scaffolding", self._run_scaffold),
            ("Update pip", self._update_pip),
            ("Update All Packages", self._update_all),
            ("Package Executable", self._package_executable),
            ("Open in Editor", self._open_in_editor),
            ("Open Terminal", self._open_terminal),
            ("Clear Log", self._clear_log)
        ]
        for text, cmd in actions:
            ttk.Button(frame, text=text, command=cmd).pack(side='left', expand=True, fill='x', padx=3, pady=5)

    def _create_notebook(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=15, pady=5)
        log_tab = ttk.Frame(self.notebook)
        self.log_pane = ScrolledText(log_tab, state='disabled', wrap='none')
        self.log_pane.pack(fill='both', expand=True)
        self.notebook.add(log_tab, text="Log")
        term_tab = ttk.Frame(self.notebook)
        self.term_pane = ScrolledText(term_tab, state='disabled', wrap='none')
        self.term_pane.pack(fill='both', expand=True)
        self.notebook.add(term_tab, text="Terminal")
        ttk.Label(self, text=f"© {AUTHOR}", font=(None, 8, 'italic'), foreground='gray').pack(side='bottom', pady=5)

    def _browse_folder(self, var):
        d = filedialog.askdirectory(title="Select Output Folder")
        if d:
            var.set(d)

    def _clear_form(self):
        self.project_name.set("MyApp")
        self.output_folder.set("")
        self.gui_lib.set("tkinter")
        self.license_type.set("MIT")
        for v in self.options.values():
            v.set(True)
        self._clear_log()

    def _log(self, msg):
        self.log_pane.configure(state='normal')
        self.log_pane.insert('end', msg + '\n')
        self.log_pane.see('end')
        self.log_pane.configure(state='disabled')

    def _term_log(self, msg):
        self.term_pane.configure(state='normal')
        self.term_pane.insert('end', msg + '\n')
        self.term_pane.see('end')
        self.term_pane.configure(state='disabled')

    def _clear_log(self):
        for pane in (self.log_pane, self.term_pane):
            pane.configure(state='normal')
            pane.delete('1.0', 'end')
            pane.configure(state='disabled')

    def _show_about(self):
        messagebox.showinfo("About", f"{APP_TITLE} v{VERSION}\nCreated by {AUTHOR}")

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
        proc = subprocess.Popen([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in proc.stdout:
            self._term_log(line.rstrip())
        proc.wait()
        self._log("pip update done")

    def _update_all(self):
        self._log("Checking outdated packages...")
        data = subprocess.check_output([sys.executable, '-m', 'pip', 'list', '--outdated', '--format=json'])
        for pkg in json.loads(data):
            name = pkg['name']
            self._log(f"Upgrading {name}...")
            q = subprocess.Popen([sys.executable, '-m', 'pip', 'install', '--upgrade', name], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for l in q.stdout:
                self._term_log(l.rstrip())
            q.wait()
            self._log(f"{name} upgrade complete")

    def _package_executable(self):
        exe_name = simpledialog.askstring("Executable Name", "Enter name for the bundled EXE:", initialvalue="Scaffold")
        if not exe_name:
            return

        script_path = os.path.abspath(__file__)
        output_dir = os.path.dirname(script_path)
        self._log(f"Packaging '{exe_name}.exe' from {script_path}...")

        try:
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '--upgrade', 'pyinstaller'],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
        except subprocess.CalledProcessError as e:
            self._log(f"Failed to install PyInstaller: {e.output}")
            messagebox.showerror("PyInstaller Error", e.output)
            return

        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--onefile', '--windowed',
            '--name', exe_name,
            script_path
        ]
        proc = subprocess.Popen(
            cmd,
            cwd=output_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        for line in proc.stdout:
            self._term_log(line.rstrip())
        proc.wait()

        if proc.returncode == 0:
            dist_exe = os.path.join(output_dir, 'dist', f"{exe_name}.exe")
            self._log(f"Executable created: {dist_exe}")
            messagebox.showinfo("Success", f"Executable created:\n{dist_exe}")
        else:
            self._log(f"Packaging failed with code {proc.returncode}")
            messagebox.showerror("Packaging Error", f"Exit code: {proc.returncode}")

    def _open_in_editor(self):
        if not self.last_path:
            messagebox.showwarning("No Project", "Scaffold first")
            return
        self._log(f"Opening editor at {self.last_path}")
        try:
            subprocess.Popen(["code", self.last_path])
        except:
            os.startfile(self.last_path)

    def _open_terminal(self):
        if not self.last_path:
            return
        if sys.platform.startswith('win'):
            subprocess.Popen(['cmd.exe','/K',f'cd /d {self.last_path}'])
        elif sys.platform.startswith('darwin'):
            subprocess.Popen(['open','-a','Terminal',self.last_path])
        else:
            subprocess.Popen([os.environ.get('TERMINAL','x-terminal-emulator'),'--working-directory',self.last_path])

    def _run_scaffold(self):
        name = self.project_name.get().strip()
        if not name:
            return messagebox.showwarning("Input Required", "Enter project name")
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
        except Exception as e:
            self._log(f"Error scaffolding: {e}")
            messagebox.showerror("Error", str(e))

def main():
    app = ScaffoldApp()
    app.mainloop()

if __name__ == '__main__':
    main()
S