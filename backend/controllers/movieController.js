const movieService = require("../services/movieService");

const getMoviesList = async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const pageSize = parseInt(req.query.pageSize) || 10;
    const result = await movieService.getMovies(page, pageSize);
    res.json(result);
  } catch (error) {
    console.error("Database error:", error);
    res.status(500).json({
      error: "Failed to fetch movies data",
      message: error.message,
    });
  }
};

const getMovieDetail = async (req, res) => {
  try {
    const { id } = req.params;
    const movie = await movieService.getMovieById(id);

    if (!movie) {
      return res.status(404).json({ error: "Movie not found" });
    }

    res.json(movie);
  } catch (error) {
    console.error("Database error:", error);
    res.status(500).json({
      error: "Failed to fetch movie details",
      message: error.message,
      details: error.stack,
    });
  }
};

module.exports = {
  getMoviesList,
  getMovieDetail,
};
