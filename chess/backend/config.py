import os
from dotenv import load_dotenv
import urllib.parse

# Get the backend directory path
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
# Get the root directory (ChessEngineComparator) where .env is located
ROOT_DIR = os.path.dirname(os.path.dirname(BACKEND_DIR))
# Load .env from the root directory
load_dotenv(os.path.join(ROOT_DIR, '.env'))

class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    
    # Database configuration
    db_password = os.getenv('DB_PASSWORD')
    if db_password is None:
        raise ValueError("Environment variable 'DB_PASSWORD' is not set or is empty.")
    
    # Ensure db_password is a string before encoding
    encoded_password = urllib.parse.quote_plus(str(db_password))
    SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{encoded_password}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Google OAuth config
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    REDIRECT_URI = os.getenv('REDIRECT_URI')