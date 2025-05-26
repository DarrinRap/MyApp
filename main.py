import tkinter as tk
from tkinter import messagebox

def on_click():
    messagebox.showinfo("Scaffolder", "This will scaffold a new project!")

def main():
    # Create main window
    app = tk.Tk()
    app.title("Python Project Scaffolder")
    app.geometry("450x280")

    # Welcome label
    tk.Label(
        app,
        text="📦 Python Project Scaffolder",
        font=("Helvetica", 16, "bold")
    ).pack(pady=10)

    # Info button
    tk.Button(
        app,
        text="What does this do?",
        command=on_click
    ).pack(pady=5)

    # --- Entry for project name ---
    entry = tk.Entry(app, width=35, font=("Helvetica", 12))
    entry.insert(0, "Enter project name here")
    entry.pack(pady=10)

    # Label that will display the echoed text
    echo_label = tk.Label(app, text="", font=("Helvetica", 12))
    echo_label.pack(pady=5)

    # Callback to echo text
    def echo_text():
        text = entry.get().strip()
        if not text:
            messagebox.showwarning("Empty", "Please type a project name.")
        else:
            echo_label.config(text=f"Scaffolding: {text}")

    # Scaffold button
    tk.Button(
        app,
        text="Scaffold!",
        command=echo_text
    ).pack(pady=5)

    # Footer credit
    tk.Label(
        app,
        text="Designed by Darrin A. Rapoport",
        font=("Helvetica", 8, "italic"),
        fg="gray"
    ).pack(side="bottom", pady=10)

    # Start the GUI loop
    app.mainloop()

if __name__ == "__main__":
    main()
