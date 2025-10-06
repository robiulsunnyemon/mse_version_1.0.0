# app/utils/firebase_loader.py
import os
import json
import base64
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials

load_dotenv()


def initialize_firebase():
    print("🚀 Initializing Firebase...")

    # Check if already initialized
    if firebase_admin._apps:
        print("✅ Firebase already initialized")
        return True

    try:
        # Method 1: Try Base64 first (new method)
        firebase_b64 = os.getenv('FIREBASE_CREDENTIALS_BASE64')
        if firebase_b64:
            print("🔑 Using Base64 credentials...")
            decoded = base64.b64decode(firebase_b64).decode('utf-8')
            cred_dict = json.loads(decoded)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized successfully from Base64!")
            return True

        # Method 2: Try direct JSON (old method - backup)
        firebase_json = os.getenv('FIREBASE_CREDENTIALS')
        if firebase_json:
            print("🔑 Using JSON credentials...")
            # Clean the JSON string
            cleaned_json = firebase_json.strip().strip("'")
            cred_dict = json.loads(cleaned_json)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized successfully from JSON!")
            return True

        print("⚠️ No Firebase credentials found in environment variables")
        return False

    except json.JSONDecodeError as e:
        print(f"❌ JSON Decode Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Firebase initialization failed: {e}")
        return False