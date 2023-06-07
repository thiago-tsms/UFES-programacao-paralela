import sys
from mqtt import *
import random
from resolucao import ProvaTrabalho
from interface import InterfaceMinerador, InterfaceControlador


nClients = int(sys.argv[1])

# Dados relacionados ao cliente
class ClientesData:
    def __init__(self):
        self.id = random.randint(0, 1000)
        self.id_lider = None
        self.transaction_id = -1
        self.challenge = None
        self.solution = None
        self.winner = -1 #(-1: desafio não solucionado)
        self.desafio_em_andamento = False
  
  
# Gerar um novo desafio
def gerar_desafio(cliente_data, mqtt):
        cliente_data.transaction_id += 1
        cliente_data.challenge = random.randint(1, 10)
        cliente_data.winner = -1
        cliente_data.desafio_em_andamento = True
        
        msg = {
            'id': cliente_data.id,
            'TransactionID': cliente_data.transaction_id,
            'Challenge': cliente_data.challenge
        }
        
        # Enviar desafio padronizado
        mqtt.client.publish(topico_challenge, json.dumps(msg))
        
        print(f' Gerando Novo Desafio \n-- TransactionID: {cliente_data.transaction_id} \n-- Desafio: {cliente_data.challenge} \n')


def run():
    # Inicia dados de execução do cliente
    cliente_data = ClientesData()
    
    # Inicia comunicação
    mqtt = Comunicacao(cliente_data, ProvaTrabalho())
    
    print(f'* Aguardando Clientes')
    while len(mqtt.lista_clientes) < nClients:
        time.sleep(0.5)

    # Realiza eleição
    mqtt.eleicao()
    
    # Inicia execução
    if cliente_data.id == cliente_data.id_lider:
        # Inicia interface do Coordenador
        interface = InterfaceControlador(cliente_data, lambda func: gerar_desafio(cliente_data, mqtt))
        
        # Gera desafio inicial
        gerar_desafio(cliente_data, mqtt)
    else:
        # Inicia interdace do Minerador
        interface = InterfaceMinerador(cliente_data)
    
    # Mantem programa em execução e carrega a interface
    interface.start_loop()
    

    # Finaliza comunicação
    mqtt.finalizar_mqtt()

if __name__ == '__main__':
    run()   