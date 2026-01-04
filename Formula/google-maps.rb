# Homebrew formula for Google Maps CLI
# Formula name: google-maps
# Tap: nitaiaharoni1

class GoogleMaps < Formula
  desc "Command-line interface for Google Maps Platform"
  homepage "https://github.com/nitaiaharoni1/google-maps-cli"
  url "https://github.com/nitaiaharoni1/google-maps-cli/archive/refs/tags/v1.1.0.tar.gz"
  version "1.1.0"
  sha256 "6b7a4e393f2a5e69daa085434200596a717e320c4a96de6f045af5616fc1fe2b"
  license "MIT"
  head "https://github.com/nitaiaharoni1/google-maps-cli.git", branch: "main"

  depends_on "python@3.11"

  def install
    python3 = "python3.11"
    system python3, "-m", "pip", "install", "--prefix=#{prefix}", "."
  end

  test do
    system "#{bin}/maps", "--version"
  end

  def caveats
    <<~EOS
      Google Maps CLI has been installed!

      To get started:
      1. Run setup:
         maps init

      2. Choose authentication method:
         - API Key: For public data (search, directions, geocoding, etc.)
         - OAuth 2.0: For user-specific data (saved places, lists)

      3. For API Key:
         - Go to https://console.cloud.google.com/
         - Create/select a project
         - Enable the Maps APIs you need:
           * Places API
           * Geocoding API
           * Directions API
           * Distance Matrix API
           * Time Zone API
           * Elevation API
         - Go to 'Credentials' → 'Create Credentials' → 'API Key'

      4. For OAuth 2.0:
         - Go to https://console.cloud.google.com/
         - Create/select a project
         - Enable the Maps APIs
         - Go to 'Credentials' → 'Create Credentials' → 'OAuth client ID'
         - Choose 'Desktop app' as application type
         - Download as credentials.json and place in your home directory

      5. Then use: maps help
    EOS
  end
end
