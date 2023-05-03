import grpc
import mine_grpc_pb2_grpc
import mine_grpc_pb2

import tkinter as tk


def getTransactionID(client):
    res = client.add(mine_grpc_pb2.getTransactionId())
    print(f'ID da transação: {res.intResult}')

def getChallenge(client):
    res = client.add(mine_grpc_pb2.getChallenge())
    print(f'Resultado: {res.intResult}')

def getTransactionStatus(client):
    res = client.add(mine_grpc_pb2.getTransactionStatus())
    print(f'Resultado: {res.intResult}')

def getWinner(client):
    res = client.add(mine_grpc_pb2.getWinner())
    print(f'Resultado: {res.intResult}')

def GetSolucion(client):
    res = client.add(mine_grpc_pb2.GetSolucion())
    print(f'Resultado: {res.intResult}')

def getSolucion(client):
    res = client.add(mine_grpc_pb2.GetSolucion())
    print(f'Resultado: {res.intResult}')

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