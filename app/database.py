from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Configuration spécifique pour SQLite (nécessaire pour l'asynchronisme de FastAPI)
engine_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, **engine_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dépendance pour injecter la session de base de données dans les routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
