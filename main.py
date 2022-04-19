import logging
from config import *
from helpers import *
from weather import *
from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.utils.emoji import emojize
from aiogram.dispatcher import Dispatcher
from aiogram.types.message import ContentType
from aiogram.utils.markdown import text, bold, italic, code, pre
from aiogram.types import ParseMode, \
    InputMediaPhoto, InputMediaVideo, ChatActions
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

# Настраиваем журналирование
logging.basicConfig(
    filename='myTgBot.log',
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] ' +
           '%(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    )

# Инициализация бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


# обработчик команды start
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):

    # ответим приветственным сообщением
    await message.reply('Привет!\nИспользуй /help, '
                        'чтобы узнать список доступных команд!',
                        reply_markup=ReplyKeyboardRemove())


# обработчик команды help
@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):

    # сформируем текст сообщения
    msg = text(
        'Я многое знаю, могу ответить на следующие вопросы:',
        bold('Кто такой кто-либо?') + ' или ' + bold('Что такое что-либо?'),
        'Могу ' + bold('показать фото чего угодно'),
        'Рассказать ' + bold('шутку дня'),
        'Рассказать ' + bold('какие новости'),
        'Показать прогноз ' + bold('погоды'),
        'Могу повторить данную справку /help',
        sep='\n')

    # ответим подготовленным текстом
    await message.reply(msg, parse_mode=ParseMode.MARKDOWN)


# произвольное фото
@dp.message_handler(commands=['photo'])
async def send_welcome(message: types.Message):
    img_url = get_img_url()
    await message.reply_photo(img_url)


# сюрприз - фото кота
@dp.message_handler(regexp='(^cat[s]?$|puss)')
async def cats(message: types.Message):
    with open('data/cats.jpg', 'rb') as photo:
        await message.reply_photo(photo, caption='Сюрприиииз! Cats are here 😺')


# запрос новостей
@dp.message_handler(regexp='новост[ьи]')
async def news(message: types.Message):
    await message.reply(get_news(message.text))


# запрос википедии
@dp.message_handler(regexp='тако[йе]')
async def wiki(message: types.Message):

    # возвращается обработанный текст статьи и ссылка на картинку
    text, img_url = get_wiki(message.text)

    # просто слепим их вместе, клиент TG сам подкачает фото
    await message.reply('\n'.join((text, img_url)))


# запрос фото чего-либо
@dp.message_handler(regexp='(покажи|фот(о|к[уи]))')
async def wiki(message: types.Message):

    # наша спец функция вернет ссылку на подходящую картинку
    img_url = get_img_url(message.text)

    # отправим ее спец методом
    await message.reply_photo(img_url)


# запрос шутки дня
@dp.message_handler(regexp='шутк[ау]')
async def news(message: types.Message):
    await message.reply(get_joke(message.text))


# запрос погоды
@dp.message_handler(regexp='погод[аыу]')
async def weather(message: types.Message):
    await message.reply(get_weather(message.text))


# если не подошел ни один из предыдущих обработчиков
@dp.message_handler(content_types=types.ContentType.ANY)
async def unknown_message(msg: types.Message):

    # дежурный текст
    message_text = text(
        emojize('К сожалению, я не знаю, что с этим делать :astonished:'),
        italic('\nПросто напомню,'), 'что есть',
        code('команда'), '/help'
    )

    # отправим его пользователю
    await msg.reply(message_text, parse_mode=ParseMode.MARKDOWN)


# Обработчик завершения работы
async def shutdown(dispatcher: Dispatcher):

    # завершающие процедуры
    logging.info('Завершение работы бота!')
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


# начать опрос API Telegram
if __name__ == '__main__':
    executor.start_polling(dp, on_shutdown=shutdown, skip_updates=True)
