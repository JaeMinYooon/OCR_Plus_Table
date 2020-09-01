import tensorflow as tf
from tensorflow import keras
import tensorflow_datasets as tfds
from tensorflow.keras import layers
import tensorflow_addons as tfa

import numpy as np
import os
import matplotlib.pyplot as plt
from glob import glob
import pathlib
import cv2

print(tf.__version__)
print(tf.test.gpu_device_name())

IMG_SIZE = 224

def load_model(path):
    model = keras.models.load_model(path)
    return model

def decode_image(filename):
    image = tf.io.read_file(filename)
    image = tf.image.decode_jpeg(image, channels=1)
    image = tf.image.convert_image_dtype(image, tf.float32)
    # image = 1 - image
    image = tf.image.resize(image, [IMG_SIZE, IMG_SIZE])

    parts = tf.strings.split(filename, os.sep)
    label = tf.strings.split(parts[-1], ".jpg")[0]

    return image.numpy(), label

def predicts(dir_path, model):
    test_dir = pathlib.Path(dir_path)
    test_ds = tf.data.Dataset.list_files(str(test_dir / "*.jpg"), shuffle=False)

    test = {
        'test_imaegs': [],
        'test_labels': []
    }

    for path in test_ds:
        img, label = decode_image(path)
        test['test_images.'].append(img)
        test['test_labels'].append(label)

    test_images = np.array(test_images)

    predictions = model.predict_classes(test_images)

    print(predictions)

    for j in range(int(len(test_images) / 5)):
        plt.figure(figsize=(10, 10))
        for i in range(5):
            ax = plt.subplot(1, 5, i + 1)
            temp = tf.convert_to_tensor(test_images[i + j * 5])
            temp = tf.image.grayscale_to_rgb(temp)
            plt.imshow(temp)
            test['test_labels'].append(class_names[predictions[i + j * 5]])
            plt.title(print(class_names[predictions[i + j * 5]], end=" "))
            plt.axis("off")
        plt.show()

    return test