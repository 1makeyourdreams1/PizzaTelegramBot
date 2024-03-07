import ast
import sqlite3

# Таблица для отзывов (inc*, id, review)
# Таблица для хранения информации о пользователях (*id, last_message, basket)

class Database:
    def __init__(self):
        self.connection = sqlite3.connect("data_base.db", check_same_thread=False)
        self.cursor = self.connection.cursor()

    def add_user(self, user_id):
        with self.connection:
            self.cursor.execute(f"INSERT INTO users ('id') VALUES ({user_id})")

    def user_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute(f"SELECT * FROM users WHERE id = {user_id}").fetchall()
            return bool(len(result))

    def set_last_message(self, user_id, last_message):
        with self.connection:
            return self.cursor.execute(f"UPDATE users SET last_message = {last_message} WHERE id = {user_id}")

    def get_last_message(self, user_id):
        with self.connection:
            result = self.cursor.execute(f"SELECT last_message FROM users WHERE id = {user_id}").fetchall()
            for row in result:
                last_message = int(row[0])
            return last_message

    def add_review(self, user_id, review):
        with self.connection:
            self.cursor.execute(f"INSERT INTO reviews ('id', 'review') VALUES ({user_id}, '{review}')")

    def set_basket(self, user_id, basket):
        with self.connection:
            return self.cursor.execute(f"UPDATE users SET basket = '{basket}' WHERE id = {user_id}")

    def get_basket(self, user_id):
        with self.connection:
            result = self.cursor.execute(f"SELECT basket FROM users WHERE id = {user_id}").fetchall()
            for row in result:
                basket = row[0]
            return ast.literal_eval(basket)

