#!/bin/bash
# Simple installer for Google Maps CLI

set -e

echo "🚀 Installing Google Maps CLI..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found."
    echo "Please install Python 3.8 or higher: https://www.python.org/downloads/"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python 3.8 or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi

# Install via pip
echo "📦 Installing Google Maps CLI via pip..."
pip3 install --user -e .

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Make sure ~/.local/bin is in your PATH"
echo "   Add to ~/.zshrc or ~/.bashrc:"
echo "   export PATH=\"\$HOME/.local/bin:\$PATH\""
echo ""
echo "2. Reload your shell: source ~/.zshrc"
echo ""
echo "3. Get your Google Maps API key from Google Cloud Console:"
echo "   - Go to https://console.cloud.google.com/"
echo "   - Create/select a project"
echo "   - Enable Maps APIs (Places, Geocoding, Directions, etc.)"
echo "   - Go to 'Credentials' → 'Create Credentials' → 'API Key'"
echo ""
echo "4. Run setup: maps init"
echo ""

