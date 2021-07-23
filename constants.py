import os
import sys
import requests

DICT_COLORS_PROBLEMS = {'Дорожная': 'grey', 'ЖКХ': 'orange', 'Экологическая': 'green', 'Другое': 'red'}
DICT_COLORS_LABELS = {'Дорожная': 'road_label.png', 'ЖКХ': 'survice.png', 'Экологическая': 'ecology.png',
                      'Другое': 'unnamed.png'}
DICT_COLORS_POINT = {'Дорожная': 'gr', 'ЖКХ': 'or', 'Экологическая': 'gn', 'Другое': 'rd'}
QUANTITY_CONFIRMATION = 5
URL = 8800


def transformation_date(date):
    date = date.split(' ')
    month = {'01': 'января', '02': 'февраля', '03': 'марта', '04': 'апреля', '05': 'мая', '06': 'июня',
             '07': 'июля', '08': 'августа', '09': 'сентября', '10': 'октября', '11': 'ноября', '12': 'декабря'}
    mod_date = f'{date[1].split(":")[0]}:{date[1].split(":")[1]} {date[0].split("-")[2]} {month[date[0].split("-")[1]]} {date[0].split("-")[0]}'
    return mod_date


def convert_to_binary_data(filename):
    # Преобразование данных в двоичный формат
    with open(filename, 'rb') as file:
        blob_data = file.read()
    return blob_data


def write_to_file(data, filename):
    # Преобразование двоичных данных в нужный формат
    with open(filename, 'wb') as file:
        file.write(data)


def recording_img(i_id, i_photo, pape_name='img_problems'):
    if f'{i_id}.jpg' not in os.listdir(f'static/img/{pape_name}'):
        write_to_file(i_photo, f'static/img/{pape_name}/{i_id}.jpg')


def image_scaling(img_width, img_height):
    width = 150
    if img_width >= img_height:
        width = 180
    height = round((width * img_height) / img_width, 0)
    return (width, height)


def write_map(ll_spn, size='450,450', map_file='map.png', zoom='15', point='rd'):
    map_request = f"http://static-maps.yandex.ru/1.x/?ll={ll_spn}&l=map"
    map_request += f"&size={size}&z={zoom}&pt={ll_spn},pm2{point}l"
    print(map_request)
    response = requests.get(map_request)

    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)

    # Запишем полученное изображение в файл.
    try:
        with open(map_file, "wb") as file:
            file.write(response.content)
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        sys.exit(2)

# show_map(ll_spn='60.14439582824708,55.14184738080156')
