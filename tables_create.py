from config import engine

def create_tables():
    with engine.connect() as conn:
        conn.execute("""
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
            actor_id INT REFERENCES actors(actor_id),
            PRIMARY KEY (movie_id, actor_id)
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
        print("✅ Tables created.")

if __name__ == "__main__":
    create_tables()