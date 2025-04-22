# Student Usage Guide

This guide provides instructions for students on how to use the Chess Engine Comparator platform effectively.

---

## Getting Started

### **Sign Up and Login**
- Visit the platform's homepage.
- Sign in with Google
- **Ensure that you are logging in with a Google account that is registered under your school email!**

---

## Dashboard Overview

Once logged in, you will be directed to your **Student Dashboard**, which includes the following sections:

### 1. **Profile**
- View your account details, including your username and email.
- Update your profile information if allowed by the platform.

### 2. **Bots**
- View all the chess bots you have created.
- Each bot displays:
  - **Name**
  - **Version**
  - **Status** (e.g., Draft, Active, Archived)
  - **Visibility** (e.g., Public, Private)

---

## Creating and Managing Bots

### 1. **Create a New Bot**
- Navigate to the **Bots** section.
- Click on the **Create New Bot** button.
- Fill in the following details:
  - **Name**: Give your bot a unique name.
  - **Description**: Provide a brief description of your bot.
  - **Visibility**: Choose whether the bot is public or private.
  - **Upload Bot**: Select which bot you wish to upload from your local directory
- Save your bot.

### 2. **Delete a Bot / Archiving a Bot**
- Locate the bot you want to archive.
- Click the **Archive** button.
- This does not delete your bot from the Database, so teachers can still view the bot, however this ensures that the bot cannot participate in any tournaments

---

## Additional Features

### **Leaderboard**
- Check the leaderboard to see how your bots rank against others.


---

## Troubleshooting

### **How do I program a chess Bot?**
Here is a template bot that is available for you to use:
```py
import chess
import random

class StudentChessBot:
    def __init__(self):
        self.board = chess.Board()

    def select_move(self):
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return None
        # Replace this with your own strategy!
        return random.choice(legal_moves)

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
here is more documentation on python-chess and how it works:
https://python-chess.readthedocs.io/en/latest/
