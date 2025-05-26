import sys
import tkinter as tk

def main():
    app = tk.Tk()
    app.title('Hello, Tkinter!')
    app.geometry('300x100')
    tk.Label(app, text='Hello, Tkinter!').pack(pady=20)
    app.mainloop()
    sys.exit(app.exec_() if hasattr(app, 'exec_') else 0)

if __name__ == '__main__':
    main()
