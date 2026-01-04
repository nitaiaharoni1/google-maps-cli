# Google Maps CLI

A command-line interface for Google Maps Platform, built with Python and Click.

## Features

- **Places API**: Search places, find nearby locations, get place details, autocomplete
- **Geocoding API**: Convert addresses to coordinates and vice versa
- **Directions API**: Get turn-by-turn directions and route information
- **Distance Matrix API**: Calculate distances and travel times between multiple points
- **Time Zone API**: Get timezone information for coordinates
- **Elevation API**: Get elevation data for locations

## Installation

### Using pip

```bash
pip install -e .
```

Or use the installer script:

```bash
./install.sh
```

### Using Homebrew

```bash
brew install nitaiaharoni1/tools/google-maps
```

## Setup

1. Get your Google Maps API key from [Google Cloud Console](https://console.cloud.google.com/):
   - Create or select a project
   - Enable the Maps APIs you need:
     - Places API
     - Geocoding API
     - Directions API
     - Distance Matrix API
     - Time Zone API
     - Elevation API
   - Go to 'Credentials' → 'Create Credentials' → 'API Key'

2. Initialize the CLI:

```bash
maps init
```

Enter your API key when prompted.

## Usage

### Places

```bash
# Search for places
maps search "restaurants in NYC" --max 5

# Find nearby places
maps nearby --location 40.7128,-74.0060 --radius 500 --type restaurant

# Get place details
maps place ChIJN1t_tDeuEmsRUsoyG83frY4

# Get autocomplete suggestions
maps autocomplete "coffee shop"
```

### Geocoding

```bash
# Convert address to coordinates
maps geocode "1600 Amphitheatre Parkway, Mountain View, CA"

# Convert coordinates to address
maps reverse 37.4224764,-122.0842499
```

### Directions

```bash
# Get directions
maps directions "Times Square, NYC" "Central Park, NYC" --mode walking

# Get route summary
maps route "NYC" "Boston" --mode driving
```

### Distance Matrix

```bash
# Calculate distances
maps distance "NYC" "Boston|Philadelphia|Washington DC"
```

### Utilities

```bash
# Get timezone
maps timezone 40.7128,-74.0060

# Get elevation
maps elevation 37.4224764,-122.0842499

# Open location in browser
maps open "Times Square, NYC"
```

## Account Management

```bash
# List accounts
maps accounts

# Switch account
maps use account_name

# Show current account
maps me
```

## Output Formats

```bash
# JSON output (for scripting)
maps search "restaurants" --json

# Place IDs only (for piping)
maps search "restaurants" --output keys
```

## Requirements

- Python 3.8+
- Google Maps Platform API key

## License

MIT License

