import os
import warnings

import numpy as np
import tensorflow as tf
from PIL import Image
from keras.src.utils import img_to_array

from consts import allowed_chars, image_height, image_width, data_path, models_path
from neural_network.data_helper import crop_image


def decode_model_result(res):
    return allowed_chars[np.argmax(res)]


def prepare_image_4_prediction(img):
    image = crop_image(img)
    image = image.resize((image_height, image_width))
    image = img_to_array(image)[..., :3]
    image = np.expand_dims(image, 0)
    return image


def get_model(model_name=""):
    models = os.listdir(models_path)
    models.sort()
    if len(models) == 0:
        raise OSError("No models available..")
    if model_name == "":
        model_name = models[-1]
        print(f"No model name was specified, getting the newest one {model_name}")
    return tf.keras.models.load_model(f'{models_path}/{model_name}')

def exp(nr):
    global imgs, model
    img = Image.open(f"{data_path}/{imgs[-nr]}")
    img_arr = img_to_array(img)[..., :3]
    img_arr_exp = np.expand_dims(img_arr, 0)
    img.show()
    res = allowed_chars[np.argmax(model.predict(img_arr_exp))]
    return imgs[-nr], res