import sys, subprocess, tkinter as tk
from tkinter import filedialog, messagebox
from setup_project import scaffold_project

def choose_dir(entry):
    d=filedialog.askdirectory(title="Select Output Folder")
    if d:
        entry.delete(0,tk.END)
        entry.insert(0,d)

def update_pip():
    try:
        subprocess.check_call([sys.executable,'-m','pip','install','--upgrade','pip'])
        messagebox.showinfo("Done","pip upgraded!")
    except Exception as e:
        messagebox.showerror("Error",str(e))

def update_all():
    try:
        out=subprocess.check_output([sys.executable,'-m','pip','list','--outdated','--format=freeze'])
        pkgs=[l.split(b'==')[0] for l in out.splitlines()]
        for p in pkgs:
            subprocess.check_call([sys.executable,'-m','pip','install','--upgrade',p.decode()])
        messagebox.showinfo("Done","All packages upgraded!")
    except Exception as e:
        messagebox.showerror("Error",str(e))

def on_scaffold(ne,oe,gv,gitv,tv,civ,dv,pv,ev,sv):
    name=ne.get().strip()
    out=oe.get().strip() or None
    if not name:
        messagebox.showerror("Error","Project name required")
        return
    try:
        path=scaffold_project(
            project_name=name,
            description=f"A Python desktop app named {name}",
            author="Darrin A. Rapoport",
            license_type="MIT",
            gui_lib=gv.get(),
            use_git=bool(gitv.get()),
            include_tests=bool(tv.get()),
            include_ci=bool(civ.get()),
            include_docs=bool(dv.get()),
            include_precommit=bool(pv.get()),
            include_editorconfig=bool(ev.get()),
            use_src=bool(sv.get()),
            output_dir=out
        )
        messagebox.showinfo("Done",f"Created at:\n{path}")
    except Exception as e:
        messagebox.showerror("Failed",str(e))

def build_gui():
    app=tk.Tk()
    app.title("Python Project Scaffolder")
    app.geometry("500x600")

    tk.Label(app,text="Project Name:").pack(anchor="w",padx=10,pady=(10,0))
    ne=tk.Entry(app,width=40); ne.insert(0,"MyApp"); ne.pack(padx=10,pady=5)

    tk.Label(app,text="Output Folder (blank for current):").pack(anchor="w",padx=10)
    fr=tk.Frame(app); fr.pack(fill="x",padx=10,pady=5)
    oe=tk.Entry(fr,width=30); oe.pack(side="left",fill="x",expand=True)
    tk.Button(fr,text="Browse…",command=lambda:choose_dir(oe)).pack(side="right")

    gv=tk.StringVar(value="tkinter")
    tk.Label(app,text="GUI Toolkit:").pack(anchor="w",padx=10,pady=(10,0))
    tk.OptionMenu(app,gv,"tkinter","pyqt5","pyqt6").pack(fill="x",padx=10)

    opts=[("Initialize Git repo","gitv"),("Include pytest tests","tv"),
          ("Add CI","civ"),("Include docs","dv"),
          ("Include pre-commit","pv"),("Include .editorconfig","ev"),
          ("Use src/ layout","sv")]
    vm={}
    tk.Label(app,text="Options:").pack(anchor="w",padx=10,pady=(10,0))
    for txt,vn in opts:
        iv=tk.IntVar(value=1)
        tk.Checkbutton(app,text=txt,variable=iv).pack(anchor="w",padx=20)
        vm[vn]=iv

    tk.Button(app,text="Scaffold!",font=("Helvetica",12,"bold"),
              command=lambda:on_scaffold(ne,oe,gv,vm["gitv"],vm["tv"],vm["civ"],vm["dv"],vm["pv"],vm["ev"],vm["sv"])
    ).pack(pady=10)

    tk.Button(app,text="Update pip",command=update_pip).pack(pady=5)
    tk.Button(app,text="Update All Packages",command=update_all).pack(pady=5)

    tk.Label(app,text="Designed by Darrin A. Rapoport",font=("Helvetica",8,"italic"),fg="gray").pack(side="bottom",pady=10)

    app.mainloop()

if __name__=='__main__':
    build_gui()
