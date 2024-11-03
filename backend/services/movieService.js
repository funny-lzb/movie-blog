const mysql = require("mysql2/promise");
const dbConfig = require("../config/database");

const getMovies = async (page, pageSize) => {
  const offset = (page - 1) * pageSize;
  const connection = await mysql.createConnection(dbConfig);

  const [totalResult] = await connection.execute(
    "SELECT COUNT(*) as total FROM movie"
  );
  const total = totalResult[0].total;

  const [movies] = await connection.execute(
    `SELECT id, title, release_date as releaseDate, 
            vote_average as voteAverage, poster_url as posterUrl 
     FROM movie 
     ORDER BY id ASC
     LIMIT ${pageSize} OFFSET ${offset}`
  );

  await connection.end();

  return {
    page,
    pageSize,
    total,
    totalPages: Math.ceil(total / pageSize),
    data: movies,
  };
};

const getMovieById = async id => {
  const connection = await mysql.createConnection(dbConfig);

  const [movies] = await connection.execute(
    `SELECT 
      m.id, m.title, m.release_date as releaseDate,
      m.vote_average as voteAverage, m.poster_url as posterUrl,
      md.original_title as originalTitle, md.status,
      md.original_language as originalLanguage,
      md.budget, md.revenue, md.tagline,
      md.overview, md.trailer_url as trailerUrl,
      md.cast_list as castList,
      md.recommendations
    FROM movie m
    LEFT JOIN movie_detail md ON m.id = md.movie_id
    WHERE m.id = ?`,
    [id]
  );

  await connection.end();

  if (!movies.length) return null;

  const movie = movies[0];

  try {
    if (movie.castList && movie.castList.trim()) {
      movie.castList = JSON.parse(movie.castList);
    } else {
      movie.castList = [];
    }
  } catch (e) {
    movie.castList = [];
  }

  try {
    if (movie.recommendations && movie.recommendations.trim()) {
      movie.recommendations = JSON.parse(movie.recommendations);
    } else {
      movie.recommendations = [];
    }
  } catch (e) {
    movie.recommendations = [];
  }

  return movie;
};

module.exports = {
  getMovies,
  getMovieById,
};
