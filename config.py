import os

class Config:
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    STATIC_PATH = os.environ.get("STATIC_PATH")
    WEIGHTS_PATH = os.environ.get("WEIGHTS_PATH")
    IMAGE_PATH = os.environ.get("IMAGE_PATH")
