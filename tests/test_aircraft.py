import pytest
from src.aircraft import Aircraft


class TestAircraft:

    def test_aircraft_creation_valid(self):
        aircraft = Aircraft(
            origin_country="Russia",
            callsign="SU100",
            velocity=250.5,
            altitude=10000.0
        )

        assert aircraft.origin_country == "Russia"
        assert aircraft.callsign == "SU100"
        assert aircraft.velocity == 250.5
        assert aircraft.altitude == 10000.0

    def test_aircraft_equality(self):
        aircraft1 = Aircraft("Russia", "SU100", 250.5, 10000.0)
        aircraft2 = Aircraft("USA", "AA200", 250.5, 10000.0)
        aircraft3 = Aircraft("Russia", "SU100", 300.0, 10000.0)

        assert aircraft1 == aircraft2
        assert aircraft1 != aircraft3

    def test_aircraft_comparison(self):
        aircraft1 = Aircraft("Russia", "SU100", 250.0, 10000.0)  # Меньшая скорость
        aircraft2 = Aircraft("USA", "AA200", 300.0, 10000.0)  # Большая скорость
        aircraft3 = Aircraft("Germany", "LH300", 300.0, 12000.0)  # Такая же скорость, но большая высота

        assert aircraft1 < aircraft2
        assert aircraft2 > aircraft1
        assert aircraft1 <= aircraft2
        assert aircraft2 >= aircraft1
        assert aircraft2 < aircraft3
        assert aircraft3 > aircraft2
        assert not aircraft1 > aircraft2
        assert not aircraft2 < aircraft1

    def test_aircraft_from_dict(self):
        data = {
            'origin_country': 'France',
            'callsign': 'AF500',
            'velocity': 280.0,
            'altitude': 11000.0
        }

        aircraft = Aircraft.from_dict(data)

        assert aircraft.origin_country == 'France'
        assert aircraft.callsign == 'AF500'
        assert aircraft.velocity == 280.0
        assert aircraft.altitude == 11000.0

    def test_aircraft_to_dict(self):
        aircraft = Aircraft("UK", "BA100", 260.0, 9500.0)
        data = aircraft.to_dict()
        expected = {
            'origin_country': 'UK',
            'callsign': 'BA100',
            'velocity': 260.0,
            'altitude': 9500.0
        }

        assert data == expected

    def test_aircraft_repr(self):
        aircraft = Aircraft("Russia", "SU100", 250.5, 10000.0)
        repr_str = repr(aircraft)

        assert "Russia" in repr_str
        assert "SU100" in repr_str
        assert "250.50" in repr_str
        assert "10000.00" in repr_str