import paho.mqtt.client as mqtt
import random
import json
import time

broker = "broker.emqx.io"
topico_anuncio = "sd/lab6/init"
topico_eleicao = "sd/lab6/voting"
topico_solution = "sd/lab6/solution"
topico_challenge = 'sd/lab6/challenge'
topico_result = 'sd/lab6/result'

class Comunicacao:

    def __init__(self, cliente_data, pt):
        self.cliente_data = cliente_data
        self.lista_clientes = [self.cliente_data.id]
        self.pt = pt
        self.inicia_mqtt()
        self.subscribe()
        self.lista_eleicao = []

        time.sleep(4)
        self.client.publish(topico_anuncio, json.dumps({
            'id': self.cliente_data.id
        }))

    
    # Inicia o MQTT
    def inicia_mqtt(self):
        self.client = mqtt.Client(f'client-{self.cliente_data.id}')
        self.client.connect(broker)
    
    # Finaliza o MQTT
    def finalizar_mqtt(self):
        self.client.loop_stop()
        self.client.disconnect()
    
    # Se inscreve nos tópicos (server)
    def subscribe(self):

        self.client.subscribe(topico_eleicao)
        self.client.subscribe(topico_anuncio)
        
        self.client.on_message = self.on_message
        self.client.loop_start()
        
    # Inscrições do Coodenador
    def subscribe_server(self):
        self.client.subscribe(topico_solution)
    
    # Inscrições do Minerador
    def subscribe_client(self):
        self.client.subscribe(topico_challenge)
        self.client.subscribe(topico_result)

    # Recebe as mensagens
    def on_message(self, client, userdata, msg):
        data = json.loads(str(msg.payload.decode("utf-8")))
        origin_id = data['id']
        
        # Elimina mensagens da mesma origem
        if origin_id == self.cliente_data.id:
            return

        # Recebe id de novo integrante
        if msg.topic == topico_anuncio:
            self.lista_clientes.append(origin_id)
        
        # Recebe id e pesos da eleição
        elif msg.topic == topico_eleicao:
            c_id = data['id']
            peso = data['peso']

            self.lista_eleicao.append((c_id, peso))
        
        # Realiza o desafio
        elif msg.topic == topico_challenge:
            self.cliente_data.transaction_id = data['TransactionID']
            self.cliente_data.challenge = data['Challenge']
            
            print(f'\n ** Desafio recebido:')
            print(f'-- TransactionID: {self.cliente_data.transaction_id} \n-- Challenge: {self.cliente_data.challenge} \n')
            
            (hash, self.cliente_data.solution) = self.pt.buscar_solucao(self.cliente_data.challenge)
            
            print(f'* Solução Encontrada \nSolução: {self.cliente_data.solution} \n')
        
            msg = {
                'id': self.cliente_data.id,
                'TransactionID': self.cliente_data.transaction_id,
                'Solution': self.cliente_data.solution,
            }
            
            # Envia solução
            self.client.publish(topico_solution, json.dumps(msg))

        # Avalia a solução
        elif msg.topic == topico_solution:
            client_id = data['id']
            transaction_id = data['TransactionID']
            solution = data['Solution']
            
            print(f'* Solução recebida:')
            print(f'-- ClientID: {client_id} \n-- TransactionID: {transaction_id} \n-- Solution: {solution}')
            
            # Desafio não corrente
            if self.cliente_data.transaction_id != transaction_id:
                print(f'-- Desafio não encontrado')
            
            # # Desafio já solucionado
            elif self.cliente_data.winner != -1:
                print(f'-- Este desafio já foi solucionado [Winner: {self.cliente_data.winner}] \n')
                
                msg = {
                    'id': self.cliente_data.id,
                    'ClientID': client_id,
                    'TransactionID': transaction_id,
                    'Solution': solution,
                    'Result': -1
                }
                
                self.client.publish(topico_result, json.dumps(msg))
            
            # Solução correta
            elif self.pt.avaliar_hash(self.cliente_data.challenge, self.pt.gerar_hash(solution)):
                print(f'-- Solução aprovado \n')
                
                self.cliente_data.winner = client_id
                self.cliente_data.solution = solution
                
                msg = {
                    'id': self.cliente_data.id,
                    'ClientID': client_id,
                    'TransactionID': transaction_id,
                    'Solution': solution,
                    'Result': 1
                }
                
                self.client.publish(topico_result, json.dumps(msg))
            
            # Solução incorreta
            else:
                print(f'-- Solução reprovado \n')
                
                msg = {
                    'id': self.cliente_data.id,
                    'ClientID': client_id,
                    'TransactionID': transaction_id,
                    'Solution': solution,
                    'Result': 0
                }
                
                self.client.publish(topico_result, json.dumps(msg))
        
        # Recebe resultado do desafio
        elif msg.topic == topico_result:
            client_id = data['ClientID']
            transaction_id = data['TransactionID']
            solution = data['Solution']
            result = data['Result']
            

    # Realiza a eleição
    def eleicao(self):
        print(f'* Iniciando Eleição')

        v_rand = random.randint(0, 65536)
        self.lista_eleicao.append((self.cliente_data.id, v_rand))

        time.sleep(8)

        # Envia id e pesos gerado
        self.client.publish(topico_eleicao, json.dumps({
            'id': self.cliente_data.id,
            'peso': v_rand
        }))

        time.sleep(6)

        mv = max([le[1] for le in self.lista_eleicao])
        for le in self.lista_eleicao:
            if le[1] == mv:
                self.cliente_data.id_lider = le[0]
        
        # Se inscreve nos tópicos pertinentes
        if self.cliente_data.id == self.cliente_data.id_lider:
            self.subscribe_server()
        else:
            self.subscribe_client()
        
        time.sleep(2)
        
        print(f'\n** Resultado da Eleição \nIntegrantes: {self.lista_eleicao} \nID: {self.cliente_data.id} \nID Coordenador: {self.cliente_data.id_lider} \n')
