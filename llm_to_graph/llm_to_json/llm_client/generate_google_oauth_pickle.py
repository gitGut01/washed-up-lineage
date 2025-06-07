import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# Configuration
CLIENT_ID = "Your CLIENT ID"
CLIENT_SECRET = "Your CLIENT SECRET"
TOKEN_PICKLE_PATH = "token.pickle"  # Update this path as needed
SCOPES = ['https://www.googleapis.com/auth/cloud-platform']  # Update scopes as needed

def generate_credentials():
    # Create client configuration
    client_config = {
        "installed": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"]
        }
    }
    
    # Create the flow using the client configuration
    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    
    # Run the OAuth flow
    credentials = flow.run_local_server(port=0)
    
    # Save credentials to pickle file
    with open(TOKEN_PICKLE_PATH, "wb") as token:
        pickle.dump(credentials, token)
    
    print(f"Credentials saved to {TOKEN_PICKLE_PATH}")
    print(f"Token valid: {credentials.valid}")
    print(f"Token expiry: {credentials.expiry}")

if __name__ == "__main__":
    # Remove existing token file if it exists
    if os.path.exists(TOKEN_PICKLE_PATH):
        os.remove(TOKEN_PICKLE_PATH)
        print(f"Removed existing {TOKEN_PICKLE_PATH}")
    
    generate_credentials()