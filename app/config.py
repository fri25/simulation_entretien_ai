import os
from dotenv import load_dotenv

# Charger les variables d'environnement du fichier .env
load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./simulation.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "digiinnova_super_secret_session_key_2026")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    LARAVEL_API_BASE_URL: str = os.getenv("LARAVEL_API_BASE_URL", "")
    LARAVEL_API_KEY: str = os.getenv("LARAVEL_API_KEY", "")

settings = Settings()
