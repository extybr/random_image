import requests
from bs4 import BeautifulSoup
import urllib3
import random
import re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_all_movie_links():
    """Получаем все ссылки на фильмы с главной страницы чарта"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    url = "https://www.imdb.com/chart/moviemeter/"
    try:
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser')
        list_links = []
        # Ищем все ссылки, которые начинаются с /title/tt
        movie_links = soup.find_all('a', href=re.compile(r'^/title/tt\d+/'))
        
        for link in movie_links:
            href = link.get('href', '')
            if href:
                # Преобразуем относительную ссылку в абсолютную
                full_url = f"https://www.imdb.com{href}" if href.startswith('/') else href
                list_links.append(full_url)
        # Убираем дубликаты
        list_links = list(set(list_links))
        return list_links
    except Exception as e:
        print(f"Error getting movie links: {e}")
        return []


def get_hd_poster_url(movie_url):
    """Получаем HD постер для конкретного фильма"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        response = requests.get(movie_url, headers=headers, timeout=10, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser')
        # Ищем HD постер в мета-тегах
        meta_image = soup.find('meta', property='og:image')
        if meta_image:
            image_url = meta_image.get('content', '')
            if image_url:
                # Увеличиваем качество и очищаем URL
                hd_url = image_url.replace('._V1_', '._V1_SX3000_SY3000_')
                hd_url = hd_url.replace('_SY445_SX445_', '_SY2000_SX2000_')
                hd_url = hd_url.replace('\n', '').replace('\r', '').replace(' ', '')
                return hd_url
        return None
    except Exception as e:
        print(f"Error getting poster from {movie_url}: {e}")
        return None


# Получаем все ссылки на фильмы
list_links = get_all_movie_links()

if list_links:
    # Генерируем случайное число для выбора фильма (от 0 до 99)
    random_number = random.randint(0, len(list_links) - 1)
    # Получаем случайную ссылку на фильм
    random_movie_url = list_links[random_number]
    # Получаем HD постер
    poster_url = get_hd_poster_url(random_movie_url)
    
    if poster_url:
        print(poster_url)
    else:
        print("No poster found")
else:
    print("No movie links found")
