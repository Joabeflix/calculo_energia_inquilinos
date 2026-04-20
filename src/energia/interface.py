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
        self.resumo_labels: dict[str, tb.Label] = {}

        self.root = tb.Window(themename="flatly")
        self.root.title("Sistema de Energia")
        self.root.geometry("840x560")
        self.root.minsize(760, 520)

        self._montar_tela_principal()

    def _montar_tela_principal(self) -> None:
        self.frame = tb.Frame(self.root, padding=28)
        self.frame.pack(fill=BOTH, expand=True)
        self.frame.columnconfigure(0, weight=3)
        self.frame.columnconfigure(1, weight=2)
        self.frame.rowconfigure(1, weight=1)

        hero = tb.Frame(self.frame, bootstyle="light", padding=24)
        hero.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 18))
        hero.columnconfigure(0, weight=1)

        tb.Label(
            hero,
            text="Gestao de Energia",
            font=("Segoe UI", 24, "bold"),
            bootstyle="dark",
        ).grid(row=0, column=0, sticky=W, padx=24, pady=(22, 6))
        tb.Label(
            hero,
            text="Controle leituras, tarifas e gere faturas com mais clareza.",
            font=("Segoe UI", 11),
            bootstyle="secondary",
        ).grid(row=1, column=0, sticky=W, padx=24, pady=(0, 22))

        painel_acoes = tb.Labelframe(self.frame, text="Acoes principais", padding=22)
        painel_acoes.grid(row=1, column=0, sticky="nsew", padx=(0, 12))
        painel_acoes.columnconfigure(0, weight=1)

        acoes = [
            (
                "Gerar faturas em PDF",
                "Executa o calculo, salva o rateio no data.json e monta os PDFs.",
                SUCCESS,
                self.gerar_pdf,
            ),
            (
                "Gerenciar inquilinos",
                "Adicione moradores, ajuste leituras e remova registros antigos.",
                PRIMARY,
                self.tela_inquilinos,
            ),
            (
                "Atualizar taxas e consumo",
                "Edite valores da conta principal usados no rateio do mes.",
                WARNING,
                self.tela_taxas,
            ),
        ]

        for indice, (titulo, descricao, estilo, comando) in enumerate(acoes):
            card = tb.Frame(painel_acoes, bootstyle="light", padding=18)
            card.grid(row=indice, column=0, sticky="ew", pady=(0, 12))
            card.columnconfigure(0, weight=1)

            tb.Label(card, text=titulo, font=("Segoe UI", 13, "bold"), bootstyle="dark").grid(
                row=0, column=0, sticky=W
            )
            tb.Label(
                card,
                text=descricao,
                font=("Segoe UI", 10),
                bootstyle="secondary",
                wraplength=420,
                justify=LEFT,
            ).grid(row=1, column=0, sticky=W, pady=(4, 12))
            tb.Button(card, text=titulo, bootstyle=estilo, command=comando).grid(
                row=2, column=0, sticky=W
            )

        painel_resumo = tb.Labelframe(self.frame, text="Resumo rapido", padding=22)
        painel_resumo.grid(row=1, column=1, sticky="nsew", padx=(12, 0))
        painel_resumo.columnconfigure(0, weight=1)

        self._construir_resumo(painel_resumo)

    def _construir_resumo(self, parent) -> None:
        cards = [
            ("quantidade_inquilinos", "Inquilinos cadastrados", "primary"),
            ("preco_base", "Preco base kWh", "success"),
            ("iluminacao_publica", "Iluminacao publica", "warning"),
            ("total_consumo", "Consumo total", "info"),
        ]

        for indice, (chave, titulo, estilo) in enumerate(cards):
            card = tb.Frame(parent, bootstyle="light", padding=16)
            card.grid(row=indice, column=0, sticky="ew", pady=(0, 10))
            card.columnconfigure(0, weight=1)

            tb.Label(
                card,
                text=titulo,
                font=("Segoe UI", 10),
                foreground="#52606d",
            ).grid(row=0, column=0, sticky=W)
            valor_label = tb.Label(
                card,
                text="",
                font=("Segoe UI", 16, "bold"),
                foreground="#1f2933",
            )
            valor_label.grid(row=1, column=0, sticky=W, pady=(4, 0))
            self.resumo_labels[chave] = valor_label

        tb.Label(
            parent,
            text="Os dados usados pelo sistema sao centralizados em dados/data.json.",
            font=("Segoe UI", 10),
            bootstyle="secondary",
            wraplength=250,
            justify=LEFT,
        ).grid(row=len(cards), column=0, sticky=W, pady=(10, 0))

        self.atualizar_resumo()

    def atualizar_resumo(self) -> None:
        self.gd.recarregar()

        valores = {
            "quantidade_inquilinos": str(self.gd.quantidade_inquilinos),
            "preco_base": f"R$ {self.gd.preco_base:.4f}",
            "iluminacao_publica": f"R$ {self.gd.iluminacao_publica:.2f}",
            "total_consumo": f"{self.gd.total_consumo:.2f} kWh",
        }

        for chave, valor in valores.items():
            label = self.resumo_labels.get(chave)
            if label is not None:
                label.configure(text=valor)

    def gerar_pdf(self) -> None:
        try:
            calc = CalcularEnergia(self.gd)
            calc.calcular_energia()
            gerar_faturas_pdf(self.gd)
            self.atualizar_resumo()
            messagebox.showinfo("Sucesso", "PDF gerado com sucesso!")
        except EnergiaError as exc:
            messagebox.showerror("Erro", str(exc))
        except Exception as exc:
            messagebox.showerror("Erro inesperado", str(exc))

    def tela_inquilinos(self) -> None:
        win = tb.Toplevel(self.root)
        win.title("Inquilinos")
        win.geometry("860x620")
        win.minsize(760, 560)

        root_frame = tb.Frame(win, padding=18)
        root_frame.pack(fill=BOTH, expand=True)
        root_frame.rowconfigure(1, weight=1)
        root_frame.columnconfigure(0, weight=1)

        header = tb.Frame(root_frame)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        header.columnconfigure(0, weight=1)

        tb.Label(header, text="Inquilinos", font=("Segoe UI", 20, "bold")).grid(
            row=0, column=0, sticky=W
        )
        tb.Label(
            header,
            text="Edite leituras com mais conforto e adicione novos moradores no formulario abaixo.",
            font=("Segoe UI", 10),
            bootstyle="secondary",
        ).grid(row=1, column=0, sticky=W, pady=(4, 0))

        container = tb.Labelframe(root_frame, text="Leituras cadastradas", padding=14)
        container.grid(row=1, column=0, sticky="nsew")
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        canvas = tb.Canvas(container, highlightthickness=0)
        scrollbar = tb.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_frame = tb.Frame(canvas)

        scroll_frame.bind("<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        def atualizar_cards() -> None:
            self.gd.recarregar()
            for widget in scroll_frame.winfo_children():
                widget.destroy()

            if not self.gd.dados_inquilinos:
                vazio = tb.Frame(scroll_frame, bootstyle="light", padding=18)
                vazio.pack(fill=X, pady=4)
                tb.Label(
                    vazio,
                    text="Nenhum inquilino cadastrado ainda.",
                    font=("Segoe UI", 11, "bold"),
                    bootstyle="dark",
                ).pack(anchor=W)
                tb.Label(
                    vazio,
                    text="Use o formulario ao final da janela para adicionar o primeiro registro.",
                    font=("Segoe UI", 10),
                    bootstyle="secondary",
                ).pack(anchor=W, pady=(4, 0))
                return

            for nome, dados in self.gd.dados_inquilinos.items():
                card = tb.Frame(scroll_frame, bootstyle="light", padding=16)
                card.pack(fill=X, pady=6)
                card.columnconfigure(0, weight=1)
                card.columnconfigure(1, weight=1)

                tb.Label(card, text=nome, font=("Segoe UI", 12, "bold"), bootstyle="dark").grid(
                    row=0, column=0, columnspan=2, sticky=W
                )
                tb.Label(
                    card,
                    text="Atualize as leituras e salve para manter o rateio sincronizado.",
                    font=("Segoe UI", 9),
                    bootstyle="secondary",
                ).grid(row=1, column=0, columnspan=2, sticky=W, pady=(2, 10))

                campo_anterior = tb.Frame(card)
                campo_anterior.grid(row=2, column=0, sticky="ew", padx=(0, 8))
                campo_anterior.columnconfigure(0, weight=1)
                tb.Label(campo_anterior, text="Leitura anterior", font=("Segoe UI", 9, "bold")).grid(
                    row=0, column=0, sticky=W, pady=(0, 4)
                )
                anterior = tb.Entry(campo_anterior)
                anterior.insert(0, str(dados["consumo_anterior"]))
                anterior.grid(row=1, column=0, sticky="ew")

                campo_atual = tb.Frame(card)
                campo_atual.grid(row=2, column=1, sticky="ew", padx=(8, 0))
                campo_atual.columnconfigure(0, weight=1)
                tb.Label(campo_atual, text="Leitura atual", font=("Segoe UI", 9, "bold")).grid(
                    row=0, column=0, sticky=W, pady=(0, 4)
                )
                atual = tb.Entry(campo_atual)
                atual.insert(0, str(dados["consumo_atual"]))
                atual.grid(row=1, column=0, sticky="ew")

                def salvar(
                    nome_inquilino: str = nome,
                    anterior_entry: tb.Entry = anterior,
                    atual_entry: tb.Entry = atual,
                ) -> None:
                    try:
                        self.gd.cadastrar_atualizar_inquilino(
                            {
                                "nome": nome_inquilino,
                                "consumo_anterior": anterior_entry.get(),
                                "consumo_atual": atual_entry.get(),
                            }
                        )
                        atualizar_cards()
                        self.atualizar_resumo()
                    except EnergiaError as exc:
                        messagebox.showerror("Erro", str(exc))

                def remover(nome_inquilino: str = nome) -> None:
                    self.gd.remover_inquilino(nome_inquilino)
                    atualizar_cards()
                    self.atualizar_resumo()

                btn_frame = tb.Frame(card)
                btn_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(12, 0))
                tb.Button(btn_frame, text="Salvar alteracoes", command=salvar, bootstyle=SUCCESS).pack(
                    side=LEFT
                )
                tb.Button(btn_frame, text="Remover", command=remover, bootstyle=DANGER).pack(
                    side=LEFT, padx=(10, 0)
                )

        atualizar_cards()

        add_frame = tb.Labelframe(root_frame, text="Novo inquilino", padding=16)
        add_frame.grid(row=2, column=0, sticky="ew", pady=(16, 0))
        for coluna in range(3):
            add_frame.columnconfigure(coluna, weight=1)

        tb.Label(add_frame, text="Nome", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky=W, pady=(0, 4))
        tb.Label(add_frame, text="Leitura anterior", font=("Segoe UI", 9, "bold")).grid(
            row=0, column=1, sticky=W, padx=(12, 0), pady=(0, 4)
        )
        tb.Label(add_frame, text="Leitura atual", font=("Segoe UI", 9, "bold")).grid(
            row=0, column=2, sticky=W, padx=(12, 0), pady=(0, 4)
        )

        nome = tb.Entry(add_frame)
        nome.grid(row=1, column=0, sticky="ew")

        anterior = tb.Entry(add_frame)
        anterior.grid(row=1, column=1, sticky="ew", padx=(12, 0))

        atual = tb.Entry(add_frame)
        atual.grid(row=1, column=2, sticky="ew", padx=(12, 0))

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
                self.atualizar_resumo()
                for entry in (nome, anterior, atual):
                    entry.delete(0, "end")
            except ValidationError as exc:
                messagebox.showerror("Erro", str(exc))
            except Exception as exc:
                messagebox.showerror("Erro inesperado", str(exc))

        tb.Button(add_frame, text="Adicionar inquilino", command=adicionar, bootstyle=PRIMARY).grid(
            row=2, column=0, columnspan=3, sticky=W, pady=(14, 0)
        )

        win.bind("<Destroy>", lambda event: self.atualizar_resumo() if event.widget is win else None)

    def tela_taxas(self) -> None:
        win = tb.Toplevel(self.root)
        win.title("Taxas e Consumo")
        win.geometry("760x620")
        win.minsize(680, 560)

        root_frame = tb.Frame(win, padding=22)
        root_frame.pack(fill=BOTH, expand=True)
        root_frame.columnconfigure(0, weight=1)
        root_frame.columnconfigure(1, weight=1)

        tb.Label(root_frame, text="Taxas e Consumo", font=("Segoe UI", 20, "bold")).grid(
            row=0, column=0, columnspan=2, sticky=W
        )
        tb.Label(
            root_frame,
            text="Atualize os valores da conta principal usados pelo calculo do rateio.",
            font=("Segoe UI", 10),
            bootstyle="secondary",
        ).grid(row=1, column=0, columnspan=2, sticky=W, pady=(4, 18))

        secoes = {
            "Tarifas": (
                ("preco_base", "Preco base do kWh"),
                ("adicional_amarelo", "Adicional bandeira amarela"),
                ("adicional_vermelho", "Adicional bandeira vermelha"),
            ),
            "Consumo da conta": (
                ("total_consumo", "Consumo total da fatura"),
                ("consumo_verde", "Consumo em bandeira verde"),
                ("consumo_amarelo", "Consumo em bandeira amarela"),
                ("consumo_vermelho", "Consumo em bandeira vermelha"),
                ("iluminacao_publica", "Iluminacao publica"),
            ),
        }

        campos: dict[str, tb.Entry] = {}
        for indice, (titulo, itens) in enumerate(secoes.items()):
            frame = tb.Labelframe(root_frame, text=titulo, padding=16)
            frame.grid(row=2, column=indice, sticky="nsew", padx=(0, 10) if indice == 0 else (10, 0))
            frame.columnconfigure(0, weight=1)

            for linha, (campo, legenda) in enumerate(itens):
                tb.Label(frame, text=legenda, font=("Segoe UI", 9, "bold")).grid(
                    row=linha * 2, column=0, sticky=W, pady=(0 if linha == 0 else 8, 4)
                )
                entry = tb.Entry(frame)
                entry.insert(0, str(getattr(self.gd, campo)))
                entry.grid(row=linha * 2 + 1, column=0, sticky="ew")
                campos[campo] = entry

        aviso = tb.Frame(root_frame, bootstyle="light", padding=14)
        aviso.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(18, 0))
        tb.Label(
            aviso,
            text="Dica: a soma das bandeiras deve acompanhar o consumo total para o calculo funcionar sem inconsistencias.",
            font=("Segoe UI", 10),
            bootstyle="dark",
            wraplength=680,
            justify=LEFT,
        ).pack(anchor=W)

        def salvar() -> None:
            try:
                self.gd.atualizar_configuracoes({campo: entry.get() for campo, entry in campos.items()})
                self.atualizar_resumo()
                messagebox.showinfo("Sucesso", "Dados atualizados!")
            except EnergiaError as exc:
                messagebox.showerror("Erro", str(exc))
            except Exception as exc:
                messagebox.showerror("Erro inesperado", str(exc))

        tb.Button(root_frame, text="Salvar configuracoes", command=salvar, bootstyle=SUCCESS).grid(
            row=4, column=0, columnspan=2, sticky=W, pady=(18, 0)
        )

        win.bind("<Destroy>", lambda event: self.atualizar_resumo() if event.widget is win else None)

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    App().run()
