import os

from io import BytesIO
from PIL import Image
from aiogram import types

from LookGenerator.main import process_image, load_models

class ImagePipeline:

    def __init__(self, config):
        self.static_path = config.STATIC_PATH
        self.models = load_models(config.WEIGHTS_PATH)

    def get_labels_list(self,):
        _dir_list = os.listdir(self.static_path)
        labels = sorted([x.split('.')[0] for x in _dir_list], key=lambda x: int(x))
        return labels
    

    def get_mediagroup(self):
        images = [Image.open(os.path.join(self. static_path, x)) for x in os.listdir(self.static_path)]
        labels = self.get_labels_list()

        media = types.MediaGroup()

        for image, label in sorted(zip(images, labels), key=lambda x: int(x[1])):
            bio = BytesIO()
            
            image.save(bio, "JPEG")
            bio.seek(0)
            media.attach_photo(types.InputMediaPhoto(bio, caption=label))
        
        return  media



    def process_image(self, image: BytesIO, choosed_label: str):

        image.seek(0)
        pil_image = Image.open(image)
        clothes_image = Image.open(os.path.join(self.static_path, choosed_label + '.jpg'))

        processed_image = process_image(pil_image, clothes_image, self.models)

        result = BytesIO()

        processed_image.save(result, "JPEG")
        result.seek(0)
        return result