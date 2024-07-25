import os
import shutil
import pandas as pd
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

API_TOKEN = '7067090296:AAExj1Z-u-L_0foR8-Ktjv1CdCQ5UgUtSP0'
CHAT_ID = '-1002214136948'

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Загружаем таблицу с моделями и памятью телефонов
df_dict = pd.read_excel('phones.xlsx')

# Создаем клавиатуру с кнопками категорий устройств
device_categories_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
device_categories_keyboard.add(KeyboardButton('IPhone'))
device_categories_keyboard.add(KeyboardButton('Mac'))
device_categories_keyboard.add(KeyboardButton('Apple Watch'))
device_categories_keyboard.add(KeyboardButton('Google Pixel'))
device_categories_keyboard.add(KeyboardButton('Samsung'))
device_categories_keyboard.add(KeyboardButton('Другое'))
device_categories_keyboard.add(KeyboardButton('Вернуться в меню'))

# Создаем клавиатуру для админки
admin_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
admin_keyboard.add(KeyboardButton('Обновить таблицу'))
admin_keyboard.add(KeyboardButton('Вернуться в меню'))

class Form(StatesGroup):
    brand = State()
    model = State()
    memory = State()
    color = State()
    sim = State()
    battery = State()
    condition = State()
    completeness = State()
    completeness_details = State()
    repair_details = State()
    photos = State()
    confirm_update = State()

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await Form.brand.set()
    await message.reply("Привет! Это Technodeus. Мы поможем тебе оценить твой девайс, который можно сдать нам в Trade-in, чтобы получить хорошую скидку на новое устройство!\nВыберите категорию устройства:", reply_markup=device_categories_keyboard)

@dp.message_handler(commands=['Technoadmin'])
async def admin_panel(message: types.Message):
    await message.reply("Добро пожаловать в админку. Вы можете обновить таблицу, отправив новый файл.", reply_markup=admin_keyboard)

@dp.message_handler(lambda message: message.text in ['IPhone', 'Mac', 'Apple Watch', 'Google Pixel', 'Samsung', 'Другое'], state=Form.brand)
async def select_device_category(message: types.Message, state: FSMContext):
    selected_category = message.text
    await state.update_data(brand=selected_category)
    if selected_category == 'Другое':
        await Form.model.set()
        await message.reply("Напишите полное название модели своего устройства:")
    else:
        models = []
        for df in df_dict.values():
            models.extend(df[df['Модель'].str.startswith(selected_category)]['Модель'].unique())
        models = list(set(models))  # Remove duplicates
        models_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        for model in models:
            models_keyboard.add(KeyboardButton(model))
        models_keyboard.add(KeyboardButton('Вернуться в меню'))
        await Form.model.set()
        await message.reply(f"Выберите модель {selected_category}:", reply_markup=models_keyboard)


@dp.message_handler(state=Form.model)
async def select_memory(message: types.Message, state: FSMContext):
    if message.text == 'Вернуться в меню':
        await return_to_menu(message, state)
        return
    selected_model = message.text
    await state.update_data(model=selected_model)
    user_data = await state.get_data()
    if user_data['brand'] == 'Другое':
        await Form.memory.set()
        await message.reply("Напишите конфигурацию памяти своего устройства:")
    else:
        available_memories = df[df['Модель'] == selected_model].dropna(axis=1).columns[1:]  # Убираем пустые столбцы и первый столбец с моделями
        memory_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        for memory in available_memories:
            memory_keyboard.add(KeyboardButton(memory))
        memory_keyboard.add(KeyboardButton('Вернуться в меню'))
        await Form.memory.set()
        await message.reply(f"Выберите конфигурацию памяти для {selected_model}:", reply_markup=memory_keyboard)

@dp.message_handler(state=Form.memory)
async def select_sim_version(message: types.Message, state: FSMContext):
    if message.text == 'Вернуться в меню':
        await return_to_menu(message, state)
        return
    selected_memory = message.text
    await state.update_data(memory=selected_memory)
    user_data = await state.get_data()
    if user_data['brand'] == 'IPhone':
        sim_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        sim_keyboard.add(KeyboardButton('e-sim'))
        sim_keyboard.add(KeyboardButton('e-sim+micro-sim'))
        sim_keyboard.add(KeyboardButton('2 micro-sim'))
        sim_keyboard.add(KeyboardButton('Вернуться в меню'))
        await Form.sim.set()
        await message.reply("Укажите версию сим-карты вашего iPhone:", reply_markup=sim_keyboard)
    else:
        await Form.color.set()
        await message.reply("Напишите цвет своего устройства:")

@dp.message_handler(state=Form.sim)
async def select_color(message: types.Message, state: FSMContext):
    if message.text == 'Вернуться в меню':
        await return_to_menu(message, state)
        return
    selected_sim = message.text
    await state.update_data(sim=selected_sim)
    await Form.color.set()
    await message.reply("Напишите цвет своего устройства:")

