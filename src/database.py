import psycopg2
from psycopg2 import sql
from typing import Optional


class DBManager:
    """ Класс для работы с БД PostgreSQL для хранения данных о странах и самолётах """

    def __init__(self, db_params: dict):
        """ Подключение к БД """
        self.db_params = db_params
        self.conn: Optional[psycopg2.extensions.connection] = None

    def connect(self):
        """ Установка соединения с БД """
        self.conn = psycopg2.connect(**self.db_params)
        self.conn.autocommit = True

    def close(self):
        """ Закрытие соединения с БД"""
        if self.conn and not self.conn.closed:
            self.conn.close()

    def create_tables(self):
        """ Создание таблиц countries и aircraft, если они ещё не существуют """
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS countries (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL UNIQUE,
                    south DOUBLE PRECISION,
                    north DOUBLE PRECISION,
                    west DOUBLE PRECISION,
                    east DOUBLE PRECISION,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS aircraft (
                    id SERIAL PRIMARY KEY,
                    icao24 VARCHAR(10),
                    callsign VARCHAR(20),
                    origin_country VARCHAR(255),
                    velocity DOUBLE PRECISION,
                    altitude DOUBLE PRECISION,
                    country_id INTEGER REFERENCES countries(id) ON DELETE CASCADE,
                    tracked_at TIMESTAMP DEFAULT NOW()
                );
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_aircraft_country_id ON aircraft(country_id);
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_aircraft_callsign ON aircraft(callsign);
            """)

    def save_country(self, name: str, bounds: tuple) -> int:
        """ Сохранение страны в таблицу countries.
        Если страна уже существует, возвращает её id """
        south, north, west, east = bounds
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO countries (name, south, north, west, east)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (name) DO UPDATE
                    SET south = EXCLUDED.south,
                        north = EXCLUDED.north,
                        west = EXCLUDED.west,
                        east = EXCLUDED.east
                RETURNING id;
            """, (name, south, north, west, east))
            return cur.fetchone()[0]

    def save_aircraft(self, icao24: str, callsign: str, origin_country: str,
                      velocity: float, altitude: float, country_id: int):
        """ Сохранение данных о самолёте в таблицу aircraft """
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO aircraft (icao24, callsign, origin_country, velocity, altitude, country_id)
                VALUES (%s, %s, %s, %s, %s, %s);
            """, (icao24, callsign, origin_country, velocity, altitude, country_id))

    def get_countries_and_aeroplanes_count(self) -> list[tuple[str, int]]:
        """ Получает список всех стран и количество самолётов в их воздушных пространствах """
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT c.name, COUNT(a.id) AS aeroplanes_count
                FROM countries c
                LEFT JOIN aircraft a ON c.id = a.country_id
                GROUP BY c.id, c.name
                ORDER BY aeroplanes_count DESC;
            """)
            return cur.fetchall()

    def get_all_aeroplanes(self) -> list[tuple]:
        """ Получает список всех воздушных судов """
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, icao24, callsign, origin_country, velocity, altitude, tracked_at
                FROM aircraft
                ORDER BY tracked_at DESC;
            """)
            return cur.fetchall()

    def get_avg_speed(self) -> Optional[float]:
        """ Получает среднюю скорость по всем самолётам """
        with self.conn.cursor() as cur:
            cur.execute("SELECT AVG(velocity) FROM aircraft WHERE velocity IS NOT NULL;")
            result = cur.fetchone()
            return result[0] if result and result[0] is not None else None

    def get_aeroplanes_with_higher_speed(self) -> list[tuple]:
        """ Получает список всех самолётов, у которых скорость выше средней """
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, icao24, callsign, origin_country, velocity, altitude
                FROM aircraft
                WHERE velocity > (SELECT AVG(velocity) FROM aircraft WHERE velocity IS NOT NULL)
                ORDER BY velocity DESC;
            """)
            return cur.fetchall()

    def get_aeroplanes_with_keyword(self, keyword: str) -> list[tuple]:
        """ Получает список всех самолётов, в позывном которых содержатся переданные символы """
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, icao24, callsign, origin_country, velocity, altitude
                FROM aircraft
                WHERE callsign ILIKE %s
                ORDER BY velocity DESC;
            """, (f'%{keyword}%',))
            return cur.fetchall()
