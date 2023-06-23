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
        
        accuracy = self.mqtt.aguarda_end_round()[2]['accuracy']
        
        return accuracy
            

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
        # INICIO -- AGREGADOR CENTRAL
        ###
        
        self.mqtt.envia_pesos_agergador_avaliacao(new_weight)
        (origin_id, new_weight, accuracy) = self.wait_queue_agregador_federated_averaging_return()
        #avaliacao.append(accuracy[2]['accuracy'])
        new_weight = self.aprendizado.re_shape(new_weight)
        self.aprendizado.set_weights(new_weight)
        
        ###
        # FIM -- AGREGADOR CENTRAL
        ###
        
        
        # Envia pesos agergados (pesos já são setados no modelo no processo de avaliação dos resultados)
        #self.mqtt.envia_peso(new_weight)
        
        # Envia pesos para avaliação (enviando para todos) / Faz a avaliação global
        local_evaluate = self.aprendizado.evaluate(new_weight)
        clientes_enviados = self.mqtt.envia_pesos_avaliacao(new_weight)
        avaliacao.append(local_evaluate[2]['accuracy'])
        
        # Recebe todos os pesos
        for _ in range(len(clientes_enviados)):
            (id, accuracy) = self.mqtt.wait_queue_evaluate()
            id_avaliacao.append(id)
            avaliacao.append(accuracy)
        
        aux = [a[2]['accuracy'] for a in avaliacao]
        accuracy = sum(aux)/len(aux)
        
        
        ###
        # INICIO -- AGREGADOR CENTRAL
        ###
        
        # Envia accuracy para o agregador central
        self.mqtt.envia_accuracy_agregador(accuracy)
        
        # Recebe accuracy final do round
        accuracy = self.mqtt.aguarda_agregador_end_round()[2]['accuracy']
        
        ###
        # FIM -- AGREGADOR CENTRAL
        ###
        
        time.sleep(2)
        
        # Aguarda fim do round (clientes)
        self.mqtt.finaliza_round(accuracy)
        
        return accuracy

 
 # Realiza tarefas do agregador central
class AgregadorCentral():
    def __init__(self, cliente_data, mqtt, aprendizado):
        self.cliente_data = cliente_data
        self.mqtt = mqtt
        self.aprendizado = aprendizado
        
        print(f"** Agregador Central-- Round: {self.cliente_data.round} - ID: {self.cliente_data.id}")
        
        while True:
            cliente_data.round = cliente_data.round + 1
            pesos_recebidos = []
            avaliacao = []
            
            # Aguarda os pesos para agregação
            for _ in range(1):
                weight = self.wait_queue_agregador_federated_averaging()
                pesos_recebidos.append(self.aprendizado.re_shape(weight))
            
            # Efetua a agregação dos pesos
            new_weight = self.aprendizado.federated_averaging(pesos_recebidos)
            local_evaluate = self.aprendizado.evaluate(new_weight)
            
            # Envia os pesos
            self.mqtt.devolve_pesos_agergador_avaliacao(new_weight, local_evaluate)
            
            # Receba a avaliação dos clientes agregadores
            for _ in range(1):
                avaliacao.append(self.mqtt.wait_queue_agregador_accuracy())
            
            aux = [a[2]['accuracy'] for a in avaliacao]
            accuracy = sum(aux)/len(aux)
            
            # Envia a avaliação para os clientes agregadores e finaliza o round
            self.mqtt.finaliza_round_servidor(accuracy)