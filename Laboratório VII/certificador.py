import sys
from crypto import *
from mqtt import *
from execucao import ClientesData
import time

nClients = int(sys.argv[1])

def run():
    # Inicia dados de execução do cliente
    cliente_data = ClientesData()
    
    # Inicia comunicação
    mqtt = Comunicacao(cliente_data, None)
    mqtt.subscribe_certificador()

    print(f'* Aguardando Clientes')
    while len(cliente_data.lista_certificados) < nClients:
        time.sleep(0.5)
    
    time.sleep(6)
    

if __name__ == '__main__':
    run()