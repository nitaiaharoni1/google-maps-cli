"""Utility functions for Google Maps CLI."""

import os
import json
from pathlib import Path


def get_accounts_config_path():
    """Get the path to accounts configuration file."""
    return Path.home() / ".google_maps_accounts.json"


def get_default_account():
    """Get the default account name."""
    config_path = get_accounts_config_path()
    if config_path.exists():
        try:
            with open(config_path) as f:
                config = json.load(f)
                return config.get("default_account")
        except:
            pass
    return None


def set_default_account(account_name):
    """Set the default account name."""
    config_path = get_accounts_config_path()
    config = {}
    if config_path.exists():
        try:
            with open(config_path) as f:
                config = json.load(f)
        except:
            pass
    
    config["default_account"] = account_name
    if "accounts" not in config:
        config["accounts"] = []
    if account_name not in config["accounts"]:
        config["accounts"].append(account_name)
    
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    ensure_token_permissions(config_path)


def list_accounts():
    """List all configured accounts."""
    config_path = get_accounts_config_path()
    if config_path.exists():
        try:
            with open(config_path) as f:
                config = json.load(f)
                return config.get("accounts", [])
        except:
            pass
    return []


def get_api_key_path(account=None):
    """Get the path to the API key file for a specific account."""
    if account is None:
        account = get_default_account()
    
    if account:
        return Path.home() / f".google_maps_api_key_{account}.json"
    else:
        # Legacy: default API key file
        return Path.home() / ".google_maps_api_key.json"


def get_credentials_path():
    """Get the path to credentials.json file (for OAuth if needed)."""
    # Check current directory first
    current_dir = Path.cwd() / "credentials.json"
    if current_dir.exists():
        return current_dir
    
    # Check home directory
    home_dir = Path.home() / "credentials.json"
    if home_dir.exists():
        return home_dir
    
    return None


def ensure_token_permissions(token_path):
    """Ensure token file has secure permissions (600)."""
    if token_path.exists():
        os.chmod(token_path, 0o600)


def format_coordinates(lat, lng):
    """Format coordinates for display."""
    return f"{lat:.6f},{lng:.6f}"


def parse_coordinates(coord_str):
    """Parse coordinate string (lat,lng) into tuple."""
    try:
        parts = coord_str.split(",")
        if len(parts) != 2:
            raise ValueError("Invalid coordinate format")
        return float(parts[0].strip()), float(parts[1].strip())
    except Exception as e:
        raise ValueError(f"Invalid coordinate format: {coord_str}") from e


def format_distance(meters):
    """Format distance in meters to human-readable format."""
    if meters < 1000:
        return f"{meters:.0f}m"
    elif meters < 10000:
        return f"{meters/1000:.2f}km"
    else:
        return f"{meters/1000:.1f}km"


def format_duration(seconds):
    """Format duration in seconds to human-readable format."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        secs = int(seconds % 60)
        if secs > 0:
            return f"{minutes}m {secs}s"
        return f"{minutes}m"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        if minutes > 0:
            return f"{hours}h {minutes}m"
        return f"{hours}h"

