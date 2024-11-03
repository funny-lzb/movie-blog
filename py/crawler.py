import requests
from bs4 import BeautifulSoup
import json
import time
import mysql.connector
from datetime import datetime
from dotenv import load_dotenv
import os

# 加载指定的环境文件
env_path = f".env.{os.getenv('PYTHON_ENV', 'development')}"
load_dotenv(env_path)

class DatabaseConnection:
    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD'),
            'database': os.getenv('DB_NAME', 'movie')
        }
    
    def __enter__(self):
        self.conn = mysql.connector.connect(**self.db_config)
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn.is_connected():
            self.conn.close()

def fetch_movie_detail(detail_url):
    try:
        print(f"正在获取电影详情: {detail_url}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(detail_url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 初始化所有变量
        original_title = None
        status = None
        original_language = None
        budget = None
        revenue = None
        cast_list = []  # 初始化演员列表
        recommendations = []  # 初始化推荐列表
        
        # 基本信息
        facts_section = soup.select_one('section.facts.left_column')
        if facts_section:
            # 遍历所有 p 标签获取信息
            p_tags = facts_section.find_all('p')
            for p in p_tags:
                # 获取 strong 标签中的文本（可能包含 bdi 标签）
                strong = p.find('strong')
                if not strong:
                    continue
                
                # 获取标签名（需要获取 strong 标签内的所有文本）
                label = ''.join(strong.stripped_strings)
                
                # 获取值（去掉 strong 标签后的文本）
                value = ''.join(text for text in p.stripped_strings if text not in strong.stripped_strings)
                
                print(f"Debug - 标签: '{label}', 值: '{value}'")  # 调试输出
                
                # 修改判断条件，同时支持简体和繁体
                if any(x in label for x in ['原名', '原始標題']):
                    original_title = value.strip()
                elif any(x in label for x in ['状态', '狀態']):
                    status = value.strip()
                elif any(x in label for x in ['原始语言', '原始語言']):
                    original_language = value.strip()
                elif any(x in label for x in ['预算', '電影成本']):
                    try:
                        budget = float(value.replace('$', '').replace(',', '').replace('.00', ''))
                    except:
                        budget = None
                elif any(x in label for x in ['票房', '收入']):
                    try:
                        revenue = float(value.replace('$', '').replace(',', '').replace('.00', ''))
                    except:
                        revenue = None
        
        # 其他基本信息
        tagline = soup.select_one('.tagline')
        tagline = tagline.text.strip() if tagline else None
        
        overview = soup.select_one('.overview')
        overview = overview.text.strip() if overview else None
        
        # 预告片 - 获取 YouTube iframe
        trailer_url = None
        play_trailer = soup.select_one('a.play_trailer')
        if play_trailer:
            video_id = play_trailer.get('data-id')
            if video_id and video_id != '#':
                # 构造完整的 iframe HTML
                trailer_url = f'<iframe type="text/html" style="background-color: #000;" width="796" height="447" src="//www.youtube.com/embed/{video_id}?autoplay=1&origin=https%3A%2F%2Fwww.themoviedb.org&hl=zh&modestbranding=1&fs=1&autohide=1" frameborder="0" allowfullscreen=""></iframe>'
                print(f"Debug - 找到预告片iframe: {trailer_url}")
        
        # 演员列表
        cast_elems = soup.select('.cast_list .card')
        for cast in cast_elems:
            name = cast.select_one('.name')
            image = cast.select_one('img')
            url = cast.select_one('a')
            if name and image and url:
                cast_list.append({
                    'name': name.text.strip(),
                    'image': image['src'],
                    'url': url['href']
                })
        
        # 推荐列表
        rec_elems = soup.select('.recommendations .card')
        for rec in rec_elems:
            title = rec.select_one('.title')
            image = rec.select_one('img')
            url = rec.select_one('a')
            if title and image and url:
                recommendations.append({
                    'title': title.text.strip(),
                    'image': image['src'],
                    'url': url['href']
                })
        
        print(f"获取到原标题: {original_title}")
        print(f"获取到状态: {status}")
        print(f"获取到原始语言: {original_language}")
        print(f"获取到预算: {budget}")
        print(f"获取到票房: {revenue}")
        print(f"获取到预告片iframe: {trailer_url}")
        
        return {
            'original_title': original_title,
            'status': status,
            'original_language': original_language,
            'budget': budget,
            'revenue': revenue,
            'tagline': tagline,
            'overview': overview,
            'trailer_url': trailer_url,
            'cast_list': cast_list,
            'recommendations': recommendations
        }
        
    except Exception as e:
        print(f"获取详情页出错: {e}")
        return None

def save_movie_and_detail(movie_info, detail_data):
    with DatabaseConnection() as conn:
        cursor = conn.cursor(buffered=True)
        try:
            # 1. 检查电影是否存在
            check_movie = "SELECT id FROM movie WHERE title = %s"
            cursor.execute(check_movie, (movie_info['title'],))
            result = cursor.fetchone()
            
            if result:
                movie_id = result[0]
                # 更新电影信息
                update_movie = """
                UPDATE movie 
                SET release_date = %s, vote_average = %s, poster_url = %s
                WHERE id = %s
                """
                movie_values = (
                    datetime.strptime(movie_info['releaseDate'], '%Y-%m-%d').date(),
                    movie_info['voteAverage'],
                    movie_info['posterUrl'],
                    movie_id
                )
                cursor.execute(update_movie, movie_values)
            else:
                # 插入新电影
                insert_movie = """
                INSERT INTO movie (title, release_date, vote_average, poster_url)
                VALUES (%s, %s, %s, %s)
                """
                movie_values = (
                    movie_info['title'],
                    datetime.strptime(movie_info['releaseDate'], '%Y-%m-%d').date(),
                    movie_info['voteAverage'],
                    movie_info['posterUrl']
                )
                cursor.execute(insert_movie, movie_values)
                movie_id = cursor.lastrowid
            
            # 2. 保存详情信息
            if detail_data:
                # 检查详情是否存在
                check_detail = "SELECT id FROM movie_detail WHERE movie_id = %s"
                cursor.execute(check_detail, (movie_id,))
                if cursor.fetchone():
                    # 更新详情
                    update_detail = """
                    UPDATE movie_detail SET
                        original_title = %s, status = %s, original_language = %s,
                        budget = %s, revenue = %s, tagline = %s, overview = %s,
                        trailer_url = %s, main_actor = %s, cast_list = %s,
                        recommendations = %s
                    WHERE movie_id = %s
                    """
                    detail_values = (
                        detail_data.get('original_title'),
                        detail_data.get('status'),
                        detail_data.get('original_language'),
                        detail_data.get('budget'),
                        detail_data.get('revenue'),
                        detail_data.get('tagline'),
                        detail_data.get('overview'),
                        detail_data.get('trailer_url'),
                        json.dumps(detail_data.get('main_actor')),
                        json.dumps(detail_data.get('cast_list')),
                        json.dumps(detail_data.get('recommendations')),
                        movie_id
                    )
                    cursor.execute(update_detail, detail_values)
                else:
                    # 插入新详情
                    insert_detail = """
                    INSERT INTO movie_detail (
                        movie_id, original_title, status, original_language,
                        budget, revenue, tagline, overview, trailer_url,
                        main_actor, cast_list, recommendations
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    """
                    detail_values = (
                        movie_id,
                        detail_data.get('original_title'),
                        detail_data.get('status'),
                        detail_data.get('original_language'),
                        detail_data.get('budget'),
                        detail_data.get('revenue'),
                        detail_data.get('tagline'),
                        detail_data.get('overview'),
                        detail_data.get('trailer_url'),
                        json.dumps(detail_data.get('main_actor')),
                        json.dumps(detail_data.get('cast_list')),
                        json.dumps(detail_data.get('recommendations'))
                    )
                    cursor.execute(insert_detail, detail_values)
            
            conn.commit()
            print(f"保存电影 {movie_info['title']} 及其详情成功")
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"保存数据时出错: {e}")
            return False
        finally:
            cursor.close()

