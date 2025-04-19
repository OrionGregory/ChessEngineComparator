import os
import sys
import time
import uuid
import chess
import chess.pgn
import importlib.util
import signal
import resource
import traceback
import logging
import io
from datetime import datetime
from pathlib import Path
from celery import shared_task
from django.conf import settings
from django.core.files.base import ContentFile
from .models import Match, Tournament

# Configure logging
logger = logging.getLogger(__name__)

# Define resource limits for subprocesses
# 1GB memory limit
MEMORY_LIMIT = 1024 * 1024 * 1024
# 5 seconds per move
MOVE_TIME_LIMIT = 5
# Maximum 200 moves per game
MAX_MOVES = 200

class TimeoutException(Exception):
    """Exception raised when a move takes too long"""
    pass

def timeout_handler(signum, frame):
    """Handler for SIGALRM to enforce time limits"""
    raise TimeoutException("Move timed out")

class ChessBotRunner:
    """Manages loading and running chess bots in a safe environment"""
    
    def __init__(self, bot_path, name, is_white=True):
        self.bot_path = bot_path
        self.name = name
        self.is_white = is_white
        self.bot_instance = None
        self.error_log = []
    
    def load_bot(self):
        """Load the chess bot module and create an instance"""
        try:
            # Extract the filename without extension to use as the module name
            module_name = Path(self.bot_path).stem
            
            # Import the module from file
            spec = importlib.util.spec_from_file_location(module_name, self.bot_path)
            if spec is None:
                self.error_log.append(f"Failed to load bot: {self.bot_path}")
                return False
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find the bot class in the module
            bot_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and "ChessBot" in attr_name:
                    bot_class = attr
                    break
                    
            if bot_class is None:
                self.error_log.append(f"No ChessBot class found in {self.bot_path}")
                return False
                
            # Create an instance of the bot
            self.bot_instance = bot_class()
            
            # Verify the bot has the required methods
            if not hasattr(self.bot_instance, 'select_move') or not hasattr(self.bot_instance, 'board'):
                self.error_log.append(f"Bot {self.name} is missing required methods or attributes")
                return False
                
            return True
            
        except Exception as e:
            error_msg = f"Error loading bot {self.name}: {str(e)}\n{traceback.format_exc()}"
            self.error_log.append(error_msg)
            return False
    
    def make_move(self):
        """Get the next move from the bot with resource limits"""
        if not self.bot_instance:
            self.error_log.append(f"Cannot make move: Bot {self.name} not loaded")
            return None
            
        try:
            # Set CPU time limit
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(MOVE_TIME_LIMIT)
            
            # Set memory limit
            resource.setrlimit(resource.RLIMIT_AS, (MEMORY_LIMIT, MEMORY_LIMIT))
            
            # Get move from the bot
            move = self.bot_instance.select_move()
            
            # Reset alarm
            signal.alarm(0)
            
            return move
            
        except TimeoutException:
            self.error_log.append(f"Bot {self.name} timed out when making a move")
            return None
            
        except Exception as e:
            error_msg = f"Error while {self.name} was making a move: {str(e)}\n{traceback.format_exc()}"
            self.error_log.append(error_msg)
            return None
            
    def send_opponent_move(self, move):
        """Send the opponent's move to the bot"""
        if not self.bot_instance:
            self.error_log.append(f"Cannot send move: Bot {self.name} not loaded")
            return False
            
        try:
            move_uci = move.uci()
            if hasattr(self.bot_instance, 'make_move'):
                result = self.bot_instance.make_move(move_uci)
                if not result:
                    self.error_log.append(f"Bot {self.name} rejected move {move_uci}")
                    return False
            else:
                # If make_move is not implemented, update the board directly
                self.bot_instance.board.push(move)
            return True
            
        except Exception as e:
            error_msg = f"Error while sending opponent move to {self.name}: {str(e)}\n{traceback.format_exc()}"
            self.error_log.append(error_msg)
            return False
    
    def get_error_log(self):
        """Return the error log as a string"""
        return "\n".join(self.error_log)

