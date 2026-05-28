#Запуск приложения


import tkinter as tk
from tkinter import messagebox
from db import DatabaseHandler
from app import OrderApp

def main():
    root = tk.Tk()

    db_handler = DatabaseHandler(
        host="localhost",
        user="root",
        password="",
        database="orders_db"
    )

    if not db_handler.connect():
        messagebox.showerror("Не удалось подключиться к базе данных")
        return

    app = OrderApp(root, db_handler)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()