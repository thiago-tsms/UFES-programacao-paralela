import paho.mqtt.client as mqtt
import random
import time

    # identifica a transação
transaction_iD = 0

    # valor do desafio
challenge = 0

    # string que se aplicada a solução resolvera o desafio
solution = 0

    # id do minirador que resolveu
winner = 0

    # solução usada pelo cliente
fila_solution = "sd/lab5/solution"
fila_challenge = 'sd/lab5/challenge'
fila_result = 'sd/lab5/result'



def run():
    print(f'Iniciando Controlador')

    challenge = random.randint(0, 10)

    client = mqtt.Client("controlado-ufes-lv")
    client.connect("broker.emqx.io")
    #client.connect("10.9.13.138", 1883)

    while True:
        print(f'Enviando')
        client.publish(fila_solution, "teste")
        time.sleep(2)


if __name__ == '__main__':
    run()