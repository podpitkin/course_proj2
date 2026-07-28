import sys
import os
from src.api_client import OpenSkyNominatimClient
from src.database import DBManager


def get_db_params() -> dict:
    """Получение параметров подключения к БД из переменных окружения или значений по умолчанию"""
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "database": os.getenv("DB_NAME", "aircraft_tracker"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "postgres"),
    }


def fetch_and_save_country_data(api_client, db_manager, country_name: str) -> int:
    """
    Получение данных о стране и самолётах в её воздушном пространстве,
    сохранение в БД.

    :return: Количество сохранённых самолётов
    """
    print(f"\n{'=' * 50}")
    print(f"Обработка страны: {country_name}")
    print('=' * 50)

    # Получаем координаты страны
    print(f"Получение координат для страны: {country_name}")
    bounds = api_client.get_country_coordinates(country_name)
    if not bounds:
        print(f"Не удалось получить координаты для страны: {country_name}")
        return 0

    print(f"Координаты получены: юг={bounds[0]:.4f}, север={bounds[1]:.4f}, "
          f"запад={bounds[2]:.4f}, восток={bounds[3]:.4f}")

    # Сохраняем страну в БД
    country_id = db_manager.save_country(country_name, bounds)
    print(f"Страна сохранена в БД (id={country_id})")

    # Получаем данные о самолётах
    print("Получение данных о самолётах...")
    aircraft_data = api_client.get_aircraft_in_area(bounds)

    if not aircraft_data:
        print("Самолёты не найдены в указанной области")
        return 0

    print(f"Найдено {len(aircraft_data)} самолётов")

    saved_count = 0
    for data in aircraft_data:
        try:
            if (data.get('origin_country') and data.get('callsign') and
                    data.get('velocity') is not None and data.get('altitude') is not None):
                db_manager.save_aircraft(
                    icao24=data.get('icao24', ''),
                    callsign=data['callsign'].strip(),
                    origin_country=data['origin_country'],
                    velocity=float(data['velocity']),
                    altitude=float(data['altitude']),
                    country_id=country_id
                )
                saved_count += 1
        except (ValueError, KeyError) as e:
            print(f"Ошибка при обработке данных самолёта: {e}")
            continue

    print(f"Сохранено {saved_count} самолётов в БД")
    return saved_count


def print_db_summary(db_manager):
    """Вывод сводки по данным из БД"""
    print("\n" + "=" * 50)
    print("СВОДКА ПО ДАННЫМ В БАЗЕ ДАННЫХ")
    print("=" * 50)

    # 1. Страны и количество самолётов
    print("\n1. Страны и количество самолётов в их воздушных пространствах:")
    countries_count = db_manager.get_countries_and_aeroplanes_count()
    if countries_count:
        for name, count in countries_count:
            print(f"   - {name}: {count} самолётов")
    else:
        print("   Данные отсутствуют")

    # 2. Все самолёты
    print("\n2. Все воздушные суда:")
    all_aircraft = db_manager.get_all_aeroplanes()
    if all_aircraft:
        print(f"   Всего записей: {len(all_aircraft)}")
        for ac in all_aircraft[:10]:  # Показываем первые 10
            print(f"   - {ac[2]} ({ac[3]}), скорость: {ac[4]:.2f} м/с, высота: {ac[5]:.2f} м")
        if len(all_aircraft) > 10:
            print(f"   ... и ещё {len(all_aircraft) - 10} записей")
    else:
        print("   Данные отсутствуют")

    # 3. Средняя скорость
    print("\n3. Средняя скорость по всем самолётам:")
    avg_speed = db_manager.get_avg_speed()
    if avg_speed is not None:
        print(f"   {avg_speed:.2f} м/с ({avg_speed * 3.6:.2f} км/ч)")
    else:
        print("   Данные отсутствуют")

    # 4. Самолёты со скоростью выше средней
    print("\n4. Самолёты со скоростью выше средней:")
    high_speed = db_manager.get_aeroplanes_with_higher_speed()
    if high_speed:
        print(f"   Найдено: {len(high_speed)}")
        for ac in high_speed[:10]:
            print(f"   - {ac[2]} ({ac[3]}), скорость: {ac[4]:.2f} м/с")
        if len(high_speed) > 10:
            print(f"   ... и ещё {len(high_speed) - 10} записей")
    else:
        print("   Данные отсутствуют")

    # 5. Поиск по позывному
    print("\n5. Поиск самолётов по позывному (пример: 'ACA'):")
    keyword_aircraft = db_manager.get_aeroplanes_with_keyword("ACA")
    if keyword_aircraft:
        print(f"   Найдено по ключу 'ACA': {len(keyword_aircraft)}")
        for ac in keyword_aircraft[:5]:
            print(f"   - {ac[2]} ({ac[3]}), скорость: {ac[4]:.2f} м/с")
    else:
        print("   Самолёты с 'ACA' в позывном не найдены")


def main():
    """Точка входа в программу"""
    # Список стран для отслеживания (не менее 4)
    countries = [
        "France",
        "Germany",
        "Italy",
        "Spain",
        "United Kingdom",
    ]

    # Инициализация API клиента
    api_client = OpenSkyNominatimClient()

    # Проверка подключения к API
    print("Проверка подключения к API...")
    if not api_client.connect():
        print("Ошибка: не удалось подключиться к API")
        sys.exit(1)
    print("Подключение к API успешно")

    # Инициализация подключения к БД
    db_params = get_db_params()
    db_manager = DBManager(db_params)

    try:
        print("Подключение к БД PostgreSQL...")
        db_manager.connect()
        print("Подключение к БД успешно")

        # Создание таблиц
        print("Создание таблиц (если не существуют)...")
        db_manager.create_tables()
        print("Таблицы готовы")

        # Сбор данных для каждой страны
        total_saved = 0
        for country in countries:
            saved = fetch_and_save_country_data(api_client, db_manager, country)
            total_saved += saved

        print(f"\n{'=' * 50}")
        print(f"ИТОГО: сохранено {total_saved} самолётов по {len(countries)} странам")
        print('=' * 50)

        # Вывод сводки
        print_db_summary(db_manager)

    except Exception as e:
        print(f"\nКритическая ошибка: {e}")
        sys.exit(1)
    finally:
        db_manager.close()
        print("\nСоединение с БД закрыто")


if __name__ == "__main__":
    main()