from app.database.connection import DBConnection
from app.lib.exceptions import NoAvailableSeatsError, DatabaseError, AlreadyBookedError
from app.lib.logger import setup_logger

logger = setup_logger()

class TripManager:
    """Класс для управления путевками и пользователями в базе данных."""
    
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
    
    def get_all_users(self):
        """Возвращает всех пользователей."""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, full_name FROM users ORDER BY full_name")
            
            users = cursor.fetchall()
            conn.close()
            
            logger.info(f"Загружено {len(users)} пользователей")
            return users
            
        except Exception as e:
            logger.error(f"Ошибка при загрузке пользователей: {e}")
            raise DatabaseError(f"Ошибка при загрузке пользователей: {e}")
    
    def get_user_bookings(self, user_id):
        """Возвращает список забронированных путевок пользователя."""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT t.id, t.destination, t.start_date, t.end_date, t.price, b.booked_at
                FROM trips t
                JOIN bookings b ON t.id = b.trip_id
                WHERE b.user_id = ?
                ORDER BY b.booked_at DESC
            """, (user_id,))
            
            bookings = cursor.fetchall()
            conn.close()
            
            logger.info(f"Загружено {len(bookings)} бронирований для пользователя {user_id}")
            return bookings
            
        except Exception as e:
            logger.error(f"Ошибка при загрузке бронирований пользователя {user_id}: {e}")
            raise DatabaseError(f"Ошибка при загрузке бронирований: {e}")
    
    def check_booking_exists(self, user_id, trip_id):
        """Проверяет, есть ли уже бронирование пользователя на эту путевку."""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id FROM bookings WHERE user_id = ? AND trip_id = ?",
                (user_id, trip_id)
            )
            
            exists = cursor.fetchone() is not None
            conn.close()
            
            return exists
            
        except Exception as e:
            logger.error(f"Ошибка при проверке бронирования: {e}")
            raise DatabaseError(f"Ошибка при проверке бронирования: {e}")
    
    def book_trip(self, user_id, trip_id):
        """Бронирует место в путевке для пользователя."""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Проверяем, не бронировал ли уже пользователь эту путевку
            if self.check_booking_exists(user_id, trip_id):
                raise AlreadyBookedError("Вы уже забронировали эту путевку ранее")
            
            # Проверяем доступность мест
            cursor.execute("SELECT available_seats FROM trips WHERE id = ?", (trip_id,))
            result = cursor.fetchone()
            
            if not result:
                raise DatabaseError("Путевка не найдена")
            
            available_seats = result[0]
            
            if available_seats <= 0:
                raise NoAvailableSeatsError("К сожалению, все места в этой путевке уже заняты")
            
            # Начинаем транзакцию
            cursor.execute("BEGIN TRANSACTION")
            
            try:
                # Бронируем место
                cursor.execute(
                    "UPDATE trips SET available_seats = available_seats - 1 WHERE id = ?", 
                    (trip_id,)
                )
                
                # Добавляем запись о бронировании
                cursor.execute(
                    "INSERT INTO bookings (user_id, trip_id) VALUES (?, ?)",
                    (user_id, trip_id)
                )
                
                conn.commit()
                
            except Exception as e:
                conn.rollback()
                raise e
            
            # Получаем обновленные данные
            cursor.execute("""
                SELECT t.destination, t.available_seats, u.full_name 
                FROM trips t, users u 
                WHERE t.id = ? AND u.id = ?
            """, (trip_id, user_id))
            
            trip_data = cursor.fetchone()
            conn.close()
            
            logger.info(f"Успешное бронирование: пользователь {user_id} на путевку {trip_id}. Осталось мест: {trip_data[1]}")
            
            return {
                "destination": trip_data[0],
                "remaining_seats": trip_data[1],
                "user_name": trip_data[2]
            }
            
        except (NoAvailableSeatsError, AlreadyBookedError):
            raise
        except Exception as e:
            logger.error(f"Ошибка при бронировании путевки {trip_id} пользователем {user_id}: {e}")
            raise DatabaseError(f"Ошибка при бронировании: {e}")