from mqtt import ComunicacaoMQTTServer

#Parametros de inicialização
nClients = 3
nMinClients = 5
nMaxRouds = 10
MetaAcuracia = 100
TimeOut = 5


def avalia_condicoes_iniciais(id_clientes):
    if len(id_clientes) < nMinClients:
        print(f'Número insuficiente de clientes disponível - min: {nClients} - atual: {len(id_clientes)}')


def run():
    mqtt = ComunicacaoMQTTServer(TimeOut)
    
    # Obtem todos os clientes conectados
    #id_clientes = mqtt.obter_clientes()
    
    # Avalia as condições para início do aprendizado
    #avalia_condicoes_iniciais(id_clientes)
    
    
    
    #print(id_clientes)
    
    while True:
        None
    
    
if __name__ == '__main__':
    run()   