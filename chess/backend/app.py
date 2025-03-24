import os
import chess
import datetime
from stockfish import Stockfish
from flask import Flask, request, jsonify
from flask_cors import CORS
import importlib.util
import sys
import traceback
from io import StringIO
from contextlib import contextmanager
from werkzeug.utils import secure_filename
from flask_login import login_required
from extensions import db, login_manager
from auth import auth_bp

app = Flask(__name__)
app.config.from_object('config.Config')

# Secure cookie settings
app.config['SESSION_COOKIE_SECURE'] = True  # Ensures cookies are sent over HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevents JavaScript from accessing cookies
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Restricts cross-site cookie sharing

CORS(app, supports_credentials=True,
     resources={r"/*": {"origins": "https://localhost:3000"}},
     allow_headers=["Content-Type", "Authorization"])

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)

# Register the auth blueprint
app.register_blueprint(auth_bp)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

GLOBAL_BOTS = {}

def get_stockfish_path():
    current_dir = os.getcwd()
    windows_path = r"D:\Cs495\ChessEngineComparator\chess\backend\stockfish\stockfish-windows-x86-64-avx2.exe"
    return windows_path

STOCKFISH_PATH = get_stockfish_path()

def create_bot_instance(filepath):
    # Load the bot dynamically
    spec = importlib.util.spec_from_file_location("bot", filepath)
    bot_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bot_module)

    # Get all classes defined in the module
    chess_bot_class = None
    for name, obj in bot_module.__dict__.items():
        if not isinstance(obj, type):
            continue
            
        # Create a temporary instance to check board attribute
        try:
            temp_instance = obj()
            has_required_attributes = (
                hasattr(temp_instance, 'board') and
                hasattr(obj, 'select_move') and callable(getattr(obj, 'select_move'))
            )
            
            if has_required_attributes:
                chess_bot_class = obj
                print(f"Found valid chess bot class: {name}")
                break
                
        except Exception as e:
            print(f"Error checking class {name}: {str(e)}")
            continue

    if not chess_bot_class:
        raise ValueError(
            "No valid chess bot class found. "
            "Your class must have a 'board' attribute and a 'select_move' method"
        )

    try:
        # Try to instantiate with stockfish_path
        return chess_bot_class(stockfish_path=STOCKFISH_PATH)
    except TypeError:
        try:
            # Fallback: try to instantiate without parameters
            return chess_bot_class()
        except Exception as e:
            raise ValueError(f"Failed to instantiate bot class: {str(e)}")

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
@login_required
def upload():
    try:
        file = request.files["file"]
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        print(f"Uploaded file saved to: {filepath}")  # Debugging log

        # Create bot instance
        bot_instance = create_bot_instance(filepath)
        
        # Store bot instance in global dictionary
        GLOBAL_BOTS[file.filename] = bot_instance
        print(f"Bot added to GLOBAL_BOTS: {file.filename}")  # Debugging log

        return jsonify({
            "filename": file.filename, 
            "initial_fen": bot_instance.board.fen()
        }), 200

    except Exception as e:
        print(f"Upload error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/make_move", methods=["POST"])
@login_required
def make_move():
    try:
        data = request.json
        filename = data.get("filename") or "default"
        user_move = data.get("user_move")

        print(f"Received move request: filename={filename}, move={user_move}")

        if filename not in GLOBAL_BOTS:
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
            bot.board.push(move)
            print(f"User move applied: {move}")

            if bot.board.is_game_over():
                return jsonify({
                    "valid": True, 
                    "fen": bot.board.fen(), 
                    "game_over": True, 
                    "result": bot.board.result()
                })

            bot_move = bot.select_move()
            bot.board.push(bot_move)
            print(f"Bot move: {bot_move}")

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
@login_required
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
@login_required
def remove_bot():
    try:
        data = request.json
        filename = data.get("filename")
        print(f"Attempting to remove bot: {filename}")  # Debugging log

        if filename in GLOBAL_BOTS:
            del GLOBAL_BOTS[filename]
            print(f"Removed bot from GLOBAL_BOTS: {filename}")  # Debugging log
            
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"Removed bot file from uploads: {filepath}")  # Debugging log
                
            return jsonify({"success": True, "message": "Bot removed successfully"})
        
        print(f"Bot not found in GLOBAL_BOTS: {filename}")  # Debugging log
        return jsonify({"success": False, "error": "Bot not found"}), 404
        
    except Exception as e:
        print(f"Remove bot error: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/run_tournament", methods=["GET"])
@login_required
def run_tournament():
    try:
        print("\n=== Tournament Execution Start ===")
        print(f"Current working directory: {os.getcwd()}")
        
        backend_dir = os.path.dirname(__file__)
        uploads_dir = os.path.join(backend_dir, "uploads")
        sys.path.append(backend_dir)
        sys.path.append(uploads_dir)
        print(f"Python path updated: {sys.path}")
        
        print("\nFiles in backend directory:")
        for file in os.listdir(backend_dir):
            print(f"- {file}")
            
        print("\nFiles in uploads directory:")
        for file in os.listdir(uploads_dir):
            print(f"- {file}")
        
        tournament_path = os.path.join(backend_dir, "tournament.py")
        print(f"\nLooking for tournament file at: {tournament_path}")
        
        if not os.path.exists(tournament_path):
            print(f"ERROR: Tournament file not found!")
            return jsonify({"error": f"Tournament file not found at {tournament_path}"}), 404
            
        print("Found tournament.py, checking dependencies...")
        
        dependencies = [('game_duel.py', backend_dir), ('chess_bot.py', uploads_dir)]
        missing_files = []
        for dep_file, dep_dir in dependencies:
            dep_path = os.path.join(dep_dir, dep_file)
            if os.path.exists(dep_path):
                print(f"✓ Found {dep_file} in {dep_dir}")
            else:
                print(f"✗ Missing {dep_file} in {dep_dir}")
                missing_files.append(f"{dep_file} in {dep_dir}")
        
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
            
            tournament_logs = output.getvalue()
            print(f"\nOutput captured successfully ({len(tournament_logs)} characters)")
            
            sys.path.remove(backend_dir)
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
    if not os.path.exists(STOCKFISH_PATH):
        print(f"Error: Stockfish executable not found at {STOCKFISH_PATH}")
    else:
        print(f"Using Stockfish path: {STOCKFISH_PATH}")

    default_bot_path = os.path.join(UPLOAD_FOLDER, "chess_game.py")
    if os.path.exists(default_bot_path):
        try:
            GLOBAL_BOTS["default"] = create_bot_instance(default_bot_path)
            print("Default bot loaded from uploads/chess_game.py")
        except Exception as e:
            print(f"Error loading default bot: {e}")
    else:
        print("No default bot found at uploads/chess_game.py")

    app.run(debug=True, ssl_context=('cert.pem', 'key.pem'))