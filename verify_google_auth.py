import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://127.0.0.1:8000"

def test_google_login_mock():
    print("Testing /auth/user/google-login with mock data...")
    
    # NOTE: This token is fake and will cause verify_oauth2_token to fail 
    # unless we mock the google.oauth2.id_token.verify_oauth2_token function.
    # For a real test, the user needs to provide a valid id_token from their frontend.
    
    url = f"{BASE_URL}/auth/user/google-login"
    payload = {
        "id_token": "mock_token_123",
        "fcm_token": "mock_fcm_token_123"
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 401:
            print("SUCCESS: Endpoint reached, but token was (correctly) rejected as invalid.")
        else:
            print("UNEXPECTED: Response code was not 401.")
            
    except Exception as e:
        print(f"FAILED: Could not connect to the server: {e}")

if __name__ == "__main__":
    # Check if server is running
    try:
        requests.get(BASE_URL)
        test_google_login_mock()
    except Exception:
        print(f"Server is not running at {BASE_URL}. Please start it with 'uvicorn app.main:app --reload' before running this test.")
