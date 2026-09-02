# src/connections/alphabet.py
import os
import sys
import logging
import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


# Scope: read/write to spreadsheets
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]


def show_setup_instructions():
    """Display persistent setup instructions in terminal."""
    print("\n" + "=" * 60)
    print("GOOGLE SHEETS SETUP REQUIRED")
    print("=" * 60)
    print("""
To get started with Google Sheets, you need a 'client_secrets.json' file.

STEPS:
1. Go to: https://console.cloud.google.com/apis/credentials
2. Create a new project (e.g., 'InvoiceBuddy')
3. Enable 'Google Sheets API' (APIs & Services → Library)
4. Create OAuth Client ID → Desktop app
5. Download the JSON file

SUPPORT:
- Use a personal Gmail account (school/work accounts often blocked)
- File should be named 'client_secrets.json' for simplicity
""")
    print("=" * 60 + "\n")


def google_authenticate_cli(secrets_path=None):
    """
    CLI-based Google authentication with user prompts.
    
    Flow:
    1. Check for existing token → auto-load if found
    2. Prompt user if no token → select file or provide path
    3. Run browser OAuth flow
    4. Cache token for future runs
    """
    # Default paths
    token_dir = os.path.expanduser("~/.config/invoicebuddy/")
    os.makedirs(token_dir, exist_ok=True)
    token_path = os.path.join(token_dir, "google_token.json")
    
    # Step 1: Check for existing token first
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            
            # Refresh if expired
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(token_path, 'w') as f:
                    f.write(creds.to_json())
                logging.info("Refreshed expired Google token.")
            
            logging.info("✓ Loaded existing Google token.")
            return gspread.authorize(creds)
        
        except Exception as e:
            logging.warning(f"Token invalid/expired: {e}")
    
    # Step 2: No valid token — need setup
    print("\nNo Google authentication found. Setting up...")
    
    # Ask user about credentials file
    if not secrets_path:
        answer = input("\nDo you already have a 'client_secrets.json' file? [y/n]: ").strip().lower()
        
        if answer in ['y', 'yes']:
            # User has file — get path
            secrets_path = input("\nEnter the full path to your client_secrets.json: ").strip()
            secrets_path = os.path.expanduser(secrets_path)  # Expand ~ for home dir
            
            if not os.path.exists(secrets_path):
                print(f"\n❌ File not found at: {secrets_path}")
                print("Please verify the path is correct.\n")
                return None
        else:
            # User needs to create file
            show_setup_instructions()
            secrets_path = input("\nEnter the path where you saved your client_secrets.json: ").strip()
            secrets_path = os.path.expanduser(secrets_path)
            
            if not os.path.exists(secrets_path):
                print(f"\n⚠️  File not found at: {secrets_path}")
                print("Make sure you downloaded it from Google Cloud Console.")
                print("Try running this command again after confirming the file exists.\n")
                return None
    
    # Step 3: Run browser OAuth flow
    print(f"\n📝 Using secrets file: {secrets_path}")
    print("🌐 Browser will open for Google sign-in...\n")
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file(secrets_path, SCOPES)
        creds = flow.run_local_server(port=0)
        
        # Save token for future use
        with open(token_path, 'w') as f:
            f.write(creds.to_json())
        
        print("\n✅ Google OAuth successful!")
        print(f"   Token saved to: {token_path}")
        print("   Future runs will authenticate automatically.\n")
        return gspread.authorize(creds)
    
    except Exception as e:
        logging.error(f"OAuth flow failed: {e}")
        print(f"\n❌ Authentication failed: {e}\n")
        return None


# CLI test
if __name__ == "__main__":
    print("=" * 50)
    print("Google Sheets Authentication Test")
    print("=" * 50)
    
    gc = google_authenticate_cli()
    
    if gc:
        # Quick test: list spreadsheets
        print("\n📊 Testing connection...")
        try:
            spreadsheets = gc.openall()
            print(f"✅ Connected! Found {len(spreadsheets)} spreadsheet(s):")
            for s in spreadsheets[:5]:  # Show first 5
                print(f"   - {s.title}")
            if len(spreadsheets) > 5:
                print(f"   ... and {len(spreadsheets) - 5} more")
        except Exception as e:
            print(f"⚠️  Connection OK but couldn't list spreadsheets: {e}")
    else:
        print("\n❌ Authentication failed or cancelled.")
