"""API key authentication for Google Maps Platform APIs."""

import os
import json
from pathlib import Path
from .utils import get_api_key_path, ensure_token_permissions, set_default_account


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


def check_auth(account=None):
    """Check if API key is configured, prompt to set up if not."""
    api_key = get_api_key(account)
    
    if not api_key:
        print("⚠️  No API key configured. Run 'maps init' to set up.")
        return None
    
    return api_key

