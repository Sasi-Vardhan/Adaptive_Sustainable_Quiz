from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials,firestore
import os,json


# Load JSON from environment variable
firebase_json = os.environ.get("FIREBASE_CREDENTIALS_JSON")

# Convert JSON string to dictionary
cred_dict = json.loads(firebase_json)

# cred_dict = json.loads(os.getenv("FIREBASE_CRED_JSON"))

cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)

# Create Firestore client
db = firestore.client()

# cred = credentials.Certificate("authenticationf-db6f1-firebase-adminsdk-fbsvc-942685adc5.json")
# firebase_admin.initialize_app(cred)
# db = firestore.client()
