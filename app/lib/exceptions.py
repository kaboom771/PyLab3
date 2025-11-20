class TravelAppError(Exception):
    """Базовое исключение для приложения."""
    pass

class NoAvailableSeatsError(TravelAppError):
    """Исключение когда нет доступных мест."""
    pass

class DatabaseError(TravelAppError):
    """Исключение для ошибок базы данных."""
    pass

class AlreadyBookedError(TravelAppError):
    """Исключение когда пользователь уже бронировал эту путевку."""
    pass