@dp.message_handler(state=Form.color)
async def select_battery(message: types.Message, state: FSMContext):
    if message.text == 'Вернуться в меню':
        await return_to_menu(message, state)
        return
    selected_color = message.text
    await state.update_data(color=selected_color)
    await Form.battery.set()
    await message.reply("Напишите, какая сейчас емкость аккумулятора вашего устройства (напишите просто число, проценты указывать не нужно):")

@dp.message_handler(state=Form.battery)
async def select_condition(message: types.Message, state: FSMContext):
    if message.text == 'Вернуться в меню':
        await return_to_menu(message, state)
        return
    battery_capacity = message.text
    await state.update_data(battery=battery_capacity)
    condition_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    condition_keyboard.add(KeyboardButton('Отличное'))
    condition_keyboard.add(KeyboardButton('Хорошее'))
    condition_keyboard.add(KeyboardButton('Удовлетворительное'))
    condition_keyboard.add(KeyboardButton('Вернуться в меню'))
    await Form.condition.set()
    await message.reply("Оцените состояние своего устройства:", reply_markup=condition_keyboard)

@dp.message_handler(state=Form.condition)
async def select_completeness(message: types.Message, state: FSMContext):
    if message.text == 'Вернуться в меню':
        await return_to_menu(message, state)
        return
    condition = message.text
    await state.update_data(condition=condition)
    completeness_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    completeness_keyboard.add(KeyboardButton('Полная'))
    completeness_keyboard.add(KeyboardButton('Неполная'))
    completeness_keyboard.add(KeyboardButton('Вернуться в меню'))
    await Form.completeness.set()
    await message.reply("У вас есть полный комплект устройства (коробка, кабель, наушники и т.п.)?", reply_markup=completeness_keyboard)

@dp.message_handler(state=Form.completeness)
async def select_completeness_details(message: types.Message, state: FSMContext):
    if message.text == 'Вернуться в меню':
        await return_to_menu(message, state)
        return
    completeness = message.text
    await state.update_data(completeness=completeness)
    if completeness == 'Неполная':
        await Form.completeness_details.set()
        await message.reply("Подскажите, что отсутствует в комплекте?")
    else:
        await request_repair_details(message, state)

@dp.message_handler(state=Form.completeness_details)
async def request_repair_details(message: types.Message, state: FSMContext):
    if message.text == 'Вернуться в меню':
        await return_to_menu(message, state)
        return
    completeness_details = message.text
    await state.update_data(completeness_details=completeness_details)
    await Form.repair_details.set()
    await message.reply("Опишите проблему вашего устройства:")

@dp.message_handler(state=Form.repair_details)
async def request_photos(message: types.Message, state: FSMContext):
    if message.text == 'Вернуться в меню':
        await return_to_menu(message, state)
        return
    repair_details = message.text
    await state.update_data(repair_details=repair_details)
    await Form.photos.set()
    await message.reply("Пожалуйста, отправьте фотографии вашего устройства или нажмите 'Пропустить'.", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Пропустить')).add(KeyboardButton('Вернуться в меню')))

@dp.message_handler(content_types=['photo'], state=Form.photos)
async def handle_photos(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    user_id = message.from_user.id
    photos = user_data.get('photos', [])
    photo_message_id = message.message_id
    photos.append(photo_message_id)
    await state.update_data(photos=photos)
    await message.reply("Фотография добавлена. Отправьте еще фотографии или нажмите 'Пропустить'.")

@dp.message_handler(lambda message: message.text == 'Пропустить', state=Form.photos)
async def skip_photos(message: types.Message, state: FSMContext):
    await Form.confirm_update.set()
    await message.reply("Вы хотите подтвердить обновление информации? (да/нет)")

@dp.message_handler(state=Form.confirm_update)
async def confirm_update(message: types.Message, state: FSMContext):
    if message.text.lower() == 'да':
        user_data = await state.get_data()
        photos = user_data.get('photos', [])
        for photo_message_id in photos:
            await bot.delete_message(chat_id=message.chat.id, message_id=photo_message_id)
        await bot.send_message(CHAT_ID, f"Информация о гаджете:\n{user_data}\nID пользователя: {message.from_user.id}")
        await state.finish()
        await message.reply("Информация обновлена и фотографии удалены.")
    else:
        await state.finish()
        await message.reply("Обновление отменено.")

@dp.message_handler(lambda message: message.text == 'Обновить таблицу')
async def update_table(message: types.Message):
    await message.reply("Пожалуйста, отправьте новый файл 'phones.xlsx'.")

@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def handle_new_table(message: types.Message):
    document = message.document
    if document.file_name == 'phones.xlsx':
        await document.download(destination_file='phones.xlsx')
        global df
        df = pd.read_excel('phones.xlsx')
        await message.reply("Таблица успешно обновлена.")
    else:
        await message.reply("Пожалуйста, отправьте файл с именем 'phones.xlsx'.")

async def return_to_menu(message: types.Message, state: FSMContext):
    await state.finish()
    await message.reply("Вы вернулись в меню.", reply_markup=device_categories_keyboard)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
