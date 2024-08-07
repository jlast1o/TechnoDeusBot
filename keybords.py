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



mac_memory_keybord = ReplyKeyboardMarkup(resize_keyboard=True)
mac_memory_keybord.add(KeyboardButton('8/256'))
mac_memory_keybord.add(KeyboardButton('16/256'))
mac_memory_keybord.add(KeyboardButton('8/512'))
mac_memory_keybord.add(KeyboardButton('16/512'))

watches_size_keybord = ReplyKeyboardMarkup(resize_keyboard=True)
watches_size_keybord.add(KeyboardButton('38 mm'))
watches_size_keybord.add(KeyboardButton('40 mm'))
watches_size_keybord.add(KeyboardButton('41 mm'))
watches_size_keybord.add(KeyboardButton('42 mm'))
watches_size_keybord.add(KeyboardButton('44 mm'))
watches_size_keybord.add(KeyboardButton('45 mm'))
watches_size_keybord.add(KeyboardButton('48 mm'))

way_contact = ReplyKeyboardMarkup(resize_keyboard=True)
way_contact.add(KeyboardButton('WhatsApp'))
way_contact.add(KeyboardButton('По номеру телефона'))
way_contact.add(KeyboardButton('Telegram'))

# Создаем клавиатуру для админки
admin_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
admin_keyboard.add(KeyboardButton('Обновить таблицу'))
admin_keyboard.add(KeyboardButton('Вернуться в меню'))


one_more_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
one_more_keyboard.add(KeyboardButton('Начать оценку заново'))