"""Google Maps CLI - Main command-line interface."""

import click
import sys
import json
import webbrowser
from urllib.parse import quote
from .auth import authenticate, authenticate_oauth, get_api_key, check_auth
from .api import MapsAPI
from .utils import (
    list_accounts, get_default_account, set_default_account,
    format_coordinates, parse_coordinates, format_distance, format_duration
)


@click.group(context_settings={"allow_interspersed_args": False})
@click.version_option(version="1.0.0")
@click.option("--account", "-a", help="Account name to use (default: current default account)")
@click.pass_context
def cli(ctx, account):
    """Google Maps CLI - Command-line interface for Google Maps Platform."""
    ctx.ensure_object(dict)
    ctx.obj["ACCOUNT"] = account


@cli.command(name="help")
@click.argument("command", required=False)
@click.pass_context
def help_command(ctx, command):
    """Show help message. Use 'help <command>' for command-specific help."""
    if command:
        try:
            cmd = ctx.parent.command.get_command(ctx.parent, command)
            if cmd:
                click.echo(cmd.get_help(ctx))
            else:
                click.echo(f"❌ Unknown command: {command}", err=True)
                click.echo(f"\nAvailable commands:")
                for name in sorted(ctx.parent.command.list_commands(ctx.parent)):
                    click.echo(f"  {name}")
        except Exception:
            click.echo(f"❌ Unknown command: {command}", err=True)
            click.echo(f"\nAvailable commands:")
            for name in sorted(ctx.parent.command.list_commands(ctx.parent)):
                click.echo(f"  {name}")
    else:
        if ctx.parent:
            click.echo(ctx.parent.get_help())
        else:
            click.echo(ctx.get_help())


_account_option = click.option("--account", "-a", help="Account name to use (default: current default account)")


@cli.command()
@click.option("--account", "-a", help="Account name (optional, defaults to 'default')")
def init(account):
    """Initialize and authenticate with Google Maps API."""
    click.echo("🔐 Google Maps CLI Setup\n")
    
    # Check what's available
    from .utils import get_credentials_path
    from .auth import OAUTH_AVAILABLE
    
    has_oauth_credentials = get_credentials_path() is not None
    has_oauth_libs = OAUTH_AVAILABLE
    
    # Determine authentication method
    if has_oauth_credentials and has_oauth_libs:
        click.echo("Multiple authentication methods available:")
        click.echo("  1. API Key (simple, for public data)")
        click.echo("  2. OAuth 2.0 (for user-specific data like saved places)")
        click.echo()
        
        choice = click.prompt(
            "Choose authentication method",
            type=click.Choice(['1', '2']),
            default='1'
        )
        
        use_oauth = (choice == '2')
    elif has_oauth_credentials:
        click.echo("⚠️  OAuth credentials found but libraries not installed.")
        click.echo("Install with: pip install google-auth google-auth-oauthlib google-api-python-client")
        click.echo()
        click.echo("Using API Key authentication instead...")
        use_oauth = False
    else:
        click.echo("Using API Key authentication...")
        click.echo("(For user-specific features like saved places, you'll need OAuth credentials)")
        use_oauth = False
    
    click.echo()
    
    if use_oauth:
        click.echo("Setting up OAuth 2.0 authentication...")
        creds = authenticate_oauth(account)
        if creds:
            click.echo(f"✅ OAuth authentication successful!")
            if account:
                click.echo(f"   Account name: {account}")
            click.echo("\n💡 You can now use: maps lists")
        else:
            sys.exit(1)
    else:
        click.echo("Setting up API Key authentication...")
        api_key = authenticate(account)
        
        if api_key:
            try:
                api = MapsAPI(account)
                # Test the API key with a simple geocode request
                test_result = api.geocode("New York")
                if test_result:
                    click.echo(f"✅ Authentication successful!")
                    click.echo(f"   API key verified")
                    if account:
                        click.echo(f"   Account name: {account}")
                    click.echo("\n💡 Try: maps search 'restaurants near me'")
            except Exception as e:
                click.echo(f"⚠️  API key saved but verification failed: {e}")
                click.echo("   Make sure the API key has the required APIs enabled.")
        else:
            sys.exit(1)


