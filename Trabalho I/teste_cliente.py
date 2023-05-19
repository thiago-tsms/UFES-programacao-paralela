from mqtt import ComunicacaoMQTTCliente
#from aprendizado import *


input_shape = (28, 28, 1)
num_classes = 10
num_clients = 10


#(x_train, y_train, x_test, y_test) = obtem_dados(num_clients)
#aprendizado = Aprendizado(x_train, y_train, x_test, y_test, input_shape, num_classes)


# Efetua as operações de cada iteração
def executa_aprendizado(msg):
    print(msg)
    
    # Efetua o aprendizado e retorna os gradientes
    #return aprendizado.fit(grad)


def run():
    mqtt = ComunicacaoMQTTCliente(executa_aprendizado)
    
    # Dentro do MQTT tem uma função que esta escutando as mensagens

    while True:
        None
    
    mqtt.finalizar_mqtt()


if __name__ == '__main__':
    run()   