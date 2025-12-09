"""
Google Drive Uploader
Uploads reports and visualizations to Google Drive.
"""

import os
import sys
from pathlib import Path
from datetime import datetime


def upload_with_google_api(file_path: str, folder_id: str = None, credentials_path: str = "credentials.json") -> bool:
    """
    Upload file using Google Drive API.
    
    Args:
        file_path: Local file to upload
        folder_id: Google Drive folder ID (optional)
        credentials_path: Path to Google API credentials JSON
    
    Returns:
        True if successful, False otherwise
    """
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        import pickle
    except ImportError:
        print("❌ Google API libraries not installed.")
        print("Installing: google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        os.system("pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        import pickle
    
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
                    print("\nTo upload to Google Drive, you need to:")
                    print("1. Go to https://console.cloud.google.com/")
                    print("2. Create a project and enable Google Drive API")
                    print("3. Create OAuth 2.0 credentials (Desktop app)")
                    print("4. Download credentials.json to this directory")
                    print("\nSee GDRIVE_SETUP.md for detailed instructions.")
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next time
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        # Upload the file
        print(f"📤 Uploading to Google Drive: {file_path}")
        service = build('drive', 'v3', credentials=creds)
        
        file_metadata = {
            'name': os.path.basename(file_path)
        }
        
        if folder_id:
            file_metadata['parents'] = [folder_id]
        
        media = MediaFileUpload(file_path, resumable=True)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        print(f"✅ Uploaded successfully!")
        print(f"   File ID: {file.get('id')}")
        print(f"   View at: {file.get('webViewLink')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error uploading to Google Drive: {e}")
        return False


def upload_latest_reports(credentials_path: str = "credentials.json", folder_id: str = None):
    """Upload the latest reports to Google Drive."""
    print("=" * 70)
    print("UPLOAD REPORTS TO GOOGLE DRIVE")
    print("=" * 70)
    print()
    
    # Find latest files
    import glob
    
    files_to_upload = []
    
    # Latest summary
    summaries = sorted(glob.glob("qa_summary_*.txt"), reverse=True)
    if summaries:
        files_to_upload.append(summaries[0])
    
    # Latest CSV
    csvs = sorted(glob.glob("qa_results_*.csv"), reverse=True)
    if csvs:
        files_to_upload.append(csvs[0])
    
    # HTML report
    html_report = "visualizations/visualizations_report.html"
    if os.path.exists(html_report):
        files_to_upload.append(html_report)
    
    if not files_to_upload:
        print("❌ No files found to upload")
        print("Run the analysis first to generate reports.")
        return False
    
    print(f"Found {len(files_to_upload)} files to upload:")
    for f in files_to_upload:
        print(f"  • {f}")
    print()
    
    # Upload each file
    success_count = 0
    for file_path in files_to_upload:
        if upload_with_google_api(file_path, folder_id, credentials_path):
            success_count += 1
        print()
    
    print("=" * 70)
    if success_count == len(files_to_upload):
        print(f"✅ Successfully uploaded all {success_count} files!")
    else:
        print(f"⚠️  Uploaded {success_count}/{len(files_to_upload)} files")
    print("=" * 70)
    
    return success_count > 0


def main():
    """Main function to upload reports."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Upload QA reports to Google Drive")
    parser.add_argument("--folder-id", help="Google Drive folder ID to upload to")
    parser.add_argument("--credentials", default="credentials.json", help="Path to credentials.json")
    parser.add_argument("files", nargs="*", help="Specific files to upload (optional)")
    
    args = parser.parse_args()
    
    if args.files:
        # Upload specific files
        success_count = 0
        for file_path in args.files:
            if os.path.exists(file_path):
                if upload_with_google_api(file_path, args.folder_id, args.credentials):
                    success_count += 1
            else:
                print(f"❌ File not found: {file_path}")
        
        print(f"\n✅ Uploaded {success_count}/{len(args.files)} files")
    else:
        # Upload latest reports
        upload_latest_reports(args.credentials, args.folder_id)


if __name__ == "__main__":
    main()

