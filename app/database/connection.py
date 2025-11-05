import sqlite3
import os
from app.config.settings import settings

class DBConnection:
    """Класс для подключения к базе данных."""
    
    def __init__(self):
        self.db_path = settings.DB_PATH
        self.ensure_data_directory()
    
    def ensure_data_directory(self):
        """Создает папку data, если она не существует."""
        data_dir = os.path.dirname(self.db_path)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def get_connection(self):
        """Возвращает соединение с базой данных."""
        return sqlite3.connect(self.db_path)
    
    def close_connection(self, conn):
        """Закрывает соединение с базой данных."""
        if conn:
            conn.close()