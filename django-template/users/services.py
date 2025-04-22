import itertools
from typing import Dict, List, Tuple
from .models import Tournament, ChessBot

def generate_round_robin_matches(tournament: Tournament) -> List[Tuple[ChessBot, ChessBot]]:
    """
    Generate a list of matches for a round-robin tournament
    Returns a list of (white_bot, black_bot) pairs
    """
    # Get all active participants
    participants = list(tournament.participants.filter(status='active'))
    
    # Create all possible pairings (each bot plays against all others)
    matches = []
    for white_bot, black_bot in itertools.combinations(participants, 2):
        matches.append((white_bot, black_bot))
    
    return matches

def generate_round_robin_matches_with_rounds(tournament: Tournament) -> Dict[int, List[Tuple[ChessBot, ChessBot]]]:
    """
    Generate matches for a round-robin tournament, organized by rounds
    Returns a dictionary mapping round numbers to lists of (white_bot, black_bot) pairs
    
    Uses algorithm from: https://en.wikipedia.org/wiki/Round-robin_tournament#Scheduling_algorithm
    """
    # Get all active participants
    participants = list(tournament.participants.filter(status='active'))
    n = len(participants)
    
    # If odd number of participants, add a dummy participant
    if n % 2 == 1:
        participants.append(None)
        n += 1
    
    rounds = {}
    
    # n-1 rounds in total
    for round_num in range(1, n):
        round_matches = []
        
        # Generate pairings for this round
        for i in range(n // 2):
            # Skip matches involving dummy participant
            if participants[i] is not None and participants[n - i - 1] is not None:
                # Alternate white/black for fairness
                if round_num % 2 == 1:
                    round_matches.append((participants[i], participants[n - i - 1]))
                else:
                    round_matches.append((participants[n - i - 1], participants[i]))
        
        rounds[round_num] = round_matches
        
        # Rotate the participants for the next round
        # Keep first player fixed, rotate others
        participants = [participants[0]] + [participants[-1]] + participants[1:-1]
    
    return rounds