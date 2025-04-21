import chess
import random

class AdvancedChessBot:
    """
    A more advanced chess bot that uses minimax with alpha-beta pruning
    and basic position evaluation.
    """
    
    def __init__(self, stockfish_path=None):
        """Initialize the bot with a new chess board."""
        self.board = chess.Board()
        
        # Piece values (pawn=1, knight=3, bishop=3, rook=5, queen=9)
        self.piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
        }
        
        # Position values for pieces (encourages good development)
        self.pawn_position_values = [
            0, 0, 0, 0, 0, 0, 0, 0,
            50, 50, 50, 50, 50, 50, 50, 50,
            10, 10, 20, 30, 30, 20, 10, 10,
            5, 5, 10, 25, 25, 10, 5, 5,
            0, 0, 0, 20, 20, 0, 0, 0,
            5, -5, -10, 0, 0, -10, -5, 5,
            5, 10, 10, -20, -20, 10, 10, 5,
            0, 0, 0, 0, 0, 0, 0, 0
        ]
        
        self.knight_position_values = [
            -50, -40, -30, -30, -30, -30, -40, -50,
            -40, -20, 0, 0, 0, 0, -20, -40,
            -30, 0, 10, 15, 15, 10, 0, -30,
            -30, 5, 15, 20, 20, 15, 5, -30,
            -30, 0, 15, 20, 20, 15, 0, -30,
            -30, 5, 10, 15, 15, 10, 5, -30,
            -40, -20, 0, 5, 5, 0, -20, -40,
            -50, -40, -30, -30, -30, -30, -40, -50
        ]
        
        self.bishop_position_values = [
            -20, -10, -10, -10, -10, -10, -10, -20,
            -10, 0, 0, 0, 0, 0, 0, -10,
            -10, 0, 10, 10, 10, 10, 0, -10,
            -10, 5, 5, 10, 10, 5, 5, -10,
            -10, 0, 5, 10, 10, 5, 0, -10,
            -10, 10, 10, 10, 10, 10, 10, -10,
            -10, 5, 0, 0, 0, 0, 5, -10,
            -20, -10, -10, -10, -10, -10, -10, -20
        ]
        
        self.rook_position_values = [
            0, 0, 0, 0, 0, 0, 0, 0,
            5, 10, 10, 10, 10, 10, 10, 5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            0, 0, 0, 5, 5, 0, 0, 0
        ]
        
        self.queen_position_values = [
            -20, -10, -10, -5, -5, -10, -10, -20,
            -10, 0, 0, 0, 0, 0, 0, -10,
            -10, 0, 5, 5, 5, 5, 0, -10,
            -5, 0, 5, 5, 5, 5, 0, -5,
            0, 0, 5, 5, 5, 5, 0, -5,
            -10, 5, 5, 5, 5, 5, 0, -10,
            -10, 0, 5, 0, 0, 0, 0, -10,
            -20, -10, -10, -5, -5, -10, -10, -20
        ]
        
        self.king_position_values_middlegame = [
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -20, -30, -30, -40, -40, -30, -30, -20,
            -10, -20, -20, -20, -20, -20, -20, -10,
            20, 20, 0, 0, 0, 0, 20, 20,
            20, 30, 10, 0, 0, 10, 30, 20
        ]
        
        self.position_values = {
            chess.PAWN: self.pawn_position_values,
            chess.KNIGHT: self.knight_position_values,
            chess.BISHOP: self.bishop_position_values,
            chess.ROOK: self.rook_position_values,
            chess.QUEEN: self.queen_position_values,
            chess.KING: self.king_position_values_middlegame
        }
        
        # Search depth for minimax algorithm
        self.DEPTH = 3
    
    def evaluate_position(self, board):
        """Evaluate the current board position."""
        if board.is_checkmate():
            # If the current side to move is checkmated, return a large negative score
            return -10000 if board.turn == chess.WHITE else 10000
        
        if board.is_stalemate() or board.is_insufficient_material():
            return 0  # Draw
        
        # Calculate material score
        white_material = 0
        black_material = 0
        
        # Add positional score
        white_position = 0
        black_position = 0
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                value = self.piece_values[piece.piece_type]
                
                # Get positional value (flip for black pieces)
                position_index = square if piece.color == chess.WHITE else 63 - square
                position_value = self.position_values[piece.piece_type][position_index]
                
                if piece.color == chess.WHITE:
                    white_material += value
                    white_position += position_value
                else:
                    black_material += value
                    black_position += position_value
        
        material_score = white_material - black_material
        position_score = white_position - black_position
        
        # Small bonus for each legal move to encourage mobility
        mobility_score = 0
        if not board.turn:  # If it's black's turn, temporarily switch to white
            board.turn = chess.WHITE
            white_moves = len(list(board.legal_moves))
            board.turn = chess.BLACK
            black_moves = len(list(board.legal_moves))
            board.turn = chess.WHITE  # Reset to white's turn
        else:
            white_moves = len(list(board.legal_moves))
            board.turn = chess.BLACK
            black_moves = len(list(board.legal_moves))
            board.turn = chess.WHITE  # Reset to white's turn
        
        mobility_score = (white_moves - black_moves) * 5
        
        # Combine scores with appropriate weights
        total_score = material_score + position_score * 0.3 + mobility_score
        
        return total_score
    
    def minimax(self, board, depth, alpha, beta, maximizing_player):
        """
        Minimax algorithm with alpha-beta pruning.
        Returns the best score and best move for the current position.
        """
        if depth == 0 or board.is_game_over():
            return self.evaluate_position(board), None
        
        # For white (maximizing player)
        if maximizing_player:
            best_score = float('-inf')
            best_move = None
            
            for move in board.legal_moves:
                board.push(move)
                score, _ = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                
                if score > best_score:
                    best_score = score
                    best_move = move
                
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break  # Beta cutoff
            
            return best_score, best_move
        
        # For black (minimizing player)
        else:
            best_score = float('inf')
            best_move = None
            
            for move in board.legal_moves:
                board.push(move)
                score, _ = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                
                if score < best_score:
                    best_score = score
                    best_move = move
                
                beta = min(beta, best_score)
                if beta <= alpha:
                    break  # Alpha cutoff
            
            return best_score, best_move
    
    def select_move(self):
        """Select the best move using minimax with alpha-beta pruning."""
        # Check if there are any legal moves
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return None
        
        # Use random move for the first 2 moves to add variety
        if self.board.fullmove_number <= 2:
            return random.choice(legal_moves)
        
        # Use minimax to find best move
        maximizing = self.board.turn == chess.WHITE
        _, best_move = self.minimax(
            self.board, 
            self.DEPTH, 
            float('-inf'), 
            float('inf'), 
            maximizing
        )
        
        # Fall back to random move if minimax doesn't find a good move
        if best_move is None:
            return random.choice(legal_moves)
        
        return best_move
    
    def make_move(self, move_uci):
        """Make a move on the board using UCI notation."""
        try:
            move = chess.Move.from_uci(move_uci)
            if move in self.board.legal_moves:
                self.board.push(move)
                return True
            else:
                return False
        except ValueError:
            return False