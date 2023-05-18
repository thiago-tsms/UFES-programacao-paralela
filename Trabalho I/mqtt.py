import paho.mqtt.client as mqtt
from threading import Thread
import json
import random
import time
import numpy as np

topico_keep_connection = "sd/tr1/keep_connection"
topico_send_gradiente = "sd/tr1/send_gradiente"
topico_recv_gradiente = "sd/tr1/recv_gradiente"


class Parametros:
    def __init__(self):
        self.id = -1


class Conexao_Cliente:
    def __init__(self, id, last_time):
        self.id = id
        self.last_time = last_time


class ComunicacaoMQTTServer:

    def __init__(self, time_out):
        self.time_out = time_out
        self.inicia_mqtt()
        self.subscribe_server()
        self.lista_clientes = []
        
        tr = Thread(target=self.keep_connection, args=(self.lista_clientes,))
        tr.start()
    
    # Inicia o MQTT
    def inicia_mqtt(self):
        self.client = mqtt.Client("controlador-federado-ufes")
        self.client.connect("broker.emqx.io")

    # Finaliza o MQTT
    def finalizar_mqtt(self):
        self.client.loop_stop()
        self.client.disconnect()
    
    # Se inscreve nos tópicos (server)
    def subscribe_server(self):

        self.client.subscribe(topico_keep_connection)
        
        self.client.on_message = self.on_message_server
        self.client.loop_start()

    # Escuta as mansagens (server)
    def on_message_server(self, client, userdata, msg):

        # Recebe o id de todos os clientes
        if msg.topic == topico_keep_connection:
            msg = json.loads(str(msg.payload.decode("utf-8")))
            id = msg['id']
            
            if id != -1:
                
                # Adiciona um novo cliente a lisa
                if id not in [lc.id for lc in self.lista_clientes]:
                    self.lista_clientes.append(Conexao_Cliente(id, time.time()))
                    print(f'Cliente: {id} conectado')
                    
                # Marca o tempo de resposta
                else:
                    for lc in self.lista_clientes:
                        if lc.id == id:
                            lc.last_time = time.time()
                            break
                        
    # Manda mensagens a cada segundo e vê se o server ainda esta conectado
    def keep_connection(self, lista_clientes):
        while True:
            drop = []
            
            self.client.publish(topico_keep_connection, json.dumps({
                'id': -1,
            }))
            
            for lc in lista_clientes:
                t = int((time.time() - lc.last_time) * 1000)
                
                if t > (self.time_out * 1000):
                    print(f'Cliente: {lc.id} desconectado')
                    lista_clientes.remove(lc)
            
            time.sleep(1)
    
    
    # Obtem id dos clientes conectados
    def get_clientes(self):
        return [lc.id for lc in self.lista_clientes]
    
    # Envia os dados para um ciclo de aprendizado
    def start_iteracao(self, params):
        self.client.publish(topico_send_gradiente, params)
        
        # Desafio - Convertero os dados para enviar e converter para recebe-los
        
        #self.client.publish(topico_send_gradiente, np.array(params, dtype=object).tobytes())
        #print(np.array(params).dtype)
            

class ComunicacaoMQTTCliente:

    def __init__(self, executa_aprendizado):
        self.params = Parametros()
        self.params.id = random.randint(0, 1000)
        self.executa_aprendizado = executa_aprendizado

        self.inicia_mqtt()
        self.subscribe_client()
        self.client.publish(topico_keep_connection, json.dumps({'id': self.params.id}))
    
    # Inicia o MQTT
    def inicia_mqtt(self):
        self.client = mqtt.Client(f'no-{self.params.id}-federado-ufes')
        self.client.connect("broker.emqx.io")
    
    # Finaliza o MQTT
    def finalizar_mqtt(self):
        self.client.loop_stop()
        self.client.disconnect()
    
    # Se inscreve nos tópicos (cliente)
    def subscribe_client(self):

        self.client.subscribe(topico_keep_connection)
        self.client.subscribe(topico_send_gradiente)

        self.client.on_message = self.on_message_client
        self.client.loop_start()
    
    # Escuta as mansagens (cliente)
    def on_message_client(self, client, userdata, msg):

        #Recebe solicitação de id do cliente
        if msg.topic == topico_keep_connection:
            msg = json.loads(str(msg.payload.decode("utf-8")))
            id = msg['id']

            if id == -1:
                self.client.publish(topico_keep_connection, json.dumps({
                    'id': self.params.id
                }))
        
        
        elif msg.topic == topico_send_gradiente:
            self.executa_aprendizado(msg.payload)
            
            # Como receber os dados
            
            #print(msg.payload)
            #print(np.frombuffer(msg.payload, 'object'))
            
            