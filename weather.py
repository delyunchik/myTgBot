import requests
import json
from aiogram.utils.markdown import text, bold, italic, code, pre
from const import WEATHER_LAT, WEATHER_LON
from config import YANDEX_WEATHER_KEY

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
    'nw': 'северо-западное',
    'n': 'северное',
    'ne': 'северо-восточное',
    'e': 'восточное',
    'se': 'юго-восточное',
    's': 'южное',
    'sw': 'юго-западное',
    'w': 'западное',
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
    # url = 'https://api.weather.yandex.ru/v2/forecast?lat=' + WEATHER_LAT + \
    #     '&lon=' + WEATHER_LON + '&extra=true'
    # r = requests.get(url, headers={'X-Yandex-API-Key': YANDEX_WEATHER_KEY})
    with open('weather.json', 'r') as f:
        # загрузим json-ответ
        data = json.load(f)

        # проанализируем ветер
        wind_dir = data['fact']['wind_dir']
        if wind_dir == 'c':
            wind = 'Полный штиль'
        else:
            wind = 'Направление ветра ' + wind_dir_dict[wind_dir]

        # наличие грозы
        is_thunder = data['fact']['is_thunder']
        if is_thunder:
            thunder = ', гроза'
        else:
            thunder = ''

        # проверим есть ли особое погодное состояние
        phenom_condition_key = data['fact'].get('phenom_condition', default=False)
        if phenom_condition_key:
            phenom_condition = ', ' + phenom_condition_dict[phenom_condition_key]
        else:
            phenom_condition = ''

        # составим итоговое сообщение
        ans = text(
            'Погода в городе '+data['geo_object']['province']['name'],
            'Сегодня '+data['now_dt'],
            'На дворе ' + season_dict[data['fact']['season']] + ', ' + \
            condition_dict[data['fact']['condition']] + thunder,
            'Температура ' + str(data['fact']['temp']) + \
            ' (ощущается как ' + str(data['fact']['feels_like']) + ')',
            ', '.join((
                wind, 
                cloudness_dict[data['fact']['cloudness']]
            )) + phenom_condition,
            '',  # отделим ссылку пустой строкой
            'Подробнее по ссылке:',
            data['info']['url'],
            sep='\n'
        )
    return ans
