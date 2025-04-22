import chess
import random

class StudentChessBot:
    def __init__(self):
        self.board = chess.Board()

    def select_move(self):
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return None
        # Replace this with your own strategy!
        return random.choice(legal_moves)

    def make_move(self, move_uci):
        try:
            move = chess.Move.from_uci(move_uci)
            if move in self.board.legal_moves:
                self.board.push(move)
                return True
        except ValueError:
            pass
        return False