@cli.command()
def accounts():
    """List all configured accounts."""
    accounts_list = list_accounts()
    default = get_default_account()
    
    if not accounts_list:
        click.echo("No accounts configured. Run 'maps init' to add an account.")
        return
    
    click.echo(f"Configured accounts ({len(accounts_list)}):\n")
    for acc in accounts_list:
        marker = " (default)" if acc == default else ""
        click.echo(f"  • {acc}{marker}")
    
    if default:
        click.echo(f"\nDefault account: {default}")


@cli.command()
@click.argument("account_name")
def use(account_name):
    """Set default account to use."""
    accounts_list = list_accounts()
    
    if account_name not in accounts_list:
        click.echo(f"❌ Error: Account '{account_name}' not found.")
        click.echo(f"Available accounts: {', '.join(accounts_list)}")
        click.echo("\nRun 'maps init --account <name>' to add a new account.")
        sys.exit(1)
    
    set_default_account(account_name)
    click.echo(f"✅ Default account set to: {account_name}")


@cli.command()
@_account_option
@click.pass_context
def me(ctx, account):
    """Show authenticated account information."""
    account = account or ctx.obj.get("ACCOUNT")
    try:
        from .auth import get_oauth_credentials, get_api_key
        
        # Check for OAuth first
        oauth_creds = get_oauth_credentials(account)
        if oauth_creds:
            click.echo(f"🔐 OAuth 2.0 configured")
            click.echo(f"   Account: {account or 'default'}")
            click.echo(f"   Token: {oauth_creds.token[:20]}...")
            if oauth_creds.expired:
                click.echo(f"   Status: Expired (will auto-refresh)")
            else:
                click.echo(f"   Status: Valid")
        
        # Check for API key
        api_key = get_api_key(account)
        if api_key:
            if oauth_creds:
                click.echo(f"\n🔑 API Key also configured")
            else:
                click.echo(f"🔑 API Key configured")
            click.echo(f"   Account: {account or 'default'}")
            click.echo(f"   Key: {api_key[:20]}...")
        
        if not oauth_creds and not api_key:
            click.echo("⚠️  No authentication configured.")
            click.echo("   Run 'maps init' for API key or 'maps init --oauth' for OAuth.")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


# Places Commands

