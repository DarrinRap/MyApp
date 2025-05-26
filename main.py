import sys
import tkinter as tk

def main():
    app = tk.Tk()
    app.title('MyApp')
    app.geometry('300x100')
    tk.Label(app, text='Welcome to MyApp!').pack(pady=20)
    app.mainloop()
    sys.exit(app.exec_() if hasattr(app, 'exec_') else 0)

if __name__ == '__main__':
    main()
