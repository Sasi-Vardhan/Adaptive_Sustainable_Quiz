import os, json
from flask import Flask,render_template,request,redirect,url_for,flash,session
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials,firestore
from auth import auth_bp
from quiz import quiz_bp
from dashboard import dash
from sustainability import sustain
from firestore_config import db
from LO import LO
from feedback import feedback
from genAI import AI

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Firebase Init


# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(quiz_bp)
app.register_blueprint(dash)
app.register_blueprint(sustain)
app.register_blueprint(LO)
app.register_blueprint(feedback)
app.register_blueprint(AI)

# Middleware to check if user is logged in

@app.before_request
def require_login():
    allowed_routes = ['auth.login', 'auth.logout', 'main', 'static']  # Added 'static'
    if 'email' not in session and request.endpoint not in allowed_routes:
        return redirect(url_for('auth.login'))
    


@app.route('/',methods=['GET', 'POST'])
def main():
    if request.method == "POST":
        name = request.form.get('rqName')
        email = request.form.get('email')
        goal = request.form.get('goal')
        objectives = request.form.get('objectives')  # Fetch textarea data

        # Validate the data
        if not name or not email or goal == "Select Learning Goal":
            flash("Please fill in all required fields.", "error")
            return redirect(url_for('index'))

        # Prepare data to store in Firestore
        demo_request = {
            "name": name,
            "email": email,
            "goal": goal,
            "objectives": objectives if objectives else "",  # Handle empty textarea
            "timestamp": firestore.SERVER_TIMESTAMP
        }
        db.collection('deom_requests').add(demo_request)
    return render_template("main.html")
if __name__ == '__main__':
    app.run(debug=True,port=3000)
