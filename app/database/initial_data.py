from app.database.connection import DBConnection
from app.lib.logger import setup_logger

logger = setup_logger()

def insert_initial_data():
    """Вставляет начальные данные в базу данных только если таблица пуста."""
    
    sample_trips = [
        # (destination, start_date, end_date, price, total_seats, available_seats)
         ("Сочи", "2024-07-01", "2024-07-14", 45000.0, 20, 20),
        ("Крым", "2024-07-05", "2024-07-19", 38000.0, 15, 15),
        ("Турция", "2024-07-10", "2024-07-24", 75000.0, 25, 25),
        ("Египет", "2024-07-15", "2024-07-29", 82000.0, 18, 18),
        ("Бали", "2024-08-01", "2024-08-21", 120000.0, 12, 12),
        ("Грузия", "2024-07-20", "2024-08-03", 35000.0, 22, 22),
        ("Кипр", "2024-08-05", "2024-08-19", 68000.0, 16, 16),
        ("Испания", "2024-08-10", "2024-08-24", 95000.0, 20, 20),
        ("Италия", "2024-08-15", "2024-08-29", 89000.0, 18, 18),
        ("Таиланд", "2024-09-01", "2024-09-15", 78000.0, 24, 24),
        ("Вьетнам", "2024-09-05", "2024-09-19", 65000.0, 20, 20),
        ("ОАЭ", "2024-09-10", "2024-09-24", 110000.0, 15, 15),
        ("Греция", "2024-09-15", "2024-09-29", 72000.0, 22, 22),
    ]
    
    try:
        db = DBConnection()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Проверяем, есть ли уже данные в таблице
        cursor.execute("SELECT COUNT(*) FROM trips")
        count = cursor.fetchone()[0]
        
        if count > 0:
            logger.info(f"В таблице уже есть {count} записей, начальные данные не добавляются")
            conn.close()
            return True
        
        # Добавляем начальные данные только если таблица пуста
        cursor.executemany(
            "INSERT INTO trips (destination, start_date, end_date, price, total_seats, available_seats) VALUES (?, ?, ?, ?, ?, ?)",
            sample_trips
        )
        
        conn.commit()
        conn.close()
        
        logger.info(f"Успешно добавлено {len(sample_trips)} тестовых путевок")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при вставке начальных данных: {e}")
        return False