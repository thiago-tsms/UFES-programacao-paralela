import grpc
import mine_grpc_pb2
import mine_grpc_pb2_grpc
#from resolucao import Resolucao
from resolucao import inicia_busca

import tkinter as tk

client_id = 20
transaction_id = 0
challenge = 0
status = 0
seed = 0
solution = ''

def leitura(input):
    try:
        id = int(input.get())
        return id
    except:
        print('É necessário inserir um valor.')
        return -1
    finally:
        input.delete(0, tk.END)

def espaco(tipo):
    txt = ''
    for i in range(0, 22):
        if(tipo == 0):
            txt += '='
        elif(tipo == 1):
            txt += '-'
    print(txt)

def getTransactionID(client, input):
    try:
        res = client.getTransactionId(mine_grpc_pb2.void())
        transaction_id = res.result
        print(f'ID da transação: {transaction_id}')
    except:
        print(f'Erro: getTransactionID')


def getChallenge(client, input):
    
    id = leitura(input)
    if(id == -1):
        return

    try:
        res = client.getChallenge(mine_grpc_pb2.transactionId(transactionId=id))
        challenge = res.result
        print(f'Valor do desafio: {challenge}')
    except:
        print(f'Erro: getChallenge')


def getTransactionStatus(client, input):

    id = leitura(input)
    if(id == -1):
        return
    
    try:
        res = client.getTransactionStatus(mine_grpc_pb2.transactionId(transactionId=id))
        status = res.result
        print(f'Status da Transação: {status}')
    except:
        print(f'Erro: getTransactionStatus')


def submitChallenge(client, input):
    try:
        res = client.submitChallenge(mine_grpc_pb2.challengeArgs(transactionId=transaction_id, clientId=client_id, seed=seed))
        print(f'Validade da solução: {res.result}')
    except:
        print(f'Erro: submitChallenge')


def getWinner(client, input):
    id = leitura(input)
    if(id == -1):
        return
    
    try:
        res = client.getWinner(mine_grpc_pb2.transactionId(transactionId=id))
        print(f'Id do vencedor: {res.result}')
    except:
        print(f'Erro: getWinner')


def getSolution(client, input):
    id = leitura(input)
    if(id == -1):
        return

    try:
        res = client.getSolution(mine_grpc_pb2.transactionId(transactionId=id))
        print(f'Status: {res.status} \nDesafio: {res.challenge} \nSolução: {res.result}')
    except:
        print(f'Erro: getSolucion')

def mine(client, input):
    try:
        #rs = Resolucao()
        sl = ''
        id = client.getTransactionId(mine_grpc_pb2.void()).result
        challenge = client.getChallenge(mine_grpc_pb2.transactionId(transactionId=id)).result
        status = client.getTransactionStatus(mine_grpc_pb2.transactionId(transactionId=id)).result
        
        espaco(0)
        print(f'ID transação: {id} \nDesafio: {challenge} \nStatus: {status}')
        
        espaco(1)
        print(f'Buscando Semente ...')
        (hash, seed) = inicia_busca(challenge, 4)

        # while True:
        #     (hash, seed) = rs.gerar_hash()
        #     if (rs.busca_solucao(challenge, hash)):
        #         break

            #Imprime a solução
        espaco(1)
        print(f'Semente: {seed}')
        
        result = client.submitChallenge(mine_grpc_pb2.challengeArgs(transactionId=id, clientId=client_id, seed=seed))
        
            #imprime result
        espaco(1)
        print(f'Resultado: {result.result}')
        espaco(0)
        
    except:
        print(f'Erro: mine')


def run():
    channel = grpc.insecure_channel('localhost:8080')
    client = mine_grpc_pb2_grpc.apiStub(channel)

    page = tk.Tk()
    input = tk.Entry(page, justify=tk.CENTER, borderwidth=3, font=12, width=30)

    opcoes = [
        ("getTransactionID", lambda: getTransactionID(client, input)),
        ("getChallenge", lambda: getChallenge(client, input)),
        ("getTransactionStatus", lambda: getTransactionStatus(client, input)),
        ("submitChallenge", lambda: submitChallenge(client, input)),
        ("getWinner", lambda: getWinner(client, input)),
        ("getSolution", lambda: getSolution(client, input)),
        ("mine", lambda: mine(client, input)),
    ]
    
    page.title('gRPC - python')

    tk.Label(page)
    tk.Label(page, text="Selecione uma das opções", justify=tk.LEFT, padx=10, pady=10, font=15).pack()
    [tk.Button(page, text=txt, command=func, width=50, pady=5, padx=15, justify=tk.CENTER).pack(anchor=tk.W) for (txt, func) in opcoes]

    input.pack(padx=10, pady=10)
    
    page.mainloop()

if __name__ == '__main__':
    run()