# dynamic_bot_loader.py
import os
import importlib.util
from uploads.chess_bot import ChessBot

def load_bot_module(filepath):
    module_name = os.path.splitext(os.path.basename(filepath))[0]
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def load_uploaded_bots(directory):
    """
    Scans the provided directory for Python files and loads any classes that
    inherit from ChessBot.
    """
    bots = {}
    for filename in os.listdir(directory):
        if filename.endswith(".py") and filename != "chess_bot.py":
            filepath = os.path.join(directory, filename)
            try:
                module = load_bot_module(filepath)
            except Exception as e:
                print(f"Error loading module {filename}: {e}")
                continue
            # Look for classes in the module that are subclasses of ChessBot.
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, ChessBot) and attr is not ChessBot:
                    bots[attr_name] = attr
    return bots

if __name__ == "__main__":
    # Example: load bots from a directory named "uploaded_bots"
    bots = load_uploaded_bots("uploads")
    print("Loaded bots:")
    for name, bot_cls in bots.items():
        print(f" - {name}")
