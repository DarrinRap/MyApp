import tkinter as tk
from tkinter import messagebox

def on_click():
    messagebox.showinfo("Clicked!", "You pressed the button!")

def main():
    # Create the main window
    app = tk.Tk()
    app.title("My First App")
    app.geometry("400x200")

    # A welcome label
    tk.Label(app, text="Welcome to MyApp!", font=("Helvetica", 14)).pack(pady=10)

    # A button that shows a message box when clicked
    tk.Button(app, text="Press Me", command=on_click).pack(pady=10)

    # Start the event loop
    app.mainloop()

if __name__ == "__main__":
    main()
