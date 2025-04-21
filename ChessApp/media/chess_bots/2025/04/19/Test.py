import chess
from stockfish import Stockfish
from uploads.chess_bot import ChessBot

# A simple mapping of piece types to values.
PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}

def evaluate_board(board):
    """
    Evaluates the board using a simple material count.
    Positive score favors White, negative favors Black.
    """
    value = 0
    for piece in board.piece_map().values():
        sign = 1 if piece.color == chess.WHITE else -1
        value += sign * PIECE_VALUES.get(piece.piece_type, 0)
    return value

def minimax(board, depth, maximizing_player):
    """
    A simple minimax search without alpha-beta pruning.
    """
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)
    
    legal_moves = list(board.legal_moves)
    if maximizing_player:
        max_eval = -float('inf')
        for move in legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, False)
            board.pop()
            max_eval = max(max_eval, eval)
        return max_eval
    else:
        min_eval = float('inf')
        for move in legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, True)
            board.pop()
            min_eval = min(min_eval, eval)
        return min_eval

class Test(ChessBot):
    """
    A chess bot that utilizes Stockfish for move selection.
    """
    def __init__(self, skill_level=1):
        self.skill_level = skill_level
        self.board = chess.Board()
        # Initialize Stockfish with the given executable.
        self.stockfish = Stockfish(r"C:\ChessEngineComparator\chess\backend\stockfish\stockfish-windows-x86-64-avx2.exe",
                                    parameters={"Threads": 2, "Minimum Thinking Time": 30})
    
    def select_move(self, legal_moves=None):
        # Use Stockfish to determine the best move.
        best_move_str = self.stockfish.get_best_move()
        if best_move_str:
            return chess.Move.from_uci(best_move_str)
        else:
            if legal_moves is None:
                legal_moves = list(self.board.legal_moves)
            return legal_moves[0]  # fallback move

    def process_fen(self, fen_string):
        # Update the board from FEN and set the engine position.
        self.board = chess.Board(fen_string)
        self.stockfish.set_fen_position(fen_string)
        move = self.select_move()
        if move:
            self.board.push(move)
        return self.board.fen()