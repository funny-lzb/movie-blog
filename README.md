# Movie Information System

一个基于 Node.js 和 Express 的电影信息展示系统，支持电影列表展示、详情查看、分页浏览等功能。

## 功能特点

- 🎬 电影列表展示
- 📝 电影详细信息查看
- 🎥 预告片播放
- 👥 演员信息展示
- 📊 分页功能
- 📱 移动端适配
- 🌐 SSR (服务端渲染)

## 技术栈

- Node.js
- Express
- EJS 模板引擎
- MySQL
- Tailwind CSS
- Python (爬虫脚本)

## 安装步骤

1. 克隆项目

   ```bash
   git clone git@github.com:funny-lzb/class-vs-function-Component.git

   cd movie-system
   ```

2. 安装依赖

   ```bash
   cd backend

   npm install 或者 pnpm install
   ```

3. 配置环境变量
   创建开发环境配置文件 .env.development

   DB_HOST=localhost
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_NAME=movie

4. 启动服务器
   ```bash
   npm run dev 或者 pnpm dev
   ```

## 数据爬虫

项目包含一个 Python 爬虫脚本，用于获取电影数据：

1. 安装 Python 依赖

   ```bash
   cd py

   pip install requests beautifulsoup4 mysql-connector-python python-dotenv
   ```

2. 配置爬虫环境变量
   创建 .env.development

   DB_HOST=localhost
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_NAME=movie

3. 运行爬虫
   ```bash
   python crawler.py
   ```

## API 端点

- 电影列表：`GET /api/movie?page=1&pageSize=10`
- 电影详情：`GET /api/movie/:id`
- SSR 页面：`GET /movie`

## 项目结构

```
movie-system/
├── backend/
│ ├── config/ # 配置文件
│ ├── routes/ # 路由定义
│ ├── services/ # 业务逻辑
│ ├── views/ # EJS 模板
│ └── app.js # 应用入口
├── py/
│ └── crawler.py # 数据爬虫
└── README.md
```

## 主要功能

### 电影列表页

- 响应式网格布局（手机端 2 列，平板 3 列，桌面 5 列）
- 分页导航（支持首页、末页、上一页、下一页）
- 电影卡片展示（标题、海报、评分、上映日期）
- 卡片悬停动画效果

### 电影详情页

- 电影基本信息展示（标题、原标题、上映日期、评分等）
- 预告片播放（YouTube 嵌入）
- 演员列表展示
- 相关电影推荐
- 返回列表按钮

## 开发环境

- Node.js >= 14
- Python >= 3.8
- MySQL >= 5.7

## 环境变量配置

项目使用 .env 文件管理环境变量：

.env.development
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=movie

```

```
