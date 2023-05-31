import paho.mqtt.client as mqtt
#from threading import Thread
from multiprocessing import Queue
import random
import json
import time
#import numpy as np

broker = "broker.emqx.io"
topico_anuncio = "sd/lab6/anuncio"
topico_eleicao = "sd/lab6/eleicao"
topico_solution = "sd/lab6/solution"
topico_challenge = 'sd/lab6/challenge'
topico_result = 'sd/lab6/result'

class Comunicacao:

    def __init__(self, cliente_data):
        self.cliente_data = cliente_data
        self.lista_clientes = [self.cliente_data.id]
        self.inicia_mqtt()
        self.subscribe_server()
        self.lista_eleicao = []
        
        # Usado para aguardat que os dados do 'on_message' tenha sido recebidos e salvos em 'cliente_data'
        self.queue_challenge = Queue()
        self.queue_solution = Queue()
        self.queue_result = Queue()

        time.sleep(4)
        self.client.publish(topico_anuncio, json.dumps({
            'id': self.cliente_data.id
        }))

    
    # Inicia o MQTT
    def inicia_mqtt(self):
        self.client = mqtt.Client(f'client-{self.cliente_data.id}')
        self.client.connect(broker)
    
    # Finaliza o MQTT
    def finalizar_mqtt(self):
        self.client.loop_stop()
        self.client.disconnect()
    
    # Se inscreve nos tópicos (server)
    def subscribe_server(self):

        self.client.subscribe(topico_eleicao)
        self.client.subscribe(topico_anuncio)
        self.client.subscribe(topico_solution)
        self.client.subscribe(topico_challenge)
        self.client.subscribe(topico_result)
        
        self.client.on_message = self.on_message
        self.client.loop_start()

    # Recebe as mensagens
    def on_message(self, client, userdata, msg):
        data = json.loads(str(msg.payload.decode("utf-8")))
        origin_id = data['id']
        
        # Elimina mensagens da mesma origem
        if origin_id == self.cliente_data.id:
            return

        # Recebe id de novo integrante
        if msg.topic == topico_anuncio:
            self.lista_clientes.append(origin_id)
        
        # Recebe id e pesos da eleição
        elif msg.topic == topico_eleicao:
            c_id = data['id']
            peso = data['peso']

            self.lista_eleicao.append((c_id, peso))
        
        # Recebe novo desafio
        elif msg.topic == topico_challenge:
            self.cliente_data.transaction_id = data['TransactionID']
            self.cliente_data.challenge = data['Challenge']
            self.queue_challenge.put(True)

        # Recebe possível solução            
        elif msg.topic == topico_solution:
            client_id = data['id']
            transaction_id = data['TransactionID']
            solution = data['Solution']
        
            self.queue_solution.put((client_id, transaction_id, solution))
        
        # Recebe resultado do desafio
        elif msg.topic == topico_result:
            client_id = data['ClientID']
            transaction_id = data['TransactionID']
            solution = data['Solution']
            result = data['Result']
            
            self.queue_result.put((client_id, transaction_id, solution, result))


    def eleicao(self):
        print(f'* Iniciando Eleição')

        v_rand = random.randint(0, 65536)
        self.lista_eleicao.append((self.cliente_data.id, v_rand))

        time.sleep(4)

        # Envia id e pesos gerado
        self.client.publish(topico_eleicao, json.dumps({
            'id': self.cliente_data.id,
            'peso': v_rand
        }))

        time.sleep(5)

        mv = max([le[1] for le in self.lista_eleicao])
        for le in self.lista_eleicao:
            if le[1] == mv:
                self.cliente_data.id_lider = le[0]
        
        print(f'\n** Resultado da Eleição \nIntegrantes: {self.lista_eleicao} \nID: {self.cliente_data.id} \nID Cordenador: {self.cliente_data.id_lider} \n')
    
    # Espera o desafio ser obtido
    def wait_challenge(self):
        return self.queue_challenge.get()
    
    # Espera que uma nova solução tenha sido recebida
    def wait_solution(self):
        return self.queue_solution.get()
    
    # ESpera que um resultado tenha sido recebido
    def wait_result(self):
        return self.queue_result.get()