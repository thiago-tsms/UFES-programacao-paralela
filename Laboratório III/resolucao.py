import hashlib
import random
from threading import Thread
from multiprocessing import Queue
from events import Events
import time

class Resolucao:
    def gerar_hash(self):
        seed = random.randint(0, 2147483647)
        hash = hashlib.sha1(seed.to_bytes(32, byteorder="big"))
        
        return (int(hash.hexdigest(), 16), seed)
        
        #print(hash.hexdigest())

    def gerar_hash_str(self, seed):
        return hashlib.sha1(seed.to_bytes(32, byteorder="big")).hexdigest()
    
    def testa_solucao(self, n, hash):
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
    
    def avalia_solucao(self, seed, n):
        hash = hashlib.sha1(seed.to_bytes(32, byteorder="big"))
        hash = int(hash.hexdigest(), 16)
        mask = 0
        for i in range((20*8 -1), (20*8 -1 -n), -1):
            mask += 2**i
        
        res = hash & mask
    
        if res == 0:
            return True
        else:
            return False

def inicia_busca(challenge, n_threads):
    threads = []
    event = Events()

    q = Queue()
    for i in range(0, n_threads):
        threads.append(Thread(target=thread_function, args=(event, challenge, q)))

    [tr.start() for tr in threads]

    (hash, seed) = q.get()

    event.set()
    time.sleep(0.001)


    #[tr.join() for tr in threads]

    #q.close()

    return (hash, seed)


def thread_function(event, challenge, q):
    rs = Resolucao()

    while True:
        (hash, seed) = rs.gerar_hash()

        if(rs.testa_solucao(challenge, hash)):
            if(event.is_set()):
                return
            else:
                q.put((hash, seed))
                return
               