import os
import re
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from tabulate import tabulate

DB_NAME = "movies_db"
DB_USER = "postgres"
DB_PASS = "postgres"
DB_HOST = "localhost"
DB_PORT = 5432
DATA_PATH = "data"
QUERIES_FILE = "queries.sql"

conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASS,
    host=DB_HOST,
    port=DB_PORT
)
cur = conn.cursor()

cur.execute("""
DROP TABLE IF EXISTS ratings, movie_actor, users, movies,
    directors, actors, genres CASCADE;

CREATE TABLE genres (
    genre_id INT PRIMARY KEY,
    name TEXT
);
CREATE TABLE directors (
    director_id INT PRIMARY KEY,
    name TEXT
);
CREATE TABLE movies (
    movie_id INT PRIMARY KEY,
    title TEXT,
    release_year INT,
    genre_id INT REFERENCES genres(genre_id),
    director_id INT REFERENCES directors(director_id),
    duration_min INT
);
CREATE TABLE actors (
    actor_id INT PRIMARY KEY,
    name TEXT
);
CREATE TABLE movie_actor (
    movie_id INT REFERENCES movies(movie_id),
    actor_id INT REFERENCES actors(actor_id)
);
CREATE TABLE users (
    user_id INT PRIMARY KEY,
    username TEXT
);
CREATE TABLE ratings (
    rating_id INT PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    movie_id INT REFERENCES movies(movie_id),
    rating NUMERIC
);
""")
conn.commit()
print(" Tables created")

tables = ["genres", "directors", "movies", "actors",
          "movie_actor", "users", "ratings"]

for t in tables:
    csv_path = os.path.join(DATA_PATH, f"{t}.csv")
    df = pd.read_csv(csv_path)
    df = df.astype(object)
    cols = ",".join(df.columns)
    values = [tuple(row) for row in df.to_numpy()]
    execute_values(cur, f"INSERT INTO {t} ({cols}) VALUES %s", values)
    conn.commit()
    print(f"Loaded {t}")

def load_queries(path=QUERIES_FILE):
    queries = []
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    pattern = r"--\s*(.*?)\n(.*?);"
    for desc, sql in re.findall(pattern, content, flags=re.S | re.M):
        queries.append((desc.strip(), sql.strip()))
    return queries

for i, (desc, sql) in enumerate(load_queries(), 1):
    print(f"\n=== Query {i}: {desc} ===")
    cur.execute(sql)
    rows = cur.fetchall()
    if rows:
        print(tabulate(rows, headers=[c[0] for c in cur.description], tablefmt="psql"))
    else:
        print("(no rows)")

cur.close()
conn.close()
print("\n Done!")
