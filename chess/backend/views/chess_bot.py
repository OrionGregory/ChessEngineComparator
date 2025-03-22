from flask import Blueprint, request, jsonify
import os
import chess
import importlib.util
import sys
import traceback
import datetime

chess_bot_bp = Blueprint('chess_bot', __name__)

@chess_bot_bp.route('/upload', methods=['POST'])
def upload():
    try:
        # Lazy imports
        from app import create_bot_instance, GLOBAL_BOTS, UPLOAD_FOLDER
        file = request.files["file"]
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        bot_instance = create_bot_instance(filepath)
        GLOBAL_BOTS[file.filename] = bot_instance

        return jsonify({
            "filename": file.filename, 
            "initial_fen": bot_instance.board.fen()
        }), 200

    except Exception as e:
        print(f"Upload error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@chess_bot_bp.route('/make_move', methods=['POST'])
def make_move():
    try:
        data = request.json
        filename = data.get("filename") or "default"
        user_move = data.get("user_move")

        # Lazy imports
        from app import create_bot_instance, GLOBAL_BOTS, UPLOAD_FOLDER

        if filename not in GLOBAL_BOTS:
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.exists(filepath):
                try:
                    GLOBAL_BOTS[filename] = create_bot_instance(filepath)
                except Exception as e:
                    return jsonify({"error": "Bot recreation failed", "valid": False}), 400
            else:
                return jsonify({"error": "Bot not found", "valid": False}), 400

        bot = GLOBAL_BOTS[filename]
        move = chess.Move.from_uci(user_move)

        if move in bot.board.legal_moves:
            bot.board.push(move)

            if bot.board.is_game_over():
                return jsonify({
                    "valid": True, 
                    "fen": bot.board.fen(), 
                    "game_over": True, 
                    "result": bot.board.result()
                })

            bot_move = bot.select_move()
            bot.board.push(bot_move)

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

@chess_bot_bp.route('/get_fen', methods=['POST'])
def get_fen():
    try:
        data = request.json
        filename = data.get("filename") or "default"

        # Lazy imports
        from app import create_bot_instance, GLOBAL_BOTS, UPLOAD_FOLDER

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

@chess_bot_bp.route('/remove_bot', methods=['POST'])
def remove_bot():
    try:
        data = request.json
        filename = data.get("filename")
        
        # Lazy imports
        from app import GLOBAL_BOTS, UPLOAD_FOLDER
        
        if filename in GLOBAL_BOTS:
            del GLOBAL_BOTS[filename]
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({"success": True, "message": "Bot removed successfully"})
        
        return jsonify({"success": False, "error": "Bot not found"}), 404
        
    except Exception as e:
        print(f"Remove bot error: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@chess_bot_bp.route('/run_tournament', methods=['GET'])
def run_tournament():
    try:
        uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
        sys.path.append(uploads_dir)
        
        tournament_path = os.path.join(uploads_dir, "tournament.py")
        if not os.path.exists(tournament_path):
            return jsonify({"error": f"Tournament file not found at {tournament_path}"}), 404
        
        dependencies = ['game_duel.py', 'chess_bot.py']
        missing_files = []
        for dep in dependencies:
            dep_path = os.path.join(uploads_dir, dep)
            if not os.path.exists(dep_path):
                missing_files.append(dep)
        
        if missing_files:
            error_msg = f"Missing required files: {', '.join(missing_files)}"
            return jsonify({"error": error_msg}), 404
        
        # Lazy import capture_output from app
        from app import capture_output
        
        with capture_output() as output:
            try:
                spec = importlib.util.spec_from_file_location("tournament", tournament_path)
                tournament_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(tournament_module)
            except Exception as e:
                raise
            tournament_logs = output.getvalue()
            sys.path.remove(uploads_dir)
            return jsonify({
                "output": tournament_logs,
                "status": "completed",
                "timestamp": datetime.datetime.now().isoformat()
            })
            
    except Exception as e:
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc(),
            "status": "failed"
        }), 500