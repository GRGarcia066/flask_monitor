import os

class Config(object):
    # Statement for enabling the development environment
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True

    # Define the application directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # True if ssl
    SECURE_CONNECTION  = False

    # ssl context
    SERVER_CERT_PATH = os.path.join(BASE_DIR, 'certs/server.crt')
    SERVER_KEY_PATH = os.path.join(BASE_DIR, 'certs/server.key')

    # Define the database - we are working with
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
    DATABASE_CONNECT_OPTIONS = {}

    # Application threads. A common general assumption is
    # using 2 per available processor cores - to handle
    # incoming requests using one and performing background
    # operations using the other.
    THREADS_PER_PAGE = 2

    # Enable protection agains *Cross-site Request Forgery (CSRF)*
    CSRF_ENABLED = True

    # Use a secure, unique and absolutely secret key for signing the data. 
    CSRF_SESSION_KEY = os.environ.get('CSRF_SESSION_KEY') or "you-shall-not-pass"  # Change this!

    # Secret key for signing cookies
    SECRET_KEY = os.environ.get('SECRET_KEY') or "you-shall-not-pass"  # Change this!

    # Secret key for WTF
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY') or 'you-shall-not-pass'  # Change this!

    # Upload forlder for assets
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')

    # Screenly
    SCREENLY_ASSET_DEFAULT_DURATION = 30
    SCREENLY_CONNECTION_TIMEOUT = 5
    SCREENLY_SECURE_CONNECTION = True

    # Allowed extensions of assets
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4'}

    # Get notified before and after changes are committed to the database
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class UnitTestConfig(object):
    # Define the application directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # Define the database - we are working with
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'test.db')

    # Secret key for signing cookies
    SECRET_KEY = "you-shall-not-pass"

    TESTING = True
    LOGIN_DISABLED = True
    WTF_CSRF_ENABLED = False
    DEBUG = False
    
    # Get notified before and after changes are committed to the database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
