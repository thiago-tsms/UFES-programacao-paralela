import sys
from mqtt import ComunicacaoMQTTServer
from aprendizado import *
import time


#Parametros de inicialização
nClients = int(sys.argv[1])
nMaxRouds = int(sys.argv[2])
MetaAcuracia = float(sys.argv[3])
accuracy_list = []

input_shape = (28, 28, 1)
num_classes = 10
num_clients = 10


def aguarda_condicoes_iniciais(mqtt):
    print(f'* Aguardando Clientes')
    while len(mqtt.get_clientes()) < nClients:
        time.sleep(1)
    

def convert(res, lista):
    for i in lista:
        return res.append

def run():
    mqtt = ComunicacaoMQTTServer()
        
    (x_train, y_train, x_test, y_test) = obtem_dados(num_clients)
    aprendizado = Aprendizado(x_train, y_train, x_test, y_test, input_shape, num_classes)
    
    model_weights = aprendizado.get_weights()
    all_accuracy = []
    
    # Espera ter o número mínimo de clientes para começar a execução
    aguarda_condicoes_iniciais(mqtt)

    print(f'* Aprendizado Federado Iniciando')
    
    for round in range(nMaxRouds):
        all_weights = []
        rounds_executados = round
    
        # Tenta enviar os gradientes // retorna para quantos estão ouvindo
        n_clientes = mqtt.start_aprendizado(model_weights)
        
        # Espera a recepção de todos
        for _ in range(n_clientes):
            all_weights.append(aprendizado.re_shape(mqtt.get_gradientes()))
        
        model_weights = aprendizado.federated_averaging(all_weights)
        
        evaluate = aprendizado.evaluate(model_weights)
        accuracy = evaluate[2]['accuracy']
        accuracy_list.append((round, accuracy))
        all_accuracy.append(accuracy)
        
        print(f'-- Round: {round+1} - Accuracy: {accuracy}')
        
        if accuracy >= MetaAcuracia:
            break
     
    # Envia para todos os clientes o modelo final
    mqtt.envia_modelo_final(model_weights)


    # Espera a recepção de todos
    for _ in range(n_clientes):
        all_accuracy.append(mqtt.recebe_pesos_finais())
        accuracy = sum(all_accuracy)/len(all_accuracy)


    print('* Aprendizado Federado Finalizado')
    print(f'** Resultado Alcançado: {accuracy} **')

    mqtt.finalizar_mqtt()
    
    with open(f'results/result_{nClients}.csv', "w") as arquivo:
        for a in accuracy_list:
            arquivo.write(f'{a[0]+1};{a[1]}\n')
    
    with open(f'results/result_final.csv', "w") as arquivo:
        arquivo.write(f'{nClients};{accuracy}\n')
    

if __name__ == '__main__':
    run()   