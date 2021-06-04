from telebot import types
from exif import Image
import numpy as np
import datetime
import tempfile
import logging
import telebot
import time
from main import add_complaint, add_thanks, add_sentense
import os

# -------------------------------------------------------------------------------------------------------------------------------------
complain_level = 0
# -------------------------------------------------------------------------------------------------------------------------------------
offer_level = 0
# -------------------------------------------------------------------------------------------------------------------------------------
gratitude_level = 0
# -------------------------------------------------------------------------------------------------------------------------------------
bot = telebot.TeleBot('1813697722:AAHP7kjaJrZ5iMOSxnUgX_nmYT5LBMTd-0A')
# -------------------------------------------------------------------------------------------------------------------------------------

output_data = {}
before_output_data = []

# -------------------------------------------------------------------------------------------------------------------------------------
f = open("log.txt", "w")
f.close()


# -------------------------------------------------------------------------------------------------------------------------------------
def write_message(message, text):
    try:
        bot.send_message(message.chat.id, text)
    except Exception as error_message:
        logging.error(str(error_message) + "  ┋  " + time.ctime() + "\n")
        log = open("log.txt", "a", encoding="UTF-8")
        log.write(str(error_message) + "  ┋  " + time.ctime() + "\n")
        log.close()


def photo_download(message, get_type):
    global before_output_data
    try:
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        current_file_exstension = (str(file_info.file_path)).split('.')[-1]
        temp_dir = tempfile.mkdtemp()
        src = temp_dir + fr'\saved_photo.{current_file_exstension}'
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
            new_file.close()

        with open(src, 'rb') as file:
            before_output_data.append(file.read())

        if get_type == 1:
            before_output_data.append(datetime.datetime.now().strftime("%d.%m.%y %H:%M"))
            asc_location(message)
        elif get_type == 2:
            create_output_data()
    except Exception as error_message:
        logging.error(str(error_message) + "  ┋  " + time.ctime() + "\n")
        log = open("log.txt", "a", encoding="UTF-8")
        log.write(str(error_message) + "  ┋  " + time.ctime() + "\n")
        log.close()


