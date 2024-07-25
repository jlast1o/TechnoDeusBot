import os
from pkgutil import get_data
import shutil
import pandas as pd
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.types import InputMediaPhoto


API_TOKEN = '7067090296:AAExj1Z-u-L_0foR8-Ktjv1CdCQ5UgUtSP0'
CHAT_ID = '-1002214136948'

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Загружаем таблицу с моделями и памятью телефонов
df_dict = pd.read_excel('phones.xlsx', sheet_name=None)

# Создаем клавиатуру с кнопками категорий устройств
device_categories_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
device_categories_keyboard.add(KeyboardButton('iPhone'))
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
    repair_status = State()
    repair_details = State()
    photos = State()
    confirm_update = State()
    contact_choice = State()

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await Form.brand.set()
    await message.reply("Привет! Это Technodeus. Мы поможем вам оценить твой девайс, который можно сдать нам в Trade-in, чтобы получить хорошую скидку на новое устройство! В случае, если ты не знаешь ответ на какой-либо из следующих вопросов - не переживай, с тобой свяжется менеджер и поможет уточнить все детали\nВыберите категорию устройства:", reply_markup=device_categories_keyboard)

@dp.message_handler(commands=['Technoadmin'], state='*')
async def admin_panel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.reply("Добро пожаловать в админку. Вы можете обновить таблицу, отправив новый файл.", reply_markup=admin_keyboard)


@dp.message_handler(lambda message: message.text in ['iPhone', 'Mac', 'Apple Watch', 'Google Pixel', 'Samsung', 'Другое'], state=Form.brand)
async def select_device_category(message: types.Message, state: FSMContext):
    selected_category = message.text
    await state.update_data(brand=selected_category)
    if selected_category == 'Другое':
        await Form.model.set()
        await message.reply("Напишите полное название модели своего устройства:", reply_markup=types.ReplyKeyboardRemove())
    else:
        models = []
        for df in df_dict.values():
            models.extend(df[df['Модель'].str.startswith(selected_category)]['Модель'].unique())
        models = list(set(models))  # Remove duplicates
        models_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        for model in models:
            models_keyboard.add(KeyboardButton(model))
        models_keyboard.add(KeyboardButton('Моей модели нет'))
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
        await message.reply("Напишите конфигурацию памяти своего устройства:", reply_markup=types.ReplyKeyboardRemove())
    else:
        available_memories = []
        for sheet_name, df in df_dict.items():
            if 'Модель' in df.columns:
                model_row = df[df['Модель'] == selected_model]
                if not model_row.empty:
                    non_empty_columns = model_row.dropna(axis=1).columns[1:]  # Skip the first column (Модель)
                    available_memories.extend(non_empty_columns)
        available_memories = list(set(available_memories))  # Remove duplicates
        memory_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        for memory in available_memories:
            memory_keyboard.add(KeyboardButton(memory))
        memory_keyboard.add(KeyboardButton('Вернуться в меню'))
        await Form.memory.set()
        if message.text == "Моей модели нет" and user_data['brand'] == "Apple Watch":
            await message.reply("Выберите размер экрана для вашего устройства:", reply_markup=types.ReplyKeyboardRemove())
        elif message.text == "Моей модели нет" and user_data['brand'] != "Apple Watch":
            await message.reply("Выберите конфигурацию памяти для вашего устройства:", reply_markup=types.ReplyKeyboardRemove())
        elif message.text != "Моей модели нет" and user_data['brand'] == "Apple Watch":
            await message.reply(f"Выберите размер экрана для {selected_model}:",reply_markup=memory_keyboard)
        else:
            await message.reply(f"Выберите конфигурацию памяти для {selected_model}:", reply_markup=memory_keyboard)

