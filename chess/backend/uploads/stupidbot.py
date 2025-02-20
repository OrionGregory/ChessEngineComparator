import chess
import random

class StupidChessBot:
    def __init__(self, stockfish_path=None, skill_level=5):
        # This bot ignores stockfish, so we don’t initialize it.
        self.board = None

    def select_move(self):
        """Selects a random legal move.
        
        Returns:
            chess.Move: A random legal move.
        """
        return random.choice(list(self.board.legal_moves))

    def process_fen(self, fen: str) -> str:
        """Processes the board given a FEN string, selects a move, and returns the new FEN.
        
        Args:
            fen (str): A string representing the current board position in FEN notation.
        
        Returns:
            str: The updated board position in FEN notation after the bot's move.
            
        Raises:
            ValueError: If the FEN is invalid or the bot selects an illegal move.
        """
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

# Example usage:
if __name__ == '__main__':
    # Starting from the initial board position
    initial_fen = chess.STARTING_FEN
    bot = StupidChessBot()
    
    print("Initial FEN:", initial_fen)
    # Process the FEN, have the bot make a move, and print the new FEN.
    new_fen = bot.process_fen(initial_fen)
    print("New FEN:", new_fen)
