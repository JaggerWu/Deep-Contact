from __future__ import absolute_import, division, print_function

import numpy as np

import tensorflow as tf

import keras
from keras import backend as K
from keras.models import Sequential
from keras.layers import (
    Dense,
    Dropout,
    Activation,
    Flatten,
    Conv2D,
    MaxPooling2D,
)
from keras import optimizers
from keras.callbacks import (
    LearningRateScheduler,
    TensorBoard,
    ModelCheckpoint,
)
from keras.layers.normalization import BatchNormalization
from keras.utils import plot_model


def loss_func(y_true, y_pred):
    # remove 0 in y_true
    flags = tf.to_float(K.not_equal(y_true, 0.0))
    return K.mean(K.square((y_pred - y_true) * flags), axis=-1)


def mean_absolute_loss(y_true, y_pred):
    flags = tf.to_float(K.not_equal(y_true, 0.0))
    return K.mean(K.abs((y_pred - y_true) * flags), axis=-1)


class learning_model(object):
    def __init__(
        self,
        log_dir,
        optimizer,
        loss_func,
        metrics,
        batch_size=100,
        iterations=500,
        epochs=100,
        dropout=0.25,
        weight_decay=0.0001,
    ):
        '''
        :param input_shape:
            loss_func:
            metrics:
        '''
        self.model = Sequential()
        self.optimizer = optimizer
        self.iterations = iterations
        self.loss_func = loss_func
        self.metrics = metrics
        self.log_dir = log_dir
        self.batch_size = batch_size
        self.epochs = epochs
        self.dropout = dropout
        self.weight_decay = weight_decay

    def build_model(self, input_shape, output_shape):
        self.model.add(Conv2D(64,
                              (2, 2),
                              padding='same',
                              kernel_regularizer=keras.regularizers.l2(self.weight_decay),
                              kernel_initializer='he_normal',
                              input_shape=input_shape))
        self.model.add(Activation('relu'))

        self.model.add(Conv2D(64,
                              (2, 2),
                              padding='same',
                              kernel_regularizer=keras.regularizers.l2(self.weight_decay),
                              kernel_initializer='he_normal',
                              input_shape=input_shape))
        self.model.add(BatchNormalization())
        self.model.add(Activation('relu'))

        self.model.add(MaxPooling2D(pool_size=(2, 2),
                                    strides=(2, 2),
                                    padding='same'))

        self.model.add(Conv2D(128,
                              (2, 2),
                              padding='same',
                              kernel_regularizer=keras.regularizers.l2(self.weight_decay),
                              kernel_initializer='he_normal'))
        self.model.add(Activation('relu'))

        self.model.add(Conv2D(128,
                              (2, 2),
                              padding='same',
                              kernel_regularizer=keras.regularizers.l2(self.weight_decay),
                              kernel_initializer='he_normal'))
        self.model.add(Activation('relu'))

        self.model.add(Conv2D(128,
                              (2, 2),
                              padding='same',
                              kernel_regularizer=keras.regularizers.l2(self.weight_decay),
                              kernel_initializer='he_normal'))
        self.model.add(Activation('relu'))

        self.model.add(Conv2D(128,
                              (2, 2),
                              padding='same',
                              kernel_regularizer=keras.regularizers.l2(self.weight_decay),
                              kernel_initializer='he_normal'))
        self.model.add(BatchNormalization())
        self.model.add(Activation('relu'))

        self.model.add(MaxPooling2D(pool_size=(2, 2),
                                    strides=(2, 2),
                                    padding='same'))

        self.model.add(Conv2D(256,
                              (2, 2),
                              padding='same',
                              kernel_regularizer=keras.regularizers.l2(self.weight_decay),
                              kernel_initializer='he_normal'))
        self.model.add(Activation('relu'))

        self.model.add(Conv2D(256,
                              (2, 2),
                              padding='same',
                              kernel_regularizer=keras.regularizers.l2(self.weight_decay),
                              kernel_initializer='he_normal'))
        self.model.add(Activation('relu'))

        self.model.add(Conv2D(256,
                              (2, 2),
                              padding='same',
                              kernel_regularizer=keras.regularizers.l2(self.weight_decay),
                              kernel_initializer='he_normal'))
        self.model.add(Activation('relu'))

        self.model.add(Conv2D(256,
                              (2, 2),
                              padding='same',
                              kernel_regularizer=keras.regularizers.l2(self.weight_decay),
                              kernel_initializer='he_normal'))
        self.model.add(BatchNormalization())
        self.model.add(Activation('relu'))

        self.model.add(MaxPooling2D(pool_size=(2, 2),
                                    strides=(2, 2),
                                    padding='same'))

        self.model.add(Conv2D(512,
                              (2, 2),
                              padding='same',
                              kernel_regularizer=keras.regularizers.l2(self.weight_decay),
                              kernel_initializer='he_normal'))
        self.model.add(Activation('relu'))
        self.model.add(Conv2D(512,
                              (2, 2),
                              padding='same',
                              kernel_regularizer=keras.regularizers.l2(self.weight_decay),
                              kernel_initializer='he_normal'))
        self.model.add(Activation('relu'))
        self.model.add(Conv2D(512,
                              (2, 2),
                              padding='same',
                              kernel_regularizer=keras.regularizers.l2(self.weight_decay),
                              kernel_initializer='he_normal'))
        self.model.add(Activation('relu'))

        self.model.add(Conv2D(512,
                              (2, 2),
                              padding='same',
                              kernel_regularizer=keras.regularizers.l2(self.weight_decay),
                              kernel_initializer='he_normal'))
        self.model.add(BatchNormalization())
        self.model.add(Activation('relu'))

        self.model.add(MaxPooling2D(pool_size=(2, 2),
                                    strides=(2, 2),
                                    padding='same'))

        self.model.add(Dropout(self.dropout))
        self.model.add(Flatten())
        
        output_size = output_shape[0]

        self.model.add(Dense(output_size))
        self.model.add(Activation('relu'))

        self.model.compile(
            loss=self.loss_func,
            optimizer=self.optimizer,
            metrics=self.metrics,
        )

    def train(self, x_train, y_train, method, validation_rate=0.2, save=True):
        input_shape = x_train.shape[1:]
        output_shape = y_train.shape[1:]

        # set call_back
        tb_cb = TensorBoard(log_dir=self.log_dir)

        # change learning rate
        change_lr = LearningRateScheduler(self.scheduler)
        # checkpoint
        filepath="weights.best.hdf5"
        checkpoint = ModelCheckpoint(
            filepath,
            monitor='val_loss',
            verbose=1,
            save_best_only=True,
            mode='min')
        cbks = [change_lr, tb_cb, checkpoint]

        # buid model firstly
        self.build_model(input_shape, output_shape)
        print(self.model.summary())

        methods = {
            'batch_method': {
                'batch_size': self.batch_size,
            },
            'fixed_iter': {
                'steps_per_epoch': self.iterations,
            },
        }

        if method not in methods.keys():
            raise ValueError(
                "method must be `batch_method` or `fixed_iter`")

        self.model.fit(
            x_train,
            y_train,
            epochs=self.epochs,
            callbacks=cbks,
            validation_split=validation_rate,
            **methods.get(method))

        if save:
            self.model.save('model.h5')

    @staticmethod
    def scheduler(epoch):
        if epoch <= 100:
            return 0.05
        if epoch <= 400:
            return 0.02
        return 0.01