@cli.command()
@click.argument("query")
@click.option("--max", "-m", default=10, help="Maximum number of results")
@click.option("--location", "-l", help="Location bias (lat,lng)")
@click.option("--radius", "-r", type=int, help="Radius in meters")
@click.option("--type", "-t", help="Place type filter")
@click.option("--language", help="Language code")
@click.option("--region", help="Region code (ccTLD)")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON")
@click.option("--output", type=click.Choice(["keys", "full"]), default="full", help="Output format")
@_account_option
@click.pass_context
def search(ctx, query, max, location, radius, type, language, region, json_output, output, account):
    """Search for places using text query."""
    account = account or ctx.obj.get("ACCOUNT")
    try:
        api = MapsAPI(account)
        results = api.search_places(
            query, location=location, radius=radius, type=type,
            language=language, region=region, max_results=max
        )
        
        if json_output:
            click.echo(json.dumps(results, indent=2))
            return
        
        if not results:
            click.echo("No places found.")
            return
        
        click.echo(f"Found {len(results)} places:\n")
        
        for i, place in enumerate(results, 1):
            if output == "keys":
                click.echo(place.get("place_id", ""))
            else:
                name = place.get("name", "Unknown")
                place_id = place.get("place_id", "")
                rating = place.get("rating")
                address = place.get("formatted_address", place.get("vicinity", ""))
                geometry = place.get("geometry", {}).get("location", {})
                lat = geometry.get("lat")
                lng = geometry.get("lng")
                
                click.echo(f"{i}. {name}")
                click.echo(f"   Place ID: {place_id}")
                if rating:
                    click.echo(f"   Rating: {rating:.1f}/5.0")
                if address:
                    click.echo(f"   Address: {address}")
                if lat and lng:
                    click.echo(f"   Location: {format_coordinates(lat, lng)}")
                click.echo()
    
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--location", "-l", required=True, help="Location (lat,lng)")
@click.option("--radius", "-r", default=1000, type=int, help="Radius in meters")
@click.option("--type", "-t", help="Place type filter")
@click.option("--keyword", "-k", help="Keyword filter")
@click.option("--max", "-m", default=10, help="Maximum number of results")
@click.option("--open-now", is_flag=True, help="Only show places open now")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON")
@_account_option
@click.pass_context
def nearby(ctx, location, radius, type, keyword, max, open_now, json_output, account):
    """Find places near a location."""
    account = account or ctx.obj.get("ACCOUNT")
    try:
        api = MapsAPI(account)
        results = api.nearby_search(
            location, radius=radius, type=type, keyword=keyword,
            open_now=open_now, max_results=max
        )
        
        if json_output:
            click.echo(json.dumps(results, indent=2))
            return
        
        if not results:
            click.echo("No places found nearby.")
            return
        
        click.echo(f"Found {len(results)} places nearby:\n")
        
        for i, place in enumerate(results, 1):
            name = place.get("name", "Unknown")
            place_id = place.get("place_id", "")
            rating = place.get("rating")
            address = place.get("vicinity", "")
            geometry = place.get("geometry", {}).get("location", {})
            lat = geometry.get("lat")
            lng = geometry.get("lng")
            
            click.echo(f"{i}. {name}")
            click.echo(f"   Place ID: {place_id}")
            if rating:
                click.echo(f"   Rating: {rating:.1f}/5.0")
            if address:
                click.echo(f"   Address: {address}")
            if lat and lng:
                click.echo(f"   Location: {format_coordinates(lat, lng)}")
            click.echo()
    
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("place_id")
@click.option("--fields", help="Comma-separated list of fields to return")
@click.option("--language", help="Language code")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON")
@_account_option
@click.pass_context
def place(ctx, place_id, fields, language, json_output, account):
    """Get detailed information about a place."""
    account = account or ctx.obj.get("ACCOUNT")
    try:
        api = MapsAPI(account)
        details = api.get_place_details(place_id, fields=fields, language=language)
        
        if json_output:
            click.echo(json.dumps(details, indent=2))
            return
        
        if not details:
            click.echo("Place not found.")
            return
        
        name = details.get("name", "Unknown")
        address = details.get("formatted_address", "")
        phone = details.get("formatted_phone_number", "")
        website = details.get("website", "")
        rating = details.get("rating")
        total_ratings = details.get("user_ratings_total")
        geometry = details.get("geometry", {}).get("location", {})
        lat = geometry.get("lat")
        lng = geometry.get("lng")
        opening_hours = details.get("opening_hours", {})
        open_now = opening_hours.get("open_now")
        types = details.get("types", [])
        reviews = details.get("reviews", [])
        
        click.echo(f"📍 {name}")
        click.echo(f"   Place ID: {place_id}")
        if address:
            click.echo(f"   Address: {address}")
        if phone:
            click.echo(f"   Phone: {phone}")
        if website:
            click.echo(f"   Website: {website}")
        if rating:
            click.echo(f"   Rating: {rating:.1f}/5.0")
            if total_ratings:
                click.echo(f"   Total Reviews: {total_ratings}")
        if lat and lng:
            click.echo(f"   Location: {format_coordinates(lat, lng)}")
        if open_now is not None:
            status = "Open" if open_now else "Closed"
            click.echo(f"   Status: {status}")
        if types:
            click.echo(f"   Types: {', '.join(types[:5])}")
        if reviews:
            click.echo(f"\n   Reviews ({len(reviews)}):")
            for review in reviews[:3]:
                author = review.get("author_name", "Anonymous")
                rating = review.get("rating")
                text = review.get("text", "")[:200]
                click.echo(f"   • {author} ({rating}/5): {text}...")
    
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("input_text")
@click.option("--location", "-l", help="Location bias (lat,lng)")
@click.option("--radius", "-r", type=int, help="Radius in meters")
@click.option("--language", help="Language code")
@click.option("--region", help="Region code")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON")
@_account_option
@click.pass_context
def autocomplete(ctx, input_text, location, radius, language, region, json_output, account):
    """Get place autocomplete suggestions."""
    account = account or ctx.obj.get("ACCOUNT")
    try:
        api = MapsAPI(account)
        predictions = api.place_autocomplete(
            input_text, location=location, radius=radius,
            language=language, region=region
        )
        
        if json_output:
            click.echo(json.dumps(predictions, indent=2))
            return
        
        if not predictions:
            click.echo("No suggestions found.")
            return
        
        click.echo(f"Found {len(predictions)} suggestions:\n")
        
        for i, pred in enumerate(predictions, 1):
            description = pred.get("description", "")
            place_id = pred.get("place_id", "")
            click.echo(f"{i}. {description}")
            if place_id:
                click.echo(f"   Place ID: {place_id}")
            click.echo()
    
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


