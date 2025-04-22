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
from django.utils import timezone  # This is the correct import for timezone.now()
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
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Find the chess module first
            global chess
            if "chess" not in sys.modules:
                self.error_log.append("Python-chess module not found in imports")
                for key in sys.modules.keys():
                    if "chess" in key and not key.startswith("_"):
                        self.error_log.append(f"Found possible chess module: {key}")
                
                # Try to import it directly
                try:
                    import chess
                except ImportError:
                    self.error_log.append("Failed to import chess module")
                    return False
            
            # Find the bot class in the module
            bot_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and not attr_name.startswith("_") and attr_name not in ["type", "object"]:
                    # Try to create an instance to check if it's compatible
                    try:
                        test_instance = attr()
                        if hasattr(test_instance, 'board'):
                            bot_class = attr
                            break
                    except Exception:
                        continue
            
            if bot_class is None:
                self.error_log.append(f"No valid chess bot class found in {self.bot_path}")
                return False
                
            # Create an instance of the bot
            self.bot_instance = bot_class()
            
            # Ensure it has a board attribute
            if not hasattr(self.bot_instance, 'board'):
                self.error_log.append(f"Bot {self.name} is missing required board attribute")
                return False
                
            # Force-initialize the board to standard starting position
            self.bot_instance.board = chess.Board()
            
            # Add missing methods if needed
            if not hasattr(self.bot_instance, 'select_move'):
                self.error_log.append(f"Bot {self.name} is missing required method: select_move")
                return False
            
            if not hasattr(self.bot_instance, 'make_move'):
                # Add a default make_move method if it's missing
                self.bot_instance.make_move = self._default_make_move.__get__(self.bot_instance)
                self.error_log.append(f"Added default make_move method to {self.name}")
                
            # Set debug flag if it exists
            if hasattr(self.bot_instance, 'debug'):
                self.bot_instance.debug = True
                
            return True
            
        except Exception as e:
            error_msg = f"Error loading bot {self.name}: {str(e)}\n{traceback.format_exc()}"
            self.error_log.append(error_msg)
            return False
    
    def _default_make_move(self, move_uci):
        """Default make_move method for bots that don't have one"""
        try:
            move = chess.Move.from_uci(move_uci)
            if move in self.board.legal_moves:
                self.board.push(move)
                return True
            else:
                return False
        except (ValueError, AttributeError) as e:
            return False
    
    def make_move(self):
        """Get the next move from the bot with resource limits"""
        if not self.bot_instance:
            self.error_log.append(f"Cannot make move: Bot {self.name} not loaded")
            return None
            
        try:
            # Debug the current board state
            self.error_log.append(f"Board state for {self.name} before move:")
            self.error_log.append(f"FEN: {self.bot_instance.board.fen()}")
            self.error_log.append(f"Turn: {'White' if self.bot_instance.board.turn else 'Black'}")
            self.error_log.append(f"Legal moves: {[m.uci() for m in self.bot_instance.board.legal_moves]}")
            
            # Check if turn matches bot color
            correct_turn = (self.bot_instance.board.turn == chess.WHITE) == self.is_white
            if not correct_turn:
                self.error_log.append(f"ERROR: Turn mismatch for {self.name}. Board shows {'white' if self.bot_instance.board.turn else 'black'}'s turn but bot is {'white' if self.is_white else 'black'}")
            
            # Set CPU time limit
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(MOVE_TIME_LIMIT)
            
            # Get move from the bot
            move = self.bot_instance.select_move()
            
            # Reset alarm
            signal.alarm(0)
            
            # Check if move is valid
            if move is None:
                self.error_log.append(f"Bot {self.name} returned None for move")
                return None
                
            # Validate the move 
            if move not in self.bot_instance.board.legal_moves:
                self.error_log.append(f"Bot {self.name} returned illegal move: {move}")
                return None
                
            # Log the move
            self.error_log.append(f"Bot {self.name} selected move: {move.uci()}")
            return move
            
        except TimeoutException:
            signal.alarm(0)  # Reset alarm
            self.error_log.append(f"Bot {self.name} timed out when making a move")
            return None
            
        except Exception as e:
            signal.alarm(0)  # Reset alarm
            error_msg = f"Error while {self.name} was making a move: {str(e)}\n{traceback.format_exc()}"
            self.error_log.append(error_msg)
            return None
            
    def send_opponent_move(self, move):
        """Send the opponent's move to the bot"""
        if not self.bot_instance:
            self.error_log.append(f"Cannot send move: Bot {self.name} not loaded")
            return False
            
        try:
            # First check if the board is in the correct state
            self.error_log.append(f"Sending move {move.uci()} to {self.name}")
            self.error_log.append(f"Current board state: {self.bot_instance.board.fen()}")
            
            # THE KEY FIX: Make sure the board is in the correct state to receive this move
            # If bot is black, and it's white's turn on its internal board, we need to sync
            if (self.is_white and not self.bot_instance.board.turn) or (not self.is_white and self.bot_instance.board.turn):
                self.error_log.append(f"Turn mismatch for {self.name}. Attempting to fix...")
                
            # Apply opponent's move directly to the board state
            if move in self.bot_instance.board.legal_moves:
                # Apply directly to board first (guaranteed to work)
                try:
                    self.bot_instance.board.push(move)
                    self.error_log.append(f"Direct board update successful for {self.name}")
                    return True
                except Exception as e:
                    self.error_log.append(f"Error directly updating board: {str(e)}")
                    return False
            else:
                self.error_log.append(f"Move {move.uci()} not legal on bot's board: {self.bot_instance.board.fen()}")
                self.error_log.append(f"Legal moves are: {[m.uci() for m in self.bot_instance.board.legal_moves]}")
                
                # Desperate measure: reset the bot's board and catch up
                try:
                    self.error_log.append("Attempting full board reset and sync...")
                    # Get the move history from the move's board
                    if hasattr(move, 'board') and hasattr(move.board, 'move_stack'):
                        self.bot_instance.board = chess.Board()
                        for m in move.board.move_stack[:-1]:  # All moves except the last one
                            if m in self.bot_instance.board.legal_moves:
                                self.bot_instance.board.push(m)
                        
                        # Now add the current move
                        if move in self.bot_instance.board.legal_moves:
                            self.bot_instance.board.push(move)
                            self.error_log.append("Board sync successful")
                            return True
                except Exception as e:
                    self.error_log.append(f"Board reset failed: {str(e)}")
                
                # If all else fails, create a new board with the FEN from the move's board
                try:
                    if hasattr(move, 'board'):
                        self.bot_instance.board = chess.Board(move.board.fen())
                        self.error_log.append("Board reset using FEN")
                        return True
                except Exception as e:
                    self.error_log.append(f"FEN reset failed: {str(e)}")
                
                return False
            
        except Exception as e:
            error_msg = f"Error while sending opponent move to {self.name}: {str(e)}\n{traceback.format_exc()}"
            self.error_log.append(error_msg)
            return False
    
    def get_error_log(self):
        """Return the error log as a string"""
        return "\n".join(self.error_log)

