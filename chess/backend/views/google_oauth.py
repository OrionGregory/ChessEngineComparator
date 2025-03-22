from flask import Blueprint, url_for, redirect, jsonify

google_oauth_bp = Blueprint('google_oauth', __name__)

def get_google_client():
    # Lazy import to avoid circular dependency
    from app import oauth
    return oauth.create_client('google')

@google_oauth_bp.route('/login/google')
def google_login():
    google = get_google_client()
    redirect_uri = url_for('google_oauth.google_authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@google_oauth_bp.route('/login/google/callback')
def google_authorize():
    # Lazy import to avoid circular dependency
    from app import get_db_connection, create_access_token
    google = get_google_client()
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM users WHERE email = %s', (user_info['email'],))
        user = cursor.fetchone()
        
        if not user:
            username = user_info['email'].split('@')[0]
            cursor.execute(
                'INSERT INTO users (username, email, oauth_provider, oauth_id) VALUES (%s, %s, %s, %s) RETURNING id',
                (username, user_info['email'], 'google', user_info['id'])
            )
            conn.commit()
            user_id = cursor.fetchone()['id']
        else:
            user_id = user['id']
            if not user.get('oauth_provider'):
                cursor.execute(
                    'UPDATE users SET oauth_provider = %s, oauth_id = %s WHERE id = %s',
                    ('google', user_info['id'], user_id)
                )
                conn.commit()
        
        access_token = create_access_token(identity=str(user_id))
        redirect_url = f"http://localhost:3001/oauth-callback?token={access_token}"
        return redirect(redirect_url)
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()