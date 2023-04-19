import logging
from .config import Config
from .form import ImageProcess
from .image_pipeline import ImagePipeline

import os

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import reply_keyboard
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage


import time
from io import BytesIO
# Setting up enviroment

config = Config()


logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_TOKEN)
bot.parse_mode = 'HTML'
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)


pipeline = ImagePipeline(config)

# Markups for replying

main_markup =  reply_keyboard.ReplyKeyboardRemove()
def label_markup(labels_list):
    markup = reply_keyboard.ReplyKeyboardMarkup(resize_keyboard=True)
    labels_count = len(labels_list)
    for i in range(0, labels_count, 3):
        if i + 3 < labels_count:
            markup.row(
                *[reply_keyboard.KeyboardButton(x) for x in labels_list[i:i+3]]
            )
        else:
            markup.row(
                *[reply_keyboard.KeyboardButton(x) for x in labels_list[i:]]
            )
    return markup


@dp.message_handler(commands=["start"])
@dp.message_handler(Text(equals="старт", ignore_case=True))
async def bot_start(message: types.Message):
    await bot.send_media_group(message.chat.id, pipeline.get_mediagroup())
    await bot.send_message(message.chat.id, 
                           """Выберите вариант одежды, который хотите примерить""", reply_markup=label_markup(pipeline.get_labels_list()))
    await ImageProcess.clothes_image_choice.set()
 
    
    

@dp.message_handler(commands=["info"])
@dp.message_handler(Text(equals="О нас", ignore_case=True))
async def about_us(message: types.Message):
    photo = open(os.path.join(config.IMAGE_PATH, "info.jpg"), "rb")
    await bot.send_photo(message.chat.id, photo=photo, caption=
                           """Кто мы?

Умное Зеркало - проект по созданию виртуальных примерочных, которые позволят покупателям не тратить время на примерку одежды, а компаниям - повысить выручку и привлечь новых клиентов.

Наша миссия - сделать процесс примерки удобным как для покупателя, так и для магазина.

На данный момент команда проекта насчитывает 19 человек, среди которых есть разработчики, дизайнеры, маркетологи и финансисты.
Нам требуются:
Разработчики: ML-инженеры, Python dev для создания Tg бота
Фронтендеры - для вёрстки сайта
3D-дизайнеры - для работы с моделями одежды
Копирайтеры - для ведения социальных сетей проекта
Финансист

Если Вы хотите принять участие в стартапе, то пишите в личные сообщения нашему менеджеру по персоналу @mc_gru
                           """)







@dp.message_handler(lambda message: message.text and message.text in pipeline.get_labels_list(), state=ImageProcess.clothes_image_choice)
async def process_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['label'] = message.text
    
    await bot.send_message(message.chat.id, "Отлично! Теперь отправьте фотографию человека для обработки")
    await ImageProcess.next()


@dp.message_handler(state=ImageProcess.clothes_image_choice)
async def no_such_choice(message: types.Message, state: FSMContext):
    await bot.send_message(message.chat.id, "Нет такой опции")


@dp.message_handler(content_types=["photo"], state=ImageProcess.human_image_load)
async def get_image(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        photo = BytesIO()
        await bot.download_file_by_id(message.photo[-1].file_id, photo)
        processed_photo = pipeline.process_image(photo, data['label'])
        await bot.send_photo(message.chat.id, processed_photo)
    
    await bot.send_message(message.chat.id, """Фото обработано!

Для связи с нами введите команду /info
    """, reply_markup=main_markup) 
    await state.finish()
    

@dp.message_handler(state=ImageProcess.human_image_load)
async def photo_not_sent(message: types.Message, state: FSMContext):
    logging.info("No photo")
    await bot.send_message(message.chat.id, "Отправьте качественную фотографию человека для обработки", reply_markup=reply_keyboard.ReplyKeyboardRemove())


@dp.message_handler(state="*")
async def handle_other_message(message: types.Message):
    await bot.send_message(message.chat.id, "Я не знаю такой команды.\nВы можете ввести <code>/info</code> для связи с нами "
                           "или <code>/start</code> для того чтобы испытать бота", reply_markup=main_markup)