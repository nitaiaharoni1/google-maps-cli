"""Basic tests for Google Maps CLI API."""

import unittest
from unittest.mock import patch, MagicMock
from google_maps_cli.api import MapsAPI


class TestMapsAPI(unittest.TestCase):
    """Test cases for MapsAPI class."""
    
    @patch('google_maps_cli.api.check_auth')
    def test_init_with_api_key(self, mock_check_auth):
        """Test MapsAPI initialization with API key."""
        mock_check_auth.return_value = "test_api_key"
        api = MapsAPI()
        self.assertEqual(api.api_key, "test_api_key")
    
    @patch('google_maps_cli.api.check_auth')
    def test_init_without_api_key(self, mock_check_auth):
        """Test MapsAPI initialization without API key."""
        mock_check_auth.return_value = None
        with self.assertRaises(Exception):
            MapsAPI()
    
    @patch('google_maps_cli.api.check_auth')
    @patch('google_maps_cli.api.requests.get')
    def test_make_request_success(self, mock_get, mock_check_auth):
        """Test successful API request."""
        mock_check_auth.return_value = "test_api_key"
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "OK", "results": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        api = MapsAPI()
        result = api._make_request("/test", {})
        
        self.assertEqual(result["status"], "OK")
        mock_get.assert_called_once()
    
    @patch('google_maps_cli.api.check_auth')
    @patch('google_maps_cli.api.requests.get')
    def test_make_request_error(self, mock_get, mock_check_auth):
        """Test API request with error status."""
        mock_check_auth.return_value = "test_api_key"
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "REQUEST_DENIED",
            "error_message": "Invalid API key"
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        api = MapsAPI()
        with self.assertRaises(Exception) as context:
            api._make_request("/test", {})
        
        self.assertIn("REQUEST_DENIED", str(context.exception))


if __name__ == "__main__":
    unittest.main()

