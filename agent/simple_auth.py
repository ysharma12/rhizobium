"""
Simple Google Drive Authentication for WSL
Even simpler approach - just get the code from URL
"""

import os
import sys
import pickle
from urllib.parse import urlparse, parse_qs


def simple_authenticate():
    """Simple authentication process."""
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
    except ImportError:
        print("Installing required packages...")
        os.system("pip install -q google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
    
    SCOPES = [
        'https://www.googleapis.com/auth/drive.readonly',
        'https://www.googleapis.com/auth/drive.file'
    ]
    
    print("\n" + "=" * 70)
    print("🔐 GOOGLE DRIVE AUTHENTICATION (WSL-Friendly)")
    print("=" * 70 + "\n")
    
    # Check credentials
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json not found!")
        print("\nYou need to download OAuth credentials from Google Cloud Console.")
        print("See TROUBLESHOOTING_GDRIVE.md for instructions.\n")
        return False
    
    # Check existing token
    if os.path.exists('token.pickle'):
        print("Found existing authentication token...")
        try:
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
            
            if creds and creds.valid:
                print("✅ Already authenticated!\n")
                return True
            elif creds and creds.expired and creds.refresh_token:
                print("Refreshing token...")
                creds.refresh(Request())
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
                print("✅ Token refreshed!\n")
                return True
        except:
            print("Token invalid, will re-authenticate...\n")
            os.remove('token.pickle')
    
    # Start authentication
    print("📋 INSTRUCTIONS FOR WSL:")
    print("=" * 70)
    print("1. A URL will appear below")
    print("2. Copy and paste it into your WINDOWS browser")
    print("3. Sign in and click 'Allow' or 'Continue'")
    print("4. Browser will redirect to localhost (may show 'can't reach')")
    print("5. Copy the 'code' from the URL in address bar")
    print("6. Paste it back here\n")
    print("Example URL after redirect:")
    print("http://localhost:12345/?code=4/0Adeu5BW...&scope=...")
    print("                              ^^^^^^^^^ copy this part")
    print("=" * 70 + "\n")
    
    input("Press ENTER when ready...")
    print()
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        
        # Get auth URL
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            prompt='consent'
        )
        
        print("=" * 70)
        print("📋 STEP 1: Copy this URL and open in your browser:")
        print("=" * 70)
        print(f"\n{auth_url}\n")
        print("=" * 70 + "\n")
        
        # Get redirect URL
        print("📋 STEP 2: After authorizing, you'll be redirected.")
        print("Copy the FULL URL from your browser's address bar.\n")
        
        redirect_url = input("Paste the redirect URL here: ").strip()
        
        if not redirect_url:
            print("\n❌ No URL provided.\n")
            return False
        
        # Extract code from URL
        if 'code=' in redirect_url:
            parsed = urlparse(redirect_url)
            params = parse_qs(parsed.query)
            code = params.get('code', [None])[0]
            
            if code:
                print("\n🔄 Exchanging code for credentials...")
                flow.fetch_token(code=code)
                creds = flow.credentials
                
                # Save credentials
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
                
                print("\n" + "=" * 70)
                print("✅ AUTHENTICATION SUCCESSFUL!")
                print("=" * 70)
                print("\nToken saved to: token.pickle")
                print("\nYou can now:")
                print("  • Download: python download_from_gdrive.py")
                print("  • Upload: ./upload.sh")
                print("  • Run analysis: ./run_complete_analysis.sh\n")
                return True
        
        print("\n❌ Could not extract code from URL.")
        print("Make sure you copied the complete URL from your browser.\n")
        return False
        
    except Exception as e:
        print(f"\n❌ Authentication failed: {e}\n")
        print("Try again with: python simple_auth.py\n")
        return False


if __name__ == "__main__":
    success = simple_authenticate()
    sys.exit(0 if success else 1)


