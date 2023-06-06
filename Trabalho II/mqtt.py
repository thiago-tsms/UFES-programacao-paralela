import paho.mqtt.client as mqtt
from multiprocessing import Queue
import random
import json
from json import JSONEncoder
import numpy as np
import time

broker = "localhost"
topico_anuncio = "sd/tr2/init"
topico_eleicao = "sd/tr2/voting"
topico_send_pesos = "sd/tr2/send/pesos"
topico_return_pesos = "sd/tr2/return/pesos"
topico_send_acuracia = 'sd/tr2/send/acuracia'
topico_return_acuracia = 'sd/tr2/result/acuracia'


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

class Comunicacao:

    def __init__(self, cliente_data):
        self.cliente_data = cliente_data
        self.lista_clientes = [self.cliente_data.id]
        self.inicia_mqtt()
        self.subscribe_server()
        self.lista_eleicao = []
        
        # Usado para aguardat que os dados do 'on_message' tenha sido recebidos e salvos em 'cliente_data'
        self.queue_return_weights = Queue()
        self.queue_return_acuracia = Queue()

        time.sleep(4)
        self.client.publish(topico_anuncio, json.dumps({
            'id': self.cliente_data.id
        }))

    def set_client_func(self, executar_aprendizado, avaliar_aprendizado):
        self.executar_aprendizado = executar_aprendizado
        self.avaliar_aprendizado = avaliar_aprendizado
    
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
        self.client.subscribe(topico_send_pesos)
        self.client.subscribe(topico_return_pesos)
        self.client.subscribe(topico_send_acuracia)
        self.client.subscribe(topico_return_acuracia)
        
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
        
        # Recebe pesos (cliente) e executa aprendizado
        elif msg.topic == topico_send_pesos:
            weight = self.executar_aprendizado(json.loads(data['data']))
            self.client.publish(topico_return_pesos, json.dumps({
            "id": self.cliente_data.id,
            "data": json.dumps(weight, cls=NumpyArrayEncoder)
        }))
            
        
        # Recebe resultados (server)
        elif msg.topic == topico_return_pesos and self.cliente_data.id_lider == self.cliente_data.id:
            self.queue_return_weights.put(json.loads(data['data']))

        elif msg.topic == topico_send_acuracia:
            acuracia = self.avaliar_aprendizado(json.loads(data['data']))
            self.client.publish(topico_return_acuracia, json.dumps({
            "id": self.cliente_data.id,
            "data": acuracia
        }))
        
        elif msg.topic == topico_return_acuracia:
            self.queue_return_acuracia.put(data['data'])


    # Realiza a eleição
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
        
        print(f'\n** Resultado da Eleição \nIntegrantes: {self.lista_eleicao} \nID: {self.cliente_data.id} \nID Coordenador: {self.cliente_data.id_lider} \n')
    
    # Envia peso para os clientes
    def enviar_peso(self, params):
        self.client.publish(topico_send_pesos, json.dumps({
            "id": self.cliente_data.id,
            "data": json.dumps(params, cls=NumpyArrayEncoder)
        }))  
        return len(self.lista_clientes) -1
        
    # Envia acuracia para resultado final
    def envia_acuracia(self, params):
        self.client.publish(topico_send_acuracia, json.dumps({
            "id": self.cliente_data.id,
            "data": json.dumps(params, cls=NumpyArrayEncoder)
        }))  
        return len(self.lista_clientes) -1
    
    
    # Espera um peso para finalizar a iteração (Client -> Server)
    def wait_return_weights(self):
        return self.queue_return_weights.get()


    # (Client -> Server)
    def wait_return_acuracia(self):
        return self.queue_return_acuracia.get()