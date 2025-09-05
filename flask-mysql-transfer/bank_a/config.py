import os

class Config:
    # Config DB (usar variables de entorno o defaults)
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_NAME = os.getenv("DB_NAME", "bank_a_db")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # URL base de la otra API (p.ej. http://127.0.0.1:5001)
    DEST_API_BASE = os.getenv("DEST_API_BASE", "http://127.0.0.1:5001")

    # Este banco (para identificar remitente)
    BANK_NAME = os.getenv("BANK_NAME", "BANK_A")

    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")

    # Puerto sugerido para correr esta app
    FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
