import ttkbootstrap as ttk
from class_dados import Consumo


class Interface:
    def __init__(self) -> None:
        self.tela = ttk.Window(themename='vapor')
        self.consumo = Consumo()

    def comando_teste(self):
        print('teste teste teste')


    def botoes(self):
        self.adicionar_inquilino = ttk.Button(self.tela, text='Adicionar', command=lambda: ...)
        self.adicionar_inquilino.place(x=500, y=15)

    def entradas(self):
        ...        

    def painel(self):
        ttk.Label(self.tela, text=f"Total Kwh: {self.consumo.total_consumo}").place(x=10, y=20)
        ttk.Label(self.tela, text=f"Consumo Verde: {self.consumo.consumo_verde}").place(x=10, y=40)
        ttk.Label(self.tela, text=f"Consumo Amarelo: {self.consumo.consumo_amarelo}").place(x=10, y=60)
        ttk.Label(self.tela, text=f"Consumo Vermelho: {self.consumo.consumo_vermelho}").place(x=10, y=80)
    
        

    def renderizar_botoes(self):
        self.botoes()

    def renderizar_painel(self):
        self.painel()

    def iniciar(self):
        self.tela.title('Cálculo Energia')
        self.tela.geometry('750x370')
        self.renderizar_botoes()
        self.renderizar_painel()
        self.tela.mainloop()



if __name__ == '__main__':
    app = Interface().iniciar()