@shared_task
def run_chess_match(match_id):
    """Run a chess match between two bots"""
    from .models import Match, Tournament
    import time
    
    try:
        match = Match.objects.get(id=match_id)
        
        # Skip if match is already completed
        if match.status == 'completed':
            return f"Match {match_id} already completed"
            
        # Update match status
        match.status = 'in_progress'
        match.started_at = timezone.now()
        match.save()
        
        # Run the match (your existing code here)
        match = None
        log_buffer = io.StringIO()
        
        try:
            # Get the match from the database
            match = Match.objects.get(id=match_id)
            
            # Update match status
            match.status = 'in_progress'
            match.started_at = timezone.now()
            match.save()
            
            # Create log buffer
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
            
            # When a bot fails to load, properly mark it as completed with an error result
            if not white_loaded:
                log_buffer.write(f"Failed to load white bot: {white_runner.get_error_log()}\n")
                match.status = 'completed'  # Changed from 'error' to 'completed'
                match.result = 'black_win'  # White bot failed to load, black wins
                match.completed_at = timezone.now()
                match.save_log_file(log_buffer.getvalue())
                match.save()
                
                # Update scores since the match is considered completed
                match.update_scores()
                
                # Check tournament completion after this match
                if match.tournament:
                    check_tournament_completion.delay(match.tournament.id)
                return f"Match {match_id} completed with white bot error"
                
            if not black_loaded:
                log_buffer.write(f"Failed to load black bot: {black_runner.get_error_log()}\n")
                match.status = 'completed'  # Changed from 'error' to 'completed'
                match.result = 'white_win'  # Black bot failed to load, white wins
                match.completed_at = timezone.now()
                match.save_log_file(log_buffer.getvalue())
                match.save()
                
                # Update scores since the match is considered completed
                match.update_scores()
                
                # Check tournament completion after this match
                if match.tournament:
                    check_tournament_completion.delay(match.tournament.id)
                return f"Match {match_id} completed with black bot error"
            
            # Create a shared master board for tracking the game state
            master_board = chess.Board()
            
            # Create new game and pgn for recording
            game = chess.pgn.Game()
            game.headers["Event"] = f"Tournament {match.tournament.name}"
            game.headers["White"] = match.white_bot.name
            game.headers["Black"] = match.black_bot.name
            game.headers["Date"] = timezone.now().strftime("%Y.%m.%d")
            
            # Keep track of move number and current node in the pgn
            move_count = 0
            node = game
            
            # Game loop
            while not master_board.is_game_over() and move_count < MAX_MOVES:
                move_count += 1
                current_turn = "White" if master_board.turn == chess.WHITE else "Black"
                log_buffer.write(f"Move {move_count} ({current_turn}): ")
                
                # Get the runner for the current player
                current_runner = white_runner if master_board.turn == chess.WHITE else black_runner
                
                # Make sure the current player's board is correct
                if current_runner.bot_instance.board.fen() != master_board.fen():
                    log_buffer.write(f"\nSynchronizing {current_turn}'s board state...\n")
                    current_runner.bot_instance.board = chess.Board(master_board.fen())
                
                # Make move
                move = current_runner.make_move()
                
                # Handle invalid moves - mark as completed rather than error
                if move is None:
                    # Invalid move - opponent wins
                    result = "black_win" if master_board.turn == chess.WHITE else "white_win"
                    log_buffer.write(f"Invalid move by {current_turn}. None\n")
                    match.status = 'completed'
                    match.result = result
                    match.completed_at = timezone.now()
                    match.save_log_file(log_buffer.getvalue() + "\n" + current_runner.get_error_log())
                    match.save()
                    
                    # Update scores since the match is considered completed
                    match.update_scores()
                    
                    # Check tournament completion after this match
                    if match.tournament:
                        check_tournament_completion.delay(match.tournament.id)
                    return f"Match {match_id} completed with invalid move"
                
                if move not in master_board.legal_moves:
                    # Illegal move - opponent wins
                    result = "black_win" if master_board.turn == chess.WHITE else "white_win"
                    log_buffer.write(f"Illegal move by {current_turn}: {move.uci()}\n")
                    match.status = 'completed'
                    match.result = result
                    match.completed_at = timezone.now()
                    match.save_log_file(log_buffer.getvalue() + "\n" + current_runner.get_error_log())
                    match.save()
                    
                    # Update scores since the match is considered completed
                    match.update_scores()
                    
                    # Check tournament completion after this match
                    if match.tournament:
                        check_tournament_completion.delay(match.tournament.id)
                    return f"Match {match_id} completed with illegal move"
                    
                # Make the move on the master board
                master_board.push(move)
                
                # Record in PGN
                node = node.add_variation(move)
                
                # Log the move
                log_buffer.write(f"{move.uci()}\n")
                
                # Game over check - don't need to update opponent if game is over
                if master_board.is_game_over():
                    break
                
                # Synchronize the opponent's board with the master board
                opponent_runner = black_runner if master_board.turn == chess.WHITE else white_runner
                opponent_runner.bot_instance.board = chess.Board(master_board.fen())
            
            # Game finished - determine result
            log_buffer.write(f"\nGame finished after {move_count} moves.\n")
            log_buffer.write(f"Result: {master_board.result()}\n")
            
            if master_board.is_checkmate():
                # The side that was checkmated lost
                result = "black_win" if master_board.turn == chess.WHITE else "white_win"
                log_buffer.write(f"{'White' if master_board.turn == chess.BLACK else 'Black'} won by checkmate\n")
            elif master_board.is_stalemate():
                result = "draw"
                log_buffer.write("Game ended in stalemate\n")
            elif master_board.is_insufficient_material():
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
            match.completed_at = timezone.now()
            
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
            
            # Save match
            match.save()
            
            # Check if tournament is complete
            check_tournament_completion.delay(match.tournament.id)
            
        except Exception as e:
            error_message = f"Error executing match: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_message)
            
            if match:
                # Save the error to the match log
                log_buffer.write(f"Chess match error at {timezone.now()}\n")
                log_buffer.write(error_message)
                
                # Determine which bot was moving when the error occurred
                current_turn = "white" if match.is_white_turn else "black"
                
                # Assign result based on which bot failed
                if current_turn == "white":
                    result = "black_win"  # White's error means black wins
                else:
                    result = "white_win"  # Black's error means white wins
                
                match.status = 'completed'  # Changed from 'error' to 'completed'
                match.result = result
                match.completed_at = timezone.now()
                match.save_log_file(log_buffer.getvalue())
                match.save()
                
                # Update scores since the match is considered completed
                if hasattr(match, 'update_scores'):
                    match.update_scores()
                
                # Check tournament completion after this match
                if match.tournament:
                    check_tournament_completion.delay(match.tournament.id)
        
        # Update the match and scores using a transaction
        from django.db import transaction
        
        with transaction.atomic():
            # Set match as completed with final status
            match = Match.objects.get(id=match_id)
            match.status = 'completed'
            match.completed_at = timezone.now()
            match.save()
            
            # Update scores for this match if the method exists
            if hasattr(match, 'update_scores'):
                match.update_scores()
            
            # Check if tournament is complete and update scores
            if match.tournament and match.tournament.status == 'in_progress':
                # Count total and completed matches
                total_matches = Match.objects.filter(tournament=match.tournament).count()
                completed_matches = Match.objects.filter(
                    tournament=match.tournament,
                    status='completed'
                ).count()
                
                # If all matches are completed, recalculate all scores
                if total_matches == completed_matches:
                    if hasattr(match.tournament, 'recalculate_scores'):
                        match.tournament.recalculate_scores()
            
            # Explicitly trigger tournament completion check to update scores
            if match.tournament:
                logger.info(f"Triggering tournament completion check for tournament {match.tournament.id}")
                # Immediately call check_tournament_completion rather than using delay
                check_tournament_completion(str(match.tournament.id))
        
        return f"Match {match_id} completed successfully"
        
    except Match.DoesNotExist:
        return f"Match {match_id} not found"
    except Exception as e:
        # Handle errors and mark match as failed
        try:
            match = Match.objects.get(id=match_id)
            
            # Set a default result rather than leaving it as error
            # If we can determine which bot was to move, that bot loses
            # Otherwise default to white_win (arbitrary choice)
            result = "white_win"  # Default
            
            try:
                # Try to determine which bot's turn it was
                if hasattr(match, 'is_white_turn') and not match.is_white_turn:
                    result = "white_win"  # Black's error means white wins
                else:
                    result = "black_win"  # White's error means black wins
            except:
                pass  # Stick with default if we can't determine
            
            match.status = 'completed'  # Mark as completed with a result
            match.result = result
            match.log_file = f"Error: {str(e)}"
            match.completed_at = timezone.now()
            match.save()
            
            # Update scores
            if hasattr(match, 'update_scores'):
                match.update_scores()
            
            # Check tournament completion after this match
            if hasattr(match, 'tournament') and match.tournament:
                check_tournament_completion.delay(str(match.tournament.id))
                
        except:
            pass
        return f"Error running match {match_id}: {str(e)}"

