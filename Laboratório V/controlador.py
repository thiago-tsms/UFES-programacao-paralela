import paho.mqtt.client as mqtt
import random
from interface import InterfaceControlador
import json
from resolucao import ProvaTrabalho
        

# Parâmetros (em classe para compartilha-los)
class Params:
    def __init__(self):
        self.transaction_id = -1    # identifica a transação
        self.challenge = 0          # valor do desafio
        self.solution = 0           # string que se aplicada a solução resolvera o desafio
        self.winer = 0              # id do minirador que resolveu (-1: o desafio não foi resolvido)
        
        self.desafio_em_andamento = False
        
        self.client = None
        

fila_solution = "sd/lab5/solution"
fila_challenge = 'sd/lab5/challenge'
fila_result = 'sd/lab5/result'


def inicia_mqtt(params):
    print(f'* Iniciando MQTT')

    client_userdata = {'params':params}
    
    client = mqtt.Client("controlado-ufes-lv-controlador", userdata=client_userdata)
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
    print(f'\n* Gerando Novo Desafio')
    
    params.transaction_id += 1
    params.challenge = random.randint(0, 10)
    params.winner = -1
    params.desafio_em_andamento = True
    
    msg = {
        'TransactionID': params.transaction_id,
        'Challenge': params.challenge
    }
    
    # Enviar desafio padronizado
    params.client.publish(fila_challenge, json.dumps(msg))
    
    print(f'-- TransactionID: {params.transaction_id} \n-- Desafio: {params.challenge} \n')
    

def ouvindo_broker(client, userdata, msg):

    params = userdata['params']
    pt = ProvaTrabalho()
    
    if msg.topic == fila_solution:
        print(f'\n* Solução Recebida')

        msg = json.loads(str(msg.payload.decode("utf-8")))
        client_id = msg['ClientID']
        transaction_id = msg['TransactionID']
        solution = msg['Solution']

        print(f'-- ClientID: {client_id} \n-- TransactionID: {transaction_id} \n-- Solution: {solution}')

        # Desafio não corrente
        if params.transaction_id != transaction_id:
            print(f'-- Não exisiste esse desafio')
        
        # Desafio já solucionado
        elif params.winer != -1:
            print('-- Este desafio já foi solucionado \nWinner: {params.winer}')
        
        # Solução correta
        elif pt.avaliar_hash(params.challenge, pt.gerar_hash(solution)):
            print(f'* Aprovado')

            params.winer = client_id
            params.solution = solution
            params.desafio_em_andamento = False
            
            msg = {
                'ClientID': client_id,
                'TransactionID': transaction_id,
                'Solution': solution,
                'Result': 1
            }
            
            params.client.publish(fila_result, json.dumps(msg))
        
        # Solução incorreta
        else:
            print(f'* Reprovado')
            
            msg = {
                'ClientID': client_id,
                'TransactionID': transaction_id,
                'Solution': solution,
                'Result': -1
            }
            
            params.client.publish(fila_result, json.dumps(msg))
        
        print()
    

def run():
    print(f'== Iniciando Controlador ==')
    params = Params()
    interface = InterfaceControlador(params, gerar_novo_desafio)
    
    params.client = inicia_mqtt(params)
    gerar_novo_desafio(params)
    
    interface.start_loop()
    finalizar_mqtt(params.client)
    print("== Programa Finalizado ==")


if __name__ == '__main__':
    run()    