"""
Google Drive Authentication Helper
Handles authentication in WSL where browsers don't auto-open.
"""

import os
import sys
from pathlib import Path


def authenticate_google_drive(credentials_path: str = "credentials.json"):
    """Authenticate with Google Drive API."""
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        import pickle
    except ImportError:
        print("❌ Google API libraries not installed.")
        print("Installing...")
        os.system("pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        import pickle
    
    SCOPES = [
        'https://www.googleapis.com/auth/drive.readonly',
        'https://www.googleapis.com/auth/drive.file'
    ]
    
    print("=" * 70)
    print("GOOGLE DRIVE AUTHENTICATION")
    print("=" * 70)
    print()
    
    # Check if credentials.json exists
    if not os.path.exists(credentials_path):
        print(f"❌ {credentials_path} not found!")
        print()
        print("You need to:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a project and enable Google Drive API")
        print("3. Create OAuth 2.0 credentials (Desktop app)")
        print("4. Download as 'credentials.json' to this directory")
        print()
        print("See TROUBLESHOOTING_GDRIVE.md for detailed steps.")
        return False
    
    token_path = 'token.pickle'
    creds = None
    
    # Check if we already have valid credentials
    if os.path.exists(token_path):
        print("Found existing token.pickle...")
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
        
        # Check if credentials are valid and have the right scopes
        if creds and creds.valid:
            print("✅ Already authenticated with correct permissions!")
            print()
            print("You can now:")
            print("  • Download: python download_from_gdrive.py")
            print("  • Upload: ./upload.sh")
            print("  • Run complete analysis: ./run_complete_analysis.sh")
            return True
        elif creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            try:
                creds.refresh(Request())
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
                print("✅ Token refreshed successfully!")
                return True
            except Exception as e:
                print(f"⚠️  Could not refresh token: {e}")
                print("Will re-authenticate...")
                os.remove(token_path)
    
    # Need to authenticate
    print("Starting authentication process...")
    print()
    print("=" * 70)
    print("IMPORTANT: WSL/Linux Instructions")
    print("=" * 70)
    print()
    print("Since you're using WSL, the browser won't open automatically.")
    print("You'll need to MANUALLY copy the URL and open it in your browser.")
    print()
    print("Steps:")
    print("  1. Copy the URL that appears below")
    print("  2. Open it in your Windows browser (Chrome, Edge, etc.)")
    print("  3. Sign in to your Google account")
    print("  4. Click 'Continue' or 'Allow' to grant access")
    print("  5. You'll be redirected to localhost (might show 'can't be reached')")
    print("  6. Copy the ENTIRE URL from your browser address bar")
    print("  7. Paste it back here when prompted")
    print()
    print("=" * 70)
    print()
    
    input("Press ENTER when ready to continue...")
    print()
    
    try:
        # Create flow with localhost redirect
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_path, 
            SCOPES
        )
        
        # Get authorization URL
        auth_url, _ = flow.authorization_url(prompt='consent')
        
        print("=" * 70)
        print("STEP 1: Open this URL in your Windows browser:")
        print("=" * 70)
        print()
        print(auth_url)
        print()
        print("=" * 70)
        print()
        print("STEP 2: After you authorize:")
        print("  1. The browser will redirect to localhost (may show error)")
        print("  2. Look at the URL in your browser's address bar")
        print("  3. It will look like:")
        print("     http://localhost:XXXXX/?code=4/0Adeu5BW...&scope=...")
        print("  4. Copy the ENTIRE URL from the address bar")
        print()
        
        # Get the full redirect URL from user
        redirect_response = input("Paste the full redirect URL here: ").strip()
        
        if not redirect_response:
            print("❌ No URL provided. Authentication cancelled.")
            return False
        
        # Extract code from URL if needed
        if 'code=' in redirect_response:
            print()
            print("Processing authorization...")
            # Let the flow handle the redirect URL
            flow.fetch_token(authorization_response=redirect_response)
            creds = flow.credentials
        else:
            print("❌ Invalid URL. Make sure you copied the complete URL.")
            return False
        
        # Save credentials
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
        
        print()
        print("=" * 70)
        print("✅ AUTHENTICATION SUCCESSFUL!")
        print("=" * 70)
        print()
        print("Token saved to: token.pickle")
        print()
        print("You can now:")
        print("  • Download: python download_from_gdrive.py")
        print("  • Upload: ./upload.sh")
        print("  • Run complete analysis: ./run_complete_analysis.sh")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Authentication failed: {e}")
        print()
        print("Common issues:")
        print("  • Make sure you copied the complete authorization code")
        print("  • Try again: python authenticate_gdrive.py")
        print("  • Check credentials.json is valid")
        return False


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Authenticate with Google Drive")
    parser.add_argument("--credentials", default="credentials.json", 
                       help="Path to credentials.json")
    parser.add_argument("--reset", action="store_true",
                       help="Delete existing token and re-authenticate")
    
    args = parser.parse_args()
    
    if args.reset and os.path.exists('token.pickle'):
        print("Removing existing token...")
        os.remove('token.pickle')
        print("✅ Token removed")
        print()
    
    success = authenticate_google_drive(args.credentials)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

