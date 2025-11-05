import logging
import os
from datetime import datetime
from app.config.settings import settings

def setup_logger():
    """Настройка и возврат логгера."""
    # Создаем папку для логов, если её нет
    logs_dir = os.path.join(settings.BASE_DIR, 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    log_filename = f"logs/travel_planner_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Преобразуем строковый уровень в числовой
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('TravelPlanner')