from flask import session, redirect, url_for, request
from functools import wraps
from cryptography.fernet import Fernet
import os

# Use a securely generated key - keep this safe!
FERNET_KEY = os.getenv("FERNET_KEY").encode()
fernet = Fernet(FERNET_KEY)

WHITELIST_ROUTES = ['/', 'auth.login', 'auth.signup', 'auth.forgot_password']


def decrypt_user_token(token):
    try:
        return fernet.decrypt(token.encode()).decode()
    except Exception:
        return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        endpoint = request.endpoint
        if endpoint in WHITELIST_ROUTES:
            return f(*args, **kwargs)

        encrypted_key = session.get("key")
        if not encrypted_key:
            return redirect(url_for('auth.login'))

        user_id = session.get("user_id")
        decrypted_email = decrypt_user_token(encrypted_key)
        if decrypted_email != session.get("email"):
            session.clear()
            return redirect(url_for('auth.login'))

        return f(*args, **kwargs)
    return decorated_function