# Geocoding Commands

@cli.command()
@click.argument("address")
@click.option("--language", help="Language code")
@click.option("--region", help="Region code")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON")
@_account_option
@click.pass_context
def geocode(ctx, address, language, region, json_output, account):
    """Convert address to coordinates."""
    account = account or ctx.obj.get("ACCOUNT")
    try:
        api = MapsAPI(account)
        results = api.geocode(address, language=language, region=region)
        
        if json_output:
            click.echo(json.dumps(results, indent=2))
            return
        
        if not results:
            click.echo("Address not found.")
            return
        
        for i, result in enumerate(results, 1):
            formatted_address = result.get("formatted_address", "")
            geometry = result.get("geometry", {}).get("location", {})
            lat = geometry.get("lat")
            lng = geometry.get("lng")
            place_id = result.get("place_id", "")
            
            click.echo(f"{i}. {formatted_address}")
            if lat and lng:
                click.echo(f"   Coordinates: {format_coordinates(lat, lng)}")
            if place_id:
                click.echo(f"   Place ID: {place_id}")
            click.echo()
    
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("coordinates")
@click.option("--language", help="Language code")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON")
@_account_option
@click.pass_context
def reverse(ctx, coordinates, language, json_output, account):
    """Convert coordinates to address."""
    account = account or ctx.obj.get("ACCOUNT")
    try:
        lat, lng = parse_coordinates(coordinates)
        api = MapsAPI(account)
        results = api.reverse_geocode(lat, lng, language=language)
        
        if json_output:
            click.echo(json.dumps(results, indent=2))
            return
        
        if not results:
            click.echo("No address found for coordinates.")
            return
        
        for i, result in enumerate(results, 1):
            formatted_address = result.get("formatted_address", "")
            place_id = result.get("place_id", "")
            
            click.echo(f"{i}. {formatted_address}")
            if place_id:
                click.echo(f"   Place ID: {place_id}")
            click.echo()
    
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


# Directions Commands

@cli.command()
@click.argument("origin")
@click.argument("destination")
@click.option("--mode", type=click.Choice(["driving", "walking", "bicycling", "transit"]), default="driving", help="Travel mode")
@click.option("--waypoints", help="Waypoints (pipe-separated or comma-separated)")
@click.option("--alternatives", is_flag=True, help="Return alternative routes")
@click.option("--avoid", type=click.Choice(["tolls", "highways", "ferries", "indoor"]), help="Avoid specific route features")
@click.option("--language", help="Language code")
@click.option("--units", type=click.Choice(["metric", "imperial"]), default="metric", help="Units")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON")
@_account_option
@click.pass_context
def directions(ctx, origin, destination, mode, waypoints, alternatives, avoid, language, units, json_output, account):
    """Get directions between two points."""
    account = account or ctx.obj.get("ACCOUNT")
    try:
        api = MapsAPI(account)
        routes = api.get_directions(
            origin, destination, mode=mode, waypoints=waypoints,
            alternatives=alternatives, avoid=avoid, language=language, units=units
        )
        
        if json_output:
            click.echo(json.dumps(routes, indent=2))
            return
        
        if not routes:
            click.echo("No routes found.")
            return
        
        for route_idx, route in enumerate(routes, 1):
            if len(routes) > 1:
                click.echo(f"\n--- Route {route_idx} ---\n")
            
            summary = route.get("summary", "")
            legs = route.get("legs", [])
            
            total_distance = 0
            total_duration = 0
            
            for leg in legs:
                distance = leg.get("distance", {}).get("value", 0)
                duration = leg.get("duration", {}).get("value", 0)
                total_distance += distance
                total_duration += duration
            
            click.echo(f"Route: {summary}")
            click.echo(f"Total Distance: {format_distance(total_distance)}")
            click.echo(f"Total Duration: {format_duration(total_duration)}")
            click.echo()
            
            for leg_idx, leg in enumerate(legs, 1):
                start_address = leg.get("start_address", "")
                end_address = leg.get("end_address", "")
                distance = leg.get("distance", {}).get("value", 0)
                duration = leg.get("duration", {}).get("value", 0)
                steps = leg.get("steps", [])
                
                if len(legs) > 1:
                    click.echo(f"Leg {leg_idx}:")
                click.echo(f"  From: {start_address}")
                click.echo(f"  To: {end_address}")
                click.echo(f"  Distance: {format_distance(distance)}")
                click.echo(f"  Duration: {format_duration(duration)}")
                click.echo()
                
                if steps:
                    click.echo("  Steps:")
                    for step in steps[:10]:  # Show first 10 steps
                        instruction = step.get("html_instructions", "").replace("<b>", "").replace("</b>", "")
                        step_distance = step.get("distance", {}).get("value", 0)
                        step_duration = step.get("duration", {}).get("value", 0)
                        click.echo(f"    • {instruction}")
                        click.echo(f"      {format_distance(step_distance)} / {format_duration(step_duration)}")
                    if len(steps) > 10:
                        click.echo(f"    ... and {len(steps) - 10} more steps")
                    click.echo()
    
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("origin")
@click.argument("destination")
@click.option("--mode", type=click.Choice(["driving", "walking", "bicycling", "transit"]), default="driving", help="Travel mode")
@_account_option
@click.pass_context
def route(ctx, origin, destination, mode, account):
    """Get simplified route summary."""
    account = account or ctx.obj.get("ACCOUNT")
    try:
        api = MapsAPI(account)
        routes = api.get_directions(origin, destination, mode=mode)
        
        if not routes:
            click.echo("No route found.")
            return
        
        route = routes[0]
        legs = route.get("legs", [])
        
        total_distance = 0
        total_duration = 0
        
        for leg in legs:
            total_distance += leg.get("distance", {}).get("value", 0)
            total_duration += leg.get("duration", {}).get("value", 0)
        
        click.echo(f"Distance: {format_distance(total_distance)}")
        click.echo(f"Duration: {format_duration(total_duration)}")
        click.echo(f"Mode: {mode}")
    
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


