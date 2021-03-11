#!/usr/bin/env python3
# coding: utf8

from keras.preprocessing import image
from keras import backend as K

from vis.utils import utils
import numpy as np
import residual_network

import calibration
import os


# Modified dictionary values for categorical_labels method, see original in calibration.py
classes_dictionary_org = {'BAS': 0, 'EBO': 1, 'EOS': 3, 'KSC': 4, 'LYA': 5, 'LYT': 6, 'MMZ': 7, 'MOB': 8,
                          'MON': 9, 'MYB': 10, 'MYO': 11, 'NGB': 12, 'NGS': 13, 'PMB': 14, 'PMO': 15}

classes_dictionary = {value: key for key, value in classes_dictionary_org.items()}

abbreviation_dict = {'NGS': 'Neutrophil (segmented)',
                     'NGB': 'Neutrophil (band)',
                     'EOS': 'Eosinophil',
                     'BAS': 'Basophil',
                     'MON': 'Monocyte',
                     'LYT': 'Lymphocyte (typical)',
                     'LYA': 'Lymphocyte (atypical)',
                     'KSC': 'Smudge Cell',
                     'MYO': 'Myeloblast',
                     'PMO': 'Promyelocyte',
                     'MYB': 'Myelocyte',
                     'MMZ': 'Metamyelocyte',
                     'MOB': 'Monoblast',
                     'EBO': 'Erythroblast',
                     'PMB': 'Promyelocyte (bilobed)'}

img_width, img_height = 400, 400

if K.image_data_format() == 'channels_first':
    input_shape = (3, img_width, img_height)
else:
    input_shape = (img_width, img_height, 3)

weight_file_path = "../data/weights_fold2.hdf5"

model = residual_network.model
model.load_weights(weight_file_path)

model.compile(loss='categorical_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])

# number of images to feed into the network:
# n_fold1 = 3773, n_fold2 = 3630, n_fold3 = 3676, n_fold_4 = 3714, n_fold_5 = 3572
n = 3630
test_folder = '../images/fold2/'
test_files = os.listdir(test_folder)[:n]

inputs = []
for file_ in test_files:
    img = utils.load_img(test_folder + file_)
    img = (img[:, :, :3] * 1. / 255)

    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    inputs.append(x)

images = np.vstack(inputs)

preds_probs = model.predict(images, batch_size=32)
preds_probs = np.array(preds_probs)
preds_probs[:, 1] += preds_probs[:, 2]  # comment these two lines out
preds_probs = np.delete(preds_probs, 2, 1)  # for temperature scaling


def categorical_labels():
    # temp_tf.py doesn't take one-hot-encoded labels
    vec = np.empty(shape=(n,))
    for i in range(n):
        vec[i] = classes_dictionary_org[test_files[i][:3]]
    return vec


def save_as_npy():
    labels = categorical_labels()
    with open('../data/arrays2.npy', 'wb') as f:
        np.save(f, labels)
        np.save(f, preds_probs)


def show_preds():
    print("Network output distribution: \n----------------------------------------------")
    for i in range(len(preds_probs)):
        for j in range(15):
            print('{0:25}  {1}'.format(abbreviation_dict[classes_dictionary[j]], str(preds_probs[i][j])))
            if j == 14:
                print("\n\nPREDICTION: \n" + abbreviation_dict[classes_dictionary[np.argmax(preds_probs[i])]] + "\n")