@shared_task
def check_tournament_completion(tournament_id):
    """
    Check if all matches in a tournament are completed and recalculate scores
    
    Args:
        tournament_id: UUID of the Tournament object
    """
    try:
        from django.db import transaction
        from .models import Tournament, Match, TournamentParticipant
        
        with transaction.atomic():
            tournament = Tournament.objects.get(id=tournament_id)
            
            # Count total matches
            total_matches = Match.objects.filter(tournament=tournament).count()
            
            # Only count completed matches (error matches should now be marked as completed)
            completed_matches = Match.objects.filter(
                tournament=tournament,
                status='completed'
            ).count()
            
            # If all matches are completed, mark the tournament as completed
            if total_matches > 0 and total_matches == completed_matches:
                # First recalculate all scores
                if hasattr(tournament, 'recalculate_scores'):
                    tournament.recalculate_scores()
                elif hasattr(tournament, 'complete_tournament'):
                    tournament.complete_tournament()
                else:
                    # Fallback if neither method exists
                    tournament.status = 'completed'
                    tournament.completed_at = timezone.now()
                    tournament.save()
                
                logger.info(f"Tournament {tournament_id} completed with all scores recalculated")
                
    except Exception as e:
        logger.error(f"Error checking tournament completion: {str(e)}")
        return f"Error checking tournament completion: {str(e)}"
    
    return f"Tournament completion check executed for {tournament_id}"