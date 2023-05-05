import grpc
import mine_grpc_pb2
import mine_grpc_pb2_grpc
from concurrent import futures
import random
from resolucao import Resolucao

class ApiServicer(mine_grpc_pb2_grpc.apiServicer):
    
    transaction_id = 0
    challenge = random.randint(0, 6)
    solution = None
    winner = -1

    status = False

    def getTransactionId(self, request, context):
        return mine_grpc_pb2.intResult(result=(self.transaction_id))


    def getChallenge(self, request, context):
        transaction_id = request.transactionId

        if(self.transaction_id == transaction_id):
            return mine_grpc_pb2.intResult(result=(self.challenge))
        else:
            return mine_grpc_pb2.intResult(result=(-1))

       
    def getTransactionStatus(self, request, context):
        transaction_id = request.transactionId

        if(self.transaction_id != transaction_id):
            return mine_grpc_pb2.intResult(result=-1)
        elif(self.status == False):
            return mine_grpc_pb2.intResult(result=0)
        elif(self.status == True):
            return mine_grpc_pb2.intResult(result=1)


    def submitChallenge(self, request, context):
        transaction_id = request.transactionId
        client_id = request.clientId
        seed = request.seed

        if(self.transaction_id != transaction_id):
            return mine_grpc_pb2.intResult(result=(-1))
        
        elif (self.solution is not None):
            return mine_grpc_pb2.intResult(result=(2))
        
        else:
            print(f'{transaction_id} - {client_id} - {seed}')

            rs = Resolucao()
            if(rs.avalia_solucao(seed, self.challenge)):
                self.winner = client_id
                self.solution = rs.gerar_hash_str(seed)
                print(f'Debug: {client_id} -- {rs.gerar_hash_str(seed)}')
                return mine_grpc_pb2.intResult(result=1)
            
            else:
                return mine_grpc_pb2.intResult(result=0)
        
            # 1 OK
            # 0 Inválida
            # 2 Desafio solucionado


    def getWinner(self, request, context):
        transaction_id = request.transactionId

        if(self.transaction_id != transaction_id):
            return mine_grpc_pb2.intResult(result=-1)
        elif(self.solution is None):
            return mine_grpc_pb2.intResult(result=0)
        else:
            return mine_grpc_pb2.intResult(result=self.winner)
        
   
    def getSolution(self, request, context):
        transaction_id = request.transactionId

        if(self.transaction_id != transaction_id):
            return mine_grpc_pb2.structResult(status=-1, result='---', challenge=-1)
        else:
            print(self.solution)
            return mine_grpc_pb2.structResult(status=self.status, result=self.solution, challenge=self.challenge)


def run():
    grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    mine_grpc_pb2_grpc.add_apiServicer_to_server(ApiServicer(), grpc_server)
    grpc_server.add_insecure_port('[::]:8080')
    grpc_server.start()
    grpc_server.wait_for_termination()

if __name__ == '__main__':
    run()