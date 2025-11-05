import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DB_PATH = os.path.join(BASE_DIR, os.getenv('DB_PATH', 'data/travel_planner.db'))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

settings = Settings()