import random
from mqtt import *
from execucao import *
import time


nMaxRouds = 10#int(sys.argv[2])
metaAcuracia = 1#float(sys.argv[3])
accuracy_list = []

input_shape = (28, 28, 1)
num_classes = 10
num_clients = 5#int(sys.argv[1])
grupo = 1

agregador_central = False


# Informações do cliente
class ClientesData:
    def __init__(self):
        self.id = random.randint(0, 1000)
        self.grupo = grupo
        self.id_lider = None
        self.round = -1
        self.agregador_central = agregador_central
        
        
def run():
    # Inicia cliente
    cliente_data = ClientesData()
    
    # Inicia comunicação
    mqtt = Comunicacao(cliente_data)
    
    if agregador_central is False:
        print(f'* Aguardando Clientes')
        while len(mqtt.lista_clientes) < num_clients:
            time.sleep(0.5)
        print(f'* Grupo: {cliente_data.grupo} - N° Clientes: {len(mqtt.lista_clientes)}')
        time.sleep(10)
        
            
        while True:
            mqtt.eleicao()
            cliente_data.round = cliente_data.round + 1
            
            if cliente_data.id == cliente_data.id_lider:
                execucao = Agregador(cliente_data, mqtt, (num_clients, input_shape, num_classes, metaAcuracia, nMaxRouds))
            else:
                execucao = Cliente(cliente_data, mqtt, (num_clients, input_shape, num_classes, metaAcuracia, nMaxRouds))
                
            execucao.run()
            
            time.sleep(5)
        
        else:
            execucao = AgregadorCentral(cliente_data, mqtt, (num_clients, input_shape, num_classes, metaAcuracia, nMaxRouds), accuracy_list)

    # Realiza eleição
    mqtt.eleicao()
    

if __name__ == '__main__':
    run()   