import sqlite3
import threading


class Database:
    _lock = threading.Lock()  # Блокировка для предотвращения конфликтов

    def __init__(self, db_path="db.db"):
        self.db_path = db_path

    def _connect(self):
        """Создает и возвращает новое соединение с БД"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.execute("PRAGMA foreign_keys = ON;")  # Включаем поддержку внешних ключей
        return conn

    def execute(self, query: str, params: tuple = ()):
        """Выполняет SQL-запрос (INSERT, UPDATE, DELETE)"""
        with self._lock:  # Блокируем выполнение, чтобы избежать конфликтов
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            cursor.close()
            conn.close()

    def fetchone(self, query: str, params: tuple = ()):
        """Выполняет SELECT-запрос и возвращает одну строку"""
        with self._lock:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result

    def fetchall(self, query: str, params: tuple = ()):
        """Выполняет SELECT-запрос и возвращает все строки"""
        with self._lock:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            return result

    def init_db(self):
        """Создает таблицы, если их нет"""
        queries = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                user_id INTEGER UNIQUE,
                username TEXT
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY,
                name VARCHAR(255)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS message (
                id INTEGER PRIMARY KEY, 
                chat_id INTEGER NULL,
                last_update DATETIME,
                FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE SET NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS parking (
                id INTEGER PRIMARY KEY,
                name VARCHAR(255),
                message_id INTEGER NULL,
                FOREIGN KEY (message_id) REFERENCES message(id) ON DELETE SET NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY,
                parking_id INTEGER NULL,
                scooter_count INTEGER,
                time_update DATETIME,
                FOREIGN KEY (parking_id) REFERENCES parking(id) ON DELETE SET NULL
            );
            """,
        ]
        for query in queries:
            self.execute(query)
