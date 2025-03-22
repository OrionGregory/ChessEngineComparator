from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import get_db_connection, create_bot_instance, UPLOAD_FOLDER
from werkzeug.utils import secure_filename
import os

@jwt_required()
def run_bot_command():
    user_id = get_jwt_identity()
    data = request.json
    file_id = data.get("file_id")
    if not file_id:
        return jsonify({"error": "file_id is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT filename, filepath FROM user_files WHERE id = %s AND user_id = %s",
            (file_id, user_id)
        )
        file_record = cursor.fetchone()
        if not file_record:
            return jsonify({"error": "File not found or access denied"}), 404
        
        filepath = file_record['filepath']
        bot_instance = create_bot_instance(filepath)
        
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

@jwt_required()
def upload_file():
    user_id = get_jwt_identity()
    
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    try:
        file.save(filepath)
    except Exception as e:
        return jsonify({"error": f"File saving failed: {str(e)}"}), 500

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

@jwt_required()
def my_files():
    user_id = get_jwt_identity()
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
