from base64 import b64encode as enc64
from telebot import types
from exif import Image
import numpy as np
import tempfile
import logging
import telebot
import time
import os

# -------------------------------------------------------------------------------------------------------------------------------------
bot = telebot.TeleBot('1813697722:AAHP7kjaJrZ5iMOSxnUgX_nmYT5LBMTd-0A')
output_data = {}
is_complain = False


# -------------------------------------------------------------------------------------------------------------------------------------
def write_message(message, text):
    try:
        bot.send_message(message.chat.id, text)
    except Exception as error_message:
        logging.error(str(error_message) + "  ┋  " + time.ctime() + "\n")


def photo_download(message):
    try:
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        current_file_exstension = (str(file_info.file_path)).split('.')[-1]
        temp_dir = tempfile.mkdtemp()
        src = temp_dir + fr'\saved_photo.{current_file_exstension}'
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
            new_file.close()

        # -----------------------------------------------------------------------------------------------------------------------------

        with open(src, 'rb') as f:
            output_data["image-bite"] = enc64(f.read())
            f.close()

        # -----------------------------------------------------------------------------------------------------------------------------

        with open(src, 'rb') as image_file:
            if Image(image_file).has_exif:
                position = get_exif(src)
                if position:
                    output_data["pos"] = position
                else:
                    asc_location(message)
            else:
                asc_location(message)

        # -----------------------------------------------------------------------------------------------------------------------------

        if message.text:
            output_data["complaint"] = message.text
        else:
            output_data["complaint"] = message.caption

    except Exception as error_message:
        logging.error(str(error_message) + "  ┋  " + time.ctime() + "\n")


def get_exif(directions):
    try:
        with open(directions, 'rb') as image_file:
            exif_data = Image(image_file)
        return exif_data.gps_latitude, exif_data.gps_longitude
    except:
        return None


def asc_location(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
    keyboard.add(button_geo)
    try:
        bot.send_message(message.chat.id, "Включите локацию.", reply_markup=keyboard)
    except Exception as error_message:
        logging.error(str(error_message) + "  ┋  " + time.ctime() + "\n")


# -------------------------------------------------------------------------------------------------------------------------------------
@bot.message_handler(content_types=['location'])
def location(message):
    if message.location:
        try:
            output_data["pos"] = message.location
        except Exception as error_message:
            logging.error(str(error_message) + "  ┋  " + time.ctime() + "\n")


@bot.message_handler(commands=['start'])
def welcome(message):
    try:
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_appeal = types.KeyboardButton(text="Подать жалобу")
        button_proposal = types.KeyboardButton(text="Выдвинуть предложение")
        button_gratitude = types.KeyboardButton(text="Выразить благодарность")
        keyboard.add(button_appeal, button_proposal, button_gratitude)
        bot.send_message(message.chat.id, 'Выбирите действие:', reply_markup=keyboard)
    except Exception as error_message:
        logging.error(error_message + "  ┋  " + time.ctime() + "\n")


@bot.message_handler(commands=['help'])
def welcome(message):
    try:
        write_message(message, '!!! надо написать формы !!!')
    except Exception as error_message:
        logging.error(error_message + "  ┋  " + time.ctime() + "\n")


@bot.message_handler(content_types=['text', 'photo'])
def start(message):
    global is_complain
    try:
        if message.text:
            ms = message.text.lower()
        else:
            ms = message.caption.lower()

        if ms in ["подать жалобу", "выдвинуть предложение", "выразить благодарность"]:
            if ms == "подать жалобу":
                write_message(message, 'Для того чтобы подать жалобу, нам необходимо получить от вас:\n'
                                       '1) Фотографию🖼 с места жалобы + Описание жалобы\n'
                                       '2) *Подтвердить запрос на геоданные, чтобы мы знали, где находится проблема')
                is_complain = True
                bot.register_next_step_handler(message, photo_download)

            elif ms == 'выдвинуть предложение':
                is_complain = False
                write_message(message, 'Предложение')

            elif ms == 'выразить благодарность':
                is_complain = False
                write_message(message, 'Благодарность')
        elif is_complain:
            is_complain = False
            output_data["complaint"] = ms

    except Exception as error_message:
        logging.error(str(error_message) + "  ┋  " + time.ctime() + "\n")


# -------------------------------------------------------------------------------------------------------------------------------------
bot.polling(none_stop=True, interval=0)

"""

1) Вставить это в описание бота:
    Здравствуйте! Этот бот создан для отправки жалоб, предложений и благодарностей.\n 
    Если вы хотите узнать форму отправки для каждого вида сообщения, напишите /help

2) Добавить типы или что там по заданию
"""
