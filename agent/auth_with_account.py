"""
Google Drive Authentication with Account Selection
Ensures you authenticate with the correct Google account.
"""

import os
import sys
import pickle
from urllib.parse import urlparse, parse_qs


def authenticate_with_account_choice():
    """Authenticate with Google Drive, with clear account selection."""
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
    print("🔐 GOOGLE DRIVE AUTHENTICATION")
    print("=" * 70 + "\n")
    
    # Check credentials
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json not found!")
        print("\nPlease download OAuth credentials from Google Cloud Console.")
        print("See TROUBLESHOOTING_GDRIVE.md for instructions.\n")
        return False
    
    # Ask about existing token
    if os.path.exists('token.pickle'):
        print("Found existing authentication token.")
        print()
        
        try:
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
            
            # Try to get account info
            if creds and creds.valid:
                print("✅ You are already authenticated!")
                print()
                
                # Show which account if we can
                try:
                    from googleapiclient.discovery import build
                    service = build('drive', 'v3', credentials=creds)
                    about = service.about().get(fields='user').execute()
                    user = about.get('user', {})
                    email = user.get('emailAddress', 'Unknown')
                    print(f"📧 Authenticated as: {email}")
                except:
                    print("📧 Authenticated (account details not available)")
                
                print()
                choice = input("Do you want to re-authenticate with a different account? (y/n) [n]: ").strip().lower()
                
                if choice != 'y':
                    print("\n✅ Using existing authentication.\n")
                    return True
                else:
                    print("\nRemoving old token to re-authenticate...")
                    os.remove('token.pickle')
            
            elif creds and creds.expired and creds.refresh_token:
                print("Token expired. Refreshing...")
                try:
                    creds.refresh(Request())
                    with open('token.pickle', 'wb') as token:
                        pickle.dump(creds, token)
                    print("✅ Token refreshed!\n")
                    return True
                except:
                    print("Could not refresh. Will re-authenticate...\n")
                    os.remove('token.pickle')
        except:
            print("Token invalid. Will re-authenticate...\n")
            if os.path.exists('token.pickle'):
                os.remove('token.pickle')
    
    # Start new authentication
    print("=" * 70)
    print("🔑 STARTING AUTHENTICATION")
    print("=" * 70)
    print()
    print("⚠️  IMPORTANT: Choose the correct Google account!")
    print()
    print("You will be asked to sign in to Google.")
    print("Make sure you use the account that has access to:")
    print("  • The Excel file you want to download")
    print("  • The folder where you want to upload results")
    print()
    
    # Get account email to use
    print("Which Google account email should be used?")
    account_hint = input("Enter email (or press ENTER to choose in browser): ").strip()
    print()
    
    print("=" * 70)
    print("📋 AUTHENTICATION INSTRUCTIONS (WSL)")
    print("=" * 70)
    print()
    print("1. A URL will appear below")
    print("2. Copy and open it in your WINDOWS browser")
    print("3. Sign in with your Google account")
    if account_hint:
        print(f"   → Use: {account_hint}")
    print("4. Click 'Continue' or 'Allow' when asked for permissions")
    print("5. Browser will redirect to localhost")
    print("6. Copy the FULL URL from browser address bar")
    print("7. Paste it back here")
    print()
    print("⚠️  If you see 'invalid_request' error in browser:")
    print("   This means redirect URIs need to be added in Google Cloud Console")
    print("   See the instructions below to fix it.")
    print()
    print("=" * 70)
    print()
    
    input("Press ENTER to continue...")
    print()
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        
        # Build auth URL with account hint if provided
        auth_params = {
            'access_type': 'offline',
            'prompt': 'consent'
        }
        if account_hint:
            auth_params['login_hint'] = account_hint
        
        auth_url, _ = flow.authorization_url(**auth_params)
        
        print("=" * 70)
        print("📋 STEP 1: Copy this URL and open in your browser:")
        print("=" * 70)
        print()
        print(auth_url)
        print()
        print("=" * 70)
        print()
        
        if account_hint:
            print(f"💡 TIP: Browser should pre-select: {account_hint}")
            print()
        
        print("📋 STEP 2: After authorizing, copy the redirect URL")
        print()
        print("The browser will redirect to something like:")
        print("  http://localhost:XXXXX/?code=4/0Adeu5BW...&scope=...")
        print()
        
        redirect_url = input("Paste the FULL redirect URL here: ").strip()
        print()
        
        if not redirect_url:
            print("❌ No URL provided.\n")
            return False
        
        # Check if it's an error URL
        if 'error' in redirect_url.lower() or 'invalid' in redirect_url.lower():
            print("=" * 70)
            print("❌ AUTHENTICATION ERROR DETECTED")
            print("=" * 70)
            print()
            print("The URL shows an error, likely 'invalid_request'.")
            print()
            print("🔧 HOW TO FIX:")
            print("=" * 70)
            print()
            print("1. Go to: https://console.cloud.google.com/")
            print("2. Select your project")
            print("3. Go to: APIs & Services → Credentials")
            print("4. Click EDIT (✏️) on your OAuth client")
            print("5. Under 'Authorized redirect URIs', add:")
            print()
            print("   http://localhost:8080/")
            print("   http://localhost/")
            print()
            print("6. Click SAVE")
            print("7. Download the credentials again")
            print("8. Replace credentials.json")
            print("9. Run this script again")
            print()
            print("=" * 70)
            print()
            return False
        
        # Extract code from URL
        if 'code=' in redirect_url:
            parsed = urlparse(redirect_url)
            params = parse_qs(parsed.query)
            code = params.get('code', [None])[0]
            
            if code:
                print("🔄 Exchanging authorization code for credentials...")
                flow.fetch_token(code=code)
                creds = flow.credentials
                
                # Save credentials
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
                
                print()
                print("=" * 70)
                print("✅ AUTHENTICATION SUCCESSFUL!")
                print("=" * 70)
                print()
                
                # Try to show which account was authenticated
                try:
                    from googleapiclient.discovery import build
                    service = build('drive', 'v3', credentials=creds)
                    about = service.about().get(fields='user').execute()
                    user = about.get('user', {})
                    email = user.get('emailAddress', 'Unknown')
                    display_name = user.get('displayName', '')
                    
                    print(f"📧 Authenticated as: {email}")
                    if display_name:
                        print(f"👤 Name: {display_name}")
                except:
                    print("📧 Authentication complete!")
                
                print()
                print("Token saved to: token.pickle")
                print()
                print("✅ You can now:")
                print("  • Download: python download_from_gdrive.py")
                print("  • Upload: ./upload.sh")
                print("  • Run analysis: ./run_complete_analysis.sh")
                print()
                
                return True
        
        print("❌ Could not extract authorization code from URL.")
        print("Make sure you copied the complete URL from your browser.\n")
        return False
        
    except Exception as e:
        print(f"\n❌ Authentication failed: {e}\n")
        print("Common issues:")
        print("  • Redirect URIs not configured (see fix above)")
        print("  • Wrong Google account selected")
        print("  • Network issues")
        print()
        print("Try again: python auth_with_account.py\n")
        return False


if __name__ == "__main__":
    print()
    print("This script will help you authenticate with Google Drive.")
    print("It will ensure you're using the correct Google account.")
    print()
    
    success = authenticate_with_account_choice()
    
    if success:
        print("\n🎉 Setup complete! You're ready to use the QA analyzer.\n")
    else:
        print("\n⚠️  Authentication incomplete. Please try again.\n")
    
    sys.exit(0 if success else 1)


