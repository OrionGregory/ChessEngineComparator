# Stockfish-Based Chess Bot
This is a working example of a chess bot that uses Stockfish to select the best possible moves.

If you're looking for a strong baseline for testing or comparison, using Stockfish is a great choice—it will likely outperform any bot built purely with Python logic.


## NOTICE
If you are hosting this say, on a cloud provider, it may not have AVX2 instruction support. In which case Stockfish WILL NOT WORK!

You can run this on any server that does have AVX2 support and Stockfish will work.

# Customizing Bot Difficulty

## To change the bot's difficulty, modify the skill_level parameter in the constructor:
```py
def __init__(self, skill_level=5):
```
The skill_level can be set between 1 (easiest) and 20 (hardest).

## Example Code
```py
import chess
import subprocess
import os
import traceback

class StockfishChessBot:
    def __init__(self, skill_level=5):
        try:
            self.log_path = "/tmp/stockfish_bot_debug.log"
            with open(self.log_path, "a") as f:
                f.write("Initializing StockfishChessBot...\n")

            self.board = chess.Board()
            self.skill_level = skill_level

            current_dir = os.path.dirname(os.path.abspath(__file__))
            stockfish_path = os.path.abspath(
                os.path.join(current_dir, "../../../stockfish/stockfish-ubuntu-x86-64-avx2")
            )

            if not os.path.isfile(stockfish_path):
                raise FileNotFoundError(f"Stockfish not found at {stockfish_path}")

            self.engine = subprocess.Popen(
                [stockfish_path],
                universal_newlines=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )

            self._init_engine()

            with open(self.log_path, "a") as f:
                f.write("Initialization complete.\n")

        except Exception as e:
            with open("/tmp/stockfish_bot_debug.log", "a") as f:
                f.write("FAILED INIT\n")
                f.write(str(e) + "\n")
                f.write(traceback.format_exc())
            raise  # Still re-raise

    def _init_engine(self):
        self._send("uci")
        self._wait_for("uciok")
        self._send(f"setoption name Skill Level value {self.skill_level}")
        self._send("isready")
        self._wait_for("readyok")

    def _send(self, command):
        self.engine.stdin.write(command + "\n")
        self.engine.stdin.flush()

    def _wait_for(self, target):
        while True:
            line = self.engine.stdout.readline().strip()
            if target in line:
                break

    def _get_best_move(self):
        self._send(f"position fen {self.board.fen()}")
        self._send("go movetime 100")
        while True:
            line = self.engine.stdout.readline().strip()
            if line.startswith("bestmove"):
                return line.split()[1]

    def select_move(self):
        if self.board.is_game_over():
            return None
        move_uci = self._get_best_move()
        return chess.Move.from_uci(move_uci)

    def make_move(self, move_uci):
        try:
            move = chess.Move.from_uci(move_uci)
            if move in self.board.legal_moves:
                self.board.push(move)
                return True
        except ValueError:
            pass
        return False
```
