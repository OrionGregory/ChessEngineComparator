import os
from game_duel import game_duel
from chess_bot import SimpleChessBot
from stupidbot import StupidChessBot

# Define the Stockfish path
cwd = os.getcwd()
stockfish_path = os.path.join(cwd, "stockfish", "stockfish-ubuntu-x86-64-avx2")

best_of_series = 5

difficulties = [1, 5, 10, 15, 20]

entrants = []
for level in difficulties:
    entrant = {
        'name': f"SimpleChessBot (skill={level})",
        'bot_class': StupidChessBot,
        'skill_level': level,
        'points': 0
    }
    entrants.append(entrant)

# Run a round-robin tournament; each pair plays one series.
num_entrants = len(entrants)
for i in range(num_entrants):
    for j in range(i + 1, num_entrants):
        botA = entrants[i]
        botB = entrants[j]
        print(f"\n=== Series: {botA['name']} vs {botB['name']} ===")
        result, winner = game_duel(
            num_games=best_of_series,
            stockfish_path=stockfish_path,
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

# After all series, display tournament standings.
print("\n=== Tournament Standings ===")
entrants.sort(key=lambda e: e['points'], reverse=True)
for entrant in entrants:
    print(f"{entrant['name']}: {entrant['points']} wins")