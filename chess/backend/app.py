import chess
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Store the latest valid FEN for each session
CURRENT_FENS = {}

def is_valid_fen(fen):
    """Checks if a FEN string is valid using python-chess."""
    try:
        board = chess.Board(fen)
        return board.is_valid()
    except ValueError:
        return False

@app.route("/update_fen", methods=["POST"])
def update_fen():
    """Receives FEN from the front-end (user) or bot, validates it, and updates the game state."""
    try:
        data = request.json
        session_id = data.get("session_id")
        fen = data.get("fen")

        if not session_id or not fen:
            return jsonify({"error": "Missing session_id or FEN"}), 400

        if not is_valid_fen(fen):
            return jsonify({"error": "Invalid FEN"}), 400

        CURRENT_FENS[session_id] = fen  # Store the latest valid FEN
        return jsonify({"success": True, "fen": fen})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get_fen", methods=["GET"])
def get_fen():
    """Returns the latest FEN for a given session."""
    session_id = request.args.get("session_id")

    if not session_id or session_id not in CURRENT_FENS:
        return jsonify({"error": "Session not found"}), 400

    return jsonify({"fen": CURRENT_FENS[session_id]})

@app.route("/new_game", methods=["POST"])
def new_game():
    """Resets the game to the starting position."""
    try:
        data = request.json
        session_id = data.get("session_id")

        if not session_id:
            return jsonify({"error": "Missing session_id"}), 400

        starting_fen = chess.Board().fen()
        CURRENT_FENS[session_id] = starting_fen  # Reset game state

        return jsonify({"success": True, "fen": starting_fen})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
