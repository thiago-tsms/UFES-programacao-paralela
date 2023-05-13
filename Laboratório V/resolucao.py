import hashlib
import random
from threading import Thread
from multiprocessing import Queue
from events import Events
import time


class ProvaTrabalho:
    
    # Aplica o hash a partir de uma string
    def gerar_hash(self, solution):
        return hashlib.sha1(solution.encode('utf-8')).hexdigest()
    
    
    # Gera hash a partir da string de números aleatórios
    def gerar_hash_aleatorio(self):
        number = random.random()
        solution = str(number)
        hash = hashlib.sha1(solution.encode('utf-8')).hexdigest()
        
        return (hash, solution)
      
    
    # Avalia se o hash cumpre os requisitos do desafio
    def avaliar_hash(self, challenger, hash):
        
        # Gera uma mascara para os bits relevantes
        mask = 0
        for i in range((20*8 -1), (20*8 -1 -challenger), -1):
            mask += 2**i
        
        # Converte o hexadecimal do hash para inteiro de 32 bits
        hash = int(hash, 16)
        
        # Teste mascara
        #print(hex(mask))
        #print(hex(hash))
        #print(hex(hash & mask))
        
        # Remove todos os bits irrelevantes para a busca
        if (hash & mask) == 0:
            return True
        else:
            return False
    
    
    # Efetua uma busca até obter uma solução para o hash
    def buscar_solucao(self, challenger):
        threads = []
        event = Events()
        queue = Queue()
        
        [threads.append(Thread(target=self.thread, args=(queue, event, challenger,))) for _ in range(4)]
        [tr.start() for tr in threads]
        
        # Aguarda a resposta da primeira thread a completar o desafio
        (hash, solution) = queue.get()
        
        # Marca o evento para encerrar as demais threads
        event.set()
        time.sleep(0.001)
        
        [tr.join() for tr in threads]
        queue.close()

        return (hash, solution)
        
  
    # Thread que executa a busca
    def thread(self, queue, event, challenger):
        while True:
            (hash, solution) = self.gerar_hash_aleatorio()
            
            if event.is_set():
                return
            
            elif self.avaliar_hash(challenger, hash):
                queue.put((hash, solution))
                return