from mqtt import ComunicacaoMQTTServer
import time

#Parametros de inicialização
nClients = 3
nMinClients = 5
nMaxRouds = 10
MetaAcuracia = 100
TimeOut = 5


def aguarda_condicoes_iniciais(mqtt):
    print(f'Aguardando número de clientes')
    while len(mqtt.get_clientes()) < nMinClients:
        time.sleep(1)
    print(f'Aprendizado federado iniciando')


def run():
    mqtt = ComunicacaoMQTTServer(TimeOut)
    
    # Espera o número mínimo de clientes para comessar a execução
    aguarda_condicoes_iniciais(mqtt)
    
   
    while True:
        None
    
    mqtt.finalizar_mqtt()
    
    
if __name__ == '__main__':
    run()   