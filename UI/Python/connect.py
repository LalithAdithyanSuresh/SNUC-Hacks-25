import pymysql
import os
from dotenv import load_dotenv


def getConnection():
    load_dotenv()

    timeout = 10
    connection = pymysql.connect(
    charset="utf8mb4",
    connect_timeout=timeout,
    cursorclass=pymysql.cursors.DictCursor,
    db=os.getenv("DB_NAME"),
    host=os.getenv("DB_HOST"),
    password=os.getenv("DB_PASS"),
    read_timeout=timeout,
    port=int(os.getenv("DB_PORT")),
    user=os.getenv("DB_USER"),
    write_timeout=timeout,
    )

    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT 1")  # Check if connection is alive
    except pymysql.err.InterfaceError:
        print("Reconnecting to database...")
        connection.ping(reconnect=True)
    return connection,cursor
