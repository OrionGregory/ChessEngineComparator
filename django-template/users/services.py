from typing import List, Tuple, Dict
from .models import ChessBot, Tournament, Match, TournamentParticipant

def generate_round_robin_matches(tournament: Tournament) -> List[Tuple[ChessBot, ChessBot]]:
    """
    Generate round-robin tournament pairings for a set of bots.
    
    Args:
        tournament: Tournament object containing participant bots
    
    Returns:
        List of tuples (white_bot, black_bot) representing match pairings
    """
    # Get active bots participating in the tournament
    bots = list(tournament.participants.filter(status='active'))
    
    # Need at least 2 bots to create matches
    if len(bots) < 2:
        return []
    
    pairings = []
    
    # Generate all possible unique pairings
    for i in range(len(bots)):
        for j in range(i + 1, len(bots)):
            # Create a match with bots[i] as white and bots[j] as black
            pairings.append((bots[i], bots[j]))
    
    return pairings

def generate_round_robin_matches_with_rounds(tournament: Tournament) -> Dict[int, List[Tuple[ChessBot, ChessBot]]]:
    """
    Generate round-robin tournament pairings organized by rounds.
    
    Args:
        tournament: Tournament object containing participant bots
    
    Returns:
        Dictionary mapping round numbers to lists of (white_bot, black_bot) pairings
    """
    # Get active bots participating in the tournament
    bots = list(tournament.participants.filter(status='active'))
    n = len(bots)
    
    # Need at least 2 bots to create matches
    if n < 2:
        return {}
    
    # If odd number of participants, add a "bye" placeholder
    if n % 2 == 1:
        bots.append(None)
        n += 1
    
    # Number of rounds is n-1
    rounds = {}
    
    # Create a circle algorithm implementation
    # Keep the first bot fixed and rotate the others
    for r in range(n - 1):
        rounds[r + 1] = []  # Round numbers start at 1
        
        # Generate pairings for this round
        for i in range(n // 2):
            bot1 = bots[i]
            bot2 = bots[n - 1 - i]
            
            # Skip matches involving the "bye" placeholder
            if bot1 is not None and bot2 is not None:
                # Alternate who plays white for better fairness
                if r % 2 == 0:
                    rounds[r + 1].append((bot1, bot2))
                else:
                    rounds[r + 1].append((bot2, bot1))
        
        # Rotate the bots (except the first one)
        bots = [bots[0]] + [bots[-1]] + bots[1:-1]
    
    return rounds