import grpc
import mine_grpc_pb2_grpc
import mine_grpc_pb2

def run():
    channel = grpc.insecure_channel('localhost:8080')
    client = mine_grpc_pb2_grpc.apiStub(channel)

    print(f'Efetua a exeução do problema \n')

if __name__ == '__main__':
    run()