import grpc
import mine_grpc_pb2
import mine_grpc_pb2_grpc

import tkinter as tk


def getTransactionID(client):
    try:
        res = client.getTransactionId(mine_grpc_pb2.void())
        print(f'ID da transação: {res.result}')
    except:
        print(f'Erro: getTransactionID')
    
def getChallenge(client):
    res = client.getChallenge(mine_grpc_pb2.transactionId())
    print(f'Resultado: {res.result}')

def getTransactionStatus(client):
    res = client.getTransactionStatus(mine_grpc_pb2.transactionId())
    print(f'Resultado: {res.result}')

def getWinner(client):
    res = client.getWinner(mine_grpc_pb2.transactionId())
    print(f'Resultado: {res.result}')

def GetSolucion(client):
    res = client.GetSolucion(mine_grpc_pb2.transactionId())
    print(f'Resultado: {res.result}')

def getSolucion(client):
    res = client.getSolucion(mine_grpc_pb2.transactionId())
    
    status = res.status
    result = res.result
    challenge = res.challenge
    
    print(f'Resultado: {status} - {result} - {challenge}')

def mine(client):
    #res = client.add(mine_grpc_pb2.GetSolucion())
    print(f'Resultado: ')


def run():
    channel = grpc.insecure_channel('localhost:8080')
    client = mine_grpc_pb2_grpc.apiStub(channel)
    
    opcoes = [
        ("getTransactionID", lambda: getTransactionID(client)),
        ("getChallenge", lambda: getChallenge(client)),
        ("getTransactionStatus", lambda: getTransactionStatus(client)),
        ("getWinner", lambda: getWinner(client)),
        ("GetSolucion", lambda: getSolucion(client)),
        ("Mine", lambda: mine(client)),
    ]

    page = tk.Tk()
    page.title('gRPC - python')

    tk.Label(page)
    tk.Label(page, text="Selecione uma das opções", justify=tk.LEFT, padx=10, pady=10, font=15).pack()
    [tk.Button(page, text=txt, command=func, width=50, pady=5, padx=15, justify=tk.CENTER).pack(anchor=tk.W) for (txt, func) in opcoes]
    
    page.mainloop()


if __name__ == '__main__':
    run()