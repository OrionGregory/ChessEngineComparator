from flask import Blueprint, redirect, request, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
import google_auth_oauthlib.flow
import requests
import urllib.parse
from models import User
from extensions import db, login_manager
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash

# Create Blueprint
auth_bp = Blueprint('auth', __name__)

REDIRECT_URI = Config.REDIRECT_URI

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.route("/auth/login")
def oauth_login():
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

@auth_bp.route("/auth/callback")
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
            # Automatically create the user if not found
            username = email.split('@')[0]  # Use part of email as default username
            base_username = username
            count = 1
            while User.query.filter_by(username=username).first():
                username = f"{base_username}{count}"
                count += 1
            new_user = User(
                google_id=google_id,
                email=email,
                name=name,
                username=username
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            session["user_id"] = new_user.id
            return redirect("https://localhost:3000/home")
    except Exception as e:
        print(f"OAuth callback error: {str(e)}")
        return redirect("https://localhost:3000/error")

@auth_bp.route("/auth/logout")
@login_required
def logout_route():
    try:
        logout_user()
        session.pop("user_id", None)
        return jsonify({"message": "Logged out successfully"}), 200
    except Exception as e:
        return jsonify({"error": "Logout failed"}), 400

@auth_bp.route("/auth/status", methods=["GET"])
def auth_status():
    if current_user.is_authenticated:
        return jsonify({
            "authenticated": True,
            "user": {
                "id": current_user.id,
                "name": current_user.name,
                "username": current_user.username,
                "email": current_user.email
            }
        }), 200
    else:
        return jsonify({"authenticated": False}), 200

def credentials_to_dict(credentials):
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes
    }