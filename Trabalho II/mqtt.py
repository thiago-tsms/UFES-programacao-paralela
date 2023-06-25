import paho.mqtt.client as mqtt
from multiprocessing import Queue
import random
import json
from json import JSONEncoder
import numpy as np
import time

broker = "localhost"

topico_agregador_evaluate_client_to_server = 'sd/tr2/agregador/evaluate/client_to_server'
topico_agregador_evaluate_server_to_client = 'sd/tr2/agregador/evaluate/server_to_client'
topico_agregador_accuracy_client_to_server = 'sd/tr2/agregador/accuracy/client_to_server'
topico_agregador_accuracy_server_to_client = 'sd/tr2/agregador/accuracy/server_to_client'
topico_agregador_end_round = 'sd/tr2/agregador/end_round'

topico_anuncio = "sd/tr2/init"
topico_eleicao = "sd/tr2/voting"

topico_fit_client_to_server = "sd/tr2/fit/client_to_server"
topico_fit_server_to_client = "sd/tr2/fit/server_to_client"
topico_weights_server_to_client = "sd/tr2/weights/server_to_client"
topico_evaluate_client_to_server = "sd/tr2/evaluate/client_to_server"
topico_evaluate_server_to_client = "sd/tr2/evaluate/server_to_client"

topico_checkpoint = 'sd/tr2/agregador/end_round'
topico_end_round = "sd/tr2/end_round"