def asc_location(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_geo = types.KeyboardButton(text="Отправить местоположение  ", request_location=True)
    keyboard.add(button_geo)
    try:
        bot.send_message(message.chat.id, "Отправьте геоданные для обнаружения проблемы на карте 🗺"
                                          "(для этого надо включить геоданные).", reply_markup=keyboard)
    except Exception as error_message:
        logging.error(str(error_message) + "  ┋  " + time.ctime() + "\n")
        log = open("log.txt", "a", encoding="UTF-8")
        log.write(str(error_message) + "  ┋  " + time.ctime() + "\n")
        log.close()


def create_output_data():
    global output_data, before_output_data
    try:
        if before_output_data[0] == "Complain":
            output_data["Name"] = before_output_data[1]
            output_data["Description"] = before_output_data[2]
            output_data["Bite-photo"] = before_output_data[3]
            output_data["Date"] = before_output_data[4]
            output_data["Location"] = before_output_data[5]
            output_data["Type"] = before_output_data[6]
        elif before_output_data[0] == "Gratitude":
            output_data["Name"] = before_output_data[1]
            output_data["Description"] = before_output_data[2]
            output_data["Bite-photo"] = before_output_data[3]
            output_data["Date"] = before_output_data[4]
        elif before_output_data[0] == "Offer":
            output_data["Name"] = before_output_data[1]
            output_data["Description"] = before_output_data[2]
            output_data["Files"] = before_output_data[3]
            output_data["Date"] = before_output_data[4]
        if output_data:
            pass
        else:
            return
        if before_output_data[0] == "Complain":
            if ["Bite-photo", "Description", "Location", "Name"] == list(output_data.keys()).sort():
                add_complaint(coordinates=f'{output_data["Location"][0]},{output_data["Location"][1]}',
                              name=output_data["Name"], description=output_data["Description"],
                              photo=output_data["Bite-photo"], date=output_data["Date"])
                output_data = {}
        elif before_output_data[0] == "Gratitude":
            if ["Bite-photo", "Description", "Name"] == list(output_data.keys()).sort():
                add_thanks(coordinates=f'{output_data["Location"][0]},{output_data["Location"][1]}',
                           name=output_data["Name"], description=output_data["Description"],
                           photo=output_data["Bite-photo"])
                output_data = {}
        elif before_output_data[0] == "Offer":
            add_sentense(description=output_data["Description"],
                         file=output_data["Files"])
            output_data = {}
    except Exception as error_message:
        logging.error(str(error_message) + "  ┋  " + time.ctime() + "\n")
        log = open("log.txt", "a", encoding="UTF-8")
        log.write(str(error_message) + "  ┋  " + time.ctime() + "\n")
        log.close()


# -------------------------------------------------------------------------------------------------------------------------------------
@bot.message_handler(content_types=['location'])
def location(message):
    global complain_level
    if message.location:
        try:
            before_output_data.append(message.location)
            complain_level += 1

            # -------------------------------------------------------------------------------------------------------------------------
            keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
            for i in [types.KeyboardButton(text="Дорожная 🛣"), types.KeyboardButton(text="Экологическая 🌱"),
                      types.KeyboardButton(text="Социальная 🤷"), types.KeyboardButton(text="ЖКХ 🏚"),
                      types.KeyboardButton(text="Другое 🧩")]:
                keyboard.add(i)
            bot.send_message(message.chat.id, "В заключение выберите тип проблемы:", reply_markup=keyboard)
        except Exception as error_message:
            logging.error(str(error_message) + "  ┋  " + time.ctime() + "\n")
            log = open("log.txt", "a", encoding="UTF-8")
            log.write(str(error_message) + "  ┋  " + time.ctime() + "\n")
            log.close()
    else:
        write_message(message, "Проблемы с обнаружением. Попробуйте ещё раз")


@bot.message_handler(commands=['start'])
def welcome(message):
    try:
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_appeal = types.KeyboardButton(text="Подать жалобу ❗")
        button_proposal = types.KeyboardButton(text="Выдвинуть предложение  ✅")
        button_gratitude = types.KeyboardButton(text="Выразить благодарность 💯")
        keyboard.add(button_appeal, button_proposal, button_gratitude)
        bot.send_message(message.chat.id, f'Здравствуйте, {message.from_user.first_name}! Выбирите действие:',
                         reply_markup=keyboard)
    except Exception as error_message:
        logging.error(str(error_message) + "  ┋  " + time.ctime() + "\n")
        log = open("log.txt", "a", encoding="UTF-8")
        log.write(str(error_message) + "  ┋  " + time.ctime() + "\n")
        log.close()


@bot.message_handler(commands=['help'])
def welcome(message):
    try:
        write_message(message, 'Выбирите из предложенного списка, что вы хотите сделать.')
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_appeal = types.KeyboardButton(text="Подать жалобу ❗")
        button_proposal = types.KeyboardButton(text="Выдвинуть предложение  ✅")
        button_gratitude = types.KeyboardButton(text="Выразить благодарность 💯")
        keyboard.add(button_appeal, button_proposal, button_gratitude)
        bot.send_message(message.chat.id, 'Выбирите действие:', reply_markup=keyboard)
    except Exception as error_message:
        logging.error(str(error_message) + "  ┋  " + time.ctime() + "\n")
        log = open("log.txt", "a", encoding="UTF-8")
        log.write(str(error_message) + "  ┋  " + time.ctime() + "\n")
        log.close()


@bot.message_handler(content_types=['text', 'photo'])
def start(message):
    global complain_level, before_output_data, offer_level, gratitude_level
    try:
        if message.text:
            response = message.text.lower()
        else:
            response = ""

        if response == "подать жалобу ❗":
            complain_level = 1
            before_output_data = ["Complain"]
            gratitude_level, offer_level = 0, 0
            write_message(message, "Напишите, мне название проблемы")
        elif response == "выдвинуть предложение  ✅":
            before_output_data = ["Offer"]
            write_message(message, "Кратко назовите ваше предложение")
            gratitude_level, complain_level = 0, 0
            offer_level = 1
        elif response == "выразить благодарность 💯":
            before_output_data = ["Gratitude"]
            write_message(message, "Дайте краткое название")
            offer_level, complain_level = 0, 0
            gratitude_level = 1

        elif complain_level != 0:
            if complain_level == 1:
                before_output_data.append(message.text)
                complain_level += 1
                write_message(message, "Опишите проблему поподробней")
            elif complain_level == 2:
                before_output_data.append(message.text)
                complain_level += 1
                write_message(message, "Для подтверждения проблемы, отправьте мне фото 🖼")
            elif complain_level == 3:
                photo_download(message, 1)
            elif complain_level == 4:
                before_output_data.append(message.text)
                create_output_data()
                complain_level = 0
                before_output_data = []
                keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                button_appeal = types.KeyboardButton(text="Подать жалобу ❗")
                button_proposal = types.KeyboardButton(text="Выдвинуть предложение  ✅")
                button_gratitude = types.KeyboardButton(text="Выразить благодарность 💯")
                keyboard.add(button_appeal, button_proposal, button_gratitude)
                bot.send_message(message.chat.id,
                                 "Спасибо, что проявляете активность! Жалоба будет рассмотренна в ближайшее время",
                                 reply_markup=keyboard)
        elif offer_level != 0:
            if offer_level == 1:
                before_output_data.append(message.text)
                offer_level += 1
                write_message(message, "Опишите ваше предложение поподробней")
            elif offer_level == 2:
                before_output_data.append(message.text)
                offer_level += 1
                write_message(message, "Отправьте фотографию рассматриваемым объектом 🖼")
            elif offer_level == 3:
                photo_download(message, 2)
                keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                button_appeal = types.KeyboardButton(text="Подать жалобу ❗")
                button_proposal = types.KeyboardButton(text="Выдвинуть предложение  ✅")
                button_gratitude = types.KeyboardButton(text="Выразить благодарность 💯")
                keyboard.add(button_appeal, button_proposal, button_gratitude)
                bot.send_message(message.chat.id,
                                 "Благодорим за вашу активность. Вскоре предложение будет рассмотренно",
                                 reply_markup=keyboard)
                offer_level = 0
                before_output_data = []

        elif gratitude_level != 0:
            if gratitude_level == 1:
                before_output_data.append(message.text)
                gratitude_level += 1
                write_message(message, "Опишите вашу благодарность")
            elif gratitude_level == 2:
                before_output_data.append(message.text)
                gratitude_level += 1
                write_message(message, "Отправьте фотографию с обновленным объектом 🖼")
            elif gratitude_level == 3:
                photo_download(message, 2)

                keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                button_appeal = types.KeyboardButton(text="Подать жалобу ❗")
                button_proposal = types.KeyboardButton(text="Выдвинуть предложение  ✅")
                button_gratitude = types.KeyboardButton(text="Выразить благодарность 💯")
                keyboard.add(button_appeal, button_proposal, button_gratitude)
                bot.send_message(message.chat.id,
                                 "Нам очень приятна ваша оценка. Будем продолжать работать в том же духе",
                                 reply_markup=keyboard)

                gratitude_level = 0
                before_output_data = []
        else:
            write_message(message, "Извините, не понял вашего ответа.")

    except Exception as error_message:
        logging.error(str(error_message) + "  ┋  " + time.ctime() + "\n")
        log = open("log.txt", "a", encoding="UTF-8")
        log.write(str(error_message) + "  ┋  " + time.ctime() + "\n")
        log.close()


# -------------------------------------------------------------------------------------------------------------------------------------
bot.polling(none_stop=True, interval=0)

"""

1) Вставить это в описание бота:
    Здравствуйте! Этот бот создан для отправки жалоб, предложений и благодарностей.\n 
    Если вы хотите узнать форму отправки для каждого вида сообщения, напишите /help

"""
