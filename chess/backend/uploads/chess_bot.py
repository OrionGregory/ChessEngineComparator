import chess
from stockfish import Stockfish
import os 

# A simple chess bot using Stockfish with adjustable skill level
class SimpleChessBot:
    def __init__(self, stockfish_path=r"", skill_level=20):
        # When using process_fen, we always get an incoming FEN
        self.board = None
        # If needed, initialize your Stockfish engine.
        if stockfish_path:
            self.stockfish = Stockfish(
                path=stockfish_path, 
                parameters={
                    "Threads": 2, 
                    "Minimum Thinking Time": 30,
                    "Skill Level": skill_level
                }
            )
            print(f"Initializing Stockfish with path: {stockfish_path}")
            print(f"Stockfish skill level set to {skill_level}")

    def evaluate_board(self):
        # Example evaluation using material count:
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
        # Use Stockfish if available:
        if hasattr(self, "stockfish"):
            self.stockfish.set_fen_position(self.board.fen())
            best_move = self.stockfish.get_best_move()
            return chess.Move.from_uci(best_move)
        # Otherwise do a basic evaluation:
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

    def process_fen(self, fen: str) -> str:
        # Update the board from the incoming fen
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
                    print(f"Move {move_number} (Black): {move}, FEN = {self.board.fen()}")
                    move_number += 1
                else:
                    print(f"Illegal move by bot: {move}")
                    break

        print(self.board)
        print("\nGame Over! Result: ", self.board.result())

if __name__ == "__main__":
    cwd = os.getcwd()
    stockfish_path = r"C:\ChessEngineComparator\ChessEngineComparator\chess\backend\stockfish\stockfish-windows-x86-64-avx2.exe"
    print(f"Using Stockfish path: {stockfish_path}")  # Debugging statement
    # Adjust skill level (0 is weakest, 20 is strongest)
    skill_level = 5  # Set this to any value between 0 and 20
    bot = SimpleChessBot(stockfish_path=stockfish_path, skill_level=skill_level)
    bot.play_game()