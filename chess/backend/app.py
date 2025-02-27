import os
import chess
from stockfish import Stockfish
from flask import Flask, request, jsonify
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

@app.route("/run_bot_command", methods=["POST"])
@jwt_required()
def run_bot_command():
    user_id = get_jwt_identity()  # Authenticated user's id
    data = request.json
    file_id = data.get("file_id")
    if not file_id:
        return jsonify({"error": "file_id is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Ensure the file belongs to the current user
        cursor.execute(
            "SELECT filename, filepath FROM user_files WHERE id = %s AND user_id = %s",
            (file_id, user_id)
        )
        file_record = cursor.fetchone()
        if not file_record:
            return jsonify({"error": "File not found or access denied"}), 404
        
        # Get the file path and load the chess bot dynamically
        filepath = file_record['filepath']
        bot_instance = create_bot_instance(filepath)
        
        # Execute a command: for example, let the bot select a move.
        move = bot_instance.select_move()
        bot_instance.board.push(move)
        
        return jsonify({
            "message": "Bot command executed successfully",
            "move": str(move),
            "fen": bot_instance.board.fen()
        }), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route("/my_files", methods=["GET"])
@jwt_required()
def my_files():
    user_id = get_jwt_identity()  # Current user's id (as a string)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, filename, filepath, uploaded_at FROM user_files WHERE user_id = %s",
            (user_id,)
        )
        files = cursor.fetchall()
        return jsonify({"files": files}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route("/upload_file", methods=["POST"])
@jwt_required()
def upload_file():
    # Get the authenticated user's id from the JWT
    user_id = get_jwt_identity()
    
    # Check if a file was sent with the request
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    # Secure the filename and determine the file path
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    try:
        # Save the file to disk
        file.save(filepath)
    except Exception as e:
        return jsonify({"error": f"File saving failed: {str(e)}"}), 500

    # Save file metadata to the database
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO user_files (user_id, filename, filepath) VALUES (%s, %s, %s) RETURNING id",
            (user_id, filename, filepath)
        )
        file_id = cursor.fetchone()['id']
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Database insert failed: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "File uploaded successfully", "file_id": file_id}), 201

# Database connection
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

# User Registration
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    email = data['email']  # New: extract email from the request
    password = data['password']
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)',
            (username, email, hashed_password)
        )
        conn.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# User Login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    # Use 'password_hash' when checking the password
    if user and bcrypt.check_password_hash(user['password_hash'], password):
        access_token = create_access_token(identity=str(user['id']))
        return jsonify({'token': access_token}), 200
    return jsonify({'error': 'Invalid username or password'}), 401

def get_stockfish_path():
    current_dir = os.getcwd()
    windows_path = "/home/orion/ChessEngineComparator/stockfish/stockfish-ubuntu-x86-64-avx2"
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

@app.route("/upload", methods=["POST"])
def upload():
    try:
        file = request.files["file"]
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # Create bot instance
        bot_instance = create_bot_instance(filepath)
        
        # Store bot instance in global dictionary
        GLOBAL_BOTS[file.filename] = bot_instance

        return jsonify({
            "filename": file.filename, 
            "initial_fen": bot_instance.board.fen()
        }), 200

    except Exception as e:
        print(f"Upload error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/make_move", methods=["POST"])
def make_move():
    try:
        data = request.json
        # Use default when filename is None or falsy
        filename = data.get("filename") or "default"
        user_move = data.get("user_move")

        print(f"Received move request: filename={filename}, move={user_move}")

        # Check if bot exists, if not, try to recreate it using default or uploaded file
        if filename not in GLOBAL_BOTS:
            # Find the uploaded file
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.exists(filepath):
                try:
                    GLOBAL_BOTS[filename] = create_bot_instance(filepath)
                except Exception as e:
                    print(f"Failed to recreate bot: {e}")
                    return jsonify({"error": "Bot recreation failed", "valid": False}), 400
            else:
                print(f"Bot file not found: {filename}")
                return jsonify({"error": "Bot not found", "valid": False}), 400

        bot = GLOBAL_BOTS[filename]
        move = chess.Move.from_uci(user_move)

        if move in bot.board.legal_moves:
            bot.board.push(move)  # Apply user move
            print(f"User move applied: {move}")

            # Check if game is over after user move
            if bot.board.is_game_over():
                return jsonify({
                    "valid": True, 
                    "fen": bot.board.fen(), 
                    "game_over": True, 
                    "result": bot.board.result()
                })

            # Bot responds
            bot_move = bot.select_move()
            bot.board.push(bot_move)
            print(f"Bot move: {bot_move}")

            # Check if game is over after bot move
            if bot.board.is_game_over():
                return jsonify({
                    "valid": True, 
                    "fen": bot.board.fen(), 
                    "game_over": True, 
                    "result": bot.board.result()
                })

            return jsonify({
                "valid": True, 
                "fen": bot.board.fen(), 
                "game_over": False
            })
        
        return jsonify({"valid": False})
    
    except Exception as e:
        print(f"Move error: {e}")
        traceback.print_exc()
        return jsonify({"valid": False, "error": str(e)})

