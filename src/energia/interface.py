from tkinter import messagebox

import ttkbootstrap as tb
from ttkbootstrap.constants import BOTH, DANGER, LEFT, PRIMARY, RIGHT, SUCCESS, WARNING, W, X, Y

from energia.calculadora import CalcularEnergia
from energia.exceptions import EnergiaError, ValidationError
from energia.gerador_pdf import gerar_faturas_pdf
from energia.gerenciador_de_dados import GerenciadorDados


class App:
    def __init__(self) -> None:
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

    def gerar_pdf(self) -> None:
        try:
            calc = CalcularEnergia(self.gd)
            calc.calcular_energia()
            gerar_faturas_pdf(self.gd)
            messagebox.showinfo("Sucesso", "PDF gerado com sucesso!")
        except EnergiaError as exc:
            messagebox.showerror("Erro", str(exc))
        except Exception as exc:
            messagebox.showerror("Erro inesperado", str(exc))

    def tela_inquilinos(self) -> None:
        win = tb.Toplevel(self.root)
        win.title("Inquilinos")
        win.geometry("600x500")

        container = tb.Frame(win)
        container.pack(fill=BOTH, expand=True, padx=10, pady=10)

        canvas = tb.Canvas(container)
        scrollbar = tb.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_frame = tb.Frame(canvas)

        scroll_frame.bind("<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        def atualizar_cards() -> None:
            self.gd.recarregar()
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

                def salvar(nome_inquilino: str = nome, anterior_entry: tb.Entry = anterior, atual_entry: tb.Entry = atual) -> None:
                    try:
                        self.gd.cadastrar_atualizar_inquilino(
                            {
                                "nome": nome_inquilino,
                                "consumo_anterior": anterior_entry.get(),
                                "consumo_atual": atual_entry.get(),
                            }
                        )
                        atualizar_cards()
                    except EnergiaError as exc:
                        messagebox.showerror("Erro", str(exc))

                def remover(nome_inquilino: str = nome) -> None:
                    self.gd.remover_inquilino(nome_inquilino)
                    atualizar_cards()

                btn_frame = tb.Frame(card)
                btn_frame.pack(fill=X)

                tb.Button(btn_frame, text="Salvar", command=salvar, bootstyle=SUCCESS).pack(side=LEFT, padx=5)
                tb.Button(btn_frame, text="Remover", command=remover, bootstyle=DANGER).pack(side=LEFT, padx=5)

        atualizar_cards()

        add_frame = tb.Frame(win)
        add_frame.pack(fill=X, pady=10)

        nome = tb.Entry(add_frame)
        nome.pack(side=LEFT, expand=True, fill=X, padx=5)

        anterior = tb.Entry(add_frame)
        anterior.pack(side=LEFT, expand=True, fill=X, padx=5)

        atual = tb.Entry(add_frame)
        atual.pack(side=LEFT, expand=True, fill=X, padx=5)

        def adicionar() -> None:
            try:
                self.gd.cadastrar_atualizar_inquilino(
                    {
                        "nome": nome.get(),
                        "consumo_anterior": anterior.get(),
                        "consumo_atual": atual.get(),
                    }
                )
                atualizar_cards()
                for entry in (nome, anterior, atual):
                    entry.delete(0, "end")
            except ValidationError as exc:
                messagebox.showerror("Erro", str(exc))
            except Exception as exc:
                messagebox.showerror("Erro inesperado", str(exc))

        tb.Button(win, text="Adicionar Inquilino", command=adicionar, bootstyle=PRIMARY).pack(pady=5)

    def tela_taxas(self) -> None:
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

        for campo, entry in campos.items():
            tb.Label(win, text=campo).pack()
            entry.pack(fill=X, padx=10, pady=5)
            entry.insert(0, str(getattr(self.gd, campo)))

        def salvar() -> None:
            try:
                self.gd.atualizar_configuracoes({campo: entry.get() for campo, entry in campos.items()})
                messagebox.showinfo("Sucesso", "Dados atualizados!")
            except EnergiaError as exc:
                messagebox.showerror("Erro", str(exc))
            except Exception as exc:
                messagebox.showerror("Erro inesperado", str(exc))

        tb.Button(win, text="Salvar", command=salvar, bootstyle=SUCCESS).pack(pady=20)

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    App().run()
