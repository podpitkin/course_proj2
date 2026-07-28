from abc import ABC, abstractmethod
import requests


class APIClient(ABC):
    """Абстрактный класс для работы с API"""

    @abstractmethod
    def connect(self):
        """Подключение к API"""
        pass

    @abstractmethod
    def get_country_coordinates(self, country_name):
        """Получение координат страны (юг, север, запад, восток)"""
        pass

    @abstractmethod
    def get_aircraft_in_area(self, bounds):
        """Получение информации о самолетах в заданной области"""
        pass


class OpenSkyNominatimClient(APIClient):
    """Класс для работы с API"""

    def __init__(self, user_agent: str = "AircraftTracker/1.0"):
        self.user_agent = user_agent
        self.nominatim_url = "https://nominatim.openstreetmap.org/search"
        self.opensky_url = "https://opensky-network.org/api/states/all"
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

    def connect(self) -> bool:
        """Проверка подключения к API"""
        try:
            # Проверяем подключение к Nominatim
            test_params = {
                "q": "France",
                "format": "json",
                "limit": 1
            }
            response = self.session.get(self.nominatim_url, params=test_params, timeout=10)
            response.raise_for_status()

            # Проверяем подключение к OpenSky
            response = self.session.get(self.opensky_url, timeout=10)
            response.raise_for_status()

            return True
        except requests.RequestException:
            return False

    def get_country_coordinates(self, country_name):
        """Получение координат страны"""
        params = {
            "q": country_name,
            "format": "json",
            "limit": 1,
            "addressdetails": 1
        }

        try:
            response = self.session.get(self.nominatim_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data:
                return None

            first_result = data[0]
            boundingbox = first_result.get("boundingbox")

            if boundingbox and len(boundingbox) == 4:
                # Конвертируем строки в float
                south, north, west, east = map(float, boundingbox)
                return (south, north, west, east)

            return None

        except (requests.RequestException, ValueError, KeyError, IndexError) as e:
            print(f"Ошибка при получении координат страны {country_name}: {e}")
            return None

    def get_aircraft_in_area(self, bounds):
        """Получение информации о самолетах в заданной"""
        south, north, west, east = bounds

        params = {
            "lamin": south,
            "lamax": north,
            "lomin": west,
            "lomax": east
        }

        try:
            response = self.session.get(self.opensky_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            aircraft_list = []
            if data.get("states"):
                for state in data["states"]:
                    aircraft_info = {
                        "icao24": state[0] if len(state) > 0 else None,  # Уникальный идентификатор
                        "callsign": state[1] if len(state) > 1 else None,  # Позывной
                        "origin_country": state[2] if len(state) > 2 else None,  # Страна регистрации
                        "velocity": state[9] if len(state) > 9 else None,  # Скорость (м/с)
                        "altitude": state[13] if len(state) > 13 else None,  # Высота (м)
                    }
                    aircraft_list.append(aircraft_info)

            return aircraft_list

        except requests.RequestException as e:
            print(f"Ошибка при получении данных о самолетах: {e}")
            return []