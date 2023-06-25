import sys
import random
from mqtt import *
from execucao import *
from aprendizado import *
import time


nMaxRouds = int(sys.argv[4])
meta_acuracia = float(sys.argv[5])
accuracy_list = []

input_shape = (28, 28, 1)
num_classes = 10
num_clients = int(sys.argv[3])
grupo = int(sys.argv[2])

is_agregador_central = int(sys.argv[1])


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
        execucao_agregador_central(cliente_data, mqtt, aprendizado)
    
    # Finaliza o MQTT
    mqtt.finalizar_mqtt()
        
        
def execucao_agregador_central(cliente_data, mqtt, aprendizado):
    current_accuracy = 0
    end_resul = []
    agregador_central = AgregadorCentral(cliente_data, mqtt, aprendizado)
    
    while (current_accuracy < meta_acuracia) and (cliente_data.round < nMaxRouds):
        current_accuracy = agregador_central.run()
        end_resul.append((cliente_data.round, current_accuracy))
        print(f'\n*** CONTROLE:: round: {cliente_data.round}/{nMaxRouds} -- acuracy: {current_accuracy}/{meta_acuracia} ***\n')
    
    with open(f'results/result_{num_clients}.csv', "w") as arquivo:
        for a in end_resul:
            arquivo.write(f'{a[0]};{a[1]}\n')
        


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
    
    # Executa o treinamento
    while (current_accuracy < meta_acuracia) and (cliente_data.round < nMaxRouds):
        cliente_data.round = cliente_data.round + 1
        
        # Realiza eleição
        mqtt.set_checkpoint()
        mqtt.eleicao(len(mqtt.lista_clientes))
        mqtt.set_checkpoint()
        
        # Opera no round
        if cliente_data.id == cliente_data.id_lider:
            current_accuracy = cliente_agregador.run()
        else:
            current_accuracy = cliente_treinador.run()
        
        print(f'\n*** CONTROLE:: round: {cliente_data.round}/{nMaxRouds} -- acuracy: {current_accuracy}/{meta_acuracia} ***\n')
    

if __name__ == '__main__':
    if is_agregador_central == 0:
        is_agregador_central = False
    else:
        is_agregador_central = True
    
    run()   