@dp.message_handler(state=Form.memory)
async def select_sim_version(message: types.Message, state: FSMContext):
    if message.text == 'Вернуться в меню':
        await return_to_menu(message, state)
        return
    selected_memory = message.text
    await state.update_data(memory=selected_memory)
    user_data = await state.get_data()
    if user_data['brand'] == 'iPhone':
        sim_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        sim_keyboard.add(KeyboardButton('e-sim'))
        sim_keyboard.add(KeyboardButton('e-sim+micro-sim'))
        sim_keyboard.add(KeyboardButton('2 micro-sim'))
        sim_keyboard.add(KeyboardButton('Вернуться в меню'))
        await Form.sim.set()
        await message.reply("Укажите версию сим-карты вашего iPhone:", reply_markup=sim_keyboard)
    else:
        await Form.color.set()
        await message.reply("Напишите цвет своего устройства:", reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(state=Form.sim)
async def select_color(message: types.Message, state: FSMContext):
    if message.text == 'Вернуться в меню':
        await return_to_menu(message, state)
        return
    selected_sim = message.text
    await state.update_data(sim=selected_sim)
    await Form.color.set()
    await message.reply("Напишите цвет своего устройства:", reply_markup=types.ReplyKeyboardRemove())

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters import Text

@dp.message_handler(state=Form.color)
async def select_battery(message: types.Message, state: FSMContext):
    if message.text == 'Вернуться в меню':
        await return_to_menu(message, state)
        return
    selected_color = message.text
    await state.update_data(color=selected_color)
    await Form.battery.set()
    skip_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    skip_keyboard.add(KeyboardButton('Пропустить'))
    skip_keyboard.add(KeyboardButton('Вернуться в меню'))
    await message.reply("Напишите, какая сейчас емкость аккумулятора вашего устройства (напишите просто число, проценты указывать не нужно): \nПроцент емкости аккумулятора обычно расположен в настройках телефоне в разделе «Батарея»/«Аккумулятор»", reply_markup=skip_keyboard)

@dp.message_handler(state=Form.battery)
async def select_condition(message: types.Message, state: FSMContext):
    if message.text == 'Пропустить':
        condition_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        condition_keyboard.add(KeyboardButton('Отличное'))
        condition_keyboard.add(KeyboardButton('Хорошее'))
        condition_keyboard.add(KeyboardButton('Удовлетворительное'))
        condition_keyboard.add(KeyboardButton('Вернуться в меню'))
        await Form.condition.set()
        await message.reply("Оцените состояние своего устройства: \n• Отличное (как новый) \n• Хорошее (есть небольшие царапины) \n• Удовлетворительное (есть царапины, сколы или любые другие серьезные дефекты)", reply_markup=condition_keyboard)
        return 
    if message.text == 'Вернуться в меню':
        await return_to_menu(message, state)
        return
    if not message.text.isdigit():
        await message.reply("Пожалуйста, введите числовое значение для емкости аккумулятора.")
        return
    battery_capacity = message.text
    await state.update_data(battery=battery_capacity)
    condition_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    condition_keyboard.add(KeyboardButton('Отличное'))
    condition_keyboard.add(KeyboardButton('Хорошее'))
    condition_keyboard.add(KeyboardButton('Удовлетворительное'))
    condition_keyboard.add(KeyboardButton('Вернуться в меню'))
    await Form.condition.set()
    await message.reply("Оцените состояние своего устройства: \n• Отличное (как новый) \n• Хорошее (есть небольшие царапины) \n• Удовлетворительное (есть царапины, сколы или любые другие серьезные дефекты)", reply_markup=condition_keyboard)


@dp.message_handler(state=Form.condition)
async def select_completeness(message: types.Message, state: FSMContext):
    if message.text == 'Вернуться в меню':
        await return_to_menu(message, state)
        return
    condition = message.text
    await state.update_data(condition=condition)
    user_data = await state.get_data()
    completeness_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    completeness_keyboard.add(KeyboardButton('Полная'))
    completeness_keyboard.add(KeyboardButton('Неполная'))
    completeness_keyboard.add(KeyboardButton('Вернуться в меню'))
    await Form.completeness.set()
    if (user_data['brand'] == 'Apple Watch'):
        await message.reply("У вас есть полный комплект устройства (коробка, кабель и т.п.)?", reply_markup=completeness_keyboard)
    else:
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
        await message.reply("Подскажите, что отсутствует в комплекте?", reply_markup=types.ReplyKeyboardRemove())
    else:
        await Form.repair_status.set()
        yes_no_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        yes_no_keyboard.add(KeyboardButton('Да'))
        yes_no_keyboard.add(KeyboardButton('Нет'))
        
        await message.reply("Был ли ваш девайс в ремонте? (да/нет)", reply_markup=yes_no_keyboard)

@dp.message_handler(state=Form.completeness_details)
async def request_repair_status(message: types.Message, state: FSMContext):
    if message.text == 'Вернуться в меню':
        await return_to_menu(message, state)
        return
    completeness_details = message.text
    await state.update_data(completeness_details=completeness_details)
    await Form.repair_status.set()
    
    # Создаем клавиатуру с кнопками "Да" и "Нет"
    yes_no_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    yes_no_keyboard.add(KeyboardButton('Да'))
    yes_no_keyboard.add(KeyboardButton('Нет'))
    
    await message.reply("Был ли ваш девайс в ремонте? (да/нет)", reply_markup=yes_no_keyboard)

@dp.message_handler(state=Form.repair_status)
async def request_repair_details(message: types.Message, state: FSMContext):
    if message.text.lower() == 'да':
        await Form.repair_details.set()
        await message.reply("Подскажите, что конкретно вы ремонтировали?", reply_markup=types.ReplyKeyboardRemove())
    else:
        conf_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        conf_keyboard.add(KeyboardButton('Пропустить'))
        await Form.photos.set()
        await message.reply("Пожалуйста, отправьте фотографии вашего устройства. Фото очень помогают нам точнее оценить состояние вашего устройства, чтобы предложить лучшую стоимость для вас, поэтому очень просим тебя не пропускать этот пункт🙂", reply_markup=conf_keyboard)

@dp.message_handler(state=Form.repair_details)
async def request_photos(message: types.Message, state: FSMContext):
    repair_details = message.text
    await state.update_data(repair_details=repair_details)
    conf_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    conf_keyboard.add(KeyboardButton('Пропустить'))
    await Form.photos.set()
    await message.reply("Пожалуйста, отправьте фотографии вашего устройства. Фото очень помогают нам точнее оценить состояние вашего устройства, чтобы предложить лучшую стоимость для вас, поэтому очень просим тебя не пропускать этот пункт🙂", reply_markup=conf_keyboard)

@dp.message_handler(lambda message: message.text.lower() == 'пропустить', state=Form.photos)
async def skip_photos(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    
    if user_data['brand'] == 'Другое' or (user_data['model'] == "Моей модели нет"):
        await message.reply("Нам нужно чуть больше времени, чтоб оценить твой девайс, в ближайшее время вернемся с ответом.")
        contact_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        contact_keyboard.add(KeyboardButton('Да, свяжитесь со мной'))
        contact_keyboard.add(KeyboardButton('Спасибо, пока подумаю'))
        await Form.contact_choice.set()
    else:
        try:
            model = user_data['model']
            memory = user_data['memory']
            price = None
            
            # Iterate through all sheets to find the price
            for sheet_name, df in df_dict.items():
                if 'Модель' in df.columns and memory in df.columns:
                    price_row = df[df['Модель'] == model]
                    if not price_row.empty:
                        price = price_row[memory].values[0]
                        break

            if price is not None:
                await message.reply(f"Вот примерная оценка стоимости твоего девайса: {price} рублей. Точнее оценить стоимость может лично менеджер, если тебе это интересно, мы этим займемся и ближайшее время свяжемся с тобой.")
        except Exception as e:
            await message.reply("Нам нужно чуть больше времени, чтоб оценить твой девайс, в ближайшее время вернемся с ответом.")
            
    contact_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    contact_keyboard.add(KeyboardButton('Да, свяжитесь со мной'))
    contact_keyboard.add(KeyboardButton('Спасибо, пока подумаю'))
    await Form.contact_choice.set()
    await message.reply("Выберите, нужно ли с вами связаться:", reply_markup=contact_keyboard)

@dp.message_handler(content_types=['photo'], state=Form.photos)
async def handle_photos(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    photos = user_data.get('photos', [])
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)
    
    # Создаем клавиатуру с кнопками "Подтвердить" и "Отправить заново"
    confirm_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    confirm_keyboard.add(KeyboardButton('Подтвердить'))
    confirm_keyboard.add(KeyboardButton('Отправить заново'))
    
    await message.reply("Фото получено. Отправьте еще фото или нажмите 'Подтвердить', чтобы завершить.", reply_markup=confirm_keyboard)

@dp.message_handler(lambda message: message.text.lower() == 'подтвердить', state=Form.photos)
async def confirm_update(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    
    if user_data['brand'] == 'Другое' or (user_data['model'] == "Моей модели нет"):
        await message.reply("Нам нужно чуть больше времени, чтоб оценить твой девайс, в ближайшее время вернемся с ответом.")
        contact_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        contact_keyboard.add(KeyboardButton('Да, свяжитесь со мной'))
        contact_keyboard.add(KeyboardButton('Спасибо, пока подумаю'))
        await Form.contact_choice.set()\

    else:
        try:
            model = user_data['model']
            memory = user_data['memory']
            price = None
            
            # Iterate through all sheets to find the price
            for sheet_name, df in df_dict.items():
                if 'Модель' in df.columns and memory in df.columns:
                    price_row = df[df['Модель'] == model]
                    if not price_row.empty:
                        price = price_row[memory].values[0]
                        break

            if price is not None:
                await message.reply(f"Вот примерная оценка стоимости твоего девайса: {price} рублей. Точнее оценить стоимость может лично менеджер, если тебе это интересно, мы этим займемся и ближайшее время свяжемся с тобой.")
        except Exception as e:
            await message.reply("Нам нужно чуть больше времени, чтоб оценить твой девайс, в ближайшее время вернемся с ответом.")
            
    contact_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    contact_keyboard.add(KeyboardButton('Да, свяжитесь со мной'))
    contact_keyboard.add(KeyboardButton('Спасибо, пока подумаю'))
    await Form.contact_choice.set()
    await message.reply("Выберите, нужно ли с вами связаться:", reply_markup=contact_keyboard)


@dp.message_handler(lambda message: message.text.lower() == 'отправить заново', state=Form.photos)
async def resend_photo(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    photos = user_data.get('photos', [])
    if photos:
        photos.pop()  # Удаляем последнюю фотографию из списка
    await state.update_data(photos=photos)
    await message.reply("Пожалуйста, отправьте фотографии вашего устройства заново.", reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(state=Form.contact_choice)
async def handle_contact_choice(message: types.Message, state: FSMContext):
    if message.text.lower() == 'да, свяжитесь со мной':
        user_data = await state.get_data()
        username = message.from_user.username

        caption_text = (
            f"Новая заявка от пользователя @{username}:\n"
            f"Бренд: {user_data['brand']}\n"
            f"Модель: {user_data['model']}\n"
            f"Память: {user_data['memory']}\n"
            f"Цвет: {user_data['color']}\n"
            f"Сим-карта: {user_data.get('sim', 'N/A')}\n"
            f"Емкость аккумулятора: {user_data.get('battery', 'N/A')}\n"
            f"Состояние: {user_data['condition']}\n"
            f"Комплектность: {user_data['completeness']}\n"
            f"Детали комплектности: {user_data.get('completeness_details', 'N/A')}\n"
            f"Ремонт: {user_data.get('repair_status', 'N/A')}\n"
            f"Детали ремонта: {user_data.get('repair_details', 'N/A')}\n"
        )
        photos = user_data.get('photos', [])
        if photos:
            media_group = [InputMediaPhoto(photo, caption=caption_text if i == 0 else '') for i, photo in enumerate(photos)]
            await bot.send_media_group(CHAT_ID, media_group)
        else:
            await bot.send_message(CHAT_ID, caption_text)

        await message.reply("Спасибо! Ваша заявка принята. Мы свяжемся с вами в ближайшее время.", reply_markup=device_categories_keyboard)
    else:
        user_data = await state.get_data()
        username = message.from_user.username

        caption_text = (
            f"Новая заявка от пользователя @{username}:\n"
            f"Бренд: {user_data['brand']}\n"
            f"Модель: {user_data['model']}\n"
            f"Память: {user_data['memory']}\n"
            f"Цвет: {user_data['color']}\n"
            f"Сим-карта: {user_data.get('sim', 'N/A')}\n"
            f"Емкость аккумулятора: {user_data.get('battery', 'N/A')}\n"
            f"Состояние: {user_data['condition']}\n"
            f"Комплектность: {user_data['completeness']}\n"
            f"Детали комплектности: {user_data.get('completeness_details', 'N/A')}\n"
            f"Ремонт: {user_data.get('repair_status', 'N/A')}\n"
            f"Детали ремонта: {user_data.get('repair_details', 'N/A')}\n"
        )
        photos = user_data.get('photos', [])
        if photos:
            media_group = [InputMediaPhoto(photo, caption=caption_text if i == 0 else '') for i, photo in enumerate(photos)]
            await bot.send_media_group(CHAT_ID, media_group)
        else:
            await bot.send_message(CHAT_ID, caption_text)
    await state.finish()

    await return_to_menu(message, state)

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
    await Form.brand.set()  # Устанавливаем начальное состояние
    
    await message.reply("Вы вернулись в меню. Выберите категорию устройства:", reply_markup=device_categories_keyboard)

@dp.message_handler(lambda message: message.text == 'Вернуться в меню', state='*')
async def handle_return_to_menu(message: types.Message, state: FSMContext):
    await return_to_menu(message, state)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
