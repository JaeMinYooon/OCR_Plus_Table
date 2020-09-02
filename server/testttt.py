import tensorflow as tf
from tensorflow import keras
from tensorflow.python.client import device_lib

tf.config.list_physical_devices('GPU')
with tf.device('/GPU:0'):
    tf.debugging.set_log_device_placement(True)
    print("gpu사용중이다@@@@@@@@@@@@@@@@@@@@@@@")
# print(tf.__version__)
# print(tf.test.gpu_device_name())
# print(device_lib.list_local_devices())