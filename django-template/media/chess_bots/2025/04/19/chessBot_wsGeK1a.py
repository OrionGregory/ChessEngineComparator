import chess
from stockfish import Stockfish
import os 

# A simple chess bot using Stockfish
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

    def select_move(self, difficulty=1):
        best_move = None
        best_score = -float('inf')

        for move in self.board.legal_moves:
            self.board.push(move)
            score = self.evaluate_board()
            self.board.pop()

            if score > best_score:
                best_score = score
                best_move = move

        # Adjust move selection based on difficulty
        if difficulty < 10:
            legal_moves = list(self.board.legal_moves)
            best_move = legal_moves[min(len(legal_moves) - 1, difficulty)]

        return best_move
    
    def play_game(self):
        move_number = 1  # Keep track of the move number

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
                        # Log FEN after White's move
                        print(f"Move {move_number} (White): {move}, FEN = {self.board.fen()}")
                        move_number += 1
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
                if move in self.board.legal_moves:
                    self.board.push(move)
                    # Log FEN after Black's move
                    print(f"Move {move_number} (Black): {move}, FEN = {self.board.fen()}")
                    move_number += 1
                else:
                    print(f"Illegal move by bot: {move}")
                    break

        print(self.board)
        print("\nGame Over! Result: ", self.board.result())

if __name__ == "__main__":
    cwd = os.getcwd()
    stockfish_path = cwd+"/stockfish/stockfish-ubuntu-x86-64-avx2"
    print(f"Using Stockfish path: {stockfish_path}")  # Debugging statement
    bot = SimpleChessBot(stockfish_path=stockfish_path)
    bot.play_game()
