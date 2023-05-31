from mqtt import *

class Minerador:
    def __init__(self):
        print()
    
class Coordenador:
    def __init__(self):
        print()

nClients = 2

def aguarda_grupo(mqtt):
    print(f'* Aguardando Clientes')
    while len(mqtt.lista_clientes) < nClients:
        time.sleep(0.5)

def run():
    mqtt = Comunicacao()
    aguarda_grupo(mqtt)

    mqtt.eleicao()

    if mqtt.id == mqtt.id_lider:
        cordenador = Coordenador()
    else:
        minerador = Minerador()

    mqtt.finalizar_mqtt()

if __name__ == '__main__':
    run()   