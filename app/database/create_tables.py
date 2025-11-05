from app.database.connection import DBConnection
from app.database.models import TRIPS_TABLE
from app.lib.logger import setup_logger

logger = setup_logger()

def create_tables():
    """Создает таблицы в базе данных если они не существуют."""
    try:
        db = DBConnection()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(TRIPS_TABLE)
        
        conn.commit()
        conn.close()
        
        logger.info("Таблицы успешно созданы/проверены")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при создании таблиц: {e}")
        return False