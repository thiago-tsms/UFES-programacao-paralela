import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPool2D,Flatten,Dense
from tensorflow.keras.optimizers import SGD
import numpy as np


def obtem_dados(num_clients):
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
    
    sample_size_train = int((1/num_clients)*len(x_train))
    sample_size_test = int((1/num_clients)*len(x_test))
    
    idx_train = np.random.choice(np.arange(len(x_train)), sample_size_train, replace=False)
    x_train = x_train[idx_train]/255.0
    y_train = y_train[idx_train]
    y_train = tf.one_hot(y_train.astype(np.int32), depth=10)
    
    idx_test = np.random.choice(np.arange(len(x_test)), sample_size_test, replace=False)
    x_test = x_test[idx_test]/255.0
    y_test = y_test[idx_test]
    y_test = tf.one_hot(y_test.astype(np.int32), depth=10)
    
    return (x_train, y_train, x_test, y_test)


class Aprendizado:
    
    def __init__(self, x_train, y_train, x_test, y_test, input_shape, num_classes):
        self.x_train = x_train
        self.y_train = y_train
        self.x_test = x_test
        self.y_test = y_test
        self.define_model(input_shape, num_classes)
        self.m_shape = [s.shape for s in self.model.get_weights()]


    # Define o modelo
    def define_model(self, input_shape, num_classes):
        self.model = Sequential()
        self.model.add(Conv2D(32, (3, 3), activation='relu', kernel_initializer='he_uniform', input_shape=input_shape))
        self.model.add(MaxPool2D((2, 2)))
        
            # Transforma o array de imagens de (28x28) para (784 [28*28], uma única dimensão)
        self.model.add(Flatten())
        
            # Camada neural densely connected, ou fully connected
        self.model.add(Dense(100, activation='relu', kernel_initializer='he_uniform'))

            # Camada softmax
        self.model.add(Dense(num_classes, activation='softmax'))
        
            # Compilando Modelo
        opt = SGD(learning_rate=0.01, momentum=0.9)
        self.model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])


    # Obtem os gradientes
    def get_weights(self):
        return self.model.get_weights()
    
    
    # Efetua o aprendizado (com ou sem gradientes)
    def fit(self, params=None):
        if params is not None:
            self.model.set_weights(params)
        self.model.fit(self.x_train, self.y_train, epochs=1, verbose=2)
        return self.model.get_weights()
    
    
    # Fas a avaliação dos resultados
    def evaluate(self, params):
        self.model.set_weights(params)
        loss, acc = self.model.evaluate(self.x_test, self.y_test, verbose=2)
        return loss, len(self.x_test), {"accuracy": acc}


    # Faz o re-shape nos dados recebidos
    def re_shape(self, params):
        return [np.array(p).reshape(s) for s, p in zip(self.m_shape, params)]
    
    # Faz a agregação dos dados
    def federated_averaging(self, model_weights, all_weights):
        averaged_weights = []

        for layer_weights in zip(*all_weights):
            # Calcula a média ponderada dos pesos de cada camada
            averaged_layer_weights = np.mean(layer_weights, axis=0)
            averaged_weights.append(averaged_layer_weights)

        return averaged_weights    
