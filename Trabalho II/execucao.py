import random
import time


# Realiza tarefa do cliente treinador
class ClienteTreinador():
    def __init__(self, cliente_data, mqtt, aprendizado):
        self.cliente_data = cliente_data
        self.mqtt = mqtt
        self.aprendizado = aprendizado
        self.mqtt.set_client_func(self.executar_aprendizado, self.avaliar_aprendizado, self.adicionar_pesos)
    
    def adicionar_pesos(self, weight):
        self.aprendizado.set_weights(self.aprendizado.re_shape(weight))
        
    def executar_aprendizado(self, weight):
        if weight:
            weight = self.aprendizado.re_shape(weight)
        return self.aprendizado.fit(weight)

    def avaliar_aprendizado(self, weight):
        accuracy = self.aprendizado.evaluate(self.aprendizado.re_shape(weight))[2]['accuracy']
        print(f'** Resultado Alcançado: {accuracy} **')
        return accuracy

    def run(self):
        print(f"** Cliente ID: {self.cliente_data.id} -- Round: {self.cliente_data.round} - Grupo: {self.cliente_data.grupo}")
        
        self.mqtt.aguarda_end_round()
            

# Realiza tarefas do cliente agregador
class ClienteAgregador():
    def __init__(self, cliente_data, mqtt, aprendizado):
        self.cliente_data = cliente_data
        self.mqtt = mqtt
        self.aprendizado = aprendizado
    
    
    # Seleciona os integrantes para fazer parte do round
    def seleciona_integrantes(self, n_integrantes):
        aux_1 = self.mqtt.lista_clientes.copy()
        aux_1.remove(self.cliente_data.id)
        
        if len(aux_1) > n_integrantes:
            n = n_integrantes
        else:
            n = len(aux_1)
        
        return random.sample(aux_1, n)
    
    
    def run(self):
        pesos_recebidos = []
        id_peso_recebidos = []
        avaliacao = []
        id_avaliacao = []
        print(f"** Agregador ID: {self.cliente_data.id} -- Round: {self.cliente_data.round} - Grupo: {self.cliente_data.grupo}")
         
        # Envia dados para aprendizado para clientes determinados
        clientes_enviados = self.mqtt.enviar_peso_fit(self.seleciona_integrantes(3), None)
        
        # Recebe todos os pesos
        for _ in range(len(clientes_enviados)):
            (id, weight) = self.mqtt.wait_queue_fit()
            id_peso_recebidos.append(id)
            pesos_recebidos.append(self.aprendizado.re_shape(weight))
        
        # Efetua a agregação
        new_weight = self.aprendizado.federated_averaging(pesos_recebidos)
        
    
        ###
        # AÇÕES DO AGREGADOR CENTRAL
        ###
        
        
        # Envia pesos agergados
        #self.mqtt.envia_peso(new_weight)
        
        # Envia pesos para avaliação (enviando para todos) / Faz a avaliação global
        clientes_enviados = self.mqtt.envia_pesos_avaliacao(new_weight)
        local_evaluate = self.aprendizado.evaluate(new_weight)
        avaliacao.append(local_evaluate[2]['accuracy'])
        
        # Recebe todos os pesos
        for _ in range(len(clientes_enviados)):
            (id, accuracy) = self.mqtt.wait_queue_evaluate()
            id_avaliacao.append(id)
            avaliacao.append(accuracy)
        
        
        accuracy = sum(avaliacao)/len(avaliacao)
        
        time.sleep(2)
        self.mqtt.finaliza_round()
        
        return accuracy

 
 # Realiza tarefas do agregador central
class AgregadorCentral():
    def __init__(self, cliente_data, mqtt, aprendizado):
        #self.accuracy_list = accuracy_list
        print(f"** Agregador Central-- Round: {self.cliente_data.round} - ID: {self.cliente_data.id}")
        
        while True:
            None
        






     
        
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
    # def escolha_integrantes(self):
    #     aux_1 = self.mqtt.lista_clientes.copy()
    #     aux_1.remove(self.cliente_data.id)
    #     aux_2 = random.sample(aux_1, 3)