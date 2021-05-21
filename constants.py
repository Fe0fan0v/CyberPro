DICT_COLORS_PROBLEMS = {'Дорожная': 'grey', 'ЖКХ': 'orange', 'Экологическая': 'green', 'Другое': 'red'}
DICT_COLORS_LABELS = {'Дорожная': 'road_label.png', 'ЖКХ': 'survice.png', 'Экологическая': 'ecology.png',
                      'Другое': 'unnamed.png'}


def transformation_date(date):
    date = date.split(' ')
    month = {'01': 'Январь', '02': 'Февраль', '03': 'Март', '04': 'Апрель', '05': 'Май', '06': 'Июнь',
             '07': 'Июль', '08': 'Август', '09': 'Сентябрь', '10': 'Октябрь', '11': 'Ноябрь', '12': 'Декабрь'}
    mod_date = ''
