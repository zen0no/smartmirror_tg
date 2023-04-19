from aiogram.dispatcher.filters.state import State, StatesGroup 


class ImageProcess(StatesGroup):
    clothes_image_choice = State()
    human_image_load = State()
