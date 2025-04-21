class ChessBot:
    def process_fen(self, fen):
        """
        Process the FEN string and update the internal state of the bot.
        This method should be overridden by subclasses to implement custom logic.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def select_move(self, legal_moves):
        """
        Select a move from the list of legal moves.
        This method should be overridden by subclasses to implement custom logic.
        """
        raise NotImplementedError("Subclasses must implement this method.")