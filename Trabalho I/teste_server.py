from mqtt import ComunicacaoMQTTServer
from aprendizado import *
import time


#Parametros de inicialização
nClients = 3
nMinClients = 1
nMaxRouds = 10
MetaAcuracia = 100
TimeOut = 5

input_shape = (28, 28, 1)
num_classes = 10
num_clients = 10


def aguarda_condicoes_iniciais(mqtt):
    print(f'Aguardando número de clientes')
    while len(mqtt.get_clientes()) < nMinClients:
        time.sleep(1)
    print(f'Aprendizado federado iniciando')


def run():
    mqtt = ComunicacaoMQTTServer(TimeOut)
    
    # Espera o número mínimo de clientes para comessar a execução
    aguarda_condicoes_iniciais(mqtt)
    
    (x_train, y_train, x_test, y_test) = obtem_dados(num_clients)
    aprendizado = Aprendizado(x_train, y_train, x_test, y_test, input_shape, num_classes)
    
    grad = aprendizado.get_parameters()
    
    
    while True:
        
        # Tenta enviar os gradientes
        mqtt.start_iteracao(grad)
        time.sleep(10)
    
    mqtt.finalizar_mqtt()
    
    
if __name__ == '__main__':
    run()   