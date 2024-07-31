from imports import *


# Создаем клавиатуру с кнопками брендов устройств
brands_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
brands_keyboard.add(KeyboardButton('Apple'))
brands_keyboard.add(KeyboardButton('Samsung'))
brands_keyboard.add(KeyboardButton('Google'))
brands_keyboard.add(KeyboardButton('Другое'))

phone_memory_keybord = ReplyKeyboardMarkup(resize_keyboard=True)
phone_memory_keybord.add(KeyboardButton('32Gb'))
phone_memory_keybord.add(KeyboardButton('64Gb'))
phone_memory_keybord.add(KeyboardButton('128Gb'))
phone_memory_keybord.add(KeyboardButton('256Gb'))
phone_memory_keybord.add(KeyboardButton('512Gb'))
phone_memory_keybord.add(KeyboardButton('1Tb'))

# Создаем клавиатуру для админки
admin_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
admin_keyboard.add(KeyboardButton('Обновить таблицу'))
admin_keyboard.add(KeyboardButton('Вернуться в меню'))