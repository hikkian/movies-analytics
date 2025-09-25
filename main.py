import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import os

conn = psycopg2.connect(
    dbname="movies_db",
    user="postgres",
    password="postgres",
    host="localhost",
    port=5432
)
cur = conn.cursor()

cur.execute("""
DROP TABLE IF EXISTS ratings, movie_actor, users, movies, directors, actors, genres CASCADE;

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

data_path = "data"
tables = ["genres","directors","movies","actors","movie_actor","users","ratings"]

for t in tables:
    df = pd.read_csv(os.path.join(data_path, f"{t}.csv"))
    cols = ",".join(df.columns)
    df = df.astype(object)
    values = [tuple(row) for row in df.to_numpy()]
    execute_values(
        cur,
        f"INSERT INTO {t} ({cols}) VALUES %s",
        values,
        page_size=5000
    )
    conn.commit()


queries = [
    ("Top 10 highest-rated movies",
     """
     SELECT m.title, ROUND(AVG(r.rating),2) as avg_rating
     FROM movies m JOIN ratings r ON m.movie_id=r.movie_id
     GROUP BY m.title
     ORDER BY avg_rating DESC
     LIMIT 10;
     """),
    ("Average rating by genre",
     """
     SELECT g.name, ROUND(AVG(r.rating),2)
     FROM genres g
     JOIN movies m ON g.genre_id=m.genre_id
     JOIN ratings r ON m.movie_id=r.movie_id
     GROUP BY g.name
     ORDER BY 2 DESC;
     """)
]

for desc, q in queries:
    print("\n", desc)
    cur.execute(q)
    for row in cur.fetchall():
        print(row)

cur.close()
conn.close()
