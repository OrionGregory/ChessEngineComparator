import os
import chess
from stockfish import Stockfish
from flask import Flask, request, jsonify
from flask_cors import CORS
import importlib.util
import sys
import traceback

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Directory where chess bot files will be uploaded
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global dictionary to store bot instances
GLOBAL_BOTS = {}

def get_stockfish_path():
    current_dir = os.getcwd()
    windows_path = os.path.join(current_dir, r"stockfish\stockfish-windows-x86-64-avx2.exe")
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
        filename = data.get("filename")
        user_move = data.get("user_move")

        print(f"Received move request: filename={filename}, move={user_move}")

        # Check if bot exists, if not, try to recreate it
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
        filename = data.get("filename")

        if filename not in GLOBAL_BOTS:
            # Try to recreate the bot
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

if __name__ == "__main__":
    # Check if the Stockfish executable exists at the given path
    if not os.path.exists(STOCKFISH_PATH):
        print(f"Error: Stockfish executable not found at {STOCKFISH_PATH}")
    else:
        print(f"Using Stockfish path: {STOCKFISH_PATH}")

    app.run(debug=True, port=5000)