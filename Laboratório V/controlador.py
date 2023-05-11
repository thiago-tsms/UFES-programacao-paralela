import paho.mqtt.client as mqtt
import random
import time
from interface import InterfaceControlador
        

# Parâmetros ( em classe para compartilha-los)
class Params:
    def __init__(self):
        self.transaction_iD = -1    # identifica a transação
        self.challenge = 0          # valor do desafio
        self.solution = 0           # string que se aplicada a solução resolvera o desafio
        self.winer = 0              # id do minirador que resolveu (-1: o desafio não foi resolvido)
        
        self.client = None


fila_solution = "sd/lab5/solution"
fila_challenge = 'sd/lab5/challenge'
fila_result = 'sd/lab5/result'


def inicia_mqtt():
    print(f'* Iniciando MQTT')
    
    client = mqtt.Client("controlado-ufes-lv-controlador")
    client.connect("broker.emqx.io")
    
    # Subscreve em tópicos
    client.subscribe(fila_solution)
    client.on_message = ouvindo_broker
    client.loop_start()
    
    return client
    
    
def finalizar_mqtt(client):
    print("* Finalizando MQTT")
    client.loop_stop()
    client.disconnect()
    

def gerar_novo_desafio(params):
    print(f'* Gerando Novo Desafio')
    
    params.transaction_iD += 1
    params.challenge = random.randint(0, 10)
    params.winner = -1
    
    params.client.publish("sd/lab5/challenge", "Novo desafio:")
    # enviar edsafio padronizado


def ouvindo_broker(client, userdata, msg):
    if msg.topic == fila_solution:
        print(f'{str(msg.payload.decode("utf-8"))}')
    
        # Verificar solução
        # Se ok, atualizar estados e publicar em: fila_result
        # Se não, publicar falso na fila fila_result
    

def run():
    print(f'== Iniciando Controlador ==')
    params = Params()
    interface = InterfaceControlador(params, gerar_novo_desafio)
    
    params.client = inicia_mqtt()
    gerar_novo_desafio(params)
    
    interface.start_loop()
    finalizar_mqtt(params.client)
    print("== Programa Finalizado ==")


if __name__ == '__main__':
    run()    