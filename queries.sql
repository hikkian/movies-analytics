-- 1. Top 10 movies by average rating (at least 10 ratings)
SELECT m.title,
       ROUND(AVG(r.rating),2) AS avg_rating,
       COUNT(r.rating_id)     AS total_votes
FROM movies m
JOIN ratings r ON m.movie_id = r.movie_id
GROUP BY m.title
HAVING COUNT(r.rating_id) >= 10
ORDER BY avg_rating DESC
LIMIT 10;

-- 2. Number of movies per genre
SELECT g.name AS genre,
       COUNT(m.movie_id) AS total_movies
FROM genres g
LEFT JOIN movies m ON g.genre_id = m.genre_id
GROUP BY g.name
ORDER BY total_movies DESC;

-- 3. Top 5 directors by average movie rating
SELECT d.name AS director,
       ROUND(AVG(r.rating),2) AS avg_rating,
       COUNT(DISTINCT m.movie_id) AS movies_count
FROM directors d
JOIN movies m ON d.director_id = m.director_id
JOIN ratings r ON m.movie_id = r.movie_id
GROUP BY d.name
HAVING COUNT(r.rating_id) >= 10
ORDER BY avg_rating DESC
LIMIT 5;

-- 4. Average rating by release year
SELECT m.release_year,
       ROUND(AVG(r.rating),2) AS avg_rating,
       COUNT(r.rating_id) AS votes
FROM movies m
JOIN ratings r ON m.movie_id = r.movie_id
GROUP BY m.release_year
ORDER BY m.release_year;

-- 5. Actors with the most movie appearances
SELECT a.name AS actor,
       COUNT(ma.movie_id) AS movie_count
FROM actors a
JOIN movie_actor ma ON a.actor_id = ma.actor_id
GROUP BY a.name
ORDER BY movie_count DESC
LIMIT 10;

-- 6. Longest movies per genre (max duration)
SELECT g.name AS genre,
       m.title,
       m.duration_min
FROM movies m
JOIN genres g ON m.genre_id = g.genre_id
WHERE (g.genre_id, m.duration_min) IN (
    SELECT genre_id, MAX(duration_min)
    FROM movies
    GROUP BY genre_id
);

-- 7. Average movie duration per director
SELECT d.name AS director,
       ROUND(AVG(m.duration_min),1) AS avg_duration
FROM directors d
JOIN movies m ON d.director_id = m.director_id
GROUP BY d.name
ORDER BY avg_duration DESC
LIMIT 10;

-- 8. Users who gave the highest average ratings (min 20 ratings)
SELECT u.username,
       ROUND(AVG(r.rating),2) AS avg_user_rating,
       COUNT(r.rating_id) AS total_ratings
FROM users u
JOIN ratings r ON u.user_id = r.user_id
GROUP BY u.username
HAVING COUNT(r.rating_id) >= 20
ORDER BY avg_user_rating DESC
LIMIT 10;

-- 9. Genres with highest average rating
SELECT g.name AS genre,
       ROUND(AVG(r.rating),2) AS avg_rating,
       COUNT(r.rating_id) AS total_votes
FROM genres g
JOIN movies m ON g.genre_id = m.genre_id
JOIN ratings r ON m.movie_id = r.movie_id
GROUP BY g.name
ORDER BY avg_rating DESC;

-- 10. Users who rated movies from at least 5 different genres
SELECT u.username,
       COUNT(DISTINCT g.genre_id) AS genres_rated
FROM users u
JOIN ratings r ON u.user_id = r.user_id
JOIN movies m  ON r.movie_id = m.movie_id
JOIN genres g  ON m.genre_id = g.genre_id
GROUP BY u.username
HAVING COUNT(DISTINCT g.genre_id) >= 5
ORDER BY genres_rated DESC;
