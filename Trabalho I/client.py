import os
import paho.mqtt.client as mqtt 
from random import randint
import time
import sys
import flwr as fl
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPool2D,Flatten,Dense
from tensorflow.keras.optimizers import SGD
import numpy as np
#import ray
#from matplotlib import pyplot as plt
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"



#idClient = ""

#def on_message(client, userdata, message):
#    global idClient
#    idClient = str(message.payload.decode("utf-8"))

def define_model(input_shape,num_classes):
    model = Sequential()
    model.add(Conv2D(32, (3, 3), activation='relu', kernel_initializer='he_uniform', input_shape=input_shape))
    model.add(MaxPool2D((2, 2)))
    
        # Transforma o array de imagens de (28x28) para (784 [28*28], uma única dimensão)
    model.add(Flatten())
    
        # Camada neural densely connected, ou fully connected
    model.add(Dense(100, activation='relu', kernel_initializer='he_uniform'))

        # Camada softmax
    model.add(Dense(num_classes, activation='softmax'))
    
        # Compilando Modelo
    opt = SGD(learning_rate=0.01, momentum=0.9)
    model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
    return model


def client_fn_random():
    input_shape = (28, 28, 1)
    num_classes = 10
    num_clients = 10
    partition_size = 500

    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
    #sample_size_train = int(cid) * partition_size
    #sample_size_test = int(cid) * partition_size
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
    model = define_model(input_shape,num_classes)
    # Create and return client
    return FlowerClient(model, x_train, y_train, x_test, y_test)


class FlowerClient(fl.client.NumPyClient):
    def __init__(self, model, x_train, y_train, x_test, y_test) -> None:
        self.model = model
        self.x_train = x_train
        self.y_train = y_train
        self.x_test = x_test
        self.y_test = y_test

    def get_parameters(self, config):
        return self.model.get_weights()

    def fit(self, parameters, config):
        self.model.set_weights(parameters)
        self.model.fit(self.x_train, self.y_train, epochs=1, verbose=2)
        return self.model.get_weights(), len(self.x_train), {}

    def evaluate(self, parameters, config):
        self.model.set_weights(parameters)
        loss, acc = self.model.evaluate(self.x_test, self.y_test, verbose=2)
        return loss, len(self.x_test), {"accuracy": acc}





# Calcula total de argumentos
n = len(sys.argv)
 
mqttBroker = "broker.emqx.io" 
if len(sys.argv) >= 2:
    mqttBroker = str(sys.argv[1])

print(mqttBroker)

#Filas
fila_idClient = "sd/id/client"

idClient = randint(0, 1000000)
client = mqtt.Client("Client_Federado_" + str(idClient)) 
client.connect(mqttBroker) 

client.publish(fila_idClient, idClient)
print("Published " + str(idClient) + " to topic " + fila_idClient)

time.sleep(1)
