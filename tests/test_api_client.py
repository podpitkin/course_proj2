from unittest.mock import Mock, patch
from src.api_client import OpenSkyNominatimClient


class TestOpenSkyNominatimClient:

    def test_client_initialization(self):
        client = OpenSkyNominatimClient(user_agent="TestAgent")

        assert client.user_agent == "TestAgent"
        assert client.nominatim_url == "https://nominatim.openstreetmap.org/search"
        assert client.opensky_url == "https://opensky-network.org/api/states/all"
        assert "User-Agent" in client.session.headers
        assert client.session.headers["User-Agent"] == "TestAgent"

    @patch('src.api_client.requests.Session')
    def test_connect_success(self, mock_session_class):
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        # Настраиваем мок для успешных ответов
        mock_response1 = Mock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = [{"boundingbox": ["1", "2", "3", "4"]}]

        mock_response2 = Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {"states": []}

        mock_session.get.side_effect = [mock_response1, mock_response2]

        client = OpenSkyNominatimClient()
        client.session = mock_session

        result = client.connect()

        assert result is True
        assert mock_session.get.call_count == 2


    @patch('src.api_client.requests.Session')
    def test_get_country_coordinates_success(self, mock_session_class):
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "boundingbox": ["48.0", "49.0", "2.0", "3.0"],
                "display_name": "France"
            }
        ]

        mock_session.get.return_value = mock_response

        client = OpenSkyNominatimClient()
        client.session = mock_session

        result = client.get_country_coordinates("France")

        assert result == (48.0, 49.0, 2.0, 3.0)
        mock_session.get.assert_called_once()

    @patch('src.api_client.requests.Session')
    def test_get_country_coordinates_no_results(self, mock_session_class):
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []

        mock_session.get.return_value = mock_response

        client = OpenSkyNominatimClient()
        client.session = mock_session

        result = client.get_country_coordinates("Nonexistent Country")

        assert result is None

    @patch('src.api_client.requests.Session')
    def test_get_country_coordinates_invalid_response(self, mock_session_class):
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"no_boundingbox": True}]

        mock_session.get.return_value = mock_response

        client = OpenSkyNominatimClient()
        client.session = mock_session

        result = client.get_country_coordinates("France")

        assert result is None


    @patch('src.api_client.requests.Session')
    def test_get_aircraft_in_area_no_states(self, mock_session_class):
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"states": None}

        mock_session.get.return_value = mock_response

        client = OpenSkyNominatimClient()
        client.session = mock_session

        bounds = (48.0, 49.0, 2.0, 3.0)
        result = client.get_aircraft_in_area(bounds)

        assert result == []
