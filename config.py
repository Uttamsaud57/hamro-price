import os


def get_database_url():
    url = os.environ.get('DATABASE_URL', '')
    # Render gives 'postgres://' but SQLAlchemy needs 'postgresql://'
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
    return url or 'sqlite:///hamro_price.db'


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'hamro-price-dev-secret-key')

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Mail (Gmail SMTP)
    MAIL_SERVER  = 'smtp.gmail.com'
    MAIL_PORT    = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME       = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD       = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME', 'noreply@hamroprice.com')
