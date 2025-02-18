import requests
import chess
import random
import time
import sys
import signal

SESSION_ID = "test_session"
SERVER_URL_UPDATE = "http://localhost:5000/update_fen"
SERVER_URL_GET = "http://localhost:5000/get_fen"

board = chess.Board()
running = True

def signal_handler(sig, frame):
    global running
    print("\nGracefully shutting down...")
    running = False
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def send_fen():
    """Sends the current FEN to the server."""
    fen = board.fen()
    try:
        response = requests.post(SERVER_URL_UPDATE, json={"session_id": SESSION_ID, "fen": fen})
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending FEN: {e}")
        return None

def get_fen():
    """Fetches the latest FEN from the server."""
    try:
        response = requests.get(SERVER_URL_GET, params={"session_id": SESSION_ID})
        data = response.json()
        return data.get("fen")
    except requests.exceptions.RequestException:
        return None

def play_move():
    """Plays a move if it's the bot's turn."""
    global board, running
    
    while running and not board.is_game_over():
        try:
            fen = get_fen()
            
            if fen and fen != board.fen():
                board.set_fen(fen)
                
                if board.turn == chess.BLACK:  # Bot plays as black
                    move = random.choice(list(board.legal_moves))
                    board.push(move)
                    send_fen()
            
            time.sleep(1)  # Add small delay to prevent excessive CPU usage
            
        except Exception as e:
            print(f"Error during play: {e}")
            time.sleep(1)  # Wait before retrying

    if board.is_game_over():
        print("Game Over! Result:", board.result())

if __name__ == "__main__":
    try:
        send_fen()
        play_move()
    except KeyboardInterrupt:
        print("\nGracefully shutting down...")
        sys.exit(0)