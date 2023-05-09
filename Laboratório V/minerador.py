import paho.mqtt.client as mqtt
import time

    # solução usada pelo cliente
fila_solution = "sd/lab5/solution"
fila_challenge = 'sd/lab5/challenge'
fila_result = 'sd/lab5/result'

def run():
    print(f'Iniciando Minerador')

    client = mqtt.Client("controlado-ufes-lv-minerador")
    client.connect("broker.emqx.io")

    client.loop_start()

    client.subscribe(fila_solution)
    client.on_message = lambda client, userdata, message: print(f'{str(message.payload.decode("utf-8"))}')

    time.sleep(30000)
    client.loop_stop()

if __name__ == '__main__':
    run()