import paho.mqtt.client as mqtt
import json

topico_get_clientes = "sd/tr1/get_clientes"
topico_send_dados_clientes = "sd/tr1/send_dados_clientes"
#topico_send_gradiente = "sd/tr1/send_gradiente"
#topico_recv_gradiente = "sd/tr1/recv_gradiente"


class Parametros:
    def __init__(self):
        self.id = 0


class ComunicacaoMQTT():   

    def __init__(self):
        print(f'Iniciando MQTT')
    
    # Inicia o MQTT
    def inicia_mqtt(self, client_name):
        #"controlador-federado-ufes"
        self.client = mqtt.Client(client_name)
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
    
    # Se inscreve nos tópicos (server)
    def subscribe_server(self):

        self.client.subscribe(topico_send_dados_clientes)
        
        self.client.on_message = self.on_message_server
        self.client.loop_start()
    

    # Escuta as mansagens (cliente)
    def on_message_client(self, client, userdata, msg):

        # Recebe solicitação de id do cliente
        if msg.topic == topico_get_clientes:
            new_msg = {
                'id': 0
            }

            #self.params.client.publish(topico_get_clientes, json.dumps(new_msg))
            print(f'\n{str(msg.payload.decode("utf-8"))}\n')
    

    # Escuta as mansagens (server)
    def on_message_server(self, client, userdata, msg):

        # Recebe o id de todos os clientes
        if msg.topic == topico_send_dados_clientes:
            print(f'\n{str(msg.payload.decode("utf-8"))}\n')
    

    # Solicita o id de todos os clientes (server)
    def obter_clientes(self):
        self.params.client.publish(topico_get_clientes, "solicita id")