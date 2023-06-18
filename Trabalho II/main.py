import random
from mqtt import *
from execucao import *
from aprendizado import *
import time


nMaxRouds = 10#int(sys.argv[2])
meta_acuracia = 1#float(sys.argv[3])
accuracy_list = []

input_shape = (28, 28, 1)
num_classes = 10
num_clients = 2#int(sys.argv[1])
grupo = 1

is_agregador_central = False


# Informações do cliente
class ClientesData:
    def __init__(self):
        self.id = random.randint(0, 1000)
        self.grupo = grupo
        self.id_lider = None
        self.round = -1
        self.is_agregador_central = is_agregador_central
        
        
def run():
    # Inicia cliente
    cliente_data = ClientesData()
    
    # Inicia comunicação
    mqtt = Comunicacao(cliente_data)
    
    # Iniciando aprendizado
    (x_train, y_train, x_test, y_test) = obtem_dados(num_clients)
    aprendizado = Aprendizado(x_train, y_train, x_test, y_test, input_shape, num_classes)
    
    # Determina qual execução será realizada
    if cliente_data.is_agregador_central is False:
        execucao_clientes(cliente_data, mqtt, aprendizado)
    else:
        execucao_agregador_central()
    
    # Finaliza o MQTT
    mqtt.finalizar_mqtt()
        
        
def execucao_agregador_central(cliente_data, mqtt, aprendizado):
    agregador_central = AgregadorCentral(cliente_data, mqtt, aprendizado)


def execucao_clientes(cliente_data, mqtt, aprendizado):
    
    current_accuracy = 0
    
    # Instancia classes de execução dos clientes
    cliente_treinador = ClienteTreinador(cliente_data, mqtt, aprendizado)
    cliente_agregador = ClienteAgregador(cliente_data, mqtt, aprendizado)
    
    # Aguarda por um tempo todos os clientes estarem disponíveis
    print(f'* Aguardando Clientes')
    while len(mqtt.lista_clientes) < num_clients:
        time.sleep(0.5)
    print(f'* Grupo: {cliente_data.grupo} - N° Clientes: {len(mqtt.lista_clientes)}')
    time.sleep(10)
    
    # Executa o treinamento
    while current_accuracy < meta_acuracia:
        cliente_data.round = cliente_data.round + 1
        
        # Realiza eleição
        mqtt.eleicao()
        
        # Opera no round
        if cliente_data.id == cliente_data.id_lider:
            current_accuracy = cliente_agregador.run()
        else:
            cliente_treinador.run()
        
        print(current_accuracy)
        time.sleep(5)
    

if __name__ == '__main__':
    run()   