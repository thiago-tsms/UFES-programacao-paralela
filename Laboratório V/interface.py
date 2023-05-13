import sys
import tkinter as tk

class InterfaceControlador:
    
    # Inicia a interface
    def __init__(self, params, newChallenge_func):
        print(f'* Iniciando Interface')
        
        self.params = params
        self.newChallenge_func = newChallenge_func
        
        self.page = tk.Tk()
        #self.input = tk.Entry(self.page, justify=tk.CENTER, borderwidth=3, font=12, width=30)
    
        self.opcoes = [
            ("newChallenge", self.newChallenge),
            ("exitController", self.exitController),
        ]
        
        self.page.title('Broker - Controlador')
        
        tk.Label(self.page)
        tk.Label(self.page, text="Selecione uma das opções", justify=tk.LEFT, padx=10, pady=10, font=15).pack()
        [tk.Button(self.page, text=txt, command=func, width=50, pady=5, padx=15, justify=tk.CENTER).pack(anchor=tk.W) for (txt, func) in self.opcoes]

        #self.input.pack(padx=10, pady=10)
        
   
    # Inicia o loop
    def start_loop(self):
        print(f'== Inicialização Completa ==')
        self.page.mainloop()
    
    
    # Botão
    def newChallenge(self):
        self.newChallenge_func(self.params)
    
    
    # Botão: sair da tela
    def exitController(self):
        print(f'* Finalizando Interface')
        self.page.destroy()


class InterfaceMinerador:
    
    def __init__(self, params):
        print(f'* Iniciando Interface')
        
        self.params = params
        
        self.page = tk.Tk()
        
        self.opcoes = [
            #("newChallenge", self.newChallenge),
            ("exitController", self.exitController),
        ]
        
        self.page.title('Broker - Minerador')
        
        tk.Label(self.page)
        tk.Label(self.page, text="Selecione uma das opções", justify=tk.LEFT, padx=10, pady=10, font=15).pack()
        [tk.Button(self.page, text=txt, command=func, width=50, pady=5, padx=15, justify=tk.CENTER).pack(anchor=tk.W) for (txt, func) in self.opcoes]


   # Inicia o loop
    def start_loop(self):
        print(f'== Inicialização Completa ==')
        self.page.mainloop()
        
    
    def exitController(self):
        print(f'* Finalizando Interface')
        self.page.destroy()