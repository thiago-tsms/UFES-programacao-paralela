import grpc
import mine_grpc_pb2_grpc
import mine_grpc_pb2
from concurrent import futures

class Services(mine_grpc_pb2_grpc.apiServicer):
    transaction_id = 0
    challenge = 0
    solution = ''
    winner = -1

    def getTransactionId(self, request, context):
        return mine_grpc_pb2.result()

    def getChallenge(self, request, context):
        transaction_id = request.transactionId

        return mine_grpc_pb2.result()

    def getTransactionStatus(self, request, context):
        transaction_id = request.transactionId
        
        return mine_grpc_pb2.result()

    def submitChallenge(self, request, context):
        transaction_id = request.transactionId
        client_id = request.clientId
        soluction = request.seed

        return mine_grpc_pb2.result()

    def getWinner(self, request, context):
        transaction_id = request.transactionId

        return mine_grpc_pb2.result()

    def getSolution(self, request, context):
        transaction_id = request.transactionId

        return mine_grpc_pb2.result(status=1, result=1, challenge=1)

def run():
    grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    mine_grpc_pb2_grpc.add_apiServicer_to_server(Services(), grpc_server)
    grpc_server.add_insecure_port('[::]:8080')
    grpc_server.start()
    grpc_server.wait_for_termination()

if __name__ == '__main__':
    run()