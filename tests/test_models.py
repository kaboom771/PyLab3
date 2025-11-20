import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.models import TRIPS_TABLE, USERS_TABLE, BOOKINGS_TABLE

class TestDatabaseModels:
    """Тесты SQL моделей базы данных."""
    
    def test_trips_table_structure(self):
        """Тест структуры таблицы путевок."""
        assert "CREATE TABLE IF NOT EXISTS trips" in TRIPS_TABLE
        assert "id INTEGER PRIMARY KEY AUTOINCREMENT" in TRIPS_TABLE
        assert "destination TEXT NOT NULL" in TRIPS_TABLE
        assert "start_date TEXT NOT NULL" in TRIPS_TABLE
        assert "end_date TEXT NOT NULL" in TRIPS_TABLE
        assert "price REAL NOT NULL" in TRIPS_TABLE
        assert "total_seats INTEGER NOT NULL" in TRIPS_TABLE
        assert "available_seats INTEGER NOT NULL" in TRIPS_TABLE
    
    def test_users_table_structure(self):
        """Тест структуры таблицы пользователей."""
        assert "CREATE TABLE IF NOT EXISTS users" in USERS_TABLE
        assert "id INTEGER PRIMARY KEY AUTOINCREMENT" in USERS_TABLE
        assert "full_name TEXT NOT NULL UNIQUE" in USERS_TABLE
    
    def test_bookings_table_structure(self):
        """Тест структуры таблицы бронирований."""
        assert "CREATE TABLE IF NOT EXISTS bookings" in BOOKINGS_TABLE
        assert "id INTEGER PRIMARY KEY AUTOINCREMENT" in BOOKINGS_TABLE
        assert "user_id INTEGER NOT NULL" in BOOKINGS_TABLE
        assert "trip_id INTEGER NOT NULL" in BOOKINGS_TABLE
        assert "FOREIGN KEY (user_id) REFERENCES users (id)" in BOOKINGS_TABLE
        assert "FOREIGN KEY (trip_id) REFERENCES trips (id)" in BOOKINGS_TABLE
        assert "UNIQUE(user_id, trip_id)" in BOOKINGS_TABLE  # Предотвращение дублей