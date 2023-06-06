import sys
from mqtt import *
from aprendizado import *
import random


#Parametros de inicialização
nMaxRouds = int(sys.argv[2])
MetaAcuracia = float(sys.argv[3])
accuracy_list = []

input_shape = (28, 28, 1)
num_classes = 10
num_clients = int(sys.argv[1])


class ClientesData:
    def __init__(self):
        self.id = random.randint(0, 1000)
        self.id_lider = None


class Execucao:
    def __init__(self, cliente_data, mqtt):
        self.cliente_data = cliente_data
        self.mqtt = mqtt
        
        (x_train, y_train, x_test, y_test) = obtem_dados(num_clients)
        self.aprendizado = Aprendizado(x_train, y_train, x_test, y_test, input_shape, num_classes)

class Cliente(Execucao):
    def __init__(self, cliente_data, mqtt):
        super().__init__(cliente_data, mqtt)
        self.mqtt.set_client_func(self.executar_aprendizado, self.avaliar_aprendizado)
        print("** Cliente")
        
    def executar_aprendizado(self, weight):
        return self.aprendizado.fit(self.aprendizado.re_shape(weight))

    def avaliar_aprendizado(self, weight):
        accuracy = self.aprendizado.evaluate(self.aprendizado.re_shape(weight))[2]['accuracy']
        print(f'** Resultado Alcançado: {accuracy} **')
        return accuracy

    def run(self):
        while True:
            None
            

class Servidor(Execucao):
    def __init__(self, cliente_data, mqtt):
        super().__init__(cliente_data, mqtt)
        print("** Servidor Agregador")
    
    def run(self):
        print(f'* Aprendizado Federado Iniciando')
        
        model_weights = self.aprendizado.get_weights()
        all_accuracy = []
        
        # Executa o máximo d iterações
        for round in range(nMaxRouds):
            all_weights = []
            
            # Enviar gradientes
            n_clientes_enviados = self.mqtt.enviar_peso(model_weights)
            
            # Espera a recepção de todos os pesos (-1 server)
            for _ in range(n_clientes_enviados):
                all_weights.append(self.aprendizado.re_shape(self.mqtt.wait_return_weights()))
            
            model_weights = self.aprendizado.federated_averaging(all_weights)
            
            evaluate = self.aprendizado.evaluate(model_weights)
            accuracy = evaluate[2]['accuracy']
            accuracy_list.append((round, accuracy))
            #all_accuracy.append(accuracy)
            
            print(f'-- Round: {round+1} - Accuracy: {accuracy}')
            
            if accuracy >= MetaAcuracia:
                break
            
        # Envia para todos os clientes o modelo final
        n_clientes_enviados = self.mqtt.envia_acuracia(model_weights)


        # Espera a recepção de todos
        for _ in range(n_clientes_enviados):
            all_accuracy.append(self.mqtt.wait_return_acuracia())
            accuracy = sum(all_accuracy)/len(all_accuracy)


        print('* Aprendizado Federado Finalizado')
        print(f'** Resultado Alcançado: {accuracy} **')

        self.mqtt.finalizar_mqtt()
        
        with open(f'results/result_{num_clients}.csv', "w") as arquivo:
            for a in accuracy_list:
                arquivo.write(f'{a[0]+1};{a[1]}\n')
        
        with open(f'results/result_final.csv', "a") as arquivo:
            arquivo.write(f'{num_clients};{accuracy}\n')
        
        
def run():
    # Inicia cliente
    cliente_data = ClientesData()
    
    # Inicia comunicação
    mqtt = Comunicacao(cliente_data)
    
    print(f'* Aguardando Clientes')
    while len(mqtt.lista_clientes) < num_clients:
        time.sleep(0.5)

    # Realiza eleição
    mqtt.eleicao()
    
     # Inicia execução
    if cliente_data.id == cliente_data.id_lider:
        execucao = Servidor(cliente_data, mqtt)
    else:
        execucao = Cliente(cliente_data, mqtt)

    execucao.run()


if __name__ == '__main__':
    run()   