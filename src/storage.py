import abc
import json
from pathlib import Path
from src.aircraft import Aircraft


class Storage(abc.ABC):

    @abc.abstractmethod
    def add_aircraft(self, aircraft: Aircraft):
        """Добавление информации о самолете в хранилище"""
        pass

    @abc.abstractmethod
    def get_aircraft_by_country(self, country):
        """Получение самолетов по стране регистрации"""
        pass

    @abc.abstractmethod
    def get_top_aircraft_by_altitude(self, n):
        """Получение топ N самолетов по высоте полета"""
        pass

    @abc.abstractmethod
    def delete_aircraft_by_callsign(self, callsign):
        """Удаление информации о самолете по позывному"""
        pass


class JSONStorage(Storage):
    """Класс для сохранения информации о самолетах в JSON-файл"""

    def __init__(self, file_path: str = "data/aircraft_data.json"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Создание файла, если он не существует"""
        if not self.file_path.exists():
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def _read_data(self):
        """Чтение данных из файла"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write_data(self, data):
        """Запись данных в файл."""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_aircraft(self, aircraft: Aircraft):
        """Добавление информации о самолете в JSON-файл"""
        try:
            data = self._read_data()
            aircraft_dict = aircraft.to_dict()
            data.append(aircraft_dict)
            self._write_data(data)
            return True
        except Exception as e:
            print(f"Ошибка при добавлении самолета: {e}")
            return False

    def get_aircraft_by_country(self, country):
        """Получение самолетов по стране регистрации"""
        try:
            data = self._read_data()
            aircraft_list = []

            for item in data:
                if item.get('origin_country', '').lower() == country.lower():
                    aircraft_list.append(Aircraft.from_dict(item))

            return aircraft_list
        except Exception as e:
            print(f"Ошибка при получении самолетов по стране: {e}")
            return []

    def get_top_aircraft_by_altitude(self, n):
        """Получение топ N самолетов по высоте полет."""
        try:
            data = self._read_data()
            aircraft_list = [Aircraft.from_dict(item) for item in data]

            # Сортируем по высоте (по убыванию) и берем первые N
            aircraft_list.sort(key=lambda x: x.altitude, reverse=True)
            return aircraft_list[:n]
        except Exception as e:
            print(f"Ошибка при получении топ самолетов по высоте: {e}")
            return []

    def delete_aircraft_by_callsign(self, callsign):
        """Удаление информации о самолете по позывному"""
        try:
            data = self._read_data()
            initial_length = len(data)

            # Фильтруем данные, удаляя самолеты с указанным позывным
            data = [item for item in data if item.get('callsign', '').lower() != callsign.lower()]

            if len(data) < initial_length:
                self._write_data(data)
                return True
            return False
        except Exception as e:
            print(f"Ошибка при удалении самолета: {e}")
            return False
