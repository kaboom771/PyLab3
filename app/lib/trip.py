from app.database.connection import DBConnection
from app.lib.exceptions import NoAvailableSeatsError, DatabaseError
from app.lib.logger import setup_logger

logger = setup_logger()

class TripManager:
    """Класс для управления путевками в базе данных."""
    
    def __init__(self):
        self.db = DBConnection()
    
    def get_all_trips(self):
        """Возвращает все доступные путевки."""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, destination, start_date, end_date, price, total_seats, available_seats 
                FROM trips 
                ORDER BY start_date
            """)
            
            trips = cursor.fetchall()
            conn.close()
            
            logger.info(f"Загружено {len(trips)} путевок")
            return trips
            
        except Exception as e:
            logger.error(f"Ошибка при загрузке путевок: {e}")
            raise DatabaseError(f"Ошибка при загрузке путевок: {e}")
    
    def book_trip(self, trip_id):
        """Бронирует место в путевке."""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Проверяем доступность мест
            cursor.execute("SELECT available_seats FROM trips WHERE id = ?", (trip_id,))
            result = cursor.fetchone()
            
            if not result:
                raise DatabaseError("Путевка не найдена")
            
            available_seats = result[0]
            
            if available_seats <= 0:
                raise NoAvailableSeatsError("К сожалению, все места в этой путевке уже заняты")
            
            # Бронируем место
            cursor.execute(
                "UPDATE trips SET available_seats = available_seats - 1 WHERE id = ?", 
                (trip_id,)
            )
            
            conn.commit()
            
            # Получаем обновленные данные
            cursor.execute("SELECT destination, available_seats FROM trips WHERE id = ?", (trip_id,))
            trip_data = cursor.fetchone()
            conn.close()
            
            logger.info(f"Успешное бронирование путевки {trip_id}. Осталось мест: {trip_data[1]}")
            return {
                "destination": trip_data[0],
                "remaining_seats": trip_data[1]
            }
            
        except NoAvailableSeatsError:
            raise
        except Exception as e:
            logger.error(f"Ошибка при бронировании путевки {trip_id}: {e}")
            raise DatabaseError(f"Ошибка при бронировании: {e}")