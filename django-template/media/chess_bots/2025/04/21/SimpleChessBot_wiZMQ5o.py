import chess
import random

class SimpleChessBot:
    """
    A simple chess bot that makes random legal moves.
    """
    
    def __init__(self):
        """Initialize the bot with a new chess board."""
        self.board = chess.Board()
    
    def select_move(self):
        """Select a random legal move from the current position."""
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return None  # No legal moves available (checkmate or stalemate)
        
        # Select a random move from the list of legal moves
        return random.choice(legal_moves)
    
    def make_move(self, move_uci):
        """Make a move on the board using UCI notation."""
        try:
            move = chess.Move.from_uci(move_uci)
            if move in self.board.legal_moves:
                self.board.push(move)
                return True
            else:
                return False
        except ValueError:
            return False