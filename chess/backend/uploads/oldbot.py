import chess
import chess.engine
import random

# A simple chess bot
class SimpleChessBot:
    def __init__(self):
        self.board = chess.Board()

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

        for move in self.board.legal_moves:
            self.board.push(move)
            score = self.evaluate_board()
            self.board.pop()

            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def play_game(self):
        while not self.board.is_game_over():
            print(self.board)
            print("\n")

            if self.board.turn == chess.WHITE:
                print("White's Turn (User)")
                user_move = input("Enter your move in UCI format (e.g., e2e4): ")
                try:
                    move = chess.Move.from_uci(user_move)
                    if move in self.board.legal_moves:
                        self.board.push(move)
                    else:
                        print("Illegal move. Try again.")
                        continue
                except ValueError:
                    print("Invalid move format. Try again.")
                    continue
            else:
                print("Black's Turn (Bot)")
                move = self.select_move()
                print(f"Bot plays: {move}")
                self.board.push(move)

        print(self.board)
        print("\nGame Over! Result: ", self.board.result())

# Run the bot
if __name__ == "__main__":
    bot = SimpleChessBot()
    bot.play_game()