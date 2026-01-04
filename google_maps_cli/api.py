"""Google Maps Platform API wrapper."""

import requests
from .auth import get_api_key, check_auth


class MapsAPI:
    """Wrapper for Google Maps Platform API operations."""
    
    BASE_URL = "https://maps.googleapis.com/maps/api"
    
    def __init__(self, account=None):
        """
        Initialize Maps API client.
        
        Args:
            account: Account name (optional). If None, uses default account.
        """
        self.api_key = check_auth(account)
        if not self.api_key:
            raise Exception("Not authenticated. Run 'maps init' first.")
        self.account = account
    
    def _make_request(self, endpoint, params):
        """
        Make HTTP request to Google Maps API.
        
        Args:
            endpoint: API endpoint path (e.g., '/place/textsearch/json')
            params: Query parameters dict
        
        Returns:
            JSON response data
        """
        params["key"] = self.api_key
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") not in ["OK", "ZERO_RESULTS"]:
                error_msg = data.get("error_message", "Unknown error")
                status = data.get("status", "UNKNOWN_ERROR")
                raise Exception(f"API Error ({status}): {error_msg}")
            
            return data
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")
    
    # Places API Methods
    
    def search_places(self, query, location=None, radius=None, type=None, 
                     language=None, region=None, max_results=20):
        """
        Text search for places.
        
        Args:
            query: Search query string
            location: Optional lat,lng for location biasing
            radius: Optional radius in meters
            type: Optional place type filter
            language: Optional language code
            region: Optional region code (ccTLD)
            max_results: Maximum number of results
        
        Returns:
            List of place results
        """
        params = {"query": query}
        
        if location:
            params["location"] = location
        if radius:
            params["radius"] = radius
        if type:
            params["type"] = type
        if language:
            params["language"] = language
        if region:
            params["region"] = region
        
        results = []
        data = self._make_request("/place/textsearch/json", params)
        
        if "results" in data:
            results.extend(data["results"][:max_results])
        
        # Handle pagination
        while "next_page_token" in data and len(results) < max_results:
            import time
            time.sleep(2)  # Required delay for next_page_token
            params["pagetoken"] = data["next_page_token"]
            data = self._make_request("/place/textsearch/json", params)
            if "results" in data:
                results.extend(data["results"][:max_results - len(results)])
        
        return results[:max_results]
    
    def nearby_search(self, location, radius=1000, type=None, keyword=None,
                     language=None, min_price=None, max_price=None, 
                     open_now=False, rank_by=None, max_results=20):
        """
        Search for places near a location.
        
        Args:
            location: lat,lng coordinates
            radius: Radius in meters (default: 1000)
            type: Optional place type filter
            keyword: Optional keyword filter
            language: Optional language code
            min_price: Optional minimum price level (0-4)
            max_price: Optional maximum price level (0-4)
            open_now: If True, only return places open now
            rank_by: Optional ranking (distance or prominence)
            max_results: Maximum number of results
        
        Returns:
            List of place results
        """
        params = {
            "location": location,
            "radius": radius,
        }
        
        if type:
            params["type"] = type
        if keyword:
            params["keyword"] = keyword
        if language:
            params["language"] = language
        if min_price is not None:
            params["minprice"] = min_price
        if max_price is not None:
            params["maxprice"] = max_price
        if open_now:
            params["opennow"] = "true"
        if rank_by:
            params["rankby"] = rank_by
        
        results = []
        data = self._make_request("/place/nearbysearch/json", params)
        
        if "results" in data:
            results.extend(data["results"][:max_results])
        
        # Handle pagination
        while "next_page_token" in data and len(results) < max_results:
            import time
            time.sleep(2)
            params["pagetoken"] = data["next_page_token"]
            data = self._make_request("/place/nearbysearch/json", params)
            if "results" in data:
                results.extend(data["results"][:max_results - len(results)])
        
        return results[:max_results]
    
    def get_place_details(self, place_id, fields=None, language=None, 
                         region=None, session_token=None):
        """
        Get detailed information about a place.
        
        Args:
            place_id: Place ID
            fields: Optional comma-separated list of fields to return
            language: Optional language code
            region: Optional region code
            session_token: Optional session token for billing
        
        Returns:
            Place details object
        """
        params = {"place_id": place_id}
        
        if fields:
            params["fields"] = fields
        if language:
            params["language"] = language
        if region:
            params["region"] = region
        if session_token:
            params["sessiontoken"] = session_token
        
        data = self._make_request("/place/details/json", params)
        return data.get("result")
    
    def place_autocomplete(self, input_text, location=None, radius=None,
                          language=None, region=None, types=None,
                          components=None, session_token=None):
        """
        Get place autocomplete suggestions.
        
        Args:
            input_text: Input text to autocomplete
            location: Optional lat,lng for biasing
            radius: Optional radius in meters
            language: Optional language code
            region: Optional region code
            types: Optional type filter
            components: Optional country restriction
            session_token: Optional session token
        
        Returns:
            List of predictions
        """
        params = {"input": input_text}
        
        if location:
            params["location"] = location
        if radius:
            params["radius"] = radius
        if language:
            params["language"] = language
        if region:
            params["region"] = region
        if types:
            params["types"] = types
        if components:
            params["components"] = components
        if session_token:
            params["sessiontoken"] = session_token
        
        data = self._make_request("/place/autocomplete/json", params)
        return data.get("predictions", [])
    
    def get_place_photo(self, photo_reference, max_width=None, max_height=None):
        """
        Get place photo URL.
        
        Args:
            photo_reference: Photo reference from place details
            max_width: Optional max width in pixels
            max_height: Optional max height in pixels
        
        Returns:
            Photo URL string
        """
        params = {"photo_reference": photo_reference}
        
        if max_width:
            params["maxwidth"] = max_width
        elif max_height:
            params["maxheight"] = max_height
        else:
            params["maxwidth"] = 400  # Default
        
        url = f"{self.BASE_URL}/place/photo"
        params["key"] = self.api_key
        
        # Build URL manually since we need the redirect
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{url}?{query_string}"
    
    # Geocoding API Methods
    
    def geocode(self, address, language=None, region=None, 
                components=None, bounds=None):
        """
        Geocode an address to coordinates.
        
        Args:
            address: Address string
            language: Optional language code
            region: Optional region code
            components: Optional component filters
            bounds: Optional viewport bounds
        
        Returns:
            List of geocoding results
        """
        params = {"address": address}
        
        if language:
            params["language"] = language
        if region:
            params["region"] = region
        if components:
            params["components"] = components
        if bounds:
            params["bounds"] = bounds
        
        data = self._make_request("/geocode/json", params)
        return data.get("results", [])
    
    def reverse_geocode(self, lat, lng, language=None, result_type=None,
                       location_type=None):
        """
        Reverse geocode coordinates to address.
        
        Args:
            lat: Latitude
            lng: Longitude
            language: Optional language code
            result_type: Optional result type filter
            location_type: Optional location type filter
        
        Returns:
            List of geocoding results
        """
        params = {"latlng": f"{lat},{lng}"}
        
        if language:
            params["language"] = language
        if result_type:
            params["result_type"] = result_type
        if location_type:
            params["location_type"] = location_type
        
        data = self._make_request("/geocode/json", params)
        return data.get("results", [])
    
    # Directions API Methods
    
    def get_directions(self, origin, destination, mode="driving",
                      waypoints=None, alternatives=False, avoid=None,
                      language=None, units="metric", region=None,
                      departure_time=None, arrival_time=None,
                      transit_mode=None, transit_routing_preference=None):
        """
        Get directions between two points.
        
        Args:
            origin: Origin address or coordinates
            destination: Destination address or coordinates
            mode: Travel mode (driving, walking, bicycling, transit)
            waypoints: Optional list of waypoints
            alternatives: If True, return alternative routes
            avoid: Optional avoidances (tolls, highways, ferries, indoor)
            language: Optional language code
            units: Units (metric or imperial)
            region: Optional region code
            departure_time: Optional departure time (Unix timestamp)
            arrival_time: Optional arrival time (Unix timestamp)
            transit_mode: Optional transit modes (bus, subway, train, tram, rail)
            transit_routing_preference: Optional preference (less_walking, fewer_transfers)
        
        Returns:
            Directions response with routes
        """
        params = {
            "origin": origin,
            "destination": destination,
            "mode": mode,
        }
        
        if waypoints:
            if isinstance(waypoints, list):
                waypoints = "|".join(waypoints)
            params["waypoints"] = waypoints
        if alternatives:
            params["alternatives"] = "true"
        if avoid:
            params["avoid"] = avoid
        if language:
            params["language"] = language
        if units:
            params["units"] = units
        if region:
            params["region"] = region
        if departure_time:
            params["departure_time"] = departure_time
        if arrival_time:
            params["arrival_time"] = arrival_time
        if transit_mode:
            params["transit_mode"] = transit_mode
        if transit_routing_preference:
            params["transit_routing_preference"] = transit_routing_preference
        
        data = self._make_request("/directions/json", params)
        return data.get("routes", [])
    
    # Distance Matrix API Methods
    
    def get_distance_matrix(self, origins, destinations, mode="driving",
                           language=None, avoid=None, units="metric",
                           departure_time=None, arrival_time=None,
                           transit_mode=None, transit_routing_preference=None,
                           traffic_model=None):
        """
        Calculate distances and travel times between multiple points.
        
        Args:
            origins: List of origin addresses/coordinates (or pipe-separated string)
            destinations: List of destination addresses/coordinates (or pipe-separated string)
            mode: Travel mode (driving, walking, bicycling, transit)
            language: Optional language code
            avoid: Optional avoidances
            units: Units (metric or imperial)
            departure_time: Optional departure time
            arrival_time: Optional arrival time
            transit_mode: Optional transit modes
            transit_routing_preference: Optional preference
            traffic_model: Optional traffic model (best_guess, pessimistic, optimistic)
        
        Returns:
            Distance matrix response
        """
        params = {
            "origins": origins if isinstance(origins, str) else "|".join(origins),
            "destinations": destinations if isinstance(destinations, str) else "|".join(destinations),
            "mode": mode,
        }
        
        if language:
            params["language"] = language
        if avoid:
            params["avoid"] = avoid
        if units:
            params["units"] = units
        if departure_time:
            params["departure_time"] = departure_time
        if arrival_time:
            params["arrival_time"] = arrival_time
        if transit_mode:
            params["transit_mode"] = transit_mode
        if transit_routing_preference:
            params["transit_routing_preference"] = transit_routing_preference
        if traffic_model:
            params["traffic_model"] = traffic_model
        
        data = self._make_request("/distancematrix/json", params)
        return data
    
    # Time Zone API Methods
    
    def get_timezone(self, lat, lng, timestamp=None, language=None):
        """
        Get timezone information for coordinates.
        
        Args:
            lat: Latitude
            lng: Longitude
            timestamp: Optional Unix timestamp (defaults to current time)
            language: Optional language code
        
        Returns:
            Timezone information
        """
        import time
        params = {"location": f"{lat},{lng}"}
        
        # Time Zone API requires timestamp - use current time if not provided
        if timestamp is None:
            timestamp = int(time.time())
        params["timestamp"] = timestamp
        
        if language:
            params["language"] = language
        
        data = self._make_request("/timezone/json", params)
        return data
    
    # Elevation API Methods
    
    def get_elevation(self, locations, samples=None):
        """
        Get elevation data for locations.
        
        Args:
            locations: List of lat,lng coordinates (or pipe-separated string)
            samples: Optional number of samples for path
        
        Returns:
            List of elevation results
        """
        if isinstance(locations, list):
            locations = "|".join(locations)
        
        params = {"locations": locations}
        
        if samples:
            params["samples"] = samples
        
        data = self._make_request("/elevation/json", params)
        return data.get("results", [])

