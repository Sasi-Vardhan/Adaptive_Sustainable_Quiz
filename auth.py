from flask import Blueprint, render_template, request, redirect, url_for, session
import requests, os
from firebase_admin import auth
from cryptography.fernet import Fernet

FERNET_KEY = os.getenv("FERNET_KEY").encode()
fernet = Fernet(FERNET_KEY)



auth_bp = Blueprint('auth', __name__)
FIREBASE_WEB_API_KEY = os.getenv("FIREBASE_API_KEY")

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None  # ✅ define error upfront
    if request.method == 'POST':
        email = request.form['email']
        session["email"]=email
        password = request.form['password']
        payload = {
            'email': email,
            'password': password,
            'returnSecureToken': True
        }

        res = requests.post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}",
            json=payload
        )

        if res.ok:
            id_token = res.json()['idToken']
            decoded_token = auth.verify_id_token(id_token)
            session['user_id'] = decoded_token['uid']
            session['key'] = fernet.encrypt(email.encode()).decode()
            return redirect(url_for('dash.dashboard'))  # ✅ Make sure this route exists
        else:
            error = res.json().get('error', {}).get('message', 'Authentication Failed')
    
    return render_template('login.html', error=error)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None  # ✅ define error upfront
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        payload = {
            'email': email,
            'password': password,
            'returnSecureToken': True
        }

        res = requests.post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_WEB_API_KEY}",
            json=payload
        )

        if res.ok:
            return redirect(url_for('auth.login'))  # ✅ Use blueprint prefix
        else:
            error = res.json().get('error', {}).get('message', 'Signup Failed')
        
    return render_template('signUp.html', error=error)
@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    message = None
    error = None

    if request.method == 'POST':
        email = request.form['email']

        payload = {
            "requestType": "PASSWORD_RESET",
            "email": email
        }

        res = requests.post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_WEB_API_KEY}",
            json=payload
        )

        if res.ok:
            message = "📧 A password reset email has been sent!"
        else:
            error = res.json().get('error', {}).get('message', 'Failed to send reset email')

    return render_template('forgot_password.html', message=message, error=error)
