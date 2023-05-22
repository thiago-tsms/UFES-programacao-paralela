from mqtt import ComunicacaoMQTTServer
from aprendizado import *
import time


#Parametros de inicialização
nClients = 2
nMaxRouds = 4
MetaAcuracia = 0.98
TimeOut = 5

input_shape = (28, 28, 1)
num_classes = 10
num_clients = 10


def aguarda_condicoes_iniciais(mqtt):
    print(f'Aguardando número de clientes')
    while len(mqtt.get_clientes()) < nClients:
        time.sleep(1)
    

def convert(res, lista):
    for i in lista:
        return res.append

def run():
    mqtt = ComunicacaoMQTTServer(TimeOut)
    
    # Espera o número mínimo de clientes para comessar a execução
    #aguarda_condicoes_iniciais(mqtt)
    
    (x_train, y_train, x_test, y_test) = obtem_dados(num_clients)
    aprendizado = Aprendizado(x_train, y_train, x_test, y_test, input_shape, num_classes)
    
    #res = aprendizado.get_weights()
    
    model_weights = aprendizado.get_weights()
    
    # Espera ter o número mínimo de clientes para comessar a execução
    aguarda_condicoes_iniciais(mqtt)

    print(f'Aprendizado federado iniciando')
    
    for _ in range(nMaxRouds):
        all_weights = []
    
        # Tenta enviar os gradientes // retorna para quantos estão ouvindo
        n_clientes = mqtt.start_aprendizado(model_weights)
        
        # Espera a recepção de todos
        for _ in range(n_clientes):
            all_weights.append(aprendizado.re_shape(mqtt.get_gradientes()))
        
        model_weights = aprendizado.federated_averaging(model_weights, all_weights)
        
        evaluate = aprendizado.evaluate(model_weights)
        #print(evaluate)
        
        if evaluate[2]['accuracy'] >= MetaAcuracia:
            break
     
    print('Aprendizado finalizado')

    mqtt.finalizar_mqtt()
    
    
if __name__ == '__main__':
    run()   