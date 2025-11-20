import pytest
import sys
import os
from unittest.mock import Mock, MagicMock

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def mock_db_connection():
    """Фикстура для мока подключения к БД."""
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor

@pytest.fixture
def sample_trips_data():
    """Фикстура с тестовыми данными путевок."""
    return [
        (1, "Сочи", "2024-07-01", "2024-07-14", 45000.0, 20, 15),
        (2, "Крым", "2024-07-05", "2024-07-19", 38000.0, 15, 10),
        (3, "Турция", "2024-07-10", "2024-07-24", 75000.0, 25, 0),  # Нет мест
    ]

@pytest.fixture
def sample_users_data():
    """Фикстура с тестовыми данными пользователей."""
    return [
        (1, "Иванов Иван Иванович"),
        (2, "Петрова Анна Сергеевна"),
    ]

@pytest.fixture
def sample_bookings_data():
    """Фикстура с тестовыми данными бронирований."""
    return [
        (1, 1, 1, "2024-01-01 10:00:00"),  # User1 -> Trip1
        (2, 2, 1, "2024-01-02 11:00:00"),  # User2 -> Trip1
    ]