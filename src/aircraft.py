from dataclasses import dataclass

@dataclass
class Aircraft:
    """ Класс для представления информации о самолете """

    __slots__ = ('origin_country', 'callsign', 'velocity', 'altitude')
    origin_country: str  # Страна регистрации
    callsign: str        # Позывной
    velocity: float      # Скорость полета (м/с)
    altitude: float      # Высота полета (м)

    def __post_init__(self):
        """Валидация данных"""
        self._validate_data()

    def _validate_data(self):
        """ Валидация данных самолета """
        if not isinstance(self.origin_country, str) or not self.origin_country.strip():
            raise ValueError("Страна регистрации должна быть непустой строкой")

        if not isinstance(self.callsign, str) or not self.callsign.strip():
            raise ValueError("Позывной должен быть непустой строкой")

        if not isinstance(self.velocity, (int, float)):
            raise ValueError("Скорость должна быть числом")
        if self.velocity < 0:
            raise ValueError("Скорость не может быть отрицательной")

        if not isinstance(self.altitude, (int, float)):
            raise ValueError("Высота должна быть числом")
        if self.altitude < 0:
            raise ValueError("Высота не может быть отрицательной")

    def __eq__(self, other):
        """Сравнение самолетов по скорости и высоте"""
        if not isinstance(other, Aircraft):
            return NotImplemented
        return self.velocity == other.velocity and self.altitude == other.altitude

    def __lt__(self, other):
        """ Сравнение самолетов по скорости и высоте (меньше) """
        if not isinstance(other, Aircraft):
            return NotImplemented

        # Сначала сравниваем по скорости, затем по высоте
        if self.velocity != other.velocity:
            return self.velocity < other.velocity
        return self.altitude < other.altitude

    def __le__(self, other):
        """ Сравнение самолетов по скорости и высоте (меньше или равно) """
        if not isinstance(other, Aircraft):
            return NotImplemented
        return self < other or self == other

    def __gt__(self, other):
        """Сравнение самолетов по скорости и высоте (больше)"""
        if not isinstance(other, Aircraft):
            return NotImplemented
        return not self <= other

    def __ge__(self, other):
        """Сравнение самолетов по скорости и высоте """
        if not isinstance(other, Aircraft):
            return NotImplemented
        return not self < other

    def __repr__(self):

        return (f"Aircraft(origin_country='{self.origin_country}', "
                f"callsign='{self.callsign}', "
                f"velocity={self.velocity:.2f} м/с, "
                f"altitude={self.altitude:.2f} м)")

    @classmethod
    def from_dict(cls, data):
        return cls(
            origin_country=data.get('origin_country', 'Unknown'),
            callsign=data.get('callsign', 'Unknown'),
            velocity=float(data.get('velocity', 0)),
            altitude=float(data.get('altitude', 0))
        )

    def to_dict(self):
        """ Преобразование в словарь """
        return {
            'origin_country': self.origin_country,
            'callsign': self.callsign,
            'velocity': self.velocity,
            'altitude': self.altitude
        }