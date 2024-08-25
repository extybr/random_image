# for telegram bot

from random import randint
from loguru import logger
from requests import get, exceptions
from aiogram import Bot
from aiogram.types import Message, FSInputFile

kino_image = {}
deepfake_image = {}


async def resource_link_availability(message, bot):
    source = {get_link_kino: 'https://kinoleha.net',
              get_link_deepfake: 'https://creators.deepfake.com'}
    for key, value in source.items():
        try:
            response = get(value, timeout=1.5).status_code
            if response == 200:
                logger.info(f'Запрос к ресурсу: {value}')
                await key(message, bot, value) 
        except exceptions.ReadTimeout:
            logger.error(f'Timeout: {value}')
            continue
        except exceptions.ConnectionError:
            logger.error(f'ConnectionError: {value}')
            continue
        except Exception:
            await bot.send_message(message.chat.id, 'Сервер изображений недоступен')


async def get_link_kino(message: Message, bot: Bot, src: str) -> None:
    """ Выводит случайные изображения """
    global kino_image
    server = src[8:]
    try:
        if not kino_image:
            with open(file=f'{server[:-4]}.txt', mode='r', encoding='utf-8') as text:
                items = text.readlines()
                [items.remove(item) for item in items if not item.startswith('#')]
                for number, line in enumerate(items):
                    kino_image[number] = line
        choice = randint(1, len(kino_image) - 1)
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
                                 photo=FSInputFile(path='img/vodka.jpg'))


async def get_link_deepfake(message: Message, bot: Bot, src: str) -> None:
    """ Выводит случайные изображения """
    global deepfake_image
    server = src[8:]
    try:
        if not deepfake_image:
            with open(file=f'{server[:-4]}.txt', mode='r', encoding='utf-8') as text:
                items = text.readlines()
                for number, line in enumerate(items):
                    deepfake_image[number] = line
        choice = randint(1, len(deepfake_image) - 1)
        link = deepfake_image[choice]
        await bot.send_photo(message.chat.id, photo=link)
    except Exception as error:
        msg = f'Сервер {server} недоступен'
        logger.error(msg)
        await bot.send_message(message.chat.id, msg)
        if str(error).find('Error code: 400'):
            await bot.send_photo(message.chat.id,
                                 photo=FSInputFile(path='img/vodka.jpg'))

