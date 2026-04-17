import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox

from v2.gerenciador_de_dados import GerenciadorDados
from v2.calculadora import CalcularEnergia
from v2.gerador_pdf import gerar_faturas_pdf

class App:
    def __init__(self):
        self.gd = GerenciadorDados()

        self.root = tb.Window(themename="darkly")
        self.root.title("Sistema de Energia")
        self.root.geometry("600x400")

        self.frame = tb.Frame(self.root, padding=20)
        self.frame.pack(fill=BOTH, expand=True)

        tb.Label(self.frame, text="Sistema de Energia", font=("Arial", 20, "bold")).pack(pady=20)

        tb.Button(self.frame, text="Gerar PDF", bootstyle=SUCCESS, command=self.gerar_pdf).pack(fill=X, pady=10)
        tb.Button(self.frame, text="Inquilinos", bootstyle=PRIMARY, command=self.tela_inquilinos).pack(fill=X, pady=10)
        tb.Button(self.frame, text="Taxas e Consumo", bootstyle=WARNING, command=self.tela_taxas).pack(fill=X, pady=10)

    def gerar_pdf(self):
        try:
            calc = CalcularEnergia()
            calc.calcular_energia()
            gerar_faturas_pdf()
            messagebox.showinfo("Sucesso", "PDF gerado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def tela_inquilinos(self):
        win = tb.Toplevel(self.root)
        win.title("Inquilinos")
        win.geometry("600x500")

        container = tb.Frame(win)
        container.pack(fill=BOTH, expand=True, padx=10, pady=10)

        canvas = tb.Canvas(container)
        scrollbar = tb.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_frame = tb.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        def atualizar_cards():
            for widget in scroll_frame.winfo_children():
                widget.destroy()

            for nome, dados in self.gd.dados_inquilinos.items():
                card = tb.Frame(scroll_frame, bootstyle="secondary", padding=10)
                card.pack(fill=X, pady=5)

                tb.Label(card, text=nome, font=("Arial", 12, "bold")).pack(anchor=W)

                frame_inputs = tb.Frame(card)
                frame_inputs.pack(fill=X, pady=5)

                anterior = tb.Entry(frame_inputs, width=15)
                anterior.insert(0, str(dados["consumo_anterior"]))
                anterior.pack(side=LEFT, padx=5)

                atual = tb.Entry(frame_inputs, width=15)
                atual.insert(0, str(dados["consumo_atual"]))
                atual.pack(side=LEFT, padx=5)

                def salvar(nome=nome, anterior=anterior, atual=atual):
                    try:
                        self.gd.cadastrar_atualizar_inquilino({
                            "nome": nome,
                            "consumo_anterior": float(anterior.get()),
                            "consumo_atual": float(atual.get())
                        })
                        atualizar_cards()
                    except Exception as e:
                        messagebox.showerror("Erro", str(e))

                def remover(nome=nome):
                    self.gd.remover_inquilino(nome)
                    atualizar_cards()

                btn_frame = tb.Frame(card)
                btn_frame.pack(fill=X)

                tb.Button(btn_frame, text="Salvar", command=salvar, bootstyle=SUCCESS).pack(side=LEFT, padx=5)
                tb.Button(btn_frame, text="Remover", command=remover, bootstyle=DANGER).pack(side=LEFT, padx=5)

        atualizar_cards()

        # adicionar novo inquilino
        add_frame = tb.Frame(win)
        add_frame.pack(fill=X, pady=10)

        nome = tb.Entry(add_frame)
        nome.pack(side=LEFT, expand=True, fill=X, padx=5)
        nome.insert(0, "Nome")

        anterior = tb.Entry(add_frame)
        anterior.pack(side=LEFT, expand=True, fill=X, padx=5)
        anterior.insert(0, "Anterior")

        atual = tb.Entry(add_frame)
        atual.pack(side=LEFT, expand=True, fill=X, padx=5)
        atual.insert(0, "Atual")

        def adicionar():
            try:
                nome_val = nome.get().strip()
                anterior_val = float(anterior.get())
                atual_val = float(atual.get())

                if not nome_val:
                    raise ValueError("Nome não pode ser vazio")

                self.gd.cadastrar_atualizar_inquilino({
                    "nome": nome_val,
                    "consumo_anterior": anterior_val,
                    "consumo_atual": atual_val
                })
                atualizar_cards()

                nome.delete(0, 'end')
                anterior.delete(0, 'end')
                atual.delete(0, 'end')

            except ValueError:
                messagebox.showerror("Erro", "Consumo deve ser número (int ou float)")
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        tb.Button(win, text="Adicionar Inquilino", command=adicionar, bootstyle=PRIMARY).pack(pady=5)

    def tela_taxas(self):
        win = tb.Toplevel(self.root)
        win.title("Taxas e Consumo")
        win.geometry("400x500")

        campos = {
            "preco_base": tb.Entry(win),
            "adicional_amarelo": tb.Entry(win),
            "adicional_vermelho": tb.Entry(win),
            "total_consumo": tb.Entry(win),
            "consumo_verde": tb.Entry(win),
            "consumo_amarelo": tb.Entry(win),
            "consumo_vermelho": tb.Entry(win),
            "iluminacao_publica": tb.Entry(win),
        }

        for k, entry in campos.items():
            tb.Label(win, text=k).pack()
            entry.pack(fill=X, padx=10, pady=5)
            entry.insert(0, str(getattr(self.gd, k) if hasattr(self.gd, k) else getattr(self.gd, f"_{k}", 0)))

        def salvar():
            try:
                self.gd.preco_base = campos["preco_base"].get()
                self.gd._adicional_amarelo = campos["adicional_amarelo"].get()
                self.gd._adicional_vermelho = campos["adicional_vermelho"].get()
                self.gd.total_consumo = campos["total_consumo"].get()
                self.gd.consumo_verde = campos["consumo_verde"].get()
                self.gd.consumo_amarelo = campos["consumo_amarelo"].get()
                self.gd.consumo_vermelho = campos["consumo_vermelho"].get()
                self.gd.iluminacao_publica = campos["iluminacao_publica"].get()
                messagebox.showinfo("Sucesso", "Dados atualizados!")
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        tb.Button(win, text="Salvar", command=salvar, bootstyle=SUCCESS).pack(pady=20)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    App().run()
