import paho.mqtt.client as mqtt
import json
import random

topico_get_clientes = "sd/tr1/get_clientes"
#topico_send_dados_clientes = "sd/tr1/send_dados_clientes"
#topico_send_gradiente = "sd/tr1/send_gradiente"
#topico_recv_gradiente = "sd/tr1/recv_gradiente"


class Parametros:
    def __init__(self):
        self.id = -1


class ComunicacaoMQTTServer():   

    def __init__(self):
        self.inicia_mqtt()
        self.subscribe_server()
        self.lista_clientes = []
    
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

        self.client.subscribe(topico_get_clientes)
        
        self.client.on_message = self.on_message_server
        self.client.loop_start()

    # Escuta as mansagens (server)
    def on_message_server(self, client, userdata, msg):

        # Recebe o id de todos os clientes
        if msg.topic == topico_get_clientes:
            msg = json.loads(str(msg.payload.decode("utf-8")))
            id = msg['id']

            if id != -1:
                print(f'{msg}\n')
    

    # Solicita o id de todos os clientes (server)
    def obter_clientes(self):
        new_msg = {
            'id': -1
        }
        self.params.client.publish(topico_get_clientes, json.dumps(new_msg))


class ComunicacaoMQTTCliente():

    def __init__(self):
        self.params = Parametros()
        self.params.id = random.randint(0, 1000)

        self.inicia_mqtt()
        self.subscribe_client()
    
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

        self.client.subscribe(topico_get_clientes)

        self.client.on_message = self.on_message_client
        self.client.loop_start()
    
    # Escuta as mansagens (cliente)
    def on_message_client(self, client, userdata, msg):

        # Recebe solicitação de id do cliente
        if msg.topic == topico_get_clientes:
            msg = json.loads(str(msg.payload.decode("utf-8")))

            msg = json.loads(str(msg.payload.decode("utf-8")))
            id = msg['id']

            if id == -1:
                new_msg = {
                    'id': self.params.id
                }
                self.params.client.publish(topico_get_clientes, json.dumps(new_msg))
            