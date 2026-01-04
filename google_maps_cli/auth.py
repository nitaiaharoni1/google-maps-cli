"""Authentication for Google Maps Platform APIs (API Key and OAuth 2.0)."""

import os
import json
from pathlib import Path
from .utils import (
    get_api_key_path, get_token_path, get_credentials_path,
    ensure_token_permissions, set_default_account
)

# Try to import OAuth libraries (optional)
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    OAUTH_AVAILABLE = True
except ImportError:
    OAUTH_AVAILABLE = False

# Google Maps Platform OAuth scopes
# Note: These scopes may not exist for user saved places, but we'll try
SCOPES = [
    "openid",  # Required by Google OAuth
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    # Add Maps-specific scopes if they exist
]


def get_api_key(account=None):
    """
    Get API key from storage.
    
    Args:
        account: Account name (optional). If None, uses default account.
    
    Returns:
        API key string, or None if not found.
    """
    api_key_path = get_api_key_path(account)
    
    if api_key_path.exists():
        try:
            with open(api_key_path) as f:
                data = json.load(f)
                return data.get("api_key")
        except Exception as e:
            print(f"Warning: Could not load API key: {e}")
            return None
    
    return None


def save_api_key(api_key, account=None):
    """
    Save API key to storage.
    
    Args:
        api_key: The API key to save
        account: Account name (optional). If not provided, uses "default"
    """
    if not account:
        account = "default"
    
    api_key_path = get_api_key_path(account)
    
    data = {"api_key": api_key}
    with open(api_key_path, "w") as f:
        json.dump(data, f, indent=2)
    
    ensure_token_permissions(api_key_path)
    
    # Set as default account if it's the first one
    set_default_account(account)


def authenticate(account=None):
    """
    Prompt user for API key and save it.
    
    Args:
        account: Account name (optional). If provided, saves key for this account.
    
    Returns:
        API key string on success, None on failure.
    """
    print("🔑 Google Maps API Key Setup")
    print("\nTo get your API key:")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Create/select a project")
    print("3. Enable the Maps APIs you need:")
    print("   - Places API")
    print("   - Geocoding API")
    print("   - Directions API")
    print("   - Distance Matrix API")
    print("   - Time Zone API")
    print("   - Elevation API")
    print("4. Go to 'Credentials' → 'Create Credentials' → 'API Key'")
    print("5. Copy your API key")
    print()
    
    api_key = input("Enter your Google Maps API key: ").strip()
    
    if not api_key:
        print("❌ API key cannot be empty")
        return None
    
    if not account:
        account = "default"
    
    try:
        save_api_key(api_key, account)
        print(f"✅ API key saved for account: {account}")
        return api_key
    except Exception as e:
        print(f"❌ Failed to save API key: {e}")
        return None


def get_oauth_credentials(account=None):
    """
    Get valid OAuth credentials from storage or run OAuth flow.
    
    Args:
        account: Account name (optional). If None, uses default account.
    
    Returns:
        Credentials object, or None if not available.
    """
    if not OAUTH_AVAILABLE:
        return None
    
    token_path = get_token_path(account)
    creds = None
    
    # Load existing token if available
    if token_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        except Exception as e:
            print(f"Warning: Could not load existing OAuth token: {e}")
            creds = None
    
    # If there are no (valid) credentials available, refresh if possible
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                # Save refreshed token
                with open(token_path, "w") as token_file:
                    token_file.write(creds.to_json())
                ensure_token_permissions(token_path)
            except Exception as e:
                print(f"Error refreshing OAuth token: {e}")
                creds = None
    
    return creds


def authenticate_oauth(account=None):
    """
    Run OAuth 2.0 flow to get user credentials.
    
    Args:
        account: Account name (optional). If provided, saves token for this account.
    
    Returns:
        Credentials object on success, None on failure.
    """
    if not OAUTH_AVAILABLE:
        print("❌ OAuth libraries not available. Install with: pip install google-auth google-auth-oauthlib")
        return None
    
    credentials_path = get_credentials_path()
    
    if not credentials_path:
        print("❌ Error: credentials.json not found")
        print("\nPlease download credentials.json from Google Cloud Console:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create/select a project")
        print("3. Enable the Maps APIs you need")
        print("4. Go to 'Credentials' → 'Create Credentials' → 'OAuth client ID'")
        print("5. Choose 'Desktop app' as application type")
        print("6. Download the JSON file and save it as 'credentials.json'")
        print("7. Place it in the current directory or your home directory")
        return None
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(credentials_path), SCOPES
        )
        creds = flow.run_local_server(port=0)
        
        # Get email address to use as account name if not provided
        if not account:
            try:
                from googleapiclient.discovery import build
                service = build("oauth2", "v2", credentials=creds)
                user_info = service.userinfo().get().execute()
                account = user_info.get("email", "default")
            except:
                account = "default"
        
        # Save credentials for next run
        token_path = get_token_path(account)
        with open(token_path, "w") as token_file:
            token_file.write(creds.to_json())
        
        ensure_token_permissions(token_path)
        
        # Set as default account if it's the first one
        set_default_account(account)
        
        print("✅ OAuth authentication successful! Token saved.")
        return creds
    
    except Exception as e:
        print(f"❌ OAuth authentication failed: {e}")
        return None


def check_auth(account=None, use_oauth=False):
    """
    Check if authenticated (API key or OAuth), prompt to set up if not.
    
    Args:
        account: Account name (optional)
        use_oauth: If True, prefer OAuth over API key
    
    Returns:
        API key string, OAuth credentials object, or None
    """
    # Try OAuth first if requested
    if use_oauth:
        creds = get_oauth_credentials(account)
        if creds:
            return creds
        print("⚠️  No OAuth credentials found. Run 'maps init --oauth' to authenticate.")
        return None
    
    # Try API key
    api_key = get_api_key(account)
    if api_key:
        return api_key
    
    # Try OAuth as fallback
    creds = get_oauth_credentials(account)
    if creds:
        return creds
    
    print("⚠️  No authentication configured. Run 'maps init' to set up API key or 'maps init --oauth' for OAuth.")
    return None

