require("dotenv").config({
  path: `.env.${process.env.NODE_ENV || "development"}`,
});
const express = require("express");
const cors = require("cors");
const movieRoutes = require("./routes/movieRoute");
const path = require("path");

const app = express();
const PORT = 3000;

// 设置模板引擎
app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));
app.use(express.static(path.join(__dirname, "public")));

app.use(cors());
app.use(express.json());

// API 路由
app.use("/api/movie", movieRoutes);

// SSR 路由
app.get("/movie", async (req, res) => {
  try {
    const response = await fetch(
      `http://localhost:${PORT}/api/movie?page=${
        req.query.page || 1
      }&pageSize=${req.query.pageSize || 10}`
    );
    const result = await response.json();
    res.render("movie", { movies: result });
  } catch (error) {
    console.error("Error:", error);
    res.status(500).render("error", {
      error: "Failed to fetch movies",
      message: error.message,
    });
  }
});

app.get("/movie/:id", async (req, res) => {
  try {
    const response = await fetch(
      `http://localhost:${PORT}/api/movie/${req.params.id}`
    );
    const movie = await response.json();
    res.render("movie-detail", { movie });
  } catch (error) {
    console.error("Error:", error);
    res.status(500).render("error", {
      error: "Failed to fetch movie details",
      message: error.message,
    });
  }
});

app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({
    error: "Something broke!",
    message: err.message,
  });
});

app.listen(PORT, () => {
  console.log(`服务器运行在 http://localhost:${PORT}`);
  console.log(`
可用的API端点：
- API 电影列表：http://localhost:${PORT}/api/movie?page=1&pageSize=10
- API 电影详情：http://localhost:${PORT}/api/movie/[电影ID]
- SSR 电影列表：http://localhost:${PORT}/movie
  `);
});
