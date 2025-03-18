# tournament.py
import os
from game_duel import game_duel
from dynamic_bot_loader import load_uploaded_bots

# Construct the absolute path to the uploads directory (corrected)
current_dir = os.path.dirname(__file__)
bots_directory = os.path.abspath(os.path.join(current_dir, "uploads"))

# Load available bots dynamically.
available_bots = load_uploaded_bots(bots_directory)
if not available_bots:
    print("No bots found in the uploads directory.")
    exit(1)

# Display the available bots to the user.
print("Available bots:")
bot_list = list(available_bots.items())
for idx, (bot_name, bot_class) in enumerate(bot_list, start=1):
    print(f"{idx}. {bot_name}")

# Let the user select bots by entering comma-separated indices.
selected_indices_str = input("Enter comma-separated indices of bots to include in the tournament: ")
try:
    selected_indices = [int(x.strip()) for x in selected_indices_str.split(",")]
except ValueError:
    print("Invalid input format. Please enter comma-separated numbers.")
    exit(1)

# Build the dictionary of selected bots.
selected_bots = {}
for index in selected_indices:
    if 1 <= index <= len(bot_list):
        selected_bots[bot_list[index-1][0]] = bot_list[index-1][1]
    else:
        print(f"Index {index} is out of range. Skipping.")

if not selected_bots:
    print("No valid bots selected. Exiting.")
    exit(1)

# For demonstration purposes, assign a default skill level to each selected bot.
entrants = []
default_skill_level = 1
for bot_name, bot_class in selected_bots.items():
    entrant = {
        'name': f"{bot_name} (skill={default_skill_level})",
        'bot_class': bot_class,
        'skill_level': default_skill_level,
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
        print(f"\n=== Series: {botA['name']} vs {botB['name']} ===")
        result, winner = game_duel(
            num_games=best_of_series,
            botA_class=botA['bot_class'], botA_skill_level=botA['skill_level'],
            botB_class=botB['bot_class'], botB_skill_level=botB['skill_level']
        )
        if winner == "BotA":
            print(f"Series winner: {botA['name']}")
            botA['points'] += 1
        elif winner == "BotB":
            print(f"Series winner: {botB['name']}")
            botB['points'] += 1
        else:
            print("Series ended in a draw (should not happen with overtime)")

# Print the final tournament standings.
print("\n=== Tournament Standings ===")
entrants.sort(key=lambda e: e['points'], reverse=True)
for entrant in entrants:
    print(f"{entrant['name']}: {entrant['points']} wins")
