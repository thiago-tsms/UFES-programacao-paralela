import paho.mqtt.client as mqtt
import random

host = "localhost"
topico_peso_client_to_server = 'sd/tr2/peso/client_to_server'
topico_peso_server_to_client = 'sd/tr2/peso/server_to_client'

num_grupos = 2


# Recebe as mensagens
def handler(client, userdata, msg):
    data = msg.payload
    
    if msg.topic == topico_peso_client_to_server:
        print(data)
        client.publish(topico_peso_server_to_client, data)


# Após conectar
def conect(client, userdata, flags, rc):
    client.subscribe(topico_peso_client_to_server)


def run():
    
    # Conexão MQTT
    client = mqtt.Client(f'agregador-{random.random()}')
    client.connect(host)
    client.on_message = handler
    client.on_connect = conect
    
    return client
    

if __name__ == '__main__':
    client = run()
    client.loop_forever()