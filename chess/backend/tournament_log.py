import datetime
import sys
import io

class Tee:
    def __init__(self, stream1, stream2):
        self.stream1 = stream1
        self.stream2 = stream2

    def write(self, message):
        self.stream1.write(message)
        self.stream2.write(message)

    def flush(self):
        self.stream1.flush()
        self.stream2.flush()

class TournamentLog:
    def __init__(self, base_filename="tournament.log"):
        # Create a unique log file name using the timestamp.
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_filename = f"tournament_{timestamp}.log"
        self.log_file = open(self.log_filename, "w")
        self.winner = None
        self.participants = []  # List of bot class names.
        self.results = []       # List of log messages recorded via log().

        # Redirect sys.stdout through Tee to capture console output.
        self.original_stdout = sys.stdout
        self.console_buffer = io.StringIO()
        self.tee = Tee(self.original_stdout, self.console_buffer)
        sys.stdout = self.tee

        # Log the start.
        self.log("Tournament started.")

    def add_participant(self, bot_class):
        self.participants.append(bot_class.__name__)

    def log(self, message):
        timestamp = datetime.datetime.now().isoformat()
        log_message = f"[{timestamp}] {message}"
        self.results.append(log_message)
        # Also write to the log file immediately.
        self.log_file.write(log_message + "\n")
        self.log_file.flush()

    def set_winner(self, winner_name):
        self.winner = winner_name
        self.log(f"Tournament Winner: {winner_name}")

    def close(self):
        # Restore the original stdout.
        sys.stdout = self.original_stdout

        # Prepare a header with participants and winner.
        header_lines = []
        header_lines.append("=== Tournament Summary ===")
        header_lines.append("Participants: " + ", ".join(self.participants))
        header_lines.append("Winner: " + (self.winner if self.winner else "None"))
        header_lines.append("")
        header_lines.append("=== Console Output ===")
        header = "\n".join(header_lines)

        # Get the captured console output.
        console_output = self.console_buffer.getvalue()

        # Combine header, log messages (results), and the console output.
        combined_content = header + "\n\n" + "\n".join(self.results) + "\n\n" + console_output

        # Overwrite the log file with the combined content.
        self.log_file.seek(0)
        self.log_file.truncate()
        self.log_file.write(combined_content)
        self.log_file.close()

# Example usage:
if __name__ == "__main__":
    # Create a tournament log file
    t_log = TournamentLog()
    t_log.log("Tournament started.")

    # Suppose we have two bots.
    class BotA: pass
    class BotB: pass

    t_log.add_participant(BotA)
    t_log.add_participant(BotB)
    t_log.log("Participants added: " + ", ".join(t_log.participants))

    # Log a sample series result.
    t_log.log("Series: BotA vs BotB - Winner: BotA")
    t_log.set_winner("BotA")
    t_log.log("Tournament completed.")
    t_log.close()