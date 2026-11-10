import os
import shutil
import warnings

import pandas as pd
from PIL import Image
from matplotlib import pyplot as plt
from numpy import asarray

from consts import data_path, perfect_size, crawled_data_sub_dirs, crawled_data_path, encoded_chars, image_width, \
    image_height
from keras.preprocessing.image import img_to_array


def data_as_df():
    df = pd.DataFrame(os.listdir(data_path), columns=["img_name"])
    df["label"] = df["img_name"].str[-5]
    return df


def show_data_frequency():
    return data_as_df().groupby(["label"]).count()


def crop_image(img, wished_size=perfect_size):
    size = img.size[0]
    if size < wished_size:
        warnings.warn("Too small image...")
        return img

    diff = size - wished_size
    half_diff = diff / 2

    return img.crop((half_diff, half_diff, size - half_diff, size - half_diff))


def prepare_data():
    """
    Preparing data, load all images to a new folder and crop them to get
    the needed part only load all images to a new folder
    """
    if os.path.exists(data_path):
        shutil.rmtree(data_path)
    os.mkdir(data_path)

    for sub_dir in crawled_data_sub_dirs:

        images_names = os.listdir(f"{crawled_data_path}/{sub_dir}")
        if len(images_names) > 6:
            warnings.warn(f"Too many images here in {sub_dir}, taking only the first six...")
            images_names = images_names[:6]

        for img in images_names:

            original_path = f"{crawled_data_path}/{sub_dir}/{img}"
            image = Image.open(original_path)
            # crop image to remove any extra unnecessary parts
            image = crop_image(image)
            # shrink image to make it smaller and train faster. I'm not sure though,
            # see: https://stackoverflow.com/questions/41842310/does-image-size-matter-when-training-with-tensorflow
            image = image.resize((image_height, image_width))
            image.save(f"{data_path}/{sub_dir}_{img}")


def load_data():
    # sort list first
    imgs = os.listdir(data_path)
    imgs.sort()
    data = []
    labels = []

    for img in imgs:
        data.append(img_to_array(Image.open(f"{data_path}/{img}"))[..., :3])
        labels.append(img[-5])

    data = asarray(data)
    encoded_labels = asarray([encoded_chars[label] for label in labels])
    return imgs, data, encoded_labels


def fig_model_accuracy_over_epochs(history, epochs):
    fig = plt.figure()
    ax = fig.add_subplot()
    ax.set_xlim([0, epochs - 1])
    ax.set_ylim([0, 1])
    ax.set_ylabel('Accuracy')
    ax.set_xlabel('Epoch')
    ax.plot(history.history['accuracy'], label='accuracy')
    ax.plot(history.history['val_accuracy'], label='val_accuracy')
    ax.legend()
    ax.set_title("Accuracy over Epochs")

    return fig
