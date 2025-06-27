import os

HOST = os.getenv("DB_HOST", "localhost")
USER = os.getenv("DB_USER", "appuser")
PASSWORD = os.getenv("DB_PASSWORD", "inventory1234")
DBNAME = os.getenv("DB_NAME", "inventory")