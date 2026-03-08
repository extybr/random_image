import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import urllib3
import re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_popular_imdb_movies():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    # Главная страница IMDb с популярными фильмами
    url = "https://www.imdb.com/chart/moviemeter/"
    try:
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser')
        popular_movies = []
        # Ищем ссылки на фильмы в таблице
        movie_links = soup.find_all('a', href=re.compile(r'/title/tt\d+/'))
        
        for link in movie_links:
            href = link.get('href', '')
            # Извлекаем IMDb ID из ссылки
            match = re.search(r'/title/(tt\d+)/', href)
            if match:
                imdb_id = match.group(1)
                title = link.get_text().strip()
                if title and len(title) > 2 and title not in [m.get('title') for m in popular_movies]:
                    popular_movies.append({
                        'id': imdb_id,
                        'title': title
                    })
                if len(popular_movies) >= 15:  # Ограничиваем количество
                    break
        return popular_movies
    except Exception as e:
        print(f"Error getting popular movies: {e}")
        return []


def get_page_with_playwright(url):
    with sync_playwright() as p:
        # Запускаем браузер (headless=False, чтобы увидеть, что происходит)
        browser = p.chromium.launch(headless=True) 
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        )
        page = context.new_page()
        # Переходим на страницу и ждем загрузки
        page.goto(url, wait_until='networkidle')
        # Получаем HTML
        html = page.content()
        # Закрываем браузер
        browser.close()
        return html


def get_hd_poster_for_movie(imdb_id, title):
    """Получаем HD постер для конкретного фильма"""
    try:
        url = f"https://www.imdb.com/title/{imdb_id}/"
        response = get_page_with_playwright(url)
        soup = BeautifulSoup(response, 'html.parser')
        # Ищем HD постер в мета-тегах
        meta_image = soup.find('meta', property='og:image')
        if meta_image:
            image_url = meta_image.get('content', '')
            if image_url:
                # Увеличиваем качество
                hd_url = image_url.replace('._V1_', '._V1_SX3000_SY3000_')
                hd_url = hd_url.replace('_SY445_SX445_', '_SY2000_SX2000_')
                return hd_url
        return None
    except Exception as e:
        print(f"Error getting poster for {title}: {e}")
        return None


def parse_imdb_popular_hd():
    print("Getting popular movies from IMDb...")
    popular_movies = get_popular_imdb_movies()
    print(f"Found {len(popular_movies)} popular movies")
    movies_with_posters = []
    
    for movie in popular_movies:
        print(f"Getting HD poster for: {movie['title']}")
        hd_poster = get_hd_poster_for_movie(movie['id'], movie['title'])
        if hd_poster:
            movies_with_posters.append({
                'title': movie['title'],
                'image_url': hd_poster,
                'imdb_id': movie['id']
            })
    return movies_with_posters


print("=== IMDb Popular Movies with HD Posters ===")
results = parse_imdb_popular_hd()
print(f"\nSuccessfully got {len(results)} HD posters")

for i, movie in enumerate(results, 1):
    print(f"{i}. {movie['title']}")
    print(f"   {movie['image_url']}\n")
