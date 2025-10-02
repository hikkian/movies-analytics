import psycopg2
from config import DB_NAME, DB_USER, DB_PASS, DB_HOST, DB_PORT

def create_database():
    conn = psycopg2.connect(
        dbname="postgres",
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(f"DROP DATABASE IF EXISTS {DB_NAME};")
    cur.execute(f"CREATE DATABASE {DB_NAME};")
    print(f"✅ Database '{DB_NAME}' created.")

    cur.close()
    conn.close()

if __name__ == "__main__":
    create_database()