import tensorflow as tf
from tensorflow import keras

import numpy as np
import os
import matplotlib.pyplot as plt
import pathlib

# print(tf.__version__)
# print(tf.test.gpu_device_name())

IMG_SIZE = 224
# data_dir = pathlib.Path("/content/PTH/dataset/trainset")
# batch_size = 64
# IMG_SIZE = 224

class_names = ['0','1','2','3','4','5','6','7','8','9','가','각','간','감','강','같','개','거'
,'건','걷','검','것','게','격','겪','결','경','계','고','공','과','관','광','괴','교','구'
,'국','군','권','귄','규','그','극','근','금','급','기','긴','길','김','깊','까','께','꽃'
,'끼','낄','나','난','날','남','납','내','너','넘','네','녀','년','노','농','뉴','느','는'
,'늘','능','니','다','단','달','담','당','대','더','던','덜','데','도','독','동','되','된'
,'될','두','드','득','든','들','등','디','따','때','떠','또','라','란','람','랑','래','량'
,'러','런','럽','레','려','력','련','령','로','록','론','료','루','류','르','른','를','름'
,'리','린','릴','립','마','만','많','말','망','매','맨','며','면','명','모','목','못','무'
,'문','물','미','민','및','바','박','반','받','발','방','배','백','버','번','범','법','변'
,'별','병','보','복','본','부','북','분','불','비','뽑','쁘','사','산','살','삶','삼','상'
,'새','색','생','서','석','선','설','성','세','셀','소','속','송','수','순','술','스','슴'
,'습','승','시','식','신','실','싫','심','싶','아','안','않','알','았','액','야','약','양'
,'어','억','언','업','없','었','에','엑','여','역','연','열','였','영','예','오','온','올'
,'와','완','왜','외','요','용','우','욱','운','울','웃','워','원','월','위','유','육','윤'
,'율','으','은','을','음','응','의','이','인','일','읽','임','입','있','자','작','잖','잘'
,'잠','장','재','쟁','저','적','전','절','점','접','정','제','져','조','족','존','졸','종'
,'주','준','줄','중','줘','증','지','직','진','질','집','짝','차','찬','참','책','처','천'
,'철','청','체','초','총','최','추','축','출','충','측','치','컴','크','큼','키','타','태'
,'터','템','토','통','투','트','특','팀','팅','파','판','퍼','펭','편','평','포','표','품'
,'퓨','프','픈','피','필','하','학','한','할','함','합','항','해','했','행','향','험','헬'
,'혁','현','협','형','호','혹','화','확','환','활','회','효','후','훈','히']


def loadOCRmodel(path):
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

    return image.numpy()

def predicts(dir_path, model):
    test_dir = pathlib.Path(dir_path)
    test_ds = tf.data.Dataset.list_files(str(test_dir / "*.jpg"), shuffle=False)

    test = {
        'name': [],
        'label': []
    }
    test_images = list()

    # test_ds = list(test_dir.glob('*.jpg'))

    for path in test_ds:
        img = decode_image(path)
        test['name'].append(path)
        test_images.append(img)

    test_images = np.array(test_images)

    predictions = model.predict_classes(test_images)

    for prediction in predictions:
        test['label'].append(class_names[prediction])
    print(test)
    return test

# model = loadOCRmodel('./Model')
# print(predicts('../TextCrop/',model))