# Serialização de dados JSON
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
        self.lista_eleicao = []
        self.checkpoint_list = []
        
        self.queue_end_round = Queue()
        self.queue_agregador_end_round = Queue()
        self.queue_fit = Queue()
        self.queue_evaluate = Queue()
        self.queue_agregador_federated_averaging = Queue()
        self.queue_agregador_federated_averaging_return = Queue()
        self.queue_agregador_accuracy = Queue()

        time.sleep(4)
        self.client.publish(topico_anuncio, json.dumps({
            'id': self.cliente_data.id
        }))

    # Adiciona funções dos clientes
    def set_client_func(self, executar_aprendizado, avaliar_aprendizado, adicionar_pesos):
        self.adicionar_pesos = adicionar_pesos
        self.executar_aprendizado = executar_aprendizado
        self.avaliar_aprendizado = avaliar_aprendizado
    
    
    # Inicia o MQTT
    def inicia_mqtt(self):
        self.client = mqtt.Client(f'client-{self.cliente_data.id}')
        self.client.connect(broker)
        
        # Ajusta topicos do grupo
        global topico_anuncio
        global topico_eleicao
        global topico_checkpoint
        global topico_end_round
        global topico_fit_client_to_server
        global topico_fit_server_to_client
        global topico_weights_server_to_client
        global topico_evaluate_client_to_server
        global topico_evaluate_server_to_client
        
        topico_anuncio = f"{topico_anuncio}_{self.cliente_data.grupo}"
        topico_eleicao = f"{topico_eleicao}_{self.cliente_data.grupo}"
        topico_checkpoint = f"{topico_checkpoint}_{self.cliente_data.grupo}"
        topico_end_round = f"{topico_end_round}_{self.cliente_data.grupo}"
        topico_fit_client_to_server = f"{topico_fit_client_to_server}_{self.cliente_data.grupo}"
        topico_fit_server_to_client = f"{topico_fit_server_to_client}_{self.cliente_data.grupo}"
        topico_weights_server_to_client = f"{topico_weights_server_to_client}_{self.cliente_data.grupo}"
        topico_evaluate_client_to_server = f"{topico_evaluate_client_to_server}_{self.cliente_data.grupo}"
        topico_evaluate_server_to_client = f"{topico_evaluate_server_to_client}_{self.cliente_data.grupo}"
        
        self.client.subscribe(topico_agregador_evaluate_client_to_server, 1)
        self.client.subscribe(topico_agregador_evaluate_server_to_client, 1)
        self.client.subscribe(topico_agregador_end_round, 1)
        self.client.subscribe(topico_agregador_accuracy_client_to_server, 1)
        self.client.subscribe(topico_agregador_accuracy_server_to_client, 1)
        
        self.client.subscribe(topico_anuncio, 1)
        self.client.subscribe(topico_eleicao, 1)
        self.client.subscribe(topico_eleicao, 1)
        self.client.subscribe(topico_checkpoint, 1)
        self.client.subscribe(topico_end_round, 1)
        
        self.client.subscribe(topico_fit_client_to_server, 1)
        self.client.subscribe(topico_fit_server_to_client, 1)
        self.client.subscribe(topico_weights_server_to_client, 1)
        self.client.subscribe(topico_evaluate_client_to_server, 1)
        self.client.subscribe(topico_evaluate_server_to_client, 1)
        
        self.client.on_message = self.on_message
        self.client.loop_start()
    
    
    # Finaliza o MQTT
    def finalizar_mqtt(self):
        self.client.loop_stop()
        self.client.disconnect()
    
  
    # Recebe as mensagens
    def on_message(self, client, userdata, msg):
        data = json.loads(str(msg.payload.decode("utf-8")))
        origin_id = data['id']
        
        # Recebe mensagem de sincronia
        if msg.topic == topico_checkpoint:
            c_id = data['id']
            self.checkpoint_list.append(c_id)
            return
               
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
        
        # Tópicos do agregador
        elif self.cliente_data.is_agregador_central == True:
            if data['round'] == self.cliente_data.round:
                self.agregador_central(msg.topic, origin_id, data)
            else:
                print(f'Divergencia de round')

        
        # Tópicos agregador
        elif self.cliente_data.id == self.cliente_data.id_lider:
            if data['round'] == self.cliente_data.round:
                self.agregador(msg.topic, origin_id, data)
            else:
                print(f'Divergencia de round')
            
        
        # Tópicos cliente
        else:
            if data['round'] == self.cliente_data.round:
                self.cliente(msg.topic, origin_id, data)
            else:
                print(f'Divergencia de round')
                
        
    # Realiza a eleição
    def eleicao(self, n_integrantes):
        v_rand = random.randint(0, 65536)
        self.lista_eleicao = []    
        self.lista_eleicao.append((self.cliente_data.id, v_rand))
        
        time.sleep(2)
        
        # Envia id e pesos gerado (voto)
        self.client.publish(topico_eleicao, json.dumps({
            'id': self.cliente_data.id,
            'peso': v_rand
        }))

        # Aguarda todos votarem
        while(n_integrantes > len(self.lista_eleicao)):
            time.sleep(0.5)

        mv = max([le[1] for le in self.lista_eleicao])
        for le in self.lista_eleicao:
            if le[1] == mv:
                self.cliente_data.id_lider = le[0]
        
        print(f'\n** Resultado da Eleição \nIntegrantes: {self.lista_eleicao} \nID: {self.cliente_data.id} \nID Coordenador: {self.cliente_data.id_lider} \n')

    # Aguarda integrantes
    def set_checkpoint(self):
        print(f'--> checkpoint <--')
        self.client.publish(topico_checkpoint, json.dumps({
            "id": self.cliente_data.id,
        }))
        
        while(len(self.checkpoint_list) < (len(self.lista_clientes))):
            time.sleep(0.5)
        
        print(f'<-- checkpoint -->')
        self.checkpoint_list = []
        return
        
    # Tarefas do agregador central
    def agregador_central(self, topic, origin_id, data):
        if topic == topico_agregador_evaluate_client_to_server:
            self.queue_agregador_federated_averaging.put((origin_id, json.loads(data['weights'])))
        
        elif topic == topico_agregador_accuracy_client_to_server:
            self.queue_agregador_accuracy.put((origin_id, data['accuracy']))
        
    
    # Tarefas do Agregador
    def agregador(self, topic, origin_id, data):
        if topic == topico_fit_client_to_server:
            self.queue_fit.put((origin_id, json.loads(data['weights'])))
        
        elif topic == topico_evaluate_client_to_server:
            self.queue_evaluate.put((origin_id, data['accuracy']))
                
        elif topic == topico_agregador_evaluate_server_to_client:
            self.queue_agregador_federated_averaging_return.put((origin_id, json.loads(data['weights']), data['accuracy']))
        
        elif topic == topico_agregador_end_round:
            self.queue_agregador_end_round.put((origin_id, data['accuracy']))
    
    
    # Tarefas do Cliente
    def cliente(self, topic, origin_id, data):
        
        # Finaliza o round
        if topic == topico_end_round:
                self.queue_end_round.put((origin_id, data['accuracy']))
        
        # Recebe pesos e executa aprendizado
        elif topic == topico_fit_server_to_client:
            if self.cliente_data.id in data['c_fit']:
                weight = data['weights']
                if weight == []:
                    w = None
                else:
                    w = json.loads(weight)
                new_weight = self.executar_aprendizado(w)
                self.client.publish(topico_fit_client_to_server, json.dumps({
                    "id": self.cliente_data.id,
                    "round": self.cliente_data.round,
                    "weights": json.dumps(new_weight, cls=NumpyArrayEncoder)
                }))
            
        # Recebe novos pesos
        elif topic == topico_weights_server_to_client:
            weight = data['weights']
            self.adicionar_pesos(json.loads(weight))

        # Recebe pesos e efetua avaliação
        elif topic == topico_evaluate_server_to_client:
            weight = data['weights']
            accuracy = self.avaliar_aprendizado(json.loads(weight))
            self.client.publish(topico_evaluate_client_to_server, json.dumps({
                "id": self.cliente_data.id,
                "round": self.cliente_data.round,
                "accuracy": accuracy
            }))  
                

    # Aguarda mensagem de fim de round (Clientes)
    def aguarda_end_round(self):
        return self.queue_end_round.get()

    # Aguarda mensagem de fim de round (Agregador)
    def aguarda_agregador_end_round(self):
        return self.queue_agregador_end_round.get()


    # Envia os pesos para todos os clientes
    def envia_peso(self, weights):
        self.client.publish(topico_weights_server_to_client, json.dumps({
            "id": self.cliente_data.id,
            "round": self.cliente_data.round,
            "weights": json.dumps(weights, cls=NumpyArrayEncoder)
        }))


    # Servidor agregador envia pesos para os clientes
    def enviar_peso_fit(self, c_fit, weights):
        if weights:
            w = json.dumps(weights, cls=NumpyArrayEncoder)
        else:
            w = []
            
        self.client.publish(topico_fit_server_to_client, json.dumps({
            "id": self.cliente_data.id,
            "c_fit": c_fit,
            "round": self.cliente_data.round,
            "weights": w
        }))
        return c_fit


    # Envia pesos para avaliação dos clientes
    def envia_pesos_avaliacao(self, weights):
        self.client.publish(topico_evaluate_server_to_client, json.dumps({
            "id": self.cliente_data.id,
            "round": self.cliente_data.round,
            "weights": json.dumps(weights, cls=NumpyArrayEncoder)
        }))
        aux_1 = self.lista_clientes.copy()
        aux_1.remove(self.cliente_data.id)
        return aux_1


    # Clientes agregadores enviam os pesos para o agregador central
    def envia_pesos_agregador_avaliacao(self, weights):
        self.client.publish(topico_agregador_evaluate_client_to_server, json.dumps({
            "id": self.cliente_data.id,
            "round": self.cliente_data.round,
            "weights": json.dumps(weights, cls=NumpyArrayEncoder)
        }))


    # Agregador central envia pesos agregados para os clientes agregadores
    def devolve_pesos_agregador_avaliacao(self, weights, accuracy):
        self.client.publish(topico_agregador_evaluate_server_to_client, json.dumps({
            "id": self.cliente_data.id,
            "round": self.cliente_data.round,
            "weights": json.dumps(weights, cls=NumpyArrayEncoder),
            "accuracy": accuracy
        }))


    # Cliente agregador envia avaliação para agregador central
    def envia_accuracy_agregador(self, accuracy):
        self.client.publish(topico_agregador_accuracy_client_to_server, json.dumps({
            "id": self.cliente_data.id,
            "round": self.cliente_data.round,
            "accuracy": accuracy
        }))
        

    # Envia dados de finalização do turno
    def finaliza_round(self, accuracy):
        self.client.publish(topico_end_round, json.dumps({
            "id": self.cliente_data.id,
            "round": self.cliente_data.round,
            "accuracy": accuracy
        }))
    
    # Envia dados para o fim do turno (agregador central -> cliente agregador)
    def finaliza_round_servidor(self, accuracy):
        print(f'Finalizando round (agregador central)')
        self.client.publish(topico_agregador_end_round, json.dumps({
            "id": self.cliente_data.id,
            "round": self.cliente_data.round,
            "accuracy": accuracy
            
        }))


    def wait_queue_fit(self):
        return self.queue_fit.get()

    def wait_queue_evaluate(self):
        return self.queue_evaluate.get()

    def wait_queue_agregador_federated_averaging(self):
        return self.queue_agregador_federated_averaging.get()

    def wait_queue_agregador_federated_averaging_return(self):
        return self.queue_agregador_federated_averaging_return.get()

    # Recebe avaliações parciais dos clientes agregadores
    def wait_queue_agregador_accuracy(self):
        return self.queue_agregador_accuracy.get()