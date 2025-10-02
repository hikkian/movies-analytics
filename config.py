# config.py
from sqlalchemy import create_engine

DB_CONFIG = {
    "dbname": "movies_db",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432
}

# Создаём строку подключения
DB_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"

# Создаём движок SQLAlchemy
engine = create_engine(DB_URL)