# Distance Matrix Commands

@cli.command()
@click.argument("origins")
@click.argument("destinations")
@click.option("--mode", type=click.Choice(["driving", "walking", "bicycling", "transit"]), default="driving", help="Travel mode")
@click.option("--units", type=click.Choice(["metric", "imperial"]), default="metric", help="Units")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON")
@_account_option
@click.pass_context
def distance(ctx, origins, destinations, mode, units, json_output, account):
    """Calculate distances between multiple points."""
    account = account or ctx.obj.get("ACCOUNT")
    try:
        api = MapsAPI(account)
        result = api.get_distance_matrix(origins, destinations, mode=mode, units=units)
        
        if json_output:
            click.echo(json.dumps(result, indent=2))
            return
        
        rows = result.get("rows", [])
        origin_addresses = result.get("origin_addresses", [])
        destination_addresses = result.get("destination_addresses", [])
        
        if not rows:
            click.echo("No results found.")
            return
        
        click.echo("Distance Matrix:\n")
        
        for i, row in enumerate(rows):
            origin = origin_addresses[i] if i < len(origin_addresses) else f"Origin {i+1}"
            click.echo(f"From: {origin}")
            
            elements = row.get("elements", [])
            for j, element in enumerate(elements):
                destination = destination_addresses[j] if j < len(destination_addresses) else f"Destination {j+1}"
                status = element.get("status", "")
                
                if status == "OK":
                    distance = element.get("distance", {}).get("value", 0)
                    duration = element.get("duration", {}).get("value", 0)
                    click.echo(f"  To: {destination}")
                    click.echo(f"    Distance: {format_distance(distance)}")
                    click.echo(f"    Duration: {format_duration(duration)}")
                else:
                    click.echo(f"  To: {destination}")
                    click.echo(f"    Status: {status}")
            click.echo()
    
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


# Utility Commands

