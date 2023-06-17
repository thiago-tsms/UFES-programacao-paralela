from aprendizado import *
import random


num_clients = None
input_shape = None
num_classes = None
metaAcuracia = None
nMaxRouds = None


class Execucao:
    def __init__(self, cliente_data, mqtt, params):
        self.cliente_data = cliente_data
        self.mqtt = mqtt
        
        global num_clients
        global input_shape
        global num_classes
        global metaAcuracia
        global nMaxRouds
        
        (num_clients, input_shape, num_classes, metaAcuracia, nMaxRouds) = params
        
        (x_train, y_train, x_test, y_test) = obtem_dados(num_clients)
        self.aprendizado = Aprendizado(x_train, y_train, x_test, y_test, input_shape, num_classes)


class Cliente(Execucao):
    def __init__(self, cliente_data, mqtt, params):
        super().__init__(cliente_data, mqtt, params)
        #self.mqtt.set_client_func(self.executar_aprendizado, self.avaliar_aprendizado)
        print(f"** Cliente -- Round: {self.cliente_data.round} - Grupo: {self.cliente_data.grupo} - Cliente: {self.cliente_data.id}")
        
    # def executar_aprendizado(self, weight):
    #     return self.aprendizado.fit(self.aprendizado.re_shape(weight))

    # def avaliar_aprendizado(self, weight):
    #     accuracy = self.aprendizado.evaluate(self.aprendizado.re_shape(weight))[2]['accuracy']
    #     print(f'** Resultado Alcançado: {accuracy} **')
    #     return accuracy

    def run(self):
        while True:
            None
            

class Agregador(Execucao):
    def __init__(self, cliente_data, mqtt, params):
        super().__init__(cliente_data, mqtt, params)
        print(f"** Agregador -- Round: {self.cliente_data.round} - Grupo: {self.cliente_data.grupo} - Cliente: {self.cliente_data.id}")
    
    def run(self):
        aux_1 = self.mqtt.lista_clientes.copy()
        aux_1.remove(self.cliente_data.id)
        
        if len(aux_1) > 3:
            n = 3
        else:
            n = len(aux_1)
        
        integrantes = random.sample(aux_1, n)
        print(integrantes)
        
        # Envia dados para aprendizado para clientes determinados
        self.mqtt.enviar_peso(integrantes, self.aprendizado.get_weights())
        
        
    #     print(f'* Aprendizado Federado Iniciando')
        
    #     model_weights = self.aprendizado.get_weights()
    #     all_accuracy = []
        
    #     # Executa o máximo d iterações
    #     for round in range(nMaxRouds):
    #         all_weights = []
            
    #         # Enviar gradientes
    #         n_clientes_enviados = self.mqtt.enviar_peso(model_weights)
            
    #         # Espera a recepção de todos os pesos (-1 server)
    #         for _ in range(n_clientes_enviados):
    #             all_weights.append(self.aprendizado.re_shape(self.mqtt.wait_return_weights()))
            
    #         model_weights = self.aprendizado.federated_averaging(all_weights)
            
    #         evaluate = self.aprendizado.evaluate(model_weights)
    #         accuracy = evaluate[2]['accuracy']
    #         accuracy_list.append((round, accuracy))
    #         #all_accuracy.append(accuracy)
            
    #         print(f'-- Round: {round+1} - Accuracy: {accuracy}')
            
    #         if accuracy >= metaAcuracia:
    #             break
            
    #     # Envia para todos os clientes o modelo final
    #     n_clientes_enviados = self.mqtt.envia_acuracia(model_weights)


    #     # Espera a recepção de todos
    #     for _ in range(n_clientes_enviados):
    #         all_accuracy.append(self.mqtt.wait_return_acuracia())
    #         accuracy = sum(all_accuracy)/len(all_accuracy)


    #     print('* Aprendizado Federado Finalizado')
    #     print(f'** Resultado Alcançado: {accuracy} **')

    #     self.mqtt.finalizar_mqtt()
        
    #     with open(f'results/result_{num_clients}.csv', "w") as arquivo:
    #         for a in accuracy_list:
    #             arquivo.write(f'{a[0]+1};{a[1]}\n')
        
    #     with open(f'results/result_final.csv', "a") as arquivo:
    #         arquivo.write(f'{num_clients};{accuracy}\n')


    # Escolhe os componentes para executar o aprendizado
    def escolha_integrantes(self):
        aux_1 = self.mqtt.lista_clientes.copy()
        aux_1.remove(self.cliente_data.id)
        aux_2 = random.sample(aux_1, 3)
 
class AgregadorCentral(Execucao):
    def __init__(self, cliente_data, mqtt, params, accuracy_list):
        self.accuracy_list = accuracy_list
        super().__init__(cliente_data, mqtt, params)
        print(f"** Agregador Central-- Round: {self.cliente_data.round} - ID: {self.cliente_data.id}")
        
        while True:
            None