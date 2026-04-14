"""Modulo para gerenciar os dados do sistema."""
import json
import os
from typing import Literal

def garantir_json_base(path: str, default_content: dict):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default_content, f, indent=4, ensure_ascii=False)

class GerenciadorDados:
    def __init__(self) -> None:
        self.path = os.path.join('dados', 'data.json')
        garantir_json_base(self.path, {
            "preco_base": 0.0, 
            "adicional_amarelo": 0.0, 
            "adicional_vermelho": 0.0,
            "total_consumo": 0.0, 
            "consumo_verde": 0.0, 
            "consumo_amarelo": 0.0, 
            "consumo_vermelho": 0.0, 
            "ilumicacao_publica": 0.0
        })
        self.dados = self.carregar_dados()


    def carregar_dados(self):
        with open(self.path, "r", encoding="utf-8") as file:
            return json.load(file)

    
    funcao_usar = {
        "ATUALIZAR": ...,
        "RETORNAR": ...
    }

    def atualizar_dados(self, tipo: str, valor: float) -> None:
        dados = self.carregar_dados()
        dados[tipo] = valor
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
        self.dados = dados

    # _funcao_usar = Literal["RETORNAR", [str, float]]


    def preco_base(self, fun: Literal["RETORNAR"] | list[float, str]) -> float | None:
        if fun == "RETORNAR":
            return float(self.dados.get('preco_base', 0))
        # self.atualizar_dados(self.funcao_usar[0], self.funcao_usar[1])


    def adicional_amarelo(self, fun) -> float: 
        return float(self.dados.get('adicional_amarelo', 0))
    


    def adicional_vermelho(self, fun) -> float: 
        return float(self.dados.get('adicional_vermelho', 0))
    


    def valor_verde(self, fun) -> float: 
        return self.preco_base()
    


    def valor_amarelo(self, fun) -> float: 
        return self.preco_base() + self.adicional_amarelo()
    


    def valor_vermelho(self, fun) -> float: 
        return self.preco_base() + self.adicional_vermelho()
    


    def total_consumo(self, fun) -> float: 
        return float(self.dados.get('total_consumo', 0))
    


    def consumo_verde(self, fun) -> float: 
        return float(self.dados.get('consumo_verde', 0))
    


    def consumo_amarelo(self, fun) -> float: 
        return float(self.dados.get('consumo_amarelo', 0))
    


    def consumo_vermelho(self, fun) -> float: 
        return float(self.dados.get('consumo_vermelho', 0))



    def iluminacao_publica(self, fun) -> float: 
        return float(self.dados.get("ilumicacao_publica", 0))









if __name__ == "__main__":
    app = GerenciadorDados()
    print(app.preco_base())
    print(app.adicional_amarelo)
    print(app.adicional_vermelho)
    print(app.valor_verde)
    print(app.valor_amarelo)
    print(app.valor_vermelho)
    print(app.total_consumo)
    print(app.consumo_verde)
    print(app.consumo_amarelo)
    print(app.consumo_vermelho)
    print(app.iluminacao_publica)
