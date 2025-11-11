import sqlite3
import os
from typing import List


class Database:
    _instance = None
    _initialized = False

    def __new__(cls, path_to_db=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, path_to_db=None):
        if not Database._initialized:
            if path_to_db is None:
                data_dir = "/app/data"
                os.makedirs(data_dir, exist_ok=True)
                path_to_db = os.path.join(data_dir, "database.db")

            # Database uchun papka yaratish
            db_dir = os.path.dirname(path_to_db)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)

            self.path_to_db = path_to_db
            Database._initialized = True

    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = ()
        connection = self.connection
        cursor = connection.cursor()
        data = None
        cursor.execute(sql, parameters)

        if commit:
            connection.commit()
        if fetchall:
            data = cursor.fetchall()
        if fetchone:
            data = cursor.fetchone()
        connection.close()
        return data

    def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT,
            username TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        self.execute(sql, commit=True)

    def create_table_channels(self):
        sql = """
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id TEXT UNIQUE,
            channel_name TEXT,
            channel_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        self.execute(sql, commit=True)

    def add_user(self, user_id: int, full_name: str, username: str = None):
        sql = "INSERT INTO users (user_id, full_name, username) VALUES (?, ?, ?) ON CONFLICT(user_id) DO NOTHING"
        self.execute(sql, parameters=(user_id, full_name, username), commit=True)

    def select_all_users(self):
        sql = "SELECT * FROM users"
        return self.execute(sql, fetchall=True)

    def select_user(self, user_id: int):
        sql = "SELECT * FROM users WHERE user_id = ?"
        return self.execute(sql, parameters=(user_id,), fetchone=True)

    def count_users(self):
        return self.execute("SELECT COUNT(*) FROM users", fetchone=True)[0]

    def add_channel(self, channel_id: str, channel_name: str, channel_url: str):
        sql = "INSERT INTO channels (channel_id, channel_name, channel_url) VALUES (?, ?, ?)"
        self.execute(sql, parameters=(channel_id, channel_name, channel_url), commit=True)

    def get_all_channels(self):
        sql = "SELECT * FROM channels"
        return self.execute(sql, fetchall=True)

    def delete_channel(self, channel_id: str):
        sql = "DELETE FROM channels WHERE channel_id = ?"
        self.execute(sql, parameters=(channel_id,), commit=True)

    def get_channel_by_id(self, channel_id: str):
        sql = "SELECT * FROM channels WHERE channel_id = ?"
        return self.execute(sql, parameters=(channel_id,), fetchone=True)