import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.lib.trip import TripManager
from app.lib.exceptions import NoAvailableSeatsError, DatabaseError, AlreadyBookedError

class TestTripManager:
    """Тесты для класса TripManager с моками БД."""
    
    def test_get_all_trips_success(self, mock_db_connection, sample_trips_data):
        """Тест успешного получения всех путевок."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchall.return_value = sample_trips_data
        
        with patch('app.lib.trip.DBConnection') as MockDB:
            MockDB.return_value.get_connection.return_value = mock_conn
            
            trip_manager = TripManager()
            trips = trip_manager.get_all_trips()
            
            # Проверяем вызовы БД
            mock_cursor.execute.assert_called_once()
            assert "SELECT id, destination" in mock_cursor.execute.call_args[0][0]
            mock_conn.close.assert_called_once()
            
            # Проверяем результат
            assert len(trips) == 3
            assert trips[0][1] == "Сочи"
            assert trips[2][1] == "Турция"
    
    def test_get_all_trips_database_error(self, mock_db_connection):
        """Тест ошибки при получении путевок."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.execute.side_effect = Exception("DB error")
        
        with patch('app.lib.trip.DBConnection') as MockDB:
            MockDB.return_value.get_connection.return_value = mock_conn
            
            trip_manager = TripManager()
            
            with pytest.raises(DatabaseError) as exc_info:
                trip_manager.get_all_trips()
            
            assert "Ошибка при загрузке путевок" in str(exc_info.value)
    
    def test_get_all_users_success(self, mock_db_connection, sample_users_data):
        """Тест успешного получения всех пользователей."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchall.return_value = sample_users_data
        
        with patch('app.lib.trip.DBConnection') as MockDB:
            MockDB.return_value.get_connection.return_value = mock_conn
            
            trip_manager = TripManager()
            users = trip_manager.get_all_users()
            
            mock_cursor.execute.assert_called_once()
            assert "SELECT id, full_name FROM users" in mock_cursor.execute.call_args[0][0]
            assert len(users) == 2
            assert users[0][1] == "Иванов Иван Иванович"
    
    def test_check_booking_exists_true(self, mock_db_connection):
        """Тест проверки существующего бронирования."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = (1,)  # Бронирование существует
        
        with patch('app.lib.trip.DBConnection') as MockDB:
            MockDB.return_value.get_connection.return_value = mock_conn
            
            trip_manager = TripManager()
            exists = trip_manager.check_booking_exists(1, 1)
            
            mock_cursor.execute.assert_called_once_with(
                "SELECT id FROM bookings WHERE user_id = ? AND trip_id = ?",
                (1, 1)
            )
            assert exists is True
    
    def test_check_booking_exists_false(self, mock_db_connection):
        """Тест проверки отсутствующего бронирования."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = None  # Бронирования нет
        
        with patch('app.lib.trip.DBConnection') as MockDB:
            MockDB.return_value.get_connection.return_value = mock_conn
            
            trip_manager = TripManager()
            exists = trip_manager.check_booking_exists(1, 999)
            
            assert exists is False
    
    def test_book_trip_success(self, mock_db_connection):
        """Тест успешного бронирования путевки."""
        mock_conn, mock_cursor = mock_db_connection
        
        # Мокаем проверку существования бронирования
        with patch.object(TripManager, 'check_booking_exists', return_value=False):
            # Мокаем проверку доступности мест
            mock_cursor.fetchone.side_effect = [
                (5,),  # available_seats > 0
                ("Сочи", 4, "Иванов Иван")  # После бронирования
            ]
            
            with patch('app.lib.trip.DBConnection') as MockDB:
                MockDB.return_value.get_connection.return_value = mock_conn
                
                trip_manager = TripManager()
                result = trip_manager.book_trip(1, 1)
                
                # Проверяем вызовы UPDATE и INSERT
                assert mock_cursor.execute.call_count >= 3
                
                # Проверяем результат
                assert result["destination"] == "Сочи"
                assert result["remaining_seats"] == 4
                assert result["user_name"] == "Иванов Иван"
    
    def test_book_trip_already_booked(self, mock_db_connection):
        """Тест бронирования уже забронированной путевки."""
        with patch.object(TripManager, 'check_booking_exists', return_value=True):
            with patch('app.lib.trip.DBConnection') as MockDB:
                trip_manager = TripManager()
                
                with pytest.raises(AlreadyBookedError) as exc_info:
                    trip_manager.book_trip(1, 1)
                
                assert "уже забронировал" in str(exc_info.value).lower()
    
    def test_book_trip_no_seats(self, mock_db_connection):
        """Тест бронирования путевки без свободных мест."""
        mock_conn, mock_cursor = mock_db_connection
        
        with patch.object(TripManager, 'check_booking_exists', return_value=False):
            mock_cursor.fetchone.return_value = (0,)  # available_seats = 0
            
            with patch('app.lib.trip.DBConnection') as MockDB:
                MockDB.return_value.get_connection.return_value = mock_conn
                
                trip_manager = TripManager()
                
                with pytest.raises(NoAvailableSeatsError) as exc_info:
                    trip_manager.book_trip(1, 3)  # Trip с ID 3 нет мест
                
                assert "все места" in str(exc_info.value).lower()
    
    def test_book_trip_trip_not_found(self, mock_db_connection):
        """Тест бронирования несуществующей путевки."""
        mock_conn, mock_cursor = mock_db_connection
        
        with patch.object(TripManager, 'check_booking_exists', return_value=False):
            mock_cursor.fetchone.return_value = None  # Путевка не найдена
            
            with patch('app.lib.trip.DBConnection') as MockDB:
                MockDB.return_value.get_connection.return_value = mock_conn
                
                trip_manager = TripManager()
                
                with pytest.raises(DatabaseError) as exc_info:
                    trip_manager.book_trip(1, 999)  # Несуществующий ID
                
                assert "Путевка не найдена" in str(exc_info.value)
    
    def test_get_user_bookings_success(self, mock_db_connection):
        """Тест получения бронирований пользователя."""
        mock_conn, mock_cursor = mock_db_connection
        sample_bookings = [
            (1, "Сочи", "2024-07-01", "2024-07-14", 45000.0, "2024-01-01 10:00:00"),
            (2, "Крым", "2024-07-05", "2024-07-19", 38000.0, "2024-01-02 11:00:00"),
        ]
        mock_cursor.fetchall.return_value = sample_bookings
        
        with patch('app.lib.trip.DBConnection') as MockDB:
            MockDB.return_value.get_connection.return_value = mock_conn
            
            trip_manager = TripManager()
            bookings = trip_manager.get_user_bookings(1)
            
            mock_cursor.execute.assert_called_once()
            assert "WHERE b.user_id = ?" in mock_cursor.execute.call_args[0][0]
            assert mock_cursor.execute.call_args[0][1] == (1,)
            
            assert len(bookings) == 2
            assert bookings[0][1] == "Сочи"
            assert bookings[1][1] == "Крым"