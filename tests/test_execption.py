import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.lib.exceptions import (
    TravelAppError, 
    NoAvailableSeatsError, 
    DatabaseError, 
    AlreadyBookedError
)

class TestExceptions:
    """Тесты пользовательских исключений."""
    
    def test_travel_app_error(self):
        """Тест базового исключения приложения."""
        with pytest.raises(TravelAppError):
            raise TravelAppError("Базовая ошибка")
    
    def test_no_available_seats_error(self):
        """Тест исключения при отсутствии мест."""
        with pytest.raises(NoAvailableSeatsError) as exc_info:
            raise NoAvailableSeatsError("Места закончились")
        assert "Места закончились" in str(exc_info.value)
        assert isinstance(exc_info.value, TravelAppError)
    
    def test_database_error(self):
        """Тест исключения для ошибок БД."""
        with pytest.raises(DatabaseError) as exc_info:
            raise DatabaseError("Ошибка БД")
        assert "Ошибка БД" in str(exc_info.value)
        assert isinstance(exc_info.value, TravelAppError)
    
    def test_already_booked_error(self):
        """Тест исключения при повторном бронировании."""
        with pytest.raises(AlreadyBookedError) as exc_info:
            raise AlreadyBookedError("Уже забронировано")
        assert "Уже забронировано" in str(exc_info.value)
        assert isinstance(exc_info.value, TravelAppError)