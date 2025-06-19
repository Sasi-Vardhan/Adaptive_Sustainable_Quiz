from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials,firestore
import os,json

# cred_dict = json.loads(os.getenv("FIREBASE_CRED_JSON"))
cred = credentials.Certificate("authenticationf-db6f1-firebase-adminsdk-fbsvc-942685adc5.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
