import chess
from stockfish import Stockfish
import os 

# A simple chess bot using Stockfish
class SimpleChessBot:
    def __init__(self, stockfish_path):
        self.board = chess.Board()
        print(f"Initializing Stockfish with path: {stockfish_path}")  # Debugging statement
        self.stockfish = Stockfish(path=stockfish_path, parameters={"Threads": 2, "Minimum Thinking Time": 30})
    
    def evaluate_board(self):
        # Set the current board position in Stockfish
        self.stockfish.set_fen_position(self.board.fen())
        
        # Get the evaluation from Stockfish
        evaluation = self.stockfish.get_evaluation()
        
        if evaluation['type'] == 'cp':
            # Centipawn evaluation (positive for White, negative for Black)
            score = evaluation['value'] / 100.0
        elif evaluation['type'] == 'mate':
            # Mate in n moves (positive for White, negative for Black)
            # Assign a high score for mate positions
            score = 1000 if evaluation['value'] > 0 else -1000
        else:
            score = 0  # Unknown evaluation
        
        return score
    
    def select_move(self):
        # Use Stockfish to select the best move
        self.stockfish.set_fen_position(self.board.fen())
        best_move = self.stockfish.get_best_move()
        print(f"Best move from Stockfish: {best_move}")  # Debugging statement
        return chess.Move.from_uci(best_move)
    
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