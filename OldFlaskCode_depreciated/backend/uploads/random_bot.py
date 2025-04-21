import chess
import random
from chess_bot import ChessBot

class RandomBot(ChessBot):
    def __init__(self, skill_level=1):
        self.skill_level = skill_level

    def process_fen(self, fen):
        board = chess.Board(fen)
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            raise ValueError("No legal moves available.")
        move = self.select_move(legal_moves)
        board.push(move)
        return board.fen()

    def select_move(self, legal_moves):
        return random.choice(legal_moves)