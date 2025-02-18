import requests
import time
import chess
import random

SESSION_ID = "test_session"  # Unique game session ID
SERVER_URL_UPDATE = "http://localhost:5000/update_fen"
SERVER_URL_GET = "http://localhost:5000/get_fen"

board = chess.Board()

piece_values = {
    chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5,
    chess.QUEEN: 9, chess.KING: 0  # King is invaluable
}

def evaluate_move(move):
    """Assigns a basic score to a move based on piece captures."""
    if board.is_capture(move):
        captured_piece = board.piece_at(move.to_square)
        if captured_piece:
            return piece_values.get(captured_piece.piece_type, 0)
    return 0

def select_move():
    """Selects the best move based on simple evaluation."""
    legal_moves = list(board.legal_moves)
    
    # Score moves based on captures
    best_moves = sorted(legal_moves, key=lambda move: evaluate_move(move), reverse=True)
    
    # Play a high-value move, but add randomness
    if best_moves:
        return random.choice(best_moves[:3])  # Random among top 3 moves

    return random.choice(legal_moves)  # Otherwise, play any legal move

def send_fen():
    """Sends the current FEN to the backend."""
    fen = board.fen()
    response = requests.post(SERVER_URL_UPDATE, json={"session_id": SESSION_ID, "fen": fen})
    print("Sent FEN:", response.json())

def get_fen():
    """Fetches the latest FEN from the backend."""
    try:
        response = requests.get(SERVER_URL_GET, params={"session_id": SESSION_ID})
        data = response.json()
        if "fen" in data:
            return data["fen"]
    except Exception as e:
        print("Error fetching FEN:", str(e))
    return None

def play_move():
    """Fetches the latest game state, plays a move, and updates the backend."""
    global board
    while not board.is_game_over():
        time.sleep(0.5)  # Slight delay to avoid overwhelming the server
        
        fen = get_fen()
        if fen:
            board.set_fen(fen)  # Load the latest board state
        
        if board.turn == chess.BLACK:  # Ensure bot only plays as black
            move = select_move()
            board.push(move)
            send_fen()

    print("Game Over! Result:", board.result())

# Start the game
send_fen()  # Send initial FEN
play_move()  # Start playing
