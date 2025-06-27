import pymysql
from db import config
from tkinter import messagebox

_conn = None

def get_conn():
    global _conn

    try:
        if _conn is None or not _conn.open:
            _conn = pymysql.connect(
                host=config.HOST,
                user=config.USER,
                password=config.PASSWORD
            )
            cursor = _conn.cursor()

            DB_NAME = config.DBNAME
            db_query = f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"
            cursor.execute(db_query)
            _conn.select_db(DB_NAME)
    except Exception as e:
        messagebox.showerror('Error', f'Database connection failed: {str(e)}')
        return None

    return _conn


# DB_NAME = config.DBNAME

# try:
#     conn = pymysql.connect(
#         host=config.HOST,
#         user=config.USER,
#         password=config.PASSWORD
#     )
#     cursor = conn.cursor()
# except Exception as e:
#     messagebox.showerror('Error', f'Database connection failed: {str(e)}')

# db_query = f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"
# cursor.execute(db_query)
# conn.select_db(DB_NAME)

# def get_conn():
#     return conn