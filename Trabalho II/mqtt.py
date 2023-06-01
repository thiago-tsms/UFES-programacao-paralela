import paho.mqtt.client as mqtt
from threading import Thread
import json
from json import JSONEncoder
import random
import time
import numpy as np
import queue

topico_keep_connection = "sd/tr1/keep_connection"
topico_send_gradiente = "sd/tr1/send_gradiente"
topico_recv_gradiente = "sd/tr1/recv_gradiente"
topico_avalia_send = "sd/tr1/avalia/send"
topico_avalia_recv = "sd/tr1/avalia/recv"

#broker = "broker.emqx.io"
broker = "localhost"


class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, (np.float, np.complexfloating)):
            return float(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.string_):
            return str(obj)
        return super(NumpyArrayEncoder, self).default(obj)
    

class Parametros:
    def __init__(self):
        self.id = -1


class Conexao_Cliente:
    def __init__(self, id, last_time):
        self.id = id
        self.last_time = last_time


class ComunicacaoMQTTServer:

    def __init__(self, time_out=5):
        self.time_out = time_out # Não funcionando
        self.inicia_mqtt()
        self.subscribe_server()
        self.lista_clientes = []
        self.queue = queue.Queue()
        self.queue2 = queue.Queue()
        
        #tr = Thread(target=self.keep_connection, args=(self.lista_clientes,))
        #tr.start()
        
        # Pergunta quais clientes que já estão rodando
        self.client.publish(topico_keep_connection, json.dumps({
            'id': -1,
        }))
        
    
    # Inicia o MQTT
    def inicia_mqtt(self):
        self.client = mqtt.Client("controlador-federado-ufes")
        self.client.connect(broker)

    # Finaliza o MQTT
    def finalizar_mqtt(self):
        self.client.loop_stop()
        self.client.disconnect()
    
    # Se inscreve nos tópicos (server)
    def subscribe_server(self):

        self.client.subscribe(topico_keep_connection)
        self.client.subscribe(topico_recv_gradiente)
        self.client.subscribe(topico_avalia_recv)
        
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
                    
        # Recebo os dados para o fim da iteração
        elif msg.topic == topico_recv_gradiente:
            self.queue.put(json.loads(msg.payload))
        
        # Avalia o resultado final
        elif msg.topic == topico_avalia_recv:
            self.queue2.put(float(msg.payload))

                        
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
        return [c.id for c in self.lista_clientes]
      
    # Envia os dados para os clientes  
    def start_aprendizado(self, params):
        self.client.publish(topico_send_gradiente, json.dumps(params, cls=NumpyArrayEncoder))
        return len(self.lista_clientes)
     
    # Recebe os dados
    def get_gradientes(self):
        return self.queue.get()

    # Envia modelo final
    def envia_modelo_final(self, params):
        self.client.publish(topico_avalia_send, json.dumps(params, cls=NumpyArrayEncoder))
        return len(self.lista_clientes)
    
    def recebe_avaliacao_final(self):
        return self.queue2.get()


class ComunicacaoMQTTCliente:

    def __init__(self, executa_aprendizado, avalia_resultado):
        self.params = Parametros()
        self.params.id = random.randint(0, 1000)
        self.executa_aprendizado = executa_aprendizado
        self.avalia_resultado = avalia_resultado

        self.inicia_mqtt()
        self.subscribe_client()
        self.client.publish(topico_keep_connection, json.dumps({'id': self.params.id}))
    
    # Inicia o MQTT
    def inicia_mqtt(self):
        self.client = mqtt.Client(f'no-{self.params.id}-federado-ufes')
        self.client.connect(broker)
    
    # Finaliza o MQTT
    def finalizar_mqtt(self):
        self.client.loop_stop()
        self.client.disconnect()
    
    # Se inscreve nos tópicos (cliente)
    def subscribe_client(self):

        self.client.subscribe(topico_keep_connection)
        self.client.subscribe(topico_send_gradiente)
        self.client.subscribe(topico_avalia_send)

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
        
        # Recebe os dados para o início da iteração
        elif msg.topic == topico_send_gradiente:
            res = self.executa_aprendizado(json.loads(msg.payload))
            self.client.publish(topico_recv_gradiente, json.dumps(res, cls=NumpyArrayEncoder))
        
        # Avalia o resultado final
        elif msg.topic == topico_avalia_send:
            res = self.avalia_resultado(json.loads(msg.payload))
            self.client.publish(topico_avalia_recv, res)
    