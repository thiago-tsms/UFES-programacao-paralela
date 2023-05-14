import paho.mqtt.client as mqtt 
import flwr as fl
#from random import randrange, uniform
import time
import sys

idClient = ""

def on_message_idclient(client, userdata, message):
    global idClient
    idClient = str(message.payload.decode("utf-8"))


def weighted_average(metrics):
    # Multiply accuracy of each client by number of examples used
    acc = [num_examples * m["accuracy"] for num_examples, m in metrics]
    examples = [num_examples for num_examples, _ in metrics]

    # Aggregate and return custom metric (weighted average)
    results = {"accuracy": sum(acc) / sum(examples)}
    return results

strategy = fl.server.strategy.FedAvg(
    fraction_fit=0.9,           # Escolher aleatoriamento 90% dos clientes
    fraction_evaluate=1,        # Usar todos os clientes para avaliação do modelo
    min_fit_clients=5,          # Minimo de 5 clientes para o treinamento
    min_evaluate_clients=5,    # Mínimo de 5 clientes para avaliação
    min_available_clients=5,    # Mínimo de 5 clientes para comessar o treinamento
    evaluate_metrics_aggregation_fn=weighted_average,   # Usar esta função como função de agregação da métricas
)



# Calcula total de argumentos
n = len(sys.argv)
 
mqttBroker = "broker.emqx.io" 
if len(sys.argv) >= 2:
    mqttBroker = str(sys.argv[1])

print(mqttBroker)

#Parametros de inicialização
nClients = 3
nMinClients = 5
nMaxRouds = 10
MetaAcuracia = 100
TimeOut = 1 #Não entendi bem este aqui

#Filas
fila_idClient = "sd/id/client"

client = mqtt.Client("Server_Federado_1")
client.connect(mqttBroker) 

while True:
    client.loop_start()
    client.subscribe(fila_idClient)
    client.on_message=on_message_idclient
    time.sleep(1)
    client.loop_stop()
    print("ID Client: " + idClient)
    idClient = ""
    
#    randNumber = uniform(0, 100)
    
#    client.publish(topic, randNumber)
    time.sleep(1)
