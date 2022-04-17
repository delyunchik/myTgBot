import logging
from markupsafe import Markup
import wikipedia
import re
import requests
from bs4 import BeautifulSoup
import random
from config import *
from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.utils.emoji import emojize
from aiogram.dispatcher import Dispatcher
from aiogram.types.message import ContentType
from aiogram.utils.markdown import text, bold, italic, code, pre
from aiogram.types import ParseMode, InputMediaPhoto, InputMediaVideo, ChatActions

# Настраиваем журналирование
logging.basicConfig(level=logging.DEBUG)

# Устанавливаем русский язык в Wikipedia
wikipedia.set_lang("ru")

# Инициализация бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def get_joke(name=''):
    try:
        # найдем картинки через Яндекс
        r = requests.get('http://bashorg.org/casual')

        # распарсим вывод
        soup = BeautifulSoup(r.content,"html.parser")

        # получим все ссылки на картинки
        d = soup.find_all("div",class_="q")

        # вернем найденный текст пропустив 6 строк заголовка
        a = d[0].text.split('\n')
        text = '\n'.join(a[6:])

        # вернем текст найденной шутки
        return text

    # что-то пошло не так    
    except Exception as e:
        # зажурналируем ошибку
        logging.error(e)

        # вернем дежурный ответ
        return emojize('Не до шуток сейчас :expressionless:')
    

def get_img_url(name=''):
    try:
        # найдем картинки через Яндекс
        response = requests.get('https://yandex.ru/images/search?text='+name)

        # распарсим вывод
        soup = BeautifulSoup(response.content,"html.parser")

        # получим все ссылки на картинки
        links = soup.find_all("img",class_="serp-item__thumb justifier__thumb")

        # выберем произвольную картинку
        n = len(links)
        link = links[random.randint(0, n-1)]
        link = link.get("src")
        return "https:" + str(link)

    # что-то пошло не так    
    except Exception as e:
        # зажурналируем ошибку
        logging.error(e)

        # вернем дежурный ответ
        return FAIL_URL


# Чистим текст статьи в Wikipedia и ограничиваем его тысячей символов
def get_wiki(s):
    try:
        result = wikipedia.search(s, results = 1)
        wkpage = wikipedia.WikipediaPage(title = result[0])
        # Получаем сводку
        wikitext = wkpage.summary
        # # Разделяем по точкам
        wikimas=wikitext.split('.')
        # # Отбрасываем всЕ после последней точки
        wikimas = wikimas[:-1]
        # Создаем пустую переменную для текста
        wikitext2 = ''
        # Проходимся по строкам, где нет знаков «равно» (то есть все, кроме заголовков)
        for x in wikimas:
            if not('==' in x):
                    # Если в строке осталось больше трех символов, добавляем ее к нашей переменной и возвращаем утерянные при разделении строк точки на место
                if(len((x.strip()))>3):
                   wikitext2=wikitext2+x+'.'
            else:
                break
        # Теперь при помощи регулярных выражений убираем разметку
        wikitext2=re.sub('\([^()]*\)', '', wikitext2)
        wikitext2=re.sub('\([^()]*\)', '', wikitext2)
        wikitext2=re.sub('\{[^\{\}]*\}', '', wikitext2)
        # Найдем подходящую картинку
        img_url = ''
        for img in wkpage.images:
            if img.find('.jpg') >= 0 or img.find('.jpeg') >= 0:
                img_url = '\n' + img
                break
        # Возвращаем текстовую строку
        return (wikitext2, img_url)
    # Обрабатываем исключение, которое мог вернуть модуль wikipedia при запросе
    except Exception as e:
        logging.error(e)
        return ('В энциклопедии нет информации об этом', '')


def get_news(name):
    NO_NEWS = emojize('Пока ничего нового :expressionless:')

    try:
        url = 'https://yandex.ru/news/rubric/computers'
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')

        # Ищет все новости и записывает в переменную
        news = soup.find_all('a', class_='mg-card__link')

        # Выводит текст каждой новости (всего их 10)
        if len(news) > 0:
            text = '\n'.join([link for link in news])
        else:
            text = NO_NEWS

    except Exception as e:
        logging.error(e) 
        text = NO_NEWS

    return text


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(
        types.KeyboardButton('Отправить свой контакт ☎️', request_contact=True)
    ).add(
        types.KeyboardButton('Отправить свою локацию 🗺️', request_location=True)
    ).add(
        types.KeyboardButton("/fact")
    ).add(
        types.KeyboardButton("/photo")
    )
    await message.reply('Привет!\nИспользуй /help, '
                        'чтобы узнать список доступных команд!', reply_markup=markup)


@dp.message_handler(commands=['photo'])
async def send_welcome(message: types.Message):
    img_url = get_img_url()
    await message.reply_photo(img_url)

    # with open('data/cat.jpg', 'rb') as photo:
    #     await message.reply_photo(photo, caption=emojize('Cats are here :cat:'))


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    msg = text(bold('Я могу ответить на следующие команды:'),
               '/voice', '/photo', '/group', '/note', '/file, /testpre', sep='\n')
    await message.reply(msg, parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(regexp='(^cat[s]?$|puss)')
async def cats(message: types.Message):
    with open('data/cats.jpg', 'rb') as photo:
        await message.reply_photo(photo, caption='Cats are here 😺')


@dp.message_handler(regexp='новост[ьи]')
async def news(message: types.Message):
    await message.reply(get_news(message.text))


@dp.message_handler(regexp='тако[йе]')
async def wiki(message: types.Message):
    text, img_url = get_wiki(message.text)
    await message.reply('\n'.join((text, img_url)))


@dp.message_handler(regexp='(покажи|фот(о|к[уи]))')
async def wiki(message: types.Message):
    img_url = get_img_url(message.text)
    await message.reply_photo(img_url)


@dp.message_handler(regexp='шутк[ау]')
async def news(message: types.Message):
    await message.reply(get_joke(message.text))


@dp.message_handler(content_types=types.ContentType.ANY)
async def unknown_message(msg: types.Message):
    message_text = text(emojize('Я не знаю, что с этим делать :astonished:'),
                        italic('\nЯ просто напомню,'), 'что есть',
                        code('команда'), '/help')
    await msg.reply(message_text, parse_mode=ParseMode.MARKDOWN)


# Обработчик завершения работы
async def shutdown(dispatcher: Dispatcher):
    logging.info('Завершение работы бота!')
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    executor.start_polling(dp, on_shutdown=shutdown, skip_updates=True)