@cli.command()
@click.argument("coordinates")
@click.option("--timestamp", type=int, help="Unix timestamp (defaults to current time)")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON")
@_account_option
@click.pass_context
def timezone(ctx, coordinates, timestamp, json_output, account):
    """Get timezone information for coordinates."""
    account = account or ctx.obj.get("ACCOUNT")
    try:
        lat, lng = parse_coordinates(coordinates)
        api = MapsAPI(account)
        result = api.get_timezone(lat, lng, timestamp=timestamp)
        
        if json_output:
            click.echo(json.dumps(result, indent=2))
            return
        
        if result.get("status") != "OK":
            click.echo(f"Error: {result.get('errorMessage', 'Unknown error')}")
            return
        
        timezone_id = result.get("timeZoneId", "")
        timezone_name = result.get("timeZoneName", "")
        raw_offset = result.get("rawOffset", 0)
        dst_offset = result.get("dstOffset", 0)
        
        click.echo(f"Timezone: {timezone_id}")
        click.echo(f"Name: {timezone_name}")
        click.echo(f"UTC Offset: {raw_offset / 3600:.1f} hours")
        if dst_offset != raw_offset:
            click.echo(f"DST Offset: {dst_offset / 3600:.1f} hours")
    
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("locations")
@click.option("--samples", type=int, help="Number of samples for path")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON")
@_account_option
@click.pass_context
def elevation(ctx, locations, samples, json_output, account):
    """Get elevation data for locations."""
    account = account or ctx.obj.get("ACCOUNT")
    try:
        # Parse locations (can be pipe-separated or comma-separated)
        if "|" in locations:
            location_list = locations.split("|")
        else:
            location_list = [locations]
        
        api = MapsAPI(account)
        results = api.get_elevation(location_list, samples=samples)
        
        if json_output:
            click.echo(json.dumps(results, indent=2))
            return
        
        if not results:
            click.echo("No elevation data found.")
            return
        
        click.echo(f"Elevation Data ({len(results)} points):\n")
        
        for i, result in enumerate(results, 1):
            location = result.get("location", {})
            lat = location.get("lat")
            lng = location.get("lng")
            elevation = result.get("elevation", 0)
            resolution = result.get("resolution", 0)
            
            click.echo(f"{i}. Location: {format_coordinates(lat, lng)}")
            click.echo(f"   Elevation: {elevation:.2f}m")
            if resolution:
                click.echo(f"   Resolution: {resolution:.2f}m")
            click.echo()
    
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("location")
@_account_option
@click.pass_context
def open(ctx, location, account):
    """Open location in Google Maps (browser)."""
    account = account or ctx.obj.get("ACCOUNT")
    try:
        # Try to parse as coordinates first
        try:
            lat, lng = parse_coordinates(location)
            url = f"https://www.google.com/maps?q={lat},{lng}"
        except ValueError:
            # Treat as address or place ID
            url = f"https://www.google.com/maps/search/?api=1&query={quote(location)}"
        
        click.echo(f"Opening: {url}")
        webbrowser.open(url)
    
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--json-output", is_flag=True, help="Output as JSON")
@_account_option
@click.pass_context
def lists(ctx, json_output, account):
    """List all your saved Google Maps lists/places (requires OAuth)."""
    account = account or ctx.obj.get("ACCOUNT")
    try:
        api = MapsAPI(account, use_oauth=True)
        saved_data = api.get_saved_places()
        
        if json_output:
            click.echo(json.dumps(saved_data, indent=2))
            return
        
        # Try to parse and display the data
        if isinstance(saved_data, dict):
            if "items" in saved_data:
                items = saved_data["items"]
            elif "lists" in saved_data:
                items = saved_data["lists"]
            elif "savedPlaces" in saved_data:
                items = saved_data["savedPlaces"]
            elif "places" in saved_data:
                items = saved_data["places"]
            else:
                # Display raw data structure
                click.echo("📋 Saved Places Data:")
                click.echo(json.dumps(saved_data, indent=2))
                return
        elif isinstance(saved_data, list):
            items = saved_data
        else:
            click.echo("📋 Saved Places Data:")
            click.echo(json.dumps(saved_data, indent=2))
            return
        
        if not items:
            click.echo("No saved places found.")
            return
        
        click.echo(f"Found {len(items)} saved items:\n")
        for i, item in enumerate(items, 1):
            if isinstance(item, dict):
                name = item.get("name") or item.get("title") or item.get("displayName") or "Unnamed"
                place_id = item.get("place_id") or item.get("placeId") or ""
                address = item.get("formatted_address") or item.get("address") or ""
                
                click.echo(f"{i}. {name}")
                if place_id:
                    click.echo(f"   Place ID: {place_id}")
                if address:
                    click.echo(f"   Address: {address}")
                click.echo()
            else:
                click.echo(f"{i}. {item}")
                click.echo()
    
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        click.echo("\nNote: This feature requires OAuth authentication.")
        click.echo("Run 'maps init --oauth' to set up OAuth.")
        sys.exit(1)


if __name__ == "__main__":
    cli()

