import os
import json
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials

load_dotenv()  # Load environment variables

def initialize_firebase():
    firebase_creds_json = os.getenv("FIREBASE_CREDENTIALS")
    if not firebase_creds_json:
        raise ValueError("❌ FIREBASE_CREDENTIALS not set in environment!")

    try:
        cred = credentials.Certificate(json.loads(firebase_creds_json))
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized successfully from JSON string!")
    except Exception as e:
        print(f"❌ Firebase initialization failed: {e}")
        raise
