import logging
import wikipedia
from const import *
import re
import requests
from bs4 import BeautifulSoup
import random
from aiogram.utils.emoji import emojize

# Устанавливаем русский язык в Wikipedia
wikipedia.set_lang("ru")


# получить произвольное фото по названию
# через поиск картинок Яндекса
def get_img_url(name=''):
    try:
        # найдем картинки через Яндекс
        response = requests.get('https://yandex.ru/images/search?text='+name)

        # распарсим вывод
        soup = BeautifulSoup(response.content, "html.parser")

        # получим все ссылки на картинки
        links = soup.find_all(
            "img",
            class_="serp-item__thumb justifier__thumb"
        )

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
        result = wikipedia.search(s, results=1)
        wkpage = wikipedia.WikipediaPage(title=result[0])

        # Получаем сводку
        wikitext = wkpage.summary

        # Разделяем по точкам
        wikimas = wikitext.split('.')

        # Отбрасываем всЕ после последней точки
        wikimas = wikimas[:-1]

        # Создаем пустую переменную для текста
        wikitext2 = ''

        # Проходимся по строкам, где нет знаков «равно»
        # (то есть все, кроме заголовков)
        for x in wikimas:
            if not('==' in x):
                # Если в строке осталось больше трех символов, добавляем ее к
                # нашей переменной и возвращаем утерянные при разделении строк
                # точки на место
                if(len((x.strip())) > 3):
                    wikitext2 = wikitext2+x+'.'
            else:
                break

        # Теперь при помощи регулярных выражений убираем разметку
        wikitext2 = re.sub('\([^()]*\)', '', wikitext2)
        wikitext2 = re.sub('\([^()]*\)', '', wikitext2)
        wikitext2 = re.sub('\{[^\{\}]*\}', '', wikitext2)

        # Найдем подходящую картинку
        img_url = ''
        for img in wkpage.images:
            if img.find('.jpg') >= 0 or img.find('.jpeg') >= 0:
                img_url = '\n' + img
                break

        # Возвращаем текстовую строку и URL картинки
        return (wikitext2, img_url)

    # Обрабатываем исключение, которое мог вернуть модуль wikipedia при запросе
    except Exception as e:
        # зажурналируем ошибку
        logging.error(e)

        # дежурная фраза и пустая ссылка
        return ('В энциклопедии нет информации об этом', '')


# получить случайную шутку
def get_joke(name=''):
    try:
        while True:
            # найдем произвольную шутку
            r = requests.get('http://bashorg.org/casual')

            # распарсим вывод
            soup = BeautifulSoup(r.content, "html.parser")

            # получим нужный блок
            d = soup.find_all("div", class_="q")

            # вернем найденный текст пропустив 6 строк заголовка
            a = d[0].text.split('\n')
            text = '\n'.join(a[6:])

            # проверим, что шутка хорошая
            good_joke = True
            for word in ['опа', 'уй', 'еба', 'пиз', 'чле']:
                if word in text:
                    good_joke = False
                    break

            # если шутка все еще хорошая, выходим из цикла
            if good_joke:
                break

        # вернем текст найденной шутки
        return text

    # что-то пошло не так
    except Exception as e:
        # зажурналируем ошибку
        logging.error(e)

        # вернем дежурный ответ
        return emojize('Не до шуток сейчас :expressionless:')


# получить новости
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

    # Обрабатываем исключение, которое мог вернуть модуль wikipedia при запросе
    except Exception as e:
        # зажурналируем ошибку
        logging.error(e)

        # дежурная фраза и пустая ссылка
        text = NO_NEWS

    return text
