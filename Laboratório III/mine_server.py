import grpc
import mine_grpc_pb2
import mine_grpc_pb2_grpc
from concurrent import futures

class ApiServicer(mine_grpc_pb2_grpc.apiServicer):
    '''transaction_id = 0
    challenge = 0
    solution = ''
    winner = -1'''

    def getTransactionId(self, request, context):
        #print(f'Executando: getTransactionId')
        
        return mine_grpc_pb2.intResult(result=0)


    def getChallenge(self, request, context):
        transaction_id = request.result
        
        print(f'{transaction_id}')

        return mine_grpc_pb2.intResult(result=0)

    def getTransactionStatus(self, request, context):
        transaction_id = request.transactionId
        
        print(f'{transaction_id}')
        
        return mine_grpc_pb2.intResult(result=0)

    def submitChallenge(self, request, context):
        transaction_id = request.result
        client_id = request.clientId
        soluction = request.seed
        
        print(f'{transaction_id} - {client_id} - {soluction}')

        return mine_grpc_pb2.intResult(result=0)

    def getWinner(self, request, context):
        transaction_id = request.result
        
        print(f'{transaction_id}')

        return mine_grpc_pb2.intResult(result=0)

    def getSolution(self, request, context):
        transaction_id = request.result
        
        print(f'{transaction_id}')

        return mine_grpc_pb2.structResult(status=1, result=1, challenge=1)

def run():
    grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    mine_grpc_pb2_grpc.add_apiServicer_to_server(ApiServicer(), grpc_server)
    grpc_server.add_insecure_port('[::]:8080')
    grpc_server.start()
    grpc_server.wait_for_termination()

if __name__ == '__main__':
    run()