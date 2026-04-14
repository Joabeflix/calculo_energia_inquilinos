import json
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from main import Inquilinos


class ConsumoManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Inquilinos - Energia")
        self.root.geometry("1100x600")
        
        # INSTANCIAÇÃO DA SUA CLASSE
        self.db = Inquilinos()

        self.main_frame = tb.Frame(self.root, padding=20)
        self.main_frame.pack(fill=BOTH, expand=YES)

        # Coluna Esquerda: Tabela
        self.left_frame = tb.Frame(self.main_frame)
        self.left_frame.pack(side=LEFT, fill=BOTH, expand=YES)

        tb.Label(self.left_frame, text="Lista de Consumo", font=("Helvetica", 12, "bold")).pack(anchor=W, pady=(0, 10))

        self.columns = ("nome", "anterior", "atual", "total")
        self.tree = tb.Treeview(self.left_frame, columns=self.columns, show="headings", bootstyle="primary")
        
        self.tree.heading("nome", text="Inquilino")
        self.tree.heading("anterior", text="Antigo (kWh)")
        self.tree.heading("atual", text="Atual (kWh)")
        self.tree.heading("total", text="Consumo")
        self.tree.pack(fill=BOTH, expand=YES)

        # Coluna Direita: Formulário
        self.form_frame = tb.Frame(self.main_frame, padding=(20, 0, 0, 0))
        self.form_frame.pack(side=RIGHT, fill=Y)

        tb.Label(self.form_frame, text="CADASTRO / EDIÇÃO", font=("Helvetica", 11, "bold")).pack(pady=(0, 20))
        
        tb.Label(self.form_frame, text="Nome:").pack(fill=X)
        self.ent_nome = tb.Entry(self.form_frame)
        self.ent_nome.pack(fill=X, pady=(0, 15))
        
        tb.Label(self.form_frame, text="Anterior:").pack(fill=X)
        self.ent_anterior = tb.Entry(self.form_frame)
        self.ent_anterior.pack(fill=X, pady=(0, 15))
        
        tb.Label(self.form_frame, text="Atual:").pack(fill=X)
        self.ent_atual = tb.Entry(self.form_frame)
        self.ent_atual.pack(fill=X, pady=(0, 20))

        tb.Button(self.form_frame, text="SALVAR", bootstyle=SUCCESS, command=self.salvar).pack(fill=X, pady=5)
        tb.Button(self.form_frame, text="LIMPAR/NOVO", bootstyle=INFO, command=self.limpar).pack(fill=X, pady=5)
        tb.Separator(self.form_frame).pack(fill=X, pady=20)
        tb.Button(self.form_frame, text="REMOVER", bootstyle=(DANGER, OUTLINE), command=self.excluir).pack(fill=X)
        
        self.tree.bind("<<TreeviewSelect>>", self.carregar_selecionado)
        self.atualizar_tabela()

    def atualizar_tabela(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        # Usa o 'dados_inquilinos' da sua classe
        for nome, val in self.db.dados_inquilinos.items():
            total = round(val['consumo_atual'] - val['consumo_anterior'], 2)
            self.tree.insert("", END, values=(nome, val['consumo_anterior'], val['consumo_atual'], total))

    def salvar(self):
        try:
            # Prepara o dicionário no formato que sua classe espera
            novo_inquilino = {
                'nome': self.ent_nome.get().strip(),
                'consumo_anterior': self.ent_anterior.get().replace(',', '.'),
                'consumo_atual': self.ent_atual.get().replace(',', '.')
            }
            
            if not novo_inquilino['nome']:
                messagebox.showwarning("Aviso", "O nome é obrigatório.")
                return

            # CHAMA O MÉTODO DA SUA CLASSE
            self.db.cadastrar_atualizar_inquilino(novo_inquilino)
            
            self.atualizar_tabela()
            self.limpar()
            messagebox.showinfo("Sucesso", "Dados salvos no JSON!")
        except ValueError:
            messagebox.showerror("Erro", "Valores numéricos inválidos.")

    def excluir(self):
        selecionado = self.tree.selection()
        if not selecionado: return
        
        nome = self.tree.item(selecionado)['values'][0]
        if messagebox.askyesno("Confirmar", f"Excluir {nome}?"):
            # CHAMA O MÉTODO DA SUA CLASSE
            if self.db.remover_inquilino(nome):
                self.atualizar_tabela()
                self.limpar()

    def carregar_selecionado(self, event):
        selecionado = self.tree.selection()
        if selecionado:
            item = self.tree.item(selecionado)['values']
            self.limpar()
            self.ent_nome.insert(0, item[0])
            self.ent_anterior.insert(0, item[1])
            self.ent_atual.insert(0, item[2])

    def limpar(self):
        self.ent_nome.delete(0, END)
        self.ent_anterior.delete(0, END)
        self.ent_atual.delete(0, END)
        self.ent_nome.focus()

if __name__ == "__main__":
    app = tb.Window(themename="darkly")
    ConsumoManager(app)
    app.mainloop()