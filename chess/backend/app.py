from flask import Flask
from flask_cors import CORS
from extensions import db, login_manager
from auth import auth_bp
from controllers.bot_controller import bot_bp
import os
from services import chess_bot_service

def create_app():
    app = Flask(__name__)
    # ...existing configuration...
    app.config.from_object('config.Config')
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    CORS(app, supports_credentials=True,
         resources={
             r"/*": {"origins": "https://localhost:3000"},
             r"/api/update_profile": {"origins": "https://localhost:3000"}
         },
         allow_headers=["Content-Type", "Authorization"])
    
    db.init_app(app)
    login_manager.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(bot_bp)
    
    return app

if __name__ == "__main__":
    app = create_app()

    # Removed stockfish path check and related messages
    default_bot_path = os.path.join(chess_bot_service.UPLOAD_FOLDER, "chess_game.py")
    if os.path.exists(default_bot_path):
        try:
            chess_bot_service.GLOBAL_BOTS["default"] = chess_bot_service.create_bot_instance(default_bot_path)
            print("Default bot loaded from uploads/chess_game.py")
        except Exception as e:
            print(f"Error loading default bot: {e}")
    else:
        print("No default bot found at uploads/chess_game.py")
    
    app.run(debug=True, ssl_context=('cert.pem', 'key.pem'))