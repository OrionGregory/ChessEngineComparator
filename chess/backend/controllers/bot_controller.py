from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
import os, sys, traceback, datetime
import chess
import importlib.util
from contextlib import contextmanager
from services import chess_bot_service
from werkzeug.utils import secure_filename
from models import User
from extensions import db

bot_bp = Blueprint("bot", __name__)

@bot_bp.route("/upload", methods=["POST"])
@login_required
def upload():
    try:
        file = request.files["file"]
        if not file:
            return jsonify({"error": "No file provided"}), 400

        filename = secure_filename(file.filename)
        os.makedirs(chess_bot_service.UPLOAD_FOLDER, exist_ok=True)
        filepath = os.path.join(chess_bot_service.UPLOAD_FOLDER, filename)
        file.save(filepath)

        if not os.path.exists(filepath):
            return jsonify({"error": f"Failed to save file at {filepath}"}), 500

        try:
            bot_instance = chess_bot_service.create_bot_instance(filepath)
            chess_bot_service.GLOBAL_BOTS[filename] = bot_instance
            return jsonify({"filename": filename, "initial_fen": bot_instance.board.fen()}), 200
        except Exception as e:
            # Remove the file if bot creation fails
            if os.path.exists(filepath):
                os.remove(filepath)
            traceback.print_exc()
            return jsonify({"error": f"File uploaded but bot creation failed: {str(e)}"}), 500

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@bot_bp.route("/make_move", methods=["POST"])
@login_required
def make_move():
    try:
        data = request.json
        filename = data.get("filename") or "default"
        user_move = data.get("user_move")

        if filename not in chess_bot_service.GLOBAL_BOTS:
            filepath = os.path.join(chess_bot_service.UPLOAD_FOLDER, filename)
            if os.path.exists(filepath):
                try:
                    chess_bot_service.GLOBAL_BOTS[filename] = chess_bot_service.create_bot_instance(filepath)
                except Exception as e:
                    return jsonify({"error": "Bot recreation failed", "valid": False}), 400
            else:
                return jsonify({"error": "Bot not found", "valid": False}), 400

        bot = chess_bot_service.GLOBAL_BOTS[filename]
        move = chess.Move.from_uci(user_move)

        if move in bot.board.legal_moves:
            bot.board.push(move)
            if bot.board.is_game_over():
                return jsonify({"valid": True, "fen": bot.board.fen(), "game_over": True, "result": bot.board.result()})
            bot_move = bot.select_move()
            bot.board.push(bot_move)
            if bot.board.is_game_over():
                return jsonify({"valid": True, "fen": bot.board.fen(), "game_over": True, "result": bot.board.result()})
            return jsonify({"valid": True, "fen": bot.board.fen(), "game_over": False})
        
        return jsonify({"valid": False})
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({"valid": False, "error": str(e)})

@bot_bp.route("/get_fen", methods=["POST"])
@login_required
def get_fen():
    try:
        data = request.json
        filename = data.get("filename") or "default"

        if filename not in chess_bot_service.GLOBAL_BOTS:
            filepath = os.path.join(chess_bot_service.UPLOAD_FOLDER, filename)
            if os.path.exists(filepath):
                chess_bot_service.GLOBAL_BOTS[filename] = chess_bot_service.create_bot_instance(filepath)
            else:
                return jsonify({"error": "Bot not found"}), 400

        bot = chess_bot_service.GLOBAL_BOTS[filename]
        return jsonify({"fen": bot.board.fen()})
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@bot_bp.route("/remove_bot", methods=["POST"])
@login_required
def remove_bot():
    try:
        data = request.json
        filename = data.get("filename")

        if filename in chess_bot_service.GLOBAL_BOTS:
            del chess_bot_service.GLOBAL_BOTS[filename]
            filepath = os.path.join(chess_bot_service.UPLOAD_FOLDER, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({"success": True, "message": "Bot removed successfully"})
        return jsonify({"success": False, "error": "Bot not found"}), 404
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@bot_bp.route("/run_tournament", methods=["GET"])
@login_required
def run_tournament():
    try:
        backend_dir = os.path.dirname(__file__).replace(r"\controllers", "")
        uploads_dir = chess_bot_service.UPLOAD_FOLDER
        sys.path.extend([backend_dir, uploads_dir])
        
        tournament_path = os.path.join(backend_dir, "tournament.py")
        if not os.path.exists(tournament_path):
            return jsonify({"error": f"Tournament file not found at {tournament_path}"}), 404

        dependencies = [('game_duel.py', backend_dir), ('chess_bot.py', uploads_dir)]
        missing_files = []
        for dep_file, dep_dir in dependencies:
            if not os.path.exists(os.path.join(dep_dir, dep_file)):
                missing_files.append(f"{dep_file} in {dep_dir}")
        if missing_files:
            return jsonify({"error": f"Missing required files: {', '.join(missing_files)}"}), 404

        with chess_bot_service.capture_output() as output:
            try:
                spec = importlib.util.spec_from_file_location("tournament", tournament_path)
                tournament_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(tournament_module)
            except Exception as e:
                traceback.print_exc()
                raise
            tournament_logs = output.getvalue()
            sys.path.remove(backend_dir)
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

@bot_bp.route("/update_profile", methods=["POST", "OPTIONS"])
@login_required
def update_profile():
    if request.method == "OPTIONS":
        return current_app.make_default_options_response()
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        new_username = data.get("username")
        if not new_username:
            return jsonify({"success": False, "error": "Username cannot be empty"}), 400
        existing_user = User.query.filter(User.username == new_username, User.id != current_user.id).first()
        if existing_user:
            return jsonify({"success": False, "error": "Username already taken"}), 400
        user = User.query.get(current_user.id)
        old_username = user.username
        user.username = new_username
        db.session.commit()
        return jsonify({"success": True, "message": "Profile updated successfully"})
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500
