import ttkbootstrap as ttk
from tkinter import messagebox
from class_dados import Consumo



class InterfacesSecundarias:
    def __init__(self) -> None:
        self.tela = ttk.Window()


    def tela_adicionar_consumo(self):
        def adicionar_consumo( 
                            total_consumo: float,
                            consumo_verde: float,
                            consumo_amarelo: float,
                            consumo_vermelho: float,
                            iluminacao_publica: float
                            ):
            
            consumo = Consumo()
            consumo.definir_valores(tipo='total_consumo', valor=total_consumo)
            consumo.definir_valores(tipo='consumo_verde', valor=consumo_verde)
            consumo.definir_valores(tipo='consumo_amarelo', valor=consumo_amarelo)
            consumo.definir_valores(tipo='consumo_vermelho', valor=consumo_vermelho)
            consumo.definir_valores(tipo='ilumicacao_publica', valor=iluminacao_publica)

        def carregar_consumo():
            consumo = Consumo()
            self.entrada_total_consumo.delete(0, 'end')
            self.entrada_total_consumo.insert(0, f'{consumo.total_consumo}')
            self.entrada_consumo_verde.delete(0, 'end')
            self.entrada_consumo_verde.insert(0, f'{consumo.consumo_verde}')
            self.entrada_consumo_amarelo.delete(0, 'end')
            self.entrada_consumo_amarelo.insert(0, f'{consumo.consumo_amarelo}')
            self.entrada_consumo_vermelho.delete(0, 'end')
            self.entrada_consumo_vermelho.insert(0, f'{consumo.consumo_vermelho}')
            self.entrada_iluminacao_publica.delete(0, 'end')
            self.entrada_iluminacao_publica.insert(0, f'{consumo.iluminacao_publica}')
        def tratar_get(x) -> float:
            try:
                x = float(x)
                return x
            except ValueError:
                mensagem = f'Valor ---> "{x}" <--- é inválido.'
                messagebox.showerror("Erro", mensagem)
                print(f'O valor: "{x}" não pode ser convertido para float')
            return 0
        ttk.Label(self.tela, text="Total Consumo   ----------------> ").place(x=15, y=15)
        self.entrada_total_consumo = ttk.Entry(self.tela, width=10)
        self.entrada_total_consumo.place(x=200, y=10)

        ttk.Label(self.tela, text="Consumo Verde    -------------> ").place(x=15, y=55)
        self.entrada_consumo_verde = ttk.Entry(self.tela, width=10)
        self.entrada_consumo_verde.place(x=200, y=50)

        ttk.Label(self.tela, text="Consumo Amarelo    ----------> ").place(x=15, y=95)
        self.entrada_consumo_amarelo = ttk.Entry(self.tela, width=10)
        self.entrada_consumo_amarelo.place(x=200, y=90)

        ttk.Label(self.tela, text="Consumo Vermelho    --------> ").place(x=15, y=135)
        self.entrada_consumo_vermelho = ttk.Entry(self.tela, width=10)
        self.entrada_consumo_vermelho.place(x=200, y=130)

        ttk.Label(self.tela, text="Iluminação Pública    ----------> ").place(x=15, y=175)
        self.entrada_iluminacao_publica = ttk.Entry(self.tela, width=10)
        self.entrada_iluminacao_publica.place(x=200, y=170)

        comando = lambda: adicionar_consumo(
            total_consumo=tratar_get(self.entrada_total_consumo.get()),
            consumo_verde=tratar_get(self.entrada_consumo_verde.get()),
            consumo_amarelo=tratar_get(self.entrada_consumo_amarelo.get()),
            consumo_vermelho=tratar_get(self.entrada_consumo_vermelho.get()),
            iluminacao_publica=tratar_get(self.entrada_iluminacao_publica.get())
        )
        
        self.botao_salvar = ttk.Button(self.tela, text="Salvar", bootstyle='success-outline', command=comando)
        self.botao_salvar.place(x=120, y=225)

        self.botao_carregar_na_memoria = ttk.Button(self.tela, text='Carregar valores', bootstyle='success-outline', command=lambda: carregar_consumo())
        self.botao_carregar_na_memoria.place(x=120, y=260)

        self.tela.title('Add Consumo')
        self.tela.geometry('300x300')
        self.tela.mainloop()





class InterfacePrincipal:
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
    # app = Interface().iniciar()
    app_2 = InterfacesSecundarias()
    app_2.tela_adicionar_consumo()