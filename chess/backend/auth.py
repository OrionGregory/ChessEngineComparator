from flask import Flask, redirect, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import google_auth_oauthlib.flow
import urllib.parse
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Flask app setup
app = Flask(__name__)

# Enable CORS with proper configuration
CORS(app, 
     supports_credentials=True,
     resources={r"/*": {"origins": "https://localhost:3000"}},
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "OPTIONS"])

app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Google OAuth config
CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

# Database configuration
db_password = os.getenv('DB_PASSWORD')
encoded_password = urllib.parse.quote_plus(db_password)
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')

# Google Cloud SQL setup
app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql+psycopg2://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Specify the login view

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/auth/login")
def login():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        "client_secret.json", 
        scopes=["openid", "email", "profile"]
    )
    flow.redirect_uri = REDIRECT_URI
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session["state"] = state
    return redirect(auth_url) 

@app.route("/auth/callback")
def callback():
    try:
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            "client_secret.json",
            scopes=["https://www.googleapis.com/auth/userinfo.profile",
                    "https://www.googleapis.com/auth/userinfo.email",
                    "openid"],
            state=session["state"]
        )
        flow.redirect_uri = REDIRECT_URI
        flow.fetch_token(authorization_response=request.url)

        credentials = flow.credentials
        session["credentials"] = credentials_to_dict(credentials)

        user_info = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {credentials.token}"}
        ).json()

        google_id = user_info["id"]
        email = user_info["email"]
        name = user_info["name"]

        user = User.query.filter_by(google_id=google_id).first()

        if user:
            login_user(user, remember=True)
            session["user_id"] = user.id
            return redirect("https://localhost:3000/home")
        else:
            params = urllib.parse.urlencode({
                'email': email,
                'name': name,
                'google_id': google_id
            })
            return redirect(f"https://localhost:3000/signup?{params}")
    except Exception as e:
        return redirect("https://localhost:3000/error")


@app.route("/auth/signup", methods=["POST"])
def signup():
    try:
        data = request.json
        google_id = data["google_id"]
        email = data["email"]
        name = data["name"]
        username = data["username"]

        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already taken"}), 400

        if User.query.filter_by(google_id=google_id).first():
            return jsonify({"error": "Account already exists"}), 400

        user = User(google_id=google_id, email=email, name=name, username=username)
        db.session.add(user)
        db.session.commit()

        login_user(user, remember=True) # Log in the user after signup
        session["user_id"] = user.id
        return jsonify({"message": "Signup successful", "redirect_url": "/home"}), 200
    except Exception as e:
        return jsonify({"error": "Signup failed", "details": str(e)}), 400

@app.route("/auth/logout")
@login_required
def logout():
    try:
        logout_user()
        session.pop("user_id", None)  # Clear user ID from session
        response = jsonify({"message": "Logged out successfully"})
        return response, 200
    except Exception as e:
        return jsonify({"error": "Logout failed"}), 400

@app.route("/home")
@login_required
def home():
    try:
        user_data = {
            "message": f"Welcome, {current_user.name}!",
            "user": {
                "name": current_user.name,
                "email": current_user.email,
                "username": current_user.username,
            },
        }
        return jsonify(user_data), 200
    except Exception as e:
        return jsonify({"error": "Failed to fetch user data"}), 400

def credentials_to_dict(credentials):
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes
    }

if __name__ == "__main__":
    print("Flask server is running on https://localhost:5000")
    app.run(debug=True, ssl_context=('cert.pem', 'key.pem'))