def fetch_movies(total_pages=50):
    print("开始爬取电影数据...")
    base_url = "https://www.themoviedb.org/movie"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }

    success_count = 0
    
    try:
        # 测试网络连接
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        print(f"成功连接到 {base_url}")
        
        for page in range(1, total_pages + 1):
            print(f"\n正在获取第 {page}/{total_pages} 页...")
            
            url = f"{base_url}?page={page}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            print(f"正在解析第 {page} 页...")
            soup = BeautifulSoup(response.text, 'html.parser')
            
            movie_cards = soup.select('.card.style_1')
            print(f"在第 {page} 页找到 {len(movie_cards)} 个电影卡片")
            
            for index, card in enumerate(movie_cards, 1):
                try:
                    title_elem = card.select_one('h2 a')
                    title = title_elem.text.strip() if title_elem else None
                    
                    # 获取详情页URL
                    detail_url = None
                    if title_elem and 'href' in title_elem.attrs:
                        detail_url = f"https://www.themoviedb.org{title_elem['href']}"
                    
                    if not title or not detail_url:
                        continue
                    
                    date_elem = card.select_one('p') or card.select_one('.release_date')
                    date = date_elem.text.strip() if date_elem else None
                    
                    vote = card.select_one('.user_score_chart')
                    vote_average = vote['data-percent'] if vote else None
                    
                    image = card.select_one('img.poster') or card.select_one('img')
                    image_path = image['src'] if image and 'src' in image.attrs else None
                    
                    if all([title, date, vote_average, image_path]):
                        movie_info = {
                            'title': title,
                            'releaseDate': date,
                            'voteAverage': float(vote_average),
                            'posterUrl': image_path,
                            'detailUrl': detail_url
                        }
                        
                        # 获取详情数据
                        detail_data = fetch_movie_detail(detail_url)
                        time.sleep(1)  # 避免请求过快
                        
                        # 保存数据
                        if save_movie_and_detail(movie_info, detail_data):
                            success_count += 1
                            print(f"成功处理第 {page} 页第 {index} 个电影: {title}")
                    
                except Exception as e:
                    print(f"处理第 {page} 页第 {index} 个电影时出错: {e}")
                    continue
            
            if page < total_pages:
                time.sleep(1)

        print(f"\n成功! 共处理 {success_count} 部电影")
        return True

    except requests.RequestException as e:
        print(f"网络请求错误: {e}")
        return False
    except Exception as e:
        print(f"发生错误: {e}")
        print("错误类型:", type(e))
        return False

if __name__ == "__main__":
    try:
        print("=== 电影数据爬虫开始运行 ===")
        success = fetch_movies(60)  # 先爬1页测试
        print("=== 爬虫运行完成 ===" if success else "=== 爬虫运行失败 ===")
    except Exception as e:
        print(f"程序执行出错: {e}")