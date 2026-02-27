import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from app.config import settings
import time

class Database:
    def __init__(self):
        self.connection_pool = None


    def connect(self):
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                1 , 20,
                host=settings.DATABASE_HOST,
                port=settings.DATABASE_PORT,
                database=settings.DATABASE_NAME,
                user=settings.DATABASE_USER,
                password=settings.DATABASE_PASSWORD,
                cursor_factory=RealDictCursor
            )
            print("Connected to the database")
        except Exception as error:
            print(f"Error connecting to the database: {error}")
            time.sleep(2)
            self.connect()

    def get_connection(self):
        return self.connection_pool.getconn()

    def return_connection(self, conn):
        return self.connection_pool.putconn(conn)

    def close_all_connections(self):
        if self.connection_pool:
            self.connection_pool.closeall()
            print("All connections closed")

db = Database()
