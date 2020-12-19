#!/usr/bin/env python3
# coding: utf8

from keras.preprocessing import image
from keras import backend as K

from vis.utils import utils
import numpy as np
import residual_network

import calibration
import os

classes_dictionary_org = {'BAS': 0, 'EBO': 1, 'EOS': 2, 'KSC': 3, 'LYA': 4, 'LYT': 5, 'MMZ': 6, 'MOB': 7, 'MON': 8, 'MYB': 9, 'MYO': 10, 'NGB': 11, 'NGS': 12, 'PMB': 13, 'PMO': 14}
classes_dictionary = {value: key for key, value in classes_dictionary_org.items()}


abbreviation_dict = { 'NGS': 'Neutrophil (segmented)',
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
                      'PMB': 'Promyelocyte (bilobed)'};


img_width, img_height = 400, 400

if K.image_data_format() == 'channels_first':
        input_shape = (3, img_width, img_height)
else:
        input_shape = (img_width, img_height, 3)


weight_file_path = "weights.hdf5"

model = residual_network.model
model.load_weights(weight_file_path)

model.compile(loss='categorical_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])

batch_size = 10
test_folder = '../data/test_data/'
test_files = os.listdir(test_folder)[:batch_size]

inputs = []

for _file in test_files:
        img = utils.load_img(test_folder + _file)
        img = (img[:,:,:3] *1./255)

        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        inputs.append(x)

images = np.vstack(inputs) # n arrays w/ shape (1, 400, 400, 3) --> 1 w/ shape (n, 400, 400, 3)

preds_probs = model.predict_on_batch(images)
preds_probs = np.array(preds_probs)
preds_probs[:,1]+=preds_probs[:,2]
preds_probs=np.delete(preds_probs,2,1)

y_true, y_prob, desert_values = calibration.extract_probs(preds_probs, test_files, classes_dictionary)
calibration.plot_calibration(y_true, y_prob)
print(f'Values between 0.3 and 0.7: {desert_values}')

def show_preds():
    print ("Network output distribution: \n----------------------------------------------")
    for i in range(len(preds_probs)):
        for j in range(15):
            print('{0:25}  {1}'.format(abbreviation_dict[classes_dictionary[j]], str(preds_probs[i][j])))
            if j == 14:
                print ("\n\nPREDICTION: \n"+abbreviation_dict[classes_dictionary[np.argmax(preds_probs[i])]]+"\n")
