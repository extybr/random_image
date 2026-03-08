import random
import re
import requests
import urllib3
import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


async def get_all_movie_links() -> list:
    """ Получаем все ссылки на фильмы с главной страницы чарта  / imdb.com """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    url = "https://www.imdb.com/chart/moviemeter/"
    
    try:
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser')   
        list_links = []
        movie_links = soup.find_all('a', href=re.compile(r'^/title/tt\d+/'))
        for link in movie_links:
            href = link.get('href', '')
            if href:
                full_url = f"https://www.imdb.com{href}" if href.startswith('/') else href
                list_links.append(full_url)
        list_links = list(set(list_links))
        return list_links
    except Exception:
        return []


async def get_page_with_playwright(url: str) -> str | None:
    """ Получаем страницу через Playwright (асинхронная версия) """
    try:
        async with async_playwright() as p:  # Используем async_playwright
            # Запускаем браузер
            browser = await p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            # Создаем контекст
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            
            page = await context.new_page()
            
            # Переходим на страницу
            await page.goto(url, wait_until='networkidle')
            
            # Получаем HTML
            html = await page.content()
            
            # Закрываем браузер
            await browser.close()
            return html
            
    except Exception as e:
        logger.error(f'Playwright error: {e}')
        return None



async def get_hd_poster_url(movie_url: str) -> str | None:
    """ Получаем HD постер для конкретного фильма """
    try:
        # Пробуем сначала простой requests (он быстрее)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }  
        response = requests.get(movie_url, headers=headers, timeout=10, verify=False)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            meta_image = soup.find('meta', property='og:image')
            
            if meta_image and meta_image.get('content'):
                image_url = meta_image['content']
                # Конвертируем в HD
                hd_url = image_url.replace('._V1_', '._V1_SX3000_')
                hd_url = hd_url.replace('_SY445_SX445_', '_SX3000_')
                return hd_url.strip()  
        # Если requests не сработал, пробуем Playwright
        html = await get_page_with_playwright(movie_url)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            meta_image = soup.find('meta', property='og:image')
            if meta_image and meta_image.get('content'):
                image_url = meta_image['content']
                hd_url = image_url.replace('._V1_', '._V1_SX3000_')
                hd_url = hd_url.replace('_SY445_SX445_', '_SX3000_')
                return hd_url.strip()
        return None
    except Exception as e:
        logger.error(f'Error getting poster: {e}')
        return None


async def get_link_imdb(src: str) -> None:
    """ Выводит случайные изображения / imdb.com """
    server = src[8:]
    try:
        list_links = await get_all_movie_links()
        if list_links:
            random_number = random.randint(0, len(list_links) - 1)
            random_movie_url = list_links[random_number]
            poster_url = await get_hd_poster_url(random_movie_url)
            if poster_url:
                print(poster_url)
            else:
                print('NO')
        else:
            print('Nooooo')
    except Exception as error:
        msg = f'Сервер {server} недоступен'
        print(msg)
        
        
asyncio.run(get_link_imdb('https://imdb.com'))
