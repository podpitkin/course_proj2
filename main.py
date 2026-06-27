import sys
from src.api_client import OpenSkyNominatimClient
from src.aircraft import Aircraft
from src.storage import JSONStorage


class AircraftTracker:
    """Класс для управления сбором и обработкой данных о самолетах"""

    def __init__(self):
        """Инициализация трекера"""
        self.api_client = OpenSkyNominatimClient()
        self.storage = JSONStorage()

    def fetch_aircraft_for_country(self, country_name):
        """ Получение данных о самолетах для указанной страны"""
        print(f"Получение координат для страны: {country_name}")
        bounds = self.api_client.get_country_coordinates(country_name)
        if not bounds:
            print(f"Не удалось получить координаты для страны: {country_name}")
            return []

        print(f"Координаты получены: {bounds}")
        print("Получение данных о самолетах...")

        # Получаем данные о самолетах
        aircraft_data = self.api_client.get_aircraft_in_area(bounds)

        if not aircraft_data:
            print("Самолеты не найдены в указанной области")
            return []

        print(f"Найдено {len(aircraft_data)} самолетов")

        aircraft_objects = []
        for data in aircraft_data:
            try:
                if (data.get('origin_country') and data.get('callsign') and
                        data.get('velocity') is not None and data.get('altitude') is not None):
                    aircraft = Aircraft(
                        origin_country=data['origin_country'],
                        callsign=data['callsign'].strip(),
                        velocity=float(data['velocity']),
                        altitude=float(data['altitude'])
                    )
                    aircraft_objects.append(aircraft)

                    self.storage.add_aircraft(aircraft)
            except (ValueError, KeyError) as e:
                print(f"Ошибка при обработке данных самолета: {e}")
                continue

        print(f"Успешно обработано {len(aircraft_objects)} самолетов")
        return aircraft_objects

    def show_top_aircraft_by_altitude(self, n):
        """Показать топ N самолетов по высоте полета"""
        print(f"\nТоп {n} самолетов по высоте полета:")

        top_aircraft = self.storage.get_top_aircraft_by_altitude(n)

        if not top_aircraft:
            print("Нет данных о самолетах")
            return

        for i, aircraft in enumerate(top_aircraft, 1):
            print(f"{i}. {aircraft.callsign} - Высота: {aircraft.altitude:.2f} м, "
                  f"Скорость: {aircraft.velocity:.2f} м/с, "
                  f"Страна: {aircraft.origin_country}")

    def show_aircraft_by_country(self, country):
        """Показать самолеты по стране регистрации."""
        print(f"\nСамолеты из страны: {country}")

        aircraft_list = self.storage.get_aircraft_by_country(country)

        if not aircraft_list:
            print(f"Самолеты из страны {country} не найдены")
            return

        print(f"Найдено {len(aircraft_list)} самолетов:")
        for i, aircraft in enumerate(aircraft_list, 1):
            print(f"{i}. {aircraft.callsign} - Высота: {aircraft.altitude:.2f} м, "
                  f"Скорость: {aircraft.velocity:.2f} м/с")


def main_menu():
    """Главное меню программы"""
    tracker = AircraftTracker()

    print("_" * 50)
    print("ПРОГРАММА ДЛЯ СБОРА ДАННЫХ О САМОЛЕТАХ")
    print("_" * 50)


    country = input("Введите название страны: ").strip()
    if country:
        tracker.fetch_aircraft_for_country(country)
    else:
        print("Название страны не может быть пустым")


    try:
        n = int(input("Введите N (количество самолетов для отображения): ").strip())
        if n > 0:
            tracker.show_top_aircraft_by_altitude(n)
        else:
            print("N должно быть положительным числом")
    except ValueError:
        print("Ошибка: введите целое число")


    country = input("Введите название страны регистрации: ").strip()
    if country:
        tracker.show_aircraft_by_country(country)
    else:
        print("Название страны не может быть пустым")




def main():
    """Точка входа в программу"""
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\nКритическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
