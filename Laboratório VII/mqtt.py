import paho.mqtt.client as mqtt
import random
import json
import time

#broker = "broker.emqx.io"
broker = "localhost"
topico_anuncio = "sd/lab7/init"
topico_pubkey = "sd/lab7/pubkey"
topico_cert = "sd/lab7/cert"
topico_eleicao = "sd/lab7/voting"
topico_solution = "sd/lab7/solution"
topico_challenge = 'sd/lab7/challenge'
topico_result = 'sd/lab7/result'

class Comunicacao:

    # Inicializa compartilhando dados do cliente e classe de resolução da prova de trabalho
    def __init__(self, cliente_data, pt):
        self.cliente_data = cliente_data
        self.lista_clientes = [self.cliente_data.id]
        self.pt = pt
        self.inicia_mqtt()
        self.lista_eleicao = []
    
    # Inicia o MQTT
    def inicia_mqtt(self):
        self.client = mqtt.Client(f'client-{self.cliente_data.id}')
        self.client.connect(broker)
    
    # Finaliza o MQTT
    def finalizar_mqtt(self):
        self.client.loop_stop()
        self.client.disconnect()
    
    def faz_anuncio(self):
        self.client.publish(topico_anuncio, json.dumps({
            'id': self.cliente_data.id
        }))

    # Se inscreve nos tópicos ao iniciar
    def subscribe_execucao(self):
        self.client.subscribe(topico_eleicao)
        self.client.subscribe(topico_anuncio)
        self.client.subscribe(topico_cert, 1)
        
        self.client.on_message = self.on_message
        self.client.loop_start()

    # incrições certificador
    def subscribe_certificador(self):
        self.client.subscribe(topico_pubkey, 1)

        self.client.on_message = self.on_message
        self.client.loop_start()

    # Inscrições do Coodenador (após eleição)
    def subscribe_server(self):
        self.client.subscribe(topico_solution)
    
    # Inscrições do Minerador (após eleição)
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

        # Recebe chave publica e cria certificado
        if msg.topic == topico_pubkey:
            c_id = data['id']
            node_id = data['NodeId']
            pub_key = data['PubKey']
            cert = self.cliente_data.security.gerar_certificado_digital(node_id, pub_key)
            self.cliente_data.lista_certificados.append((node_id, cert))

            msg = {
                'id': self.cliente_data.id,
                'NodeId': node_id,
                'Cert': cert.decode('utf-8')
            }
            self.client.publish(topico_cert, json.dumps(msg))

        # Recebe os certificados
        elif msg.topic == topico_cert:
            c_id = data['id']
            node_id = data['NodeId']
            cert = data['Cert']
            cert_bytes = bytes(cert, 'utf-8')
            pk = self.cliente_data.security.obter_public_key_certificado_digital(cert_bytes)
            self.cliente_data.lista_certificados.append((node_id, cert_bytes, pk))

        # Recebe id de novo integrante
        elif msg.topic == topico_anuncio:
            if not (origin_id in self.lista_clientes):            
                self.lista_clientes.append(origin_id)
            print(self.lista_clientes)
        
        # Recebe id e pesos da eleição
        elif msg.topic == topico_eleicao:
            new_data = self.prepara_mensagem_recepcao(data)

            if new_data:
                c_id = new_data['id']
                peso = new_data['peso']
                self.lista_eleicao.append((c_id, peso))
        
        # Realiza o desafio (minerador)
        elif msg.topic == topico_challenge:
            new_data = self.prepara_mensagem_recepcao(data)

            if new_data:
                self.cliente_data.transaction_id = new_data['TransactionID']
                self.cliente_data.challenge = new_data['Challenge']
                
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
                self.client.publish(topico_solution, self.preparar_mensagem_envio(self.cliente_data.id, msg))

        # Avalia a solução (coordenador)
        elif msg.topic == topico_solution:
            new_data = self.prepara_mensagem_recepcao(data)

            if new_data:
                client_id = new_data['id']
                transaction_id = new_data['TransactionID']
                solution = new_data['Solution']
                
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
                    
                    self.client.publish(topico_result, self.preparar_mensagem_envio(self.cliente_data.id, msg))
                
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
                    
                    self.client.publish(topico_result, self.preparar_mensagem_envio(self.cliente_data.id, msg))
                
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
                    
                    self.client.publish(topico_result, self.preparar_mensagem_envio(self.cliente_data.id, msg))
        
        # Recebe resultado do desafio (minerador)
        elif msg.topic == topico_result:
            new_data = self.prepara_mensagem_recepcao(data)

            if new_data:
                client_id = new_data['ClientID']
                transaction_id = new_data['TransactionID']
                solution = new_data['Solution']
                result = new_data['Result']
            

    # Realiza a eleição
    def eleicao(self):
        print(f'* Iniciando Eleição')

        v_rand = random.randint(0, 65536)
        self.lista_eleicao.append((self.cliente_data.id, v_rand))

        time.sleep(10)

        # Envia id e pesos gerado
        mensagem = {
            'id': self.cliente_data.id,
            'peso': v_rand
        }
        
        self.client.publish(
            topico_eleicao, 
            self.preparar_mensagem_envio(self.cliente_data.id, mensagem)
        )
                    
        # Aguarda para recepção dos votos
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
        
        # Aguarda para iniciar execução
        time.sleep(2)
        
        print(f'\n** Resultado da Eleição \nIntegrantes: {self.lista_eleicao} \nID: {self.cliente_data.id} \nID Coordenador: {self.cliente_data.id_lider} \n')


    def preparar_mensagem_envio(self, id, mensagem):
        new_mensagem = json.dumps(mensagem)
        assinatura = self.cliente_data.security.assinar_mensagem(new_mensagem)
        data = {
            'id': id,
            'msg': new_mensagem, 
            'ass': assinatura
        }
        return json.dumps(data)

    def prepara_mensagem_recepcao(self, data):
        mensagem = data['msg']
        assinatura = data['ass']
        new_data = json.loads(mensagem)
        public_key = self.buscar_public_key(new_data['id'], self.cliente_data.lista_certificados)

        # Verifica se a assinatura está correta
        if self.cliente_data.security.verificar_assinatura(public_key, mensagem, assinatura):
            return new_data
        else:
            return None


    # Efetua a busca na lista
    def buscar_public_key(self, id, lista):
        for (id_pk, cert, pk) in lista:
            if id_pk == id:
                return pk
        
        return None