@shared_task
def run_chess_match(match_id):
    """
    Celery task to run a chess match between two bots
    
    Args:
        match_id: UUID of the Match object
    """
    match = None
    
    try:
        # Get the match from the database
        match = Match.objects.get(id=match_id)
        
        # Update match status
        match.status = 'in_progress'
        match.started_at = datetime.now()
        match.save()
        
        # Create log buffer
        log_buffer = io.StringIO()
        log_buffer.write(f"Chess match started at {match.started_at}\n")
        log_buffer.write(f"White: {match.white_bot.name} (v{match.white_bot.version})\n")
        log_buffer.write(f"Black: {match.black_bot.name} (v{match.black_bot.version})\n\n")
        
        # Get the file paths for both bots
        white_bot_path = match.white_bot.file_path.path
        black_bot_path = match.black_bot.file_path.path
        
        # Create bot runners
        white_runner = ChessBotRunner(white_bot_path, match.white_bot.name, is_white=True)
        black_runner = ChessBotRunner(black_bot_path, match.black_bot.name, is_white=False)
        
        # Load bots
        white_loaded = white_runner.load_bot()
        black_loaded = black_runner.load_bot()
        
        if not white_loaded:
            log_buffer.write(f"Failed to load white bot: {white_runner.get_error_log()}\n")
            match.status = 'error'
            match.result = 'black_win'  # White bot failed to load, black wins
            match.completed_at = datetime.now()
            match.save_log_file(log_buffer.getvalue())
            match.save()
            return
            
        if not black_loaded:
            log_buffer.write(f"Failed to load black bot: {black_runner.get_error_log()}\n")
            match.status = 'error'
            match.result = 'white_win'  # Black bot failed to load, white wins
            match.completed_at = datetime.now()
            match.save_log_file(log_buffer.getvalue())
            match.save()
            return
        
        # Create new game and pgn for recording
        game = chess.pgn.Game()
        game.headers["Event"] = f"Tournament {match.tournament.name}"
        game.headers["White"] = match.white_bot.name
        game.headers["Black"] = match.black_bot.name
        game.headers["Date"] = datetime.now().strftime("%Y.%m.%d")
        
        # Reference the board from one of the bots
        board = chess.Board()
        
        # Keep track of move number and current node in the pgn
        move_count = 0
        node = game
        
        # Game loop
        while not board.is_game_over() and move_count < MAX_MOVES:
            move_count += 1
            current_turn = "White" if board.turn == chess.WHITE else "Black"
            log_buffer.write(f"Move {move_count} ({current_turn}): ")
            
            # Get the runner for the current player
            current_runner = white_runner if board.turn == chess.WHITE else black_runner
            
            # Make move
            move = current_runner.make_move()
            
            if move is None or move not in board.legal_moves:
                # Invalid move
                result = "black_win" if board.turn == chess.WHITE else "white_win"
                log_buffer.write(f"Invalid move by {current_turn}. {match.get_result_display()}\n")
                match.status = 'completed'
                match.result = result
                match.completed_at = datetime.now()
                match.save_log_file(log_buffer.getvalue())
                match.save()
                return
                
            # Make the move on our board
            board.push(move)
            
            # Record in PGN
            node = node.add_variation(move)
            
            # Log the move
            log_buffer.write(f"{move.uci()}\n")
            
            # Send the move to the opponent
            opponent_runner = black_runner if board.turn == chess.WHITE else white_runner
            if not opponent_runner.send_opponent_move(move):
                # Failed to send move to opponent
                result = "black_win" if board.turn == chess.WHITE else "white_win"
                log_buffer.write(f"Failed to send move to {opponent_runner.name}. Error: {opponent_runner.get_error_log()}\n")
                match.status = 'error'
                match.result = result
                match.completed_at = datetime.now()
                match.save_log_file(log_buffer.getvalue())
                match.save()
                return
        
        # Game finished
        log_buffer.write(f"\nGame finished after {move_count} moves.\n")
        log_buffer.write(f"Result: {board.result()}\n")
        
        # Determine match result
        if board.is_checkmate():
            # The side that was checkmated lost
            result = "black_win" if board.turn == chess.WHITE else "white_win"
            log_buffer.write(f"{'White' if board.turn == chess.BLACK else 'Black'} won by checkmate\n")
        elif board.is_stalemate():
            result = "draw"
            log_buffer.write("Game ended in stalemate\n")
        elif board.is_insufficient_material():
            result = "draw"
            log_buffer.write("Game ended due to insufficient material\n")
        elif move_count >= MAX_MOVES:
            result = "draw"
            log_buffer.write(f"Game ended after maximum number of moves ({MAX_MOVES})\n")
        else:
            # Other draw conditions (50-move rule, threefold repetition)
            result = "draw"
            log_buffer.write("Game ended in a draw\n")
        
        # Update match with results
        match.status = 'completed'
        match.result = result
        match.completed_at = datetime.now()
        
        # Add errors to log if any
        white_errors = white_runner.get_error_log()
        black_errors = black_runner.get_error_log()
        
        if white_errors:
            log_buffer.write(f"\nWhite bot errors:\n{white_errors}\n")
        if black_errors:
            log_buffer.write(f"\nBlack bot errors:\n{black_errors}\n")
        
        # Save PGN
        pgn_string = str(game)
        pgn_file = ContentFile(pgn_string.encode('utf-8'))
        match.pgn_file.save(f"match_{match.id}.pgn", pgn_file)
        
        # Save log
        match.save_log_file(log_buffer.getvalue())
        
        # Complete match in database
        match.complete_match(result)
        
        # Check if tournament is complete
        check_tournament_completion(match.tournament.id)
        
    except Exception as e:
        error_message = f"Error executing match: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_message)
        
        if match:
            # Save the error to the match log
            log_buffer = io.StringIO()
            log_buffer.write(f"Chess match error at {datetime.now()}\n")
            log_buffer.write(error_message)
            
            match.status = 'error'
            match.result = 'error'
            match.completed_at = datetime.now()
            match.save_log_file(log_buffer.getvalue())
            match.save()

@shared_task
def check_tournament_completion(tournament_id):
    """
    Check if all matches in a tournament are completed
    
    Args:
        tournament_id: UUID of the Tournament object
    """
    try:
        tournament = Tournament.objects.get(id=tournament_id)
        
        # Count total and completed matches
        total_matches = Match.objects.filter(tournament=tournament).count()
        completed_matches = Match.objects.filter(
            tournament=tournament,
            status__in=['completed', 'error']
        ).count()
        
        # If all matches are completed, mark the tournament as completed
        if total_matches > 0 and total_matches == completed_matches:
            tournament.complete_tournament()
            
    except Exception as e:
        logger.error(f"Error checking tournament completion: {str(e)}")