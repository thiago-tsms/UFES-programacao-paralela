from mqtt import *
import random
from resolucao import ProvaTrabalho


nClients = 3

# Dados relacionados ao cliente
class ClientesData:
    def __init__(self):
        self.id = random.randint(0, 1000)
        self.id_lider = None
        self.transaction_id = -1
        self.challenge = None
        self.solution = None
        self.winner = -1
        

# Método do minerador
class Minerador:
    def __init__(self, cliente_data, mqtt):
        self.cliente_data = cliente_data
        self.mqtt = mqtt
    
    # Inicia a execução
    def start(self):
        print(f'** Iniciando Minerador \n')
        
        # Aguarda novo desafio
        self.mqtt.wait_challenge()
        
        # Realiza busca por solução
        pt = ProvaTrabalho()
        (hash, self.cliente_data.solution) = pt.buscar_solucao(self.cliente_data.challenge)
        
        print(f'* Solução Encontrada \nSolução: {self.cliente_data.solution} \n')
        
        msg = {
            'id': self.cliente_data.id,
            'TransactionID': self.cliente_data.transaction_id,
            'Solution': self.cliente_data.solution,
        }
        
        # Envia solução
        self.mqtt.client.publish(topico_solution, json.dumps(msg))

        # Aguarda solução dos demais        
        for _ in range(nClients-1):
            (client_id, transaction_id, solution, result) = self.mqtt.wait_result()
            
            if (self.cliente_data.id == client_id) and (result == 1):
                print(f'** Informações recebidas')
                print(f'-- Ganhador: {client_id} \n-- TransactionID: {transaction_id} \n-- Solução: {solution}')
                print('-- Resultado Aceito \n')
                
            elif (self.cliente_data.id == client_id) and (result == -1):
                print(f'** Informações recebidas')
                print(f'-- ID: {client_id} \n-- TransactionID: {transaction_id} \n-- Solução: {solution}')
                print('-- Desafio já resolvido \n')
            
            elif (self.cliente_data.id == client_id) and (result == 0):
                print(f'** Informações recebidas')
                print(f'-- ID: {client_id} \n-- TransactionID: {transaction_id} \n-- Solução: {solution}')
                print('-- Resultado Rejeitado \n')
            
            elif result == 1:
                print(f'** Informações recebidas')
                print(f'-- Ganhador: {client_id} \n-- TransactionID: {transaction_id} \n-- Solução: {solution} \n')
    
    
# Método do Coordenador
class Coordenador:
    def __init__(self, cliente_data, mqtt):
        self.cliente_data = cliente_data
        self.mqtt = mqtt
    
    # Inicia a execução
    def start(self):
        print(f'** Iniciando Coordenador \n')
        self.gerar_desafio()
        
        # Avalia solução
        pt = ProvaTrabalho()
        
        # Mantem o loop até o fim da execução
        while True:
            
            # Result [-1: Desafio não solucionado, 0: Inválida, 1: Solução Correta]
            
            # Espera solução
            (client_id, transaction_id, solution) = self.mqtt.wait_solution()
            print(f'* Solução recebida:')
            print(f'-- ClientID: {client_id} \n-- TransactionID: {transaction_id} \n-- Solution: {solution}')
            
            # Desafio não corrente
            if self.cliente_data.transaction_id != transaction_id:
                print(f'-- Não existe esse desafio')
            
            # Desafio já solucionado
            elif self.cliente_data.winner != -1:
                print(f'-- Este desafio já foi solucionado [Winner: {self.cliente_data.winner}] \n')
                
                msg = {
                    'id': self.cliente_data.id,
                    'ClientID': client_id,
                    'TransactionID': transaction_id,
                    'Solution': solution,
                    'Result': -1
                }
                
                self.mqtt.client.publish(topico_result, json.dumps(msg))
            
            # Solução correta
            elif pt.avaliar_hash(self.cliente_data.challenge, pt.gerar_hash(solution)):
                print(f'-- Solução aprovado \n')
                
                self.cliente_data.winner = client_id
                self.cliente_data.solution = solution
                #params.desafio_em_andamento = False
                
                msg = {
                    'id': self.cliente_data.id,
                    'ClientID': client_id,
                    'TransactionID': transaction_id,
                    'Solution': solution,
                    'Result': 1
                }
                
                self.mqtt.client.publish(topico_result, json.dumps(msg))
            
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
                
                self.mqtt.client.publish(topico_result, json.dumps(msg))
        
    
    # Gera um novo desafio
    def gerar_desafio(self):
        #print(f'\n* Gerando Novo Desafio')
    
        self.cliente_data.transaction_id += 1
        self.cliente_data.challenge = random.randint(1, 10)
        self.cliente_data.winner = -1
        #params.desafio_em_andamento = True
        
        msg = {
            'id': self.cliente_data.id,
            'TransactionID': self.cliente_data.transaction_id,
            'Challenge': self.cliente_data.challenge
        }
        
        # Enviar desafio padronizado
        self.mqtt.client.publish(topico_challenge, json.dumps(msg))
        
        print(f' Gerando Novo Desafio \n-- TransactionID: {self.cliente_data.transaction_id} \n-- Desafio: {self.cliente_data.challenge} \n')


def run():
    # Inicia cliente
    cliente_data = ClientesData()
    
    # Inicia comunicação
    mqtt = Comunicacao(cliente_data)
    
    print(f'* Aguardando Clientes')
    while len(mqtt.lista_clientes) < nClients:
        time.sleep(0.5)

    # Realiza eleição
    mqtt.eleicao()
    
    # Inicia execução
    if cliente_data.id == cliente_data.id_lider:
        execucao = Coordenador(cliente_data, mqtt)
    else:
        execucao = Minerador(cliente_data, mqtt)
    
    execucao.start()

    # Finaliza comunicação
    mqtt.finalizar_mqtt()

if __name__ == '__main__':
    run()   