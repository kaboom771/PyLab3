class TravelAppError(Exception):
    """Базовое исключение для приложения."""
    pass

class NoAvailableSeatsError(TravelAppError):
    """Исключение когда нет доступных мест."""
    pass

class DatabaseError(TravelAppError):
    """Исключение для ошибок базы данных."""
    pass