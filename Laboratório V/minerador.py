import paho.mqtt.client as mqtt
from interface import InterfaceMinerador
import random
import json
from resolucao import ProvaTrabalho


# Parâmetros (em classe para compartilha-los)
class Params:
    def __init__(self):
        self.client_id = random.randint(0,1000)
        self.transaction_id = -1    # identifica a transação
        self.challenge = 0          # valor do desafio
        self.solution = 0           # string que se aplicada a solução resolvera o desafio
        self.winer = 0              # id do minirador que resolveu (-1: o desafio não foi resolvido)
        
        self.client = None

        
fila_solution = "sd/lab5/solution"
fila_challenge = 'sd/lab5/challenge'
fila_result = 'sd/lab5/result'


def inicia_mqtt(params):
    print(f'* Iniciando MQTT')
    
    client_userdata = {'params':params}
    
    client = mqtt.Client(f'controlado-ufes-lv-minerador-{params.client_id}', userdata=client_userdata)
    client.connect("broker.emqx.io")
    
    # Subscreve em tópicos
    client.subscribe(fila_challenge)
    client.subscribe(fila_result)
    client.on_message = ouvindo_broker
    client.loop_start()
    
    return client
    
    
def finalizar_mqtt(client):
    print("* Finalizando MQTT")
    client.loop_stop()
    client.disconnect()
    
    
def ouvindo_broker(client, userdata, msg):
    if msg.topic == fila_challenge:
        msg =  json.loads(str(msg.payload.decode("utf-8")))
        params = userdata['params']
        params.transaction_id = msg['TransactionID']
        params.challenge = msg['Challenge']
        
        print(f'-- Desafio Obtido --')
        print(f'Transação: {params.transaction_id} \nDesafio: {params.challenge}')
        realizando_prova(client, params)
        print(f'--------------------')
        
    elif msg.topic == fila_result:
        print(f'{str(msg.payload.decode("utf-8"))}')


def realizando_prova(client, params):
    print(f'* Iniciando Busca')
    
    pt = ProvaTrabalho()
    (hash, params.solution) = pt.buscar_solucao(params.challenge)
    
    print(f'* Solução: {params.solution}')
    
    msg = {
        'ClientID': params.client_id,
        'TransactionID': params.transaction_id,
        'Solution': params.solution,
    }
    
    params.client.publish(fila_solution, json.dumps(msg))

    
def run():
    print(f'== Iniciando Controlador ==')
    params = Params()
    interface = InterfaceMinerador(params)
    
    params.client = inicia_mqtt(params)
    
    interface.start_loop()
    finalizar_mqtt(params.client)
    print("== Programa Finalizado ==")


if __name__ == '__main__':
    run()