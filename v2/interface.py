import json
import os
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox

# Configuração do arquivo
ARQUIVO_JSON = "dados_consumo.json"

# Criar arquivo inicial se não existir
if not os.path.exists(ARQUIVO_JSON):
    dados_iniciais = {
        "joabe": {"consumo_anterior": 0.0, "consumo_atual": 20.0},
        "milly": {"consumo_anterior": 0.0, "consumo_atual": 80.0},
        "wanderson": {"consumo_anterior": 0.0, "consumo_atual": 50.0}
    }
    with open(ARQUIVO_JSON, "w") as f:
        json.dump(dados_iniciais, f, indent=4)

class AppConsumo(tb.Window):
    def __init__(self):
        super().__init__(themename="flatly")
        self.title("Gerenciador de Consumo Dinâmico")
        self.geometry("900x500")

        # Container Principal
        self.main_frame = tb.Frame(self, padding=20)
        self.main_frame.pack(fill=BOTH, expand=YES)
        
        self.renderizar_tela()

    def carregar_dados(self):
        with open(ARQUIVO_JSON, "r") as f:
            return json.load(f)

    def salvar_dados(self, dados):
        with open(ARQUIVO_JSON, "w") as f:
            json.dump(dados, f, indent=4)

    def renderizar_tela(self):
        # Limpa os cards atuais para reconstruir
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        dados = self.carregar_dados()
        
        # Grid layout dinâmico
        for i, (nome, valores) in enumerate(dados.items()):
            self.criar_card(nome, valores, i)

    def criar_card(self, nome, valores, index):
        # Estilo do Card
        card = tb.Frame(self.main_frame, bootstyle="secondary", padding=15)
        card.grid(row=0, column=index, padx=10, pady=10, sticky="nsew")
        
        tb.Label(card, text=nome.title(), font=("Sans", 14, "bold"), bootstyle="inverse-secondary").pack(pady=5)
        
        # Exibição dos valores
        tb.Label(card, text=f"Anterior: {valores['consumo_anterior']}", bootstyle="inverse-secondary").pack(anchor=W)
        tb.Label(card, text=f"Atual: {valores['consumo_atual']}", bootstyle="inverse-secondary").pack(anchor=W)
        
        # Botão de Editar
        btn_edit = tb.Button(
            card, 
            text="Editar Dados", 
            bootstyle="light-outline", 
            command=lambda n=nome: self.abrir_editor(n)
        )
        btn_edit.pack(pady=(15, 0), fill=X)

    def abrir_editor(self, nome):
        # Janela de diálogo para edição
        dados = self.carregar_dados()
        usuario = dados[nome]

        top = tb.Toplevel(title=f"Editando: {nome}")
        top.geometry("300x250")
        top.grab_set() # Foca apenas nesta janela

        tb.Label(top, text="Consumo Anterior:").pack(pady=(10,0))
        ent_ant = tb.Entry(top)
        ent_ant.insert(0, usuario['consumo_anterior'])
        ent_ant.pack(pady=5)

        tb.Label(top, text="Consumo Atual:").pack(pady=(10,0))
        ent_atu = tb.Entry(top)
        ent_atu.insert(0, usuario['consumo_atual'])
        ent_atu.pack(pady=5)

        def confirmar():
            try:
                # Atualiza o dicionário
                dados[nome]['consumo_anterior'] = float(ent_ant.get())
                dados[nome]['consumo_atual'] = float(ent_atu.get())
                
                # Salva no arquivo e atualiza tela
                self.salvar_dados(dados)
                self.renderizar_tela()
                top.destroy()
            except ValueError:
                Messagebox.show_error("Use apenas números e ponto decimal.", "Erro de entrada")

        tb.Button(top, text="Salvar Alterações", bootstyle="success", command=confirmar).pack(pady=20)

if __name__ == "__main__":
    app = AppConsumo()
    app.mainloop()