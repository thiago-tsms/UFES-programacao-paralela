import hashlib
import random

class Resolucao:
    def gerar_hash(self):
        value = random.randint(0, 2147483647)
        hash = hashlib.sha1(value.to_bytes(32, byteorder="big"))
        
        return (int(hash.hexdigest(), 16), value)
        
        #print(hash.hexdigest())
    
    def busca_solucao(self, n, hash):
        mask = 0
        for i in range((20*8 -1), (20*8 -1 -n), -1):
            mask += 2**i
        
        res = hash & mask
        
        # print(hex(hash))
        # print(hex(mask))
        # print(hex(res))
        
        if res == 0:
            return True
        else:
            return False
    
    def avalia_solucao(self, value, n):
        hash = hashlib.sha1(value.to_bytes(32, byteorder="big"))
        hash = int(hash.hexdigest(), 16)
        mask = 0
        for i in range((20*8 -1), (20*8 -1 -n), -1):
            mask += 2**i
        
        res = hash & mask
    
        if res == 0:
            return True
        else:
            return False


def teste(n, hash):
    mask = 0
    for i in range(31, (31-n), -1):
        mask += 2**i

    if (hash & mask) == 0:
        return True
    else:
        return False


# if __name__ == '__main__':
#     res = Resolucao()
    
#     solution = 0
#     n = 8
#     count = 0
    
#     while(solution == 0):
#         count += 1
#         (hash, value) = res.gerar_hash()
#         if res.busca_solucao(n, hash) == True:
#             solution = value
    
#     print(f'Solução: {value}')
#     print(f'Solução avaliada: {res.avalia_solucao(value, n)} - Tentativas: {count}')