DICT_COLORS_PROBLEMS = {'Дорожная': 'grey', 'ЖКХ': 'orange', 'Экологическая': 'green', 'Другое': 'red'}
DICT_COLORS_LABELS = {'Дорожная': 'road_label.png', 'ЖКХ': 'survice.png', 'Экологическая': 'ecology.png',
                      'Другое': 'unnamed.png'}
QUANTITY_CONFIRMATION = 5
URL = 8008


def transformation_date(date):
    date = date.split(' ')
    month = {'01': 'января', '02': 'февраля', '03': 'марта', '04': 'апреля', '05': 'мая', '06': 'июня',
             '07': 'июля', '08': 'августа', '09': 'сентября', '10': 'октября', '11': 'ноября', '12': 'декабря'}
    mod_date = f'{date[1].split(":")[0]}:{date[1].split(":")[1]} {date[0].split("-")[2]} {month[date[0].split("-")[1]]} {date[0].split("-")[0]}'
    return mod_date
