"""
Модуль графического интерфейса для работы с заказами
"""

import tkinter as tk
from tkinter import ttk, messagebox
from db import DatabaseHandler

class OrderApp:
    """Главный класс приложения для работы с заказами"""

    def __init__(self, root, db_handler: DatabaseHandler):
        """
        Инициализация приложения

        Args:
            root: корневое окно Tkinter
            db_handler: объект для работы с БД
        """
        self.root = root
        self.db = db_handler
        self.current_filter_client = None
        self.current_sort_field = None
        self.current_sort_order = None
        self.search_term = ""

        self.setup_ui()
        self.load_initial_data()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.root.title("Работа с заказами")
        self.root.geometry("1050x550")
        self.root.resizable(True, True)

        # Создание всех элементов интерфейса
        self.create_control_panel()
        self.create_table_view()
        self.create_summary_panel()

    def create_control_panel(self):
        """Создание верхней панели управления"""
        control_frame = ttk.LabelFrame(self.root, text="Управление", padding=5)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        # Строка 1: Выбор заказчика
        self.create_filter_section(control_frame)

        # Строка 2: Сортировка
        self.create_sort_section(control_frame)

        # Строка 3: Поиск
        self.create_search_section(control_frame)

    def create_filter_section(self, parent):
        """Создание секции фильтрации по клиенту"""
        # Метка
        ttk.Label(parent, text="Выберите заказчика:").grid(
            row=0, column=0, padx=5, pady=2, sticky=tk.W
        )

        # Выпадающий список
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(
            parent,
            textvariable=self.customer_var,
            state="readonly",
            width=30
        )
        self.customer_combo.grid(row=0, column=1, padx=5, pady=2)

        # Кнопки
        self.filter_btn = ttk.Button(
            parent,
            text="Фильтровать",
            command=self.filter_by_customer
        )
        self.filter_btn.grid(row=0, column=2, padx=5, pady=2)

        self.show_all_btn = ttk.Button(
            parent,
            text="Показать все",
            command=self.show_all
        )
        self.show_all_btn.grid(row=0, column=3, padx=5, pady=2)

    def create_sort_section(self, parent):
        """Создание секции сортировки"""
        # Метка
        ttk.Label(parent, text="Выберите поле для сортировки:").grid(
            row=1, column=0, padx=5, pady=2, sticky=tk.W
        )

        # Выбор поля
        self.sort_field_var = tk.StringVar()
        self.sort_combo = ttk.Combobox(
            parent,
            textvariable=self.sort_field_var,
            values=["Заказчик", "Дата заказа", "Сумма заказа"],
            state="readonly",
            width=20
        )
        self.sort_combo.grid(row=1, column=1, padx=5, pady=2)
        self.sort_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_sort())

        # Порядок сортировки
        self.sort_order_var = tk.StringVar(value="По возрастанию")

        ttk.Radiobutton(
            parent,
            text="По возрастанию",
            variable=self.sort_order_var,
            value="По возрастанию",
            command=self.apply_sort
        ).grid(row=1, column=2, padx=5, pady=2)

        ttk.Radiobutton(
            parent,
            text="По убыванию",
            variable=self.sort_order_var,
            value="По убыванию",
            command=self.apply_sort
        ).grid(row=1, column=3, padx=5, pady=2)

    def create_search_section(self, parent):
        """Создание секции поиска"""
        search_frame = ttk.Frame(parent)
        search_frame.grid(row=2, column=0, columnspan=4, pady=5, sticky=tk.EW)

        ttk.Label(search_frame, text="Найти:").pack(side=tk.LEFT, padx=5)

        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)

        self.search_btn = ttk.Button(
            search_frame,
            text="Найти",
            command=self.search_and_highlight
        )
        self.search_btn.pack(side=tk.LEFT, padx=5)

    def create_table_view(self):
        """Создание таблицы для отображения заказов"""
        columns = ("customer", "city", "phone", "order_date", "amount")
        self.tree = ttk.Treeview(
            self.root,
            columns=columns,
            show="headings",
            height=15
        )

        # Настройка заголовков
        self.tree.heading("customer", text="Заказчик")
        self.tree.heading("city", text="Город")
        self.tree.heading("phone", text="Телефон")
        self.tree.heading("order_date", text="Дата заказа")
        self.tree.heading("amount", text="Сумма заказа")

        # Настройка ширины колонок
        self.tree.column("customer", width=200)
        self.tree.column("city", width=120)
        self.tree.column("phone", width=130)
        self.tree.column("order_date", width=100)
        self.tree.column("amount", width=100, anchor=tk.E)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Настройка тега для подсветки поиска
        self.tree.tag_configure("search", background="yellow")

    def create_summary_panel(self):
        """Создание нижней панели с итогами"""
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, padx=5, pady=5)

        self.total_count_label = ttk.Label(
            bottom_frame,
            text="Всего заказов: 0",
            font=("Arial", 10, "bold")
        )
        self.total_count_label.pack(side=tk.LEFT, padx=10)

        self.total_sum_label = ttk.Label(
            bottom_frame,
            text="Общая сумма: 0.00",
            font=("Arial", 10, "bold")
        )
        self.total_sum_label.pack(side=tk.LEFT, padx=10)

    def load_initial_data(self):
        """Загрузка начальных данных"""
        self.load_customers_list()
        self.refresh_table()

    def load_customers_list(self):
        """Загрузка списка заказчиков в выпадающий список"""
        customers = self.db.get_unique_customers()
        self.customer_combo['values'] = customers
        if customers:
            self.customer_var.set(customers[0])

    def refresh_table(self, search_highlight=False):
        """
        Обновление таблицы с учётом фильтрации и сортировки

        Args:
            search_highlight: нужно ли подсвечивать результаты поиска
        """
        try:
            # Получение данных из БД
            rows = self.db.get_all_orders(
                filter_client=self.current_filter_client,
                sort_field=self.current_sort_field,
                sort_order=self.current_sort_order
            )

            # Очистка таблицы
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Вставка строк
            for row in rows:
                values = (
                    row["customer"],
                    row["city"],
                    row["phone"],
                    row["order_date"],
                    f"{row['amount']:.2f}"
                )
                item_id = self.tree.insert("", tk.END, values=values)

                # Подсветка при поиске
                if search_highlight and self.search_term:
                    self.highlight_row(item_id, values)

            # Обновление итогов
            self.update_summary()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при обновлении таблицы:\n{e}")

    def highlight_row(self, item_id, row_values):
        """
        Подсветка ячеек, содержащих строку поиска

        Args:
            item_id: идентификатор строки в таблице
            row_values: значения строки
        """
        for value in row_values:
            if self.search_term and self.search_term.lower() in str(value).lower():
                self.tree.tag_add("search", item_id)
                break

    def filter_by_customer(self):
        """Фильтрация записей по выбранному клиенту"""
        selected = self.customer_var.get()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите заказчика!")
            return

        self.current_filter_client = selected
        self.search_term = ""
        self.search_entry.delete(0, tk.END)
        self.refresh_table(search_highlight=False)

    def show_all(self):
        """Отмена фильтрации - показ всех записей"""
        self.current_filter_client = None
        self.search_term = ""
        self.search_entry.delete(0, tk.END)
        self.refresh_table(search_highlight=False)

    def apply_sort(self):
        """Применение сортировки к данным"""
        field = self.sort_field_var.get()
        if not field:
            messagebox.showwarning("Предупреждение", "Выберите поле для сортировки!")
            return

        self.current_sort_field = field
        self.current_sort_order = self.sort_order_var.get()
        self.refresh_table(search_highlight=bool(self.search_term))

    def search_and_highlight(self):
        """Поиск данных и подсветка совпадений"""
        search_term = self.search_entry.get().strip()
        if not search_term:
            messagebox.showinfo("Информация", "Введите строку для поиска")
            return

        self.search_term = search_term
        self.refresh_table(search_highlight=True)

    def update_summary(self):
        """Обновление информации о количестве заказов и общей сумме"""
        count, total_sum = self.db.get_orders_count_and_sum(
            filter_client=self.current_filter_client
        )

        self.total_count_label.config(text=f"Всего заказов: {count}")
        self.total_sum_label.config(text=f"Общая сумма: {total_sum:,.2f}")

    def on_closing(self):
        """Обработка закрытия приложения"""
        if messagebox.askokcancel("Выход", "Вы уверены, что хотите выйти?"):
            self.db.close()
            self.root.destroy()