# for telegram bot

import random
import re
import datetime
import requests
import urllib3
from bs4 import BeautifulSoup
from loguru import logger
from aiogram import Bot
from aiogram.types import Message, FSInputFile
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

kino_image = {}
deepfake_image = {}


async def resource_link_availability(message: Message, bot: Bot) -> None:
    source = {get_link_kino: 'https://kinoleha.net',
              get_link_imdb: 'https://www.imdb.com',
              get_link_deepfake: 'https://deepfake0001.s3.amazonaws.com'}
    for key, value in source.items():
        try:
            response = requests.get(value, timeout=7).status_code
            if response in (200, 403):
                logger.info(f'Запрос к ресурсу: {value}')
                await key(message, bot, value) 
        except requests.exceptions.ReadTimeout:
            logger.error(f'Timeout: {value}')
            continue
        except requests.exceptions.ConnectionError:
            logger.error(f'ConnectionError: {value}')
            continue
        except Exception:
            await bot.send_message(message.chat.id, 'Сервер изображений недоступен')


async def get_link_kino(message: Message, bot: Bot, src: str) -> None:
    """ Выводит случайные изображения / kinoleha.net """
    global kino_image
    server = src[8:]
    try:
        if not kino_image:
            with open(file=f'{server[:-4]}.txt', mode='r', encoding='utf-8') as text:
                items = text.readlines()
                [items.remove(item) for item in items if not item.startswith('#')]
                for number, line in enumerate(items):
                    kino_image[number] = line
        choice = random.randint(1, len(kino_image) - 1)
        result = kino_image[choice]
        link = result[39:]
        for i in range(len(link) - 2):
            if link[i] == '"' and link[i + 1] == ',':
                link = link[:i]
                kino_image[choice] = link
                break
        await bot.send_photo(message.chat.id, photo=link)
    except Exception as error:
        msg = f'Сервер {server} недоступен'
        logger.error(msg)
        await bot.send_message(message.chat.id, msg)
        if str(error).find('Error code: 400'):
            await bot.send_photo(message.chat.id,
                                 photo=FSInputFile(path='img/cheburnet.jpg'))


async def get_link_deepfake(message: Message, bot: Bot, src: str) -> None:
    """ Выводит случайные изображения / deepfake0001.s3.amazonaws.com """
    global deepfake_image
    src = 'https://creators.deepfake.com'
    server = src[8:]
    dt = 2 ** (datetime.datetime.now().day % 2)
    try:
        if not deepfake_image:
            with open(file=f'{server[:-4]}.{dt}.txt', mode='r', encoding='utf-8') as text:
                items = text.readlines()
                for number, line in enumerate(items):
                    deepfake_image[number] = line
        choice = random.randint(0, len(deepfake_image))
        link = deepfake_image[choice]
        await bot.send_photo(message.chat.id, photo=link)
    except Exception as error:
        msg = f'Сервер {server} недоступен'
        logger.error(msg)
        await bot.send_message(message.chat.id, msg)
        if str(error).find('Error code: 400'):
            await bot.send_photo(message.chat.id,
                                 photo=FSInputFile(path='img/cheburnet.jpg'))


async def get_all_movie_links() -> list:
    """ Получаем все ссылки на фильмы с главной страницы чарта  / imdb.com """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
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


async def get_hd_poster_url(movie_url: str) -> str | None:
    """ Получаем HD постер для конкретного фильма  / imdb.com """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    } 
    try:
        response = requests.get(movie_url, headers=headers, timeout=10, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser')
        meta_image = soup.find('meta', property='og:image')
        if meta_image:
            image_url = meta_image.get('content', '')
            if image_url:
                hd_url = image_url.replace('._V1_', '._V1_SX3000_SY3000_')
                hd_url = hd_url.replace('_SY445_SX445_', '_SY2000_SX2000_')
                hd_url = hd_url.replace('\n', '').replace('\r', '').replace(' ', '')
                return hd_url
        return None
    except Exception:
        return None


async def get_link_imdb(message: Message, bot: Bot, src: str) -> None:
    """ Выводит случайные изображения / imdb.com """
    server = src[8:]
    try:
        list_links = await get_all_movie_links()
        if list_links:
            random_number = random.randint(0, len(list_links) - 1)
            random_movie_url = list_links[random_number]
            poster_url = await get_hd_poster_url(random_movie_url)
            if poster_url:
                await bot.send_photo(message.chat.id, photo=poster_url)
            else:
                await bot.send_photo(message.chat.id, photo=FSInputFile(path='img/vodka.jpg'))
        else:
            await bot.send_photo(message.chat.id, photo=FSInputFile(path='img/vodka.jpg'))
    except Exception as error:
        msg = f'Сервер {server} недоступен'
        logger.error(msg)
        await bot.send_message(message.chat.id, msg)
        if 'Error code: 400' in str(error):
            await bot.send_photo(message.chat.id, photo=FSInputFile(path='img/vodka.jpg'))
