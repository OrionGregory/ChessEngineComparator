import chess
from uploads.chess_bot import ChessBot  # Refer to [`ChessBot`](ChessEngineComparator/chess/backend/uploads/chess_bot.py)

class TestChessBot(ChessBot):
    """
    A simple test chess bot that always selects the first legal move.
    """
    def __init__(self, skill_level=1):
        self.skill_level = skill_level
        self.board = chess.Board()

    def select_move(self, legal_moves=None):
        # Returns the first legal move.
        if legal_moves is None:
            legal_moves = list(self.board.legal_moves)
        return legal_moves[0] if legal_moves else None

    def process_fen(self, fen_string):
        # Update the board from the FEN then make the first legal move.
        self.board = chess.Board(fen_string)
        move = self.select_move()
        if move:
            self.board.push(move)
        return self.board.fen()