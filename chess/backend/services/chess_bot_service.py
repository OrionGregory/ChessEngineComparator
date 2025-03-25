import os, sys, traceback
import chess
import datetime
import importlib.util
from io import StringIO
from contextlib import contextmanager

# Define global state and upload folder
GLOBAL_BOTS = {}
BASE_DIR = os.path.dirname(os.path.abspath(__file__)).replace(r"\services", "")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def create_bot_instance(filepath):
    spec = importlib.util.spec_from_file_location("bot", filepath)
    bot_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bot_module)
    chess_bot_class = None
    for name, obj in bot_module.__dict__.items():
        if not isinstance(obj, type):
            continue
        try:
            temp_instance = obj()
            has_required_attributes = (
                hasattr(temp_instance, 'board') and 
                hasattr(obj, 'select_move') and callable(getattr(obj, 'select_move'))
            )
            if has_required_attributes:
                chess_bot_class = obj
                print(f"Found valid chess bot class: {name}")
                break
        except Exception as e:
            print(f"Error checking class {name}: {str(e)}")
            continue
    if not chess_bot_class:
        raise ValueError("No valid chess bot class found. Your class must have a 'board' attribute and a 'select_move' method")
    try:
        return chess_bot_class()
    except Exception as e:
        raise ValueError(f"Failed to instantiate bot class: {str(e)}")

@contextmanager
def capture_output():
    new_out = StringIO()
    old_out = sys.stdout
    sys.stdout = new_out
    try:
        yield new_out
    finally:
        sys.stdout = old_out
