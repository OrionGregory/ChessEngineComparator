import os
import chess
# Remove hardcoded bot imports
from game_duel import game_duel
from dynamic_bot_loader import load_uploaded_bots
from tournament_log import TournamentLog  # Import TournamentLog

# Initialize the tournament log.
t_log = TournamentLog("tournament.log")
t_log.log("Tournament started.")

# Construct the absolute path to the uploads directory (corrected)
current_dir = os.path.dirname(__file__)
bots_directory = os.path.abspath(os.path.join(current_dir, "uploads"))

# Load all bots dynamically from the uploads directory
loaded_bots = load_uploaded_bots(bots_directory)
t_log.log(f"Loaded {len(loaded_bots)} bots from {bots_directory}")

# Function to create instances of all available bots
def get_tournament_bots():
    bot_instances = []
    default_skill_level = 3  # Default skill level for bots that don't specify one
    
    for bot_name, bot_class in loaded_bots.items():
        try:
            # Try to instantiate with skill_level parameter
            if hasattr(bot_class.__init__, '__code__') and 'skill_level' in bot_class.__init__.__code__.co_varnames:
                bot_instance = bot_class(skill_level=default_skill_level)
            else:
                # If the bot doesn't accept skill_level parameter, instantiate without it
                bot_instance = bot_class()
                # Set skill_level attribute if it doesn't exist
                if not hasattr(bot_instance, 'skill_level'):
                    bot_instance.skill_level = default_skill_level
            
            bot_instances.append(bot_instance)
            t_log.log(f"Added bot: {bot_name} with skill level {bot_instance.skill_level}")
        except Exception as e:
            t_log.log(f"Error instantiating bot {bot_name}: {e}")
            continue
    
    return bot_instances

# Replace any existing bot selection logic with this
tournament_bots = get_tournament_bots()

# The rest of your tournament logic using tournament_bots

# For demonstration purposes, assign a default skill level to each selected bot.
entrants = []
default_skill_level = 1
for bot in tournament_bots:
    entrant = {
        'name': f"{bot.__class__.__name__} (skill={bot.skill_level})",
        'bot_class': bot.__class__,
        'skill_level': bot.skill_level,
        'points': 0
    }
    entrants.append(entrant)

best_of_series = 3

# Run a round robin tournament among the selected bots.
num_entrants = len(entrants)
for i in range(num_entrants):
    for j in range(i + 1, num_entrants):
        botA = entrants[i]
        botB = entrants[j]
        series_message = f"Series: {botA['name']} vs {botB['name']}"
        print("\n=== " + series_message + " ===")
        t_log.log(series_message)
        result, winner = game_duel(
            num_games=best_of_series,
            botA_class=botA['bot_class'], botA_skill_level=botA['skill_level'],
            botB_class=botB['bot_class'], botB_skill_level=botB['skill_level']
        )
        if winner == "BotA":
            win_message = f"Series winner: {botA['name']}"
            print(win_message)
            botA['points'] += 1
            t_log.log(win_message)
        elif winner == "BotB":
            win_message = f"Series winner: {botB['name']}"
            print(win_message)
            botB['points'] += 1
            t_log.log(win_message)
        else:
            draw_message = "Series ended in a draw (should not happen with overtime)"
            print(draw_message)
            t_log.log(draw_message)

# Print the final tournament standings.
print("\n=== Tournament Standings ===")
entrants.sort(key=lambda e: e['points'], reverse=True)
for entrant in entrants:
    print(f"{entrant['name']}: {entrant['points']} wins")
    t_log.log(f"{entrant['name']}: {entrant['points']} wins")

# Determine and log the tournament winner.
if entrants:
    champion = entrants[0]
    t_log.set_winner(champion['name'])
    t_log.log("Tournament completed.")
t_log.close()