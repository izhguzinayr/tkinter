# работа с бд
Содержит подключение и методы для работы с существующей БД


import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Optional, Tuple

class DatabaseHandler:

    def __init__(self, host: str = "localhost", user: str = "root",
                 password: str = "", database: str = "orders_db", port: int = 3306):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.conn = None
        self.cursor = None

    def connect(self) -> bool:

        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                autocommit=True
            )
            self.cursor = self.conn.cursor(dictionary=True)
            return True

        except Error as e:
            print(f"Ошибка подключения к БД: {e}")
            return False

    def get_all_orders(self, filter_client: Optional[str] = None,
                       sort_field: Optional[str] = None,
                       sort_order: str = "ASC") -> List[Dict]:
        """
        Получение всех заказов с возможностью фильтрации и сортировки

        Args:
            filter_client: фильтр по клиенту (если указан)
            sort_field: поле для сортировки (customer, order_date, amount)
            sort_order: направление сортировки (ASC или DESC)

        Returns:
            Список словарей с данными заказов
        """
        try:
            query = """
                SELECT
                    customer,
                    city,
                    phone,
                    DATE_FORMAT(order_date, '%%d.%%m.%%Y') as order_date,
                    amount
                FROM orders
            """
            params = []

            # Фильтрация по клиенту
            if filter_client:
                query += " WHERE customer = %s"
                params.append(filter_client)

            # Сортировка
            sort_mapping = {
                "Заказчик": "customer",
                "Дата заказа": "order_date",
                "Сумма заказа": "amount"
            }

            if sort_field and sort_field in sort_mapping:
                order = "ASC" if sort_order == "По возрастанию" else "DESC"
                query += f" ORDER BY {sort_mapping[sort_field]} {order}"

            self.cursor.execute(query, params)
            return self.cursor.fetchall()

        except Error as e:
            print(f"Ошибка получения заказов: {e}")
            return []

    def get_unique_customers(self) -> List[str]:
        """Получение списка уникальных заказчиков"""
        try:
            self.cursor.execute("SELECT DISTINCT customer FROM orders ORDER BY customer")
            return [row["customer"] for row in self.cursor.fetchall()]
        except Error as e:
            print(f"Ошибка получения списка заказчиков: {e}")
            return []

    def get_orders_count_and_sum(self, filter_client: Optional[str] = None) -> Tuple[int, float]:
        """
        Получение количества заказов и общей суммы

        Args:
            filter_client: фильтр по клиенту (если указан)

        Returns:
            Кортеж (количество_заказов, общая_сумма)
        """
        try:
            query = "SELECT COUNT(*) as cnt, COALESCE(SUM(amount), 0) as total FROM orders"
            params = []

            if filter_client:
                query += " WHERE customer = %s"
                params.append(filter_client)

            self.cursor.execute(query, params)
            result = self.cursor.fetchone()

            return result["cnt"], float(result["total"])

        except Error as e:
            print(f"Ошибка подсчёта итогов: {e}")
            return 0, 0.0

    def close(self):
        """Закрытие соединения с БД"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
        except:
            pass