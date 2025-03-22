import datetime
import os
import chess
from stockfish import Stockfish
from flask import Flask, request, jsonify, url_for, session, redirect
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import importlib.util
import sys
import traceback
from io import StringIO
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth

load_dotenv()

app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
jwt = JWTManager(app)

DATABASE_URL = os.getenv('DATABASE_URL')

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

GLOBAL_BOTS = {}

# Add OAuth configuration
oauth = OAuth(app)

# Configure OAuth providers
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope': 'openid email profile'},
)

# Import views
from views.google_oauth import google_login, google_authorize
from views.bot_commands import run_bot_command, upload_file, my_files
from views.user_auth import register, login
from views.chess_bot import upload, make_move, get_fen, remove_bot, run_tournament

# Register routes
app.add_url_rule('/login/google', view_func=google_login)
app.add_url_rule('/login/google/callback', view_func=google_authorize)
app.add_url_rule('/run_bot_command', view_func=run_bot_command, methods=['POST'])
app.add_url_rule('/upload_file', view_func=upload_file, methods=['POST'])
app.add_url_rule('/my_files', view_func=my_files, methods=['GET'])
app.add_url_rule('/register', view_func=register, methods=['POST'])
app.add_url_rule('/login', view_func=login, methods=['POST'])
app.add_url_rule('/upload', view_func=upload, methods=['POST'])
app.add_url_rule('/make_move', view_func=make_move, methods=['POST'])
app.add_url_rule('/get_fen', view_func=get_fen, methods=['POST'])
app.add_url_rule('/remove_bot', view_func=remove_bot, methods=['POST'])
app.add_url_rule('/run_tournament', view_func=run_tournament, methods=['GET'])

def get_stockfish_path():
    current_dir = os.getcwd()
    windows_path = r"C:\ChessEngineComparator\ChessEngineComparator\chess\backend\stockfish\stockfish-windows-x86-64-avx2.exe"
    return windows_path

STOCKFISH_PATH = get_stockfish_path()

def create_bot_instance(filepath):
    # Load the bot dynamically
    spec = importlib.util.spec_from_file_location("bot", filepath)
    bot_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bot_module)

    # Improved class detection
    chess_bot_class = None
    
    # Check if the exact class name is 'SimpleChessBot'
    if hasattr(bot_module, 'SimpleChessBot'):
        chess_bot_class = bot_module.SimpleChessBot
    else:
        # Fallback: find any class with these key methods
        for name, obj in bot_module.__dict__.items():
            if (isinstance(obj, type) and 
                hasattr(obj, '__init__') and 
                hasattr(obj, 'select_move') and 
                hasattr(obj, 'board')):
                chess_bot_class = obj
                break

    if not chess_bot_class:
        raise ValueError(
            "No valid chess bot class found. "
            "Your class must have methods: __init__, select_move, and attribute: board"
        )

    # Instantiate the chess bot with the correct Stockfish path
    return chess_bot_class(stockfish_path=STOCKFISH_PATH)

@contextmanager
def capture_output():
    new_out = StringIO()
    old_out = sys.stdout
    sys.stdout = new_out
    try:
        yield new_out
    finally:
        sys.stdout = old_out

if __name__ == "__main__":
    # Check if the Stockfish executable exists at the given path
    if not os.path.exists(STOCKFISH_PATH):
        print(f"Error: Stockfish executable not found at {STOCKFISH_PATH}")
    else:
        print(f"Using Stockfish path: {STOCKFISH_PATH}")

    # Preload the default bot from uploads/chess_game.py if it exists
    default_bot_path = os.path.join(UPLOAD_FOLDER, "chess_game.py")
    if os.path.exists(default_bot_path):
        try:
            GLOBAL_BOTS["default"] = create_bot_instance(default_bot_path)
            print("Default bot loaded from uploads/chess_game.py")
        except Exception as e:
            print(f"Error loading default bot: {e}")
    else:
        print("No default bot found at uploads/chess_game.py")

    app.run(debug=True, port=5000)