@app.route("/get_fen", methods=["POST"])
def get_fen():
    try:
        data = request.json
        filename = data.get("filename") or "default"

        if filename not in GLOBAL_BOTS:
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.exists(filepath):
                GLOBAL_BOTS[filename] = create_bot_instance(filepath)
            else:
                return jsonify({"error": "Bot not found"}), 400

        bot = GLOBAL_BOTS[filename]
        return jsonify({"fen": bot.board.fen()})
    
    except Exception as e:
        print(f"Get FEN error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/remove_bot", methods=["POST"])
def remove_bot():
    try:
        data = request.json
        filename = data.get("filename")
        
        if filename in GLOBAL_BOTS:
            del GLOBAL_BOTS[filename]
            
            # Remove the file from uploads folder
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                
            return jsonify({"success": True, "message": "Bot removed successfully"})
        
        return jsonify({"success": False, "error": "Bot not found"}), 404
        
    except Exception as e:
        print(f"Remove bot error: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/run_tournament", methods=["GET"])
def run_tournament():
    try:
        print("\n=== Tournament Execution Start ===")
        print(f"Current working directory: {os.getcwd()}")
        
        # Add the uploads directory to Python path
        uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
        sys.path.append(uploads_dir)
        print(f"Python path updated: {sys.path}")
        
        # List files in uploads directory
        print("\nFiles in uploads directory:")
        for file in os.listdir(uploads_dir):
            print(f"- {file}")
        
        # Use absolute path to tournament.py
        tournament_path = os.path.join(uploads_dir, "tournament.py")
        print(f"\nLooking for tournament file at: {tournament_path}")
        
        if not os.path.exists(tournament_path):
            print(f"ERROR: Tournament file not found!")
            return jsonify({"error": f"Tournament file not found at {tournament_path}"}), 404
            
        print("Found tournament.py, checking dependencies...")
        
        # Check for required files with detailed logging
        dependencies = ['game_duel.py', 'chess_bot.py']
        missing_files = []
        for dep in dependencies:
            dep_path = os.path.join(uploads_dir, dep)
            if os.path.exists(dep_path):
                print(f"✓ Found {dep}")
            else:
                print(f"✗ Missing {dep}")
                missing_files.append(dep)
        
        if missing_files:
            error_msg = f"Missing required files: {', '.join(missing_files)}"
            print(f"\nERROR: {error_msg}")
            return jsonify({"error": error_msg}), 404
            
        print("\nAll dependencies found, starting tournament...")
        
        with capture_output() as output:
            try:
                print("Importing tournament module...")
                spec = importlib.util.spec_from_file_location("tournament", tournament_path)
                tournament_module = importlib.util.module_from_spec(spec)
                print("Executing tournament module...")
                spec.loader.exec_module(tournament_module)
                print("Tournament execution completed successfully")
            except Exception as e:
                print(f"ERROR during tournament execution: {str(e)}")
                traceback.print_exc()
                raise
            
            # Get the captured output
            tournament_logs = output.getvalue()
            print(f"\nOutput captured successfully ({len(tournament_logs)} characters)")
            
            # Remove the uploads directory from Python path
            sys.path.remove(uploads_dir)
            
            return jsonify({
                "output": tournament_logs,
                "status": "completed",
                "timestamp": datetime.datetime.now().isoformat()
            })
            
    except Exception as e:
        error_msg = f"Tournament error: {str(e)}\n{traceback.format_exc()}"
        print(f"\nERROR: {error_msg}")
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc(),
            "status": "failed"
        }), 500

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