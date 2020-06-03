# -*- coding: utf-8 -*-
import os
import time
import sys

import telebot

import config

from PIL import Image
from PIL import ImageFilter
from PIL.ImageFilter import (
    GaussianBlur
)



class User:

    def __init__(self, id):
        self.id = id
        self.channel = "RGB"
        self.radius = 5
        self.image_source = ""
        self.trigger = False
    
    def set_channel(self, channel):
        if channel in ["R", "G", "B", "RGB"]:
            self.channel = channel
        else:
            bot.send_message(self.id, "Wrong channel")
    
    def set_radius_of_blur(self, radius):
        try:
            a = int(radius)
            self.radius = a
        except:
            bot.send_message(self.id, "Wrong radius")
    
    def get_channel(self):
        return self.channel
    
    def get_radius_of_blur(self):
        return self.radius

users = {}

bot = telebot.TeleBot(config.token)

@bot.message_handler(commands=['start', 'restart'])
def handle_start_new_user(message):
    users[message.chat.id] = User(message.chat.id)
    bot.send_message(message.chat.id,
    """Создан новый пользователь с начальными данными:
        канал = RGB
        радиус = 5\n
    Возможные для использования каналы:
        R
        G
        B
        RGB\n
    Радиус должен быть натуральным числом!"""
    )
    bot.send_message(message.chat.id, 
    f"""
    Чтобы изменить ппараметры( радиус и канал ) вызовите команду и укажите новое значение параметра:
    /set_params channel=RGB
    или
    /set_params radius=8
    """
    )

@bot.message_handler(commands=['set_params'])
def handle_set_params(message):
    if message.chat.id in users:
        try:
            m = message.text.split()[1].split('=')
            if m[0] == "channel":
                users[message.chat.id].set_channel(m[1])
                bot.send_message(message.chat.id, "Новый канал установлено!")  
            if m[0] == "radius":
                users[message.chat.id].set_radius_of_blur(m[1])
                bot.send_message(message.chat.id, "Новый радиус установлено!")  
        except Exception as e:
            bot.reply_to(message, e)
    else:
        bot.send_message(message.chat.id, "Вы не зарегистрированы! Вызовите команду /start или /restart")

@bot.message_handler(commands=['get_params'])
def handle_get_params(message):
    if message.chat.id in users:
        bot.reply_to(message, f"Channel = {users[message.chat.id].channel}\nRadius = {users[message.chat.id].radius}")
    else:
        bot.send_message(message.chat.id, "Вы не зарегистрированы!\nВызовите команду /start или /restart")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.chat.id in users:
        if users[message.chat.id].trigger == True:
            try:
                a, b, c, d = map(int, message.text.strip().split())

                simg = Image.open(users[message.chat.id].image_source).convert("RGB")

                dimg = blur_mask_of_image(simg, users[message.chat.id].channel, users[message.chat.id].radius, a, b, c, d)
                dimg.save("./pic/ImageFilter_GaussianBlur_10.jpg")
                m = open('pic/ImageFilter_GaussianBlur_10.jpg', "rb")
                bot.send_photo(message.chat.id, m, None)
                m.close()

                users[message.chat.id].image_source = ""
                users[message.chat.id].trigger = False

            except Exception as e:
                bot.reply_to(message, e)
    else:
        bot.send_message(message.chat.id, "Вы не зарегистрированы!\nВызовите команду /start или /restart")

@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
    if message.chat.id in users:
        try:

            file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            # bot.send_message(message.chat.id, "Well, here we go")
            # bot.send_message(message.chat.id, "Write 4 numbers in percents: zone to blur, like this:\n<x1> <y1> <x2> <y2>")

            src = './pic/' + file_info.file_path
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)
            bot.reply_to(message, "Иображение загружено")
            
            users[message.chat.id].image_source = src
            users[message.chat.id].trigger = True

            bot.send_message(message.chat.id, "Введите координаты маски в процентах от изображения по примеру:\n0 20 100 80\nГде они записаны в формате x1 y1 x2 y2")
        except Exception as e:
                bot.reply_to(message, e)
    else:
        bot.send_message(message.chat.id, "Вы не зарегистрированы!\nВызовите команду /start или /restart")

def blur_mask_of_image(image, channel, radius_my, x1, y1, x2, y2):
    """
    Функция, размывающая маску за даным каналом и радиусом
    """

    image_width, image_height = image.size

    x1_1 = int(image_width * x1 / 100)
    y1_1 = int(image_height * y1 / 100)
    x2_2 = int(image_width * x2 / 100)
    y2_2 = int(image_height * y2 / 100)

    mask = (x1_1, y1_1, x2_2, y2_2)

    image_part_to_blur = image.crop(mask)

    if channel == "RGB":
        image_part_to_blur = image_part_to_blur.filter(GaussianBlur(radius=radius_my))
    else:
        r, g, b = image_part_to_blur.split()
        if channel == "R":
            r = r.filter(GaussianBlur(radius=radius_my))
        if channel == "G":
            g = g.filter(GaussianBlur(radius=radius_my))
        if channel == "B":
            b = b.filter(GaussianBlur(radius=radius_my))
        image_part_to_blur = Image.merge("RGB", (r, g, b))
    image.paste(image_part_to_blur, mask)

    return image

if __name__ == '__main__':
    bot.polling(none_stop=True)