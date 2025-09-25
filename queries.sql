-- ===== 1. Top 10 highest-rated movies =====
SELECT m.title,
       ROUND(AVG(r.score), 2) AS avg_rating,
       COUNT(r.id) AS rating_count
FROM movies m
JOIN ratings r ON r.movie_id = m.id
GROUP BY m.title
ORDER BY avg_rating DESC, rating_count DESC
LIMIT 10;

-- ===== 2. Average rating by genre =====
SELECT g.name AS genre,
       ROUND(AVG(r.score), 2) AS avg_score
FROM genres g
JOIN movie_genres mg ON mg.genre_id = g.id
JOIN movies m ON m.id = mg.movie_id
JOIN ratings r ON r.movie_id = m.id
GROUP BY g.name
ORDER BY avg_score DESC;

-- ===== 3. Average movie duration by genre =====
SELECT g.name AS genre,
       ROUND(AVG(m.duration_min), 1) AS avg_duration
FROM genres g
JOIN movie_genres mg ON mg.genre_id = g.id
JOIN movies m ON m.id = mg.movie_id
GROUP BY g.name
ORDER BY avg_duration DESC;

-- ===== 4. All movies for a specific director (example: 'Christopher Nolan') =====
SELECT d.name AS director,
       m.title,
       m.release_year
FROM directors d
JOIN movie_directors md ON md.director_id = d.id
JOIN movies m ON m.id = md.movie_id
WHERE d.name ILIKE 'Christopher Nolan'
ORDER BY m.release_year;

-- ===== 5. Last 10 movies added to the database =====
SELECT title, release_year, created_at
FROM movies
ORDER BY created_at DESC
LIMIT 10;

-- ===== 6. Users and how many ratings they submitted =====
SELECT r.user_name,
       COUNT(r.id) AS ratings_count,
       ROUND(AVG(r.score),2) AS avg_user_score
FROM ratings r
GROUP BY r.user_name
ORDER BY ratings_count DESC;