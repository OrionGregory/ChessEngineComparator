import chess
import random

class SimpleChessBot:
    def __init__(self, stockfish_path=None, skill_level=5):
        # This bot ignores stockfish, so we don’t initialize it.
        self.board = None

    def evaluate_board(self):
        material_scores = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
        }
        score = 0
        for piece_type in material_scores:
            score += len(self.board.pieces(piece_type, chess.WHITE)) * material_scores[piece_type]
            score -= len(self.board.pieces(piece_type, chess.BLACK)) * material_scores[piece_type]
        return score

    def select_move(self):
        best_move = None
        best_score = -float('inf')
        # Iterate over legal moves, evaluating them with a simple material count
        for move in self.board.legal_moves:
            self.board.push(move)
            score = self.evaluate_board()
            self.board.pop()
            if score > best_score:
                best_score = score
                best_move = move
        return best_move

    def process_fen(self, fen: str) -> str:
        try:
            self.board = chess.Board(fen)
        except Exception as e:
            raise ValueError(f"Invalid FEN provided: {fen}") from e

        move = self.select_move()
        if move in self.board.legal_moves:
            self.board.push(move)
        else:
            raise ValueError(f"Selected illegal move: {move}")
        return self.board.fen()

# Optional aliasing if you want to refer to this bot as OldChessBot in game_duel.py
OldChessBot = SimpleChessBot