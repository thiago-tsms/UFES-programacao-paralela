from mqtt import *

nClients = 2

def aguarda_grupo(mqtt):
    print(f'* Aguardando Clientes')
    while len(mqtt.lista_clientes) < nClients:
        time.sleep(0.5)

def run():
    mqtt = Comunicacao()
    aguarda_grupo(mqtt)

    mqtt.eleicao()

    print(mqtt.lista_eleicao)
    print(mqtt.id_lider)

    mqtt.finalizar_mqtt()

if __name__ == '__main__':
    run()   