import tensorflow as tf
from tensorflow import keras
from datetime import datetime
from keras.optimizers import Adam
from keras.models import Sequential,Model
from keras.callbacks import ModelCheckpoint
from keras.preprocessing.image import ImageDataGenerator,load_img,img_to_array
from keras.layers import Input, Dense, Dropout, Conv2D, MaxPool2D, AveragePooling2D, Flatten, SeparableConv2D


classes = ['adelante', 'atras', 'derecha', 'foto', 'izquierda', 'nada']
epochs = 35
batch_size = 10
image_size=(128,128, 3)
n_classes = 6

def create_model():
  Entradas = Input(image_size)
  x = SeparableConv2D(16, kernel_size=(3,3), padding='same', activation='relu', use_bias=False)(Entradas)
  x = SeparableConv2D(16, kernel_size=(3,3), padding='same', activation='relu', use_bias=False)(x)
  x = Dropout(0.2)(x)
  x = AveragePooling2D(pool_size=(2,2))(x)
  x = SeparableConv2D(32, kernel_size=(3,3), padding='same', activation='relu', use_bias=False)(x)
  x = SeparableConv2D(32, kernel_size=(3,3), padding='same', activation='relu', use_bias=False)(x)
  x = Dropout(0.2)(x)
  x = AveragePooling2D(pool_size=(2, 2))(x)
  x = SeparableConv2D(64, kernel_size=(3,3), padding='same', activation='relu', use_bias=False)(x)
  x = SeparableConv2D(64, kernel_size=(3,3), padding='same', activation='relu', use_bias=False)(x)
  x = Dropout(0.2)(x)
  x = AveragePooling2D(pool_size=(2, 2))(x)

  # # --------------------------------------------------------
  x = Flatten()(x)
  x = Dense(64, activation='relu')(x)
  x = Dense(32, activation='relu')(x)
  x = Dense(n_classes, activation='softmax')(x)
  m = Model(inputs=Entradas, outputs=x)
  m.summary()
  m.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
  return m


def get_model_trained():
    best_weights_path = 'best_weights.h5'
    model = create_model()
    model.load_weights(best_weights_path)
    return model


import numpy as np
import cv2

def proof(model, frame):
    
    x = img_to_array(frame,dtype='float32')
    x = x*1./255
    x = np.expand_dims(x,axis=0)
    prediccion = model.predict(x, batch_size=10)
    if max(prediccion[0]) > .70:
        print("prediccion de imagen leida")
        print(f'Prediccion: {classes[np.argmax(prediccion[0])]} -> % {int(max(prediccion[0])*100)}')
    
    
    # video_capture = cv2.VideoCapture(0)

    # while(True):
        # Capture frame-by-frame
        # ret, frame1 = video_capture.read()
        # frame1 = cv2.imread("/home/omar/Escritorio/Neuronal-Network-from-I/test/derecha/derecha.jpeg")

        # Display the resulting frame
        # cv2.imshow('frame',frame1)
        # frame = cv2.cvtColor(frame1,cv2.COLOR_BGR2RGB)
        # frame = cv2.resize(frame,(128,128))
        # x = img_to_array(frame,dtype='float32')
        # x = x*1./255
        # x = np.expand_dims(x,axis=0)
        # prediccion = model.predict(x, batch_size=10)
        # if max(prediccion[0]) > .70:
        #     print("prediccion de imagen leida")
        #     print(f'Prediccion: {classes[np.argmax(prediccion[0])]} -> % {int(max(prediccion[0])*100)}')
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

    # When everything done, release the capture
    # video_capture.release()
    # cv2.destroyAllWindows()

# proof(get_model_trained())
