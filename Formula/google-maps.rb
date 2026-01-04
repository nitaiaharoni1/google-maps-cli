# Homebrew formula for Google Maps CLI
# Formula name: google-maps
# Tap: nitaiaharoni1

class GoogleMaps < Formula
  desc "Command-line interface for Google Maps Platform"
  homepage "https://github.com/nitaiaharoni1/google-maps-cli"
  url "https://github.com/nitaiaharoni1/google-maps-cli/archive/refs/tags/v1.0.0.tar.gz"
  version "1.0.0"
  sha256 "45701e0cdcd5aadf7e221a40a0b2295e4e06338022ac1cd787324b86ccac4a2e"
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
      1. Get your Google Maps API key from Google Cloud Console:
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

      2. Run setup:
         maps init

      3. Then use: maps help
    EOS
  end
end

