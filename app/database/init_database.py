import os
from app.database.connection import DBConnection
from app.database.create_tables import create_tables
from app.database.initial_data import insert_initial_data
from app.lib.logger import setup_logger

logger = setup_logger()

def database_exists():
    """Проверяет, существует ли уже база данных с таблицами."""
    try:
        db = DBConnection()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Проверяем существование таблицы trips
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trips'")
        table_exists = cursor.fetchone() is not None
        
        # Если таблица существует, проверяем есть ли в ней данные
        if table_exists:
            cursor.execute("SELECT COUNT(*) FROM trips")
            has_data = cursor.fetchone()[0] > 0
        else:
            has_data = False
            
        conn.close()
        return table_exists and has_data
        
    except Exception:
        return False

def initialize_database(force_recreate=False):
    """Инициализирует базу данных только если она не существует или принудительно."""
    
    if force_recreate:
        logger.info("Принудительное пересоздание базы данных...")
        # Удаляем файл базы данных если существует
        db_path = DBConnection().db_path
        if os.path.exists(db_path):
            os.remove(db_path)
            logger.info(f"Удален файл базы данных: {db_path}")
    
    if database_exists() and not force_recreate:
        logger.info("База данных уже существует, инициализация пропущена")
        return True
    
    logger.info("Начало инициализации базы данных...")
    
    if create_tables():
        if insert_initial_data():
            logger.info("База данных успешно инициализирована")
            return True
    
    logger.error("Ошибка инициализации базы данных")
    return False