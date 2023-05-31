import paho.mqtt.client as mqtt
#from threading import Thread
import random
import json
import time
#import numpy as np
#import queue

broker = "broker.emqx.io"
topico_anuncio = "sd/lab6/anuncio"
topico_eleicao = "sd/lab6/eleicao"

class Comunicacao:

    def __init__(self):
        self.id = random.randint(0, 1000)
        self.id_lider = None
        self.lista_clientes = [self.id]
        self.inicia_mqtt()
        self.subscribe_server()
        self.lista_eleicao = []

        time.sleep(4)
        self.client.publish(topico_anuncio, json.dumps({
            'id': self.id
        }))

    
    # Inicia o MQTT
    def inicia_mqtt(self):
        self.client = mqtt.Client(f'client-{self.id}')
        self.client.connect(broker)
    
    # Finaliza o MQTT
    def finalizar_mqtt(self):
        self.client.loop_stop()
        self.client.disconnect()
    
    # Se inscreve nos tópicos (server)
    def subscribe_server(self):

        self.client.subscribe(topico_eleicao)
        self.client.subscribe(topico_anuncio)
        
        self.client.on_message = self.on_message
        self.client.loop_start()

    # Recebe as mensagens
    def on_message(self, client, userdata, msg):

        if msg.topic == topico_anuncio:
            msg = json.loads(str(msg.payload.decode("utf-8")))
            c_id = msg['id']

            if c_id != self.id:
                self.lista_clientes.append(c_id)
        
        elif msg.topic == topico_eleicao:
            msg = json.loads(str(msg.payload.decode("utf-8")))
            c_id = msg['id']
            peso = msg['peso']

            if c_id != self.id:
                self.lista_eleicao.append((c_id, peso))


    def eleicao(self):
        print(f'* Iniciando Eleição')

        v_rand = random.randint(0, 65536)
        self.lista_eleicao.append((self.id, v_rand))

        time.sleep(4)

        # Envia id e pesos gerado
        self.client.publish(topico_eleicao, json.dumps({
            'id': self.id,
            'peso': v_rand
        }))

        time.sleep(5)

        mv = max([le[1] for le in self.lista_eleicao])
        for le in self.lista_eleicao:
            if le[1] == mv:
                self.id_lider = le[0]
        
        print(mqtt.lista_eleicao)
        print(mqtt.id_lider)





    