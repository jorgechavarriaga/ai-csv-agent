import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config.settings import settings


encoded_pass = urllib.parse.quote_plus(settings.POSTGRES_PASSWORD.get_secret_value())
DATABASE_URL = (
    f"postgresql+psycopg://{settings.POSTGRES_USER}:{encoded_pass}@"
    f"{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)

# SQLAlchemy Base + engine + session factory
engine = create_engine(
    DATABASE_URL,
    echo=False,          # Keep False in production
    future=True,
    pool_pre_ping=True,  # Ensures stale connections are recycled automatically
    pool_size=10,        # Max number of connections in pool
    max_overflow=20      # Extra connections allowed beyond pool_size
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
