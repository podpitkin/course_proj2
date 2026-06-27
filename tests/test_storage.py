from pathlib import Path
from src.storage import JSONStorage
import pytest
import json
import tempfile
import os
from src.aircraft import Aircraft


class TestJSONStorage:

    @pytest.fixture
    def temp_file(self):
        """Создание временного файла для тестов."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([], f)
            temp_path = f.name

        yield temp_path

        if os.path.exists(temp_path):
            os.unlink(temp_path)

    @pytest.fixture
    def sample_aircraft(self):
        """Создание тестового самолета."""
        return Aircraft(
            origin_country="Russia",
            callsign="SU100",
            velocity=250.5,
            altitude=10000.0
        )

    @pytest.fixture
    def sample_aircraft2(self):
        """Создание второго тестового самолета."""
        return Aircraft(
            origin_country="USA",
            callsign="AA200",
            velocity=300.0,
            altitude=12000.0
        )

    @pytest.fixture
    def sample_aircraft3(self):
        """Создание третьего тестового самолета."""
        return Aircraft(
            origin_country="Russia",
            callsign="SU200",
            velocity=280.0,
            altitude=11000.0
        )

    def test_storage_initialization(self, temp_file):
        storage = JSONStorage(temp_file)

        assert storage.file_path == Path(temp_file)
        assert storage.file_path.exists()

        with open(temp_file, 'r') as f:
            data = json.load(f)
            assert data == []

    def test_storage_initialization_new_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "new_file.json")

            # Файл не должен существовать
            assert not os.path.exists(file_path)

            storage = JSONStorage(file_path)

            # Файл должен быть создан
            assert os.path.exists(file_path)

            # Проверяем содержимое
            with open(file_path, 'r') as f:
                data = json.load(f)
                assert data == []

    def test_add_aircraft(self, temp_file, sample_aircraft):
        storage = JSONStorage(temp_file)

        result = storage.add_aircraft(sample_aircraft)

        assert result is True

        # Проверяем, что данные записаны в файл
        with open(temp_file, 'r') as f:
            data = json.load(f)

            assert len(data) == 1
            assert data[0]['origin_country'] == "Russia"
            assert data[0]['callsign'] == "SU100"
            assert data[0]['velocity'] == 250.5
            assert data[0]['altitude'] == 10000.0

    def test_add_multiple_aircraft(self, temp_file, sample_aircraft, sample_aircraft2):
        storage = JSONStorage(temp_file)

        storage.add_aircraft(sample_aircraft)
        storage.add_aircraft(sample_aircraft2)

        # Проверяем, что данные записаны в файл
        with open(temp_file, 'r') as f:
            data = json.load(f)

            assert len(data) == 2
            assert data[0]['origin_country'] == "Russia"
            assert data[1]['origin_country'] == "USA"

    def test_get_aircraft_by_country(self, temp_file, sample_aircraft, sample_aircraft2, sample_aircraft3):
        storage = JSONStorage(temp_file)

        storage.add_aircraft(sample_aircraft)  # Russia
        storage.add_aircraft(sample_aircraft2)  # USA
        storage.add_aircraft(sample_aircraft3)  # Russia

        # Получаем самолеты из России
        russian_aircraft = storage.get_aircraft_by_country("Russia")

        assert len(russian_aircraft) == 2
        assert all(a.origin_country == "Russia" for a in russian_aircraft)
        assert {a.callsign for a in russian_aircraft} == {"SU100", "SU200"}

        usa_aircraft = storage.get_aircraft_by_country("USA")

        assert len(usa_aircraft) == 1
        assert usa_aircraft[0].origin_country == "USA"
        assert usa_aircraft[0].callsign == "AA200"

        nonexistent_aircraft = storage.get_aircraft_by_country("Nonexistent")

        assert len(nonexistent_aircraft) == 0

    def test_get_aircraft_by_country_case_insensitive(self, temp_file, sample_aircraft):
        storage = JSONStorage(temp_file)

        storage.add_aircraft(sample_aircraft)

        result1 = storage.get_aircraft_by_country("RUSSIA")
        result2 = storage.get_aircraft_by_country("russia")
        result3 = storage.get_aircraft_by_country("Russia")

        assert len(result1) == 1
        assert len(result2) == 1
        assert len(result3) == 1

    def test_get_top_aircraft_by_altitude(self, temp_file, sample_aircraft, sample_aircraft2, sample_aircraft3):
        storage = JSONStorage(temp_file)

        storage.add_aircraft(sample_aircraft)  # 10000 м
        storage.add_aircraft(sample_aircraft2)  # 12000 м
        storage.add_aircraft(sample_aircraft3)  # 11000 м

        top_2 = storage.get_top_aircraft_by_altitude(2)

        assert len(top_2) == 2
        assert top_2[0].altitude == 12000.0  # Самый высокий
        assert top_2[0].callsign == "AA200"
        assert top_2[1].altitude == 11000.0  # Второй по высоте
        assert top_2[1].callsign == "SU200"

        top_1 = storage.get_top_aircraft_by_altitude(1)

        assert len(top_1) == 1
        assert top_1[0].altitude == 12000.0

        top_5 = storage.get_top_aircraft_by_altitude(5)

        assert len(top_5) == 3

    def test_get_top_aircraft_by_altitude_empty(self, temp_file):
        storage = JSONStorage(temp_file)

        top_aircraft = storage.get_top_aircraft_by_altitude(5)

        assert len(top_aircraft) == 0

    def test_delete_aircraft_by_callsign(self, temp_file, sample_aircraft, sample_aircraft2):
        storage = JSONStorage(temp_file)

        storage.add_aircraft(sample_aircraft)
        storage.add_aircraft(sample_aircraft2)

        result = storage.delete_aircraft_by_callsign("SU100")

        assert result is True

        with open(temp_file, 'r') as f:
            data = json.load(f)

            assert len(data) == 1
            assert data[0]['callsign'] == "AA200"

        result = storage.delete_aircraft_by_callsign("NONEXISTENT")

        assert result is False

        with open(temp_file, 'r') as f:
            data = json.load(f)

            assert len(data) == 1

    def test_delete_aircraft_by_callsign_case_insensitive(self, temp_file, sample_aircraft):
        storage = JSONStorage(temp_file)

        storage.add_aircraft(sample_aircraft)

        result1 = storage.delete_aircraft_by_callsign("su100")
        result2 = storage.delete_aircraft_by_callsign("SU100")

        assert result1 is True
        assert result2 is False
