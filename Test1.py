import chess
import os
from stockfish import Stockfish
from uploads.chess_bot import ChessBot

# A simple mapping of piece types to values.
PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}

def evaluate_board(board):
    """
    Evaluates the board using a simple material count.
    Positive score favors White, negative favors Black.
    """
    value = 0
    for piece in board.piece_map().values():
        sign = 1 if piece.color == chess.WHITE else -1
        value += sign * PIECE_VALUES.get(piece.piece_type, 0)
    return value

def minimax(board, depth, maximizing_player):
    """
    A simple minimax search without alpha-beta pruning.
    """
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)
    
    legal_moves = list(board.legal_moves)
    if maximizing_player:
        max_eval = -float('inf')
        for move in legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, False)
            board.pop()
            max_eval = max(max_eval, eval)
        return max_eval
    else:
        min_eval = float('inf')
        for move in legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, True)
            board.pop()
            min_eval = min(min_eval, eval)
        return min_eval

class Test(ChessBot):
    """
    A chess bot that utilizes Stockfish for move selection.
    """
    def __init__(self, skill_level=12):
        self.skill_level = skill_level
        self.board = chess.Board()
        self.stockfish = None
        
        # Try multiple possible paths for Stockfish
        possible_paths = [
            "/app/stockfish/stockfish",                  # Docker path (copied binary)
            "/app/stockfish_local/stockfish-ubuntu-x86-64-avx2",  # Docker path (mounted binary)
            r"D:\Cs495\ChessEngineComparator\stockfish\stockfish-ubuntu-x86-64-avx2"  # Windows path
        ]
        
        # Try to initialize stockfish with each path
        for path in possible_paths:
            if os.path.exists(path):
                print(f"Found Stockfish at: {path}")
                try:
                    self.stockfish = Stockfish(path, parameters={"Threads": 2, "Minimum Thinking Time": 30})
                    print(f"Successfully initialized Stockfish at {path}")
                    break
                except Exception as e:
                    print(f"Error initializing Stockfish with {path}: {str(e)}")
                    continue
        
        if self.stockfish is None:
            print("WARNING: Could not initialize Stockfish. Using fallback method.")
    
    def select_move(self, legal_moves=None):
        if legal_moves is None:
            legal_moves = list(self.board.legal_moves)
        
        if not legal_moves:
            return None
            
        # Use Stockfish to determine the best move if available
        if self.stockfish:
            try:
                best_move_str = self.stockfish.get_best_move()
                if best_move_str:
                    return chess.Move.from_uci(best_move_str)
            except Exception as e:
                print(f"Error getting best move from Stockfish: {str(e)}")
        
        # Fallback - just use the first legal move
        return legal_moves[0]

    def process_fen(self, fen_string):
        # Update the board from FEN
        self.board = chess.Board(fen_string)
        
        # Set the engine position if Stockfish is available
        if self.stockfish:
            try:
                self.stockfish.set_fen_position(fen_string)
            except Exception as e:
                print(f"Error setting FEN in Stockfish: {str(e)}")
        
        move = self.select_move()
        if move:
            self.board.push(move)
        return self.board.fen()