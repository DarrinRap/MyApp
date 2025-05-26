import sys
import subprocess
import json
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from functools import partial
from setup_project import scaffold_project

# Application metadata
APP_TITLE = "Python Project Scaffolder"
VERSION   = "1.0"
AUTHOR    = "Darrin A. Rapoport"

class ScaffoldApp(tk.Tk):
    """Main application window for the Python Project Scaffolder."""
    def __init__(self):
        super().__init__()
        # Window setup
        self.title(APP_TITLE)
        self.geometry("600x700")
        self.resizable(True, True)
        # Initialize UI components
        self._init_variables()
        self._create_menu()
        self._create_form()
        self._create_actions()
        self._create_log_pane()

    def _init_variables(self):
        # Form state variables
        self.project_name    = tk.StringVar(value="MyApp")
        self.output_folder   = tk.StringVar(value="")
        self.gui_lib         = tk.StringVar(value="tkinter")
        self.license_type    = tk.StringVar(value="MIT")
        flags = ["git", "tests", "ci", "docs", "precommit", "editor", "src"]
        self.options = {flag: tk.BooleanVar(value=True) for flag in flags}

    def _create_menu(self):
        menubar = tk.Menu(self)
        # File menu
        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="New",  command=self._clear_form)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=file_menu)
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=False)
        help_menu.add_command(label="About", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menubar)

    def _create_form(self):
        frm = tk.Frame(self)
        frm.pack(padx=10, pady=10, fill="x")
        frm.columnconfigure(1, weight=1)
        # Labels
        labels = ["Project Name:", "Output Folder:", "GUI Toolkit:", "License:"]
        for i, text in enumerate(labels):
            tk.Label(frm, text=text).grid(row=i, column=0, sticky="w", pady=5)
        # Entries and selectors
        tk.Entry(frm, textvariable=self.project_name).grid(row=0, column=1, columnspan=2, sticky="ew")
        tk.Entry(frm, textvariable=self.output_folder).grid(row=1, column=1, sticky="ew")
        tk.Button(frm, text="Browse…", command=partial(self._browse_folder, self.output_folder))\
            .grid(row=1, column=2, padx=5)
        tk.OptionMenu(frm, self.gui_lib, "tkinter", "pyqt5", "pyqt6")\
            .grid(row=2, column=1, columnspan=2, sticky="ew")
        tk.OptionMenu(frm, self.license_type, "MIT", "None")\
            .grid(row=3, column=1, columnspan=2, sticky="ew")
        # Checkboxes
        opts = [
            ("Initialize Git repo",      "git"),
            ("Include pytest tests",     "tests"),
            ("Add GitHub Actions CI",    "ci"),
            ("Include docs folder",      "docs"),
            ("Include pre-commit config","precommit"),
            ("Include .editorconfig",    "editor"),
            ("Use src/ layout",          "src"),
        ]
        for idx, (label, key) in enumerate(opts, start=4):
            tk.Checkbutton(frm, text=label, variable=self.options[key])\
                .grid(row=idx, column=0, columnspan=3, sticky="w")

    def _create_actions(self):
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Scaffold!", font=(None, 12, "bold"), command=self._run_scaffold)\
            .pack(pady=5)
        tk.Button(btn_frame, text="Update pip", command=self._update_pip)\
            .pack(pady=2)
        tk.Button(btn_frame, text="Update All Packages", command=self._update_all)\
            .pack(pady=2)

    def _create_log_pane(self):
        global log_pane
        log_pane = ScrolledText(self, height=10, state='disabled')
        log_pane.pack(fill="both", expand=True, padx=10, pady=10)
        tk.Label(self, text=f"Designed by {AUTHOR}", font=(None, 8, "italic"), fg="gray")\
            .pack(side="bottom", pady=5)

    def _browse_folder(self, var):
        path = filedialog.askdirectory(title="Select Output Folder")
        if path:
            var.set(path)

    def _log(self, message: str):
        log_pane.configure(state='normal')
        log_pane.insert(tk.END, message + "\n")
        log_pane.see(tk.END)
        log_pane.configure(state='disabled')

    def _clear_form(self):
        self.project_name.set("MyApp")
        self.output_folder.set("")
        self.gui_lib.set("tkinter")
        self.license_type.set("MIT")
        for var in self.options.values():
            var.set(True)
        log_pane.configure(state='normal')
        log_pane.delete('1.0', tk.END)
        log_pane.configure(state='disabled')

    def _show_about(self):
        messagebox.showinfo(
            "About",
            f"{APP_TITLE} v{VERSION}\nDesigned by {AUTHOR}\n\n"
            "To package: pip install pyinstaller && pyinstaller --onefile --windowed main.py"
        )

    def _update_pip(self):
        self._log("Updating pip...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
            self._log("✔ pip upgraded successfully")
            messagebox.showinfo("Updated", "pip has been upgraded!")
        except Exception as e:
            self._log(f"✖ pip update failed: {e}")
            messagebox.showerror("Error", str(e))

    def _update_all(self):
        self._log("Checking outdated packages…")
        try:
            data = subprocess.check_output([sys.executable, '-m', 'pip', 'list', '--outdated', '--format=json'])
            pkgs = [pkg['name'] for pkg in json.loads(data)]
            if not pkgs:
                self._log("✔ All packages are up to date")
                messagebox.showinfo("Done", "All packages are already up to date!")
                return
            for name in pkgs:
                self._log(f"Upgrading {name}…")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', name])
            self._log("✔ All packages upgraded")
            messagebox.showinfo("Done", "All packages have been upgraded!")
        except Exception as e:
            self._log(f"✖ update failed: {e}")
            messagebox.showerror("Error", str(e))

    def _run_scaffold(self):
        name = self.project_name.get().strip()
        if not name:
            messagebox.showerror("Error", "Project name cannot be empty.")
            return
        self._log(f"Starting scaffolding of '{name}'…")
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
            self._log("✔ Scaffolding complete")
            messagebox.showinfo("Done", f"Project created at:\n{path}")
        except Exception as e:
            self._log(f"✖ Scaffolding failed: {e}")
            messagebox.showerror("Failed", str(e))

if __name__ == '__main__':
    app = ScaffoldApp()
    app.mainloop()
