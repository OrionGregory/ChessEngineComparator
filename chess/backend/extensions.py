from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask import jsonify

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

@login_manager.unauthorized_handler
def unauthorized():
    # Return a 401 response for API requests
    return jsonify({"error": "Unauthorized"}), 401