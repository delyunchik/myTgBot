from asyncio.log import logger
import requests
import json
from aiogram.utils.markdown import text, bold, italic, code, pre
from const import WEATHER_LAT, WEATHER_LON
from config import YANDEX_WEATHER_KEY
from aiogram.utils.emoji import emojize
from datetime import datetime, timezone, timedelta

# словарь погодного описания
condition_dict = {
    'clear': 'ясно',
    'partly-cloudy': 'малооблачно',
    'cloudy': 'облачно с прояснениями',
    'overcast': 'пасмурно',
    'drizzle': 'морось',
    'light-rain': 'небольшой дождь',
    'rain': 'дождь',
    'moderate-rain': 'умеренно сильный дождь',
    'heavy-rain': 'сильный дождь',
    'continuous-heavy-rain': 'длительный сильный дождь',
    'showers': 'ливень',
    'wet-snow': 'дождь со снегом',
    'light-snow': 'небольшой снег',
    'snow': 'снег',
    'snow-showers': 'снегопад',
    'hail': 'град',
    'thunderstorm': 'гроза',
    'thunderstorm-with-rain': 'дождь с грозой',
    'thunderstorm-with-hail': 'гроза с градом'
}

# словарь направлений ветра
wind_dir_dict = {
    'nw': 'северо-западный',
    'n': 'северный',
    'ne': 'северо-восточный',
    'e': 'восточный',
    'se': 'юго-восточный',
    's': 'южный',
    'sw': 'юго-западный',
    'w': 'западный',
    'c': 'штиль'
}

# словарь времен года
season_dict = {
    'summer': 'лето',
    'autumn': 'осень',
    'winter': 'зима',
    'spring': 'весна'
}

# словарь облачности
cloudness_dict = {
    0: 'ясно',
    0.25: 'малооблачно',
    0.5: 'облачно с прояснениями',
    0.75: 'облачно с прояснениями',
    1: 'пасмурно'
}

# словарь Луны
moon_code_dict = {
    0: 'полнолуние',
    1: 'убывающая Луна',
    2: 'убывающая Луна',
    3: 'убывающая Луна',
    4: 'последняя четверть Луны',
    5: 'убывающая Луна',
    6: 'убывающая Луна',
    7: 'убывающая Луна',
    8: 'новолуние',
    9: 'растущая Луна',
    10: 'растущая Луна',
    11: 'растущая Луна',
    12: 'первая четверть Луны',
    13: 'растущая Луна',
    14: 'растущая Луна',
    15: 'растущая Луна'
}

# дополнительное погодное описание
phenom_condition_dict = {
    'fog': 'туман',
    'mist': 'дымка',
    'smoke': 'смог',
    'dust': 'пыль',
    'dust-suspension': 'пылевая взвесь',
    'duststorm': 'пыльная буря',
    'thunderstorm-with-duststorm': 'пыльная буря с грозой',
    'drifting-snow': 'слабая метель',
    'blowing-snow': 'метель',
    'ice-pellets': 'ледяная крупа',
    'freezing-rain': 'ледяной дождь',
    'tornado': 'торнадо',
    'volcanic-ash': 'вулканический пепел'
}


# получить прогноз погоды
def get_weather(name=''):

    # попробуем получить и распарсить данные сервиса погоды по API
    try:
        url = 'https://api.weather.yandex.ru/v2/forecast?lat=' + \
            WEATHER_LAT + \
            '&lon=' + WEATHER_LON + '&extra=true'
        r = requests.get(url, headers={'X-Yandex-API-Key': YANDEX_WEATHER_KEY})
        data = json.loads(r.text)

        # для тестирования
        # with open('weather.json', 'r') as f:
        #     # загрузим json-ответ
        #     data = json.load(f)

        # проанализируем ветер
        wind_dir = data['fact']['wind_dir']
        if wind_dir == 'c':
            wind = 'Полный штиль'
        else:
            wind = 'Ветер ' + str(data['fact']['wind_speed']) + ' м/с, ' + \
                wind_dir_dict[wind_dir]

        # наличие грозы
        is_thunder = data['fact']['is_thunder']
        if is_thunder:
            thunder = ', гроза'
        else:
            thunder = ''

        # проверим есть ли особое погодное состояние
        phenom_condition_key = data['fact'].get('phenom_condition', False)
        if phenom_condition_key:
            phenom_condition = ', ' + \
                phenom_condition_dict[phenom_condition_key]
        else:
            phenom_condition = ''

        # преобразуем время в читаемый формат
        ts = data['now']
        dt = datetime.fromtimestamp(ts).strftime('%H:%M:%S %d.%m.%Y')

        # составим итоговое сообщение
        ans = text(
            'Погода в городе '+data['geo_object']['province']['name'],
            'Сейчас ' + dt,
            'На дворе ' + season_dict[data['fact']['season']] + ', ' +
            condition_dict[data['fact']['condition']] + thunder,
            'Температура ' + str(data['fact']['temp']) + '℃' +
            ' (ощущается как ' + str(data['fact']['feels_like']) + '℃)',
            'Относительная влажность ' + str(data['fact']['humidity']) + '%',
            'Атмосферное давление ' + str(data['fact']['pressure_mm']) +
            ' мм.рт.ст.',
            ', '.join((
                wind,
                cloudness_dict[data['fact']['cloudness']] + phenom_condition
            )),
            '',  # пустая строка - разделитель
            sep='\n'
        )

        # прогнозы на ближайшие дни
        for forecast in data['forecasts']:

            # преобразуем время в читаемый формат
            ts = forecast['date_ts']
            dt = datetime.fromtimestamp(ts).strftime('%d.%m.%Y')

            # добавим блок к тексту ответа
            ans += text(
                '\nПрогноз на ' + dt,
                'Температура днем ' +
                str(forecast['parts']['day_short']['temp_min']) + '-' +
                str(forecast['parts']['day_short']['temp']) + ' ℃',
                'Температура ночью ' +
                str(forecast['parts']['night_short']['temp']) + ' ℃',
                moon_code_dict[forecast['moon_code']],
                '',  # пустая строка - разделитель
                sep='\n'
            )

        # финальная часть ответа
        ans += text(
            '',
            'Подробнее по ссылке: ' +
            data['info']['url'],
            sep='\n'
        )

    # что-то пошло не так
    except Exception as e:

        # зажурналируем ошибку
        logger.error(e)

        # вернем дежурный ответ
        return emojize('Sorry. Попозже проверю :expressionless:')

    # вернем сформированный ответ
    return ans
