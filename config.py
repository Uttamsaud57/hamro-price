import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Secret key — always set via environment variable in production
    SECRET_KEY = os.environ.get('SECRET_KEY', 'hamro-price-dev-secret-key')

    # Database — use DATABASE_URL env var on Render (PostgreSQL)
    # Falls back to local SQLite for development
    DATABASE_URL = os.environ.get('DATABASE_URL', '')

    if DATABASE_URL.startswith('postgres://'):
        # Render provides postgres:// but SQLAlchemy needs postgresql://
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_DATABASE_URI = DATABASE_URL or (
        'sqlite:///' + os.path.join(BASE_DIR, 'hamro_price.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Mail (Gmail SMTP)
    MAIL_SERVER  = 'smtp.gmail.com'
    MAIL_PORT    = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME       = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD       = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME', 'noreply@hamroprice.com')
