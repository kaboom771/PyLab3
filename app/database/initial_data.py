from app.database.connection import DBConnection
from app.lib.logger import setup_logger

logger = setup_logger()

def insert_initial_data():
    """Вставляет начальные данные в базу данных только если таблица пуста."""
    
    sample_trips = [
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
    ]
    
    sample_users = [
        "Иванов Иван Иванович",
        "Петрова Анна Сергеевна", 
        "Сидоров Алексей Владимирович",
        "Козлова Мария Дмитриевна",
        "Николаев Денис Олегович"
    ]
    
    try:
        db = DBConnection()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Проверяем, есть ли уже данные в таблицах
        cursor.execute("SELECT COUNT(*) FROM trips")
        trips_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchone()[0]
        
        # Добавляем путевки только если таблица пуста
        if trips_count == 0:
            cursor.executemany(
                "INSERT INTO trips (destination, start_date, end_date, price, total_seats, available_seats) VALUES (?, ?, ?, ?, ?, ?)",
                sample_trips
            )
            logger.info(f"Успешно добавлено {len(sample_trips)} тестовых путевок")
        
        # Добавляем пользователей только если таблица пуста
        if users_count == 0:
            cursor.executemany(
                "INSERT INTO users (full_name) VALUES (?)",
                [(user,) for user in sample_users]
            )
            logger.info(f"Успешно добавлено {len(sample_users)} тестовых пользователей")
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при вставке начальных данных: {e}")
        return False