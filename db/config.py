from dotenv import load_dotenv
import os

load_dotenv()

HOST = os.getenv("DB_HOST") #localhost
USER = os.getenv("DB_USER") #appuser
PASSWORD = os.getenv("DB_PASSWORD") #inventory1234
DBNAME = os.getenv("DB_NAME") #inventory
ADMIN_PASS = os.getenv("ADMIN_PASS")