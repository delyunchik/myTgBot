import logging
from config import *
from helpers import *
from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.utils.emoji import emojize
from aiogram.dispatcher import Dispatcher
from aiogram.types.message import ContentType
from aiogram.utils.markdown import text, bold, italic, code, pre
from aiogram.types import ParseMode, InputMediaPhoto, InputMediaVideo, ChatActions

# Настраиваем журналирование
logging.basicConfig(
    filename='myTgBot.log',
    encoding='utf-8',
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    )

# Инициализация бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

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
