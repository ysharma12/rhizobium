"""
Google Drive File Downloader
Downloads Excel files from Google Drive before running QA analysis.
"""

import os
import sys
from pathlib import Path
from datetime import datetime


def download_with_gdown(file_id: str, output_path: str) -> bool:
    """
    Download file using gdown (simple, works for publicly shared files).
    
    Args:
        file_id: Google Drive file ID
        output_path: Local path to save the file
    
    Returns:
        True if successful, False otherwise
    """
    try:
        import gdown
    except ImportError:
        print("❌ gdown not installed. Installing...")
        os.system("pip install gdown")
        import gdown
    
    try:
        print(f"📥 Downloading from Google Drive (ID: {file_id})...")
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, output_path, quiet=False)
        print(f"✅ Downloaded successfully to: {output_path}")
        return True
    except Exception as e:
        print(f"❌ Error downloading with gdown: {e}")
        return False


def download_with_google_api(file_id: str, output_path: str, credentials_path: str = "credentials.json") -> bool:
    """
    Download file using Google Drive API (more robust, requires OAuth setup).
    
    Args:
        file_id: Google Drive file ID
        output_path: Local path to save the file
        credentials_path: Path to Google API credentials JSON
    
    Returns:
        True if successful, False otherwise
    """
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseDownload
        import pickle
        import io
    except ImportError:
        print("❌ Google API libraries not installed.")
        print("Installing: google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        os.system("pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseDownload
        import pickle
        import io
    
    SCOPES = [
        'https://www.googleapis.com/auth/drive.readonly',
        'https://www.googleapis.com/auth/drive.file'
    ]
    
    try:
        creds = None
        token_path = 'token.pickle'
        
        # Load existing credentials
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(credentials_path):
                    print(f"❌ Credentials file not found: {credentials_path}")
                    print("Please follow setup instructions in GDRIVE_SETUP.md")
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next time
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        # Download the file
        print(f"📥 Downloading from Google Drive (ID: {file_id})...")
        service = build('drive', 'v3', credentials=creds)
        request = service.files().get_media(fileId=file_id)
        
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                print(f"   Progress: {int(status.progress() * 100)}%")
        
        # Write to file
        fh.seek(0)
        with open(output_path, 'wb') as f:
            f.write(fh.read())
        
        print(f"✅ Downloaded successfully to: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error downloading with Google API: {e}")
        return False


def extract_file_id_from_url(url: str) -> str:
    """
    Extract file ID from various Google Drive URL formats.
    
    Supports:
    - https://drive.google.com/file/d/FILE_ID/view
    - https://drive.google.com/open?id=FILE_ID
    - https://docs.google.com/spreadsheets/d/FILE_ID/edit
    """
    import re
    
    # Order matters! Try most specific patterns first
    patterns = [
        r'/spreadsheets/d/([a-zA-Z0-9_-]+)',  # Spreadsheet URLs
        r'/document/d/([a-zA-Z0-9_-]+)',      # Document URLs
        r'/file/d/([a-zA-Z0-9_-]+)',          # File URLs
        r'/folders/([a-zA-Z0-9_-]+)',         # Folder URLs
        r'[?&]id=([a-zA-Z0-9_-]+)',           # Query parameter (use [?&] to ensure it's a param)
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            file_id = match.group(1)
            # Make sure we didn't accidentally match a user ID (ouid)
            # File IDs are typically 25-40 chars, user IDs are often longer numbers
            if not file_id.isdigit() or len(file_id) < 20:
                return file_id
    
    # If no pattern matched, assume it's already a file ID
    return url


def main():
    """Main function to download file from Google Drive."""
    print("=" * 70)
    print("GOOGLE DRIVE FILE DOWNLOADER")
    print("=" * 70)
    print()
    
    # Configuration
    config_file = "gdrive_config.txt"
    
    # Check if config file exists
    if os.path.exists(config_file):
        print(f"📋 Reading configuration from {config_file}...")
        with open(config_file, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]
            # Handle different formats
            config_lines = []
            for line in lines:
                # Handle "Label: value" format
                if ':' in line and ('http' in line or '/' in line or len(line) > 20):
                    # Extract URL/path after colon
                    config_lines.append(line.split(':', 1)[1].strip())
                else:
                    config_lines.append(line)
            
            if len(config_lines) >= 1:
                file_id_or_url = config_lines[0]
                output_path = config_lines[1] if len(config_lines) > 1 else "../data/Testing master_Welcome Call 2026.xlsx"
                method = config_lines[2] if len(config_lines) > 2 else "gdown"
            else:
                print(f"❌ Invalid config file format")
                return False
    else:
        # Interactive mode
        print("No configuration file found. Creating one...")
        print()
        print("Please enter your Google Drive file information:")
        print()
        
        file_id_or_url = input("Google Drive File ID or sharing URL: ").strip()
        output_path = input("Local output path (e.g., ../data/Testing_master.xlsx): ").strip()
        
        print()
        print("Download method:")
        print("  1. gdown (simple, works for publicly shared files)")
        print("  2. Google Drive API (more reliable, requires OAuth setup)")
        method_choice = input("Choose method (1 or 2) [1]: ").strip() or "1"
        method = "gdown" if method_choice == "1" else "api"
        
        # Save configuration
        with open(config_file, 'w') as f:
            f.write(f"# Google Drive Configuration\n")
            f.write(f"# Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"# File ID or URL\n")
            f.write(f"{file_id_or_url}\n\n")
            f.write(f"# Output path\n")
            f.write(f"{output_path}\n\n")
            f.write(f"# Download method (gdown or api)\n")
            f.write(f"{method}\n")
        
        print(f"\n✅ Configuration saved to {config_file}")
        print()
    
    # Extract file ID if URL was provided
    file_id = extract_file_id_from_url(file_id_or_url)
    print(f"📝 File ID: {file_id}")
    print(f"📁 Output: {output_path}")
    print(f"🔧 Method: {method}")
    print()
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 Created directory: {output_dir}")
    
    # Download the file
    success = False
    if method.lower() == "api":
        success = download_with_google_api(file_id, output_path)
    else:
        success = download_with_gdown(file_id, output_path)
    
    if success:
        # Verify file exists and show size
        if os.path.exists(output_path):
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"📊 File size: {size_mb:.2f} MB")
            print(f"🕐 Download time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            print("=" * 70)
            print("✅ DOWNLOAD COMPLETE!")
            print("=" * 70)
            return True
        else:
            print("❌ File download reported success but file not found")
            return False
    else:
        print()
        print("=" * 70)
        print("❌ DOWNLOAD FAILED")
        print("=" * 70)
        print()
        print("Troubleshooting tips:")
        print("1. Make sure the file is shared (Anyone with the link)")
        print("2. Check that the file ID is correct")
        print("3. Try the other download method")
        print("4. See GDRIVE_SETUP.md for detailed setup instructions")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

