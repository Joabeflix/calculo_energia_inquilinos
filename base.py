import json
from tipos import *
from typing import Literal

class ValoresKwh:
    def __init__(self) -> None:
        self.dados_valores: TipoValKwr = self.carregar_dados()

    def carregar_dados(self):
        with open('valoreskwr.json') as file:
            return json.load(file)

    @property
    def preco_base(self) -> float:
        return self.dados_valores['preco_base']
    @property
    def adicional_amarelo(self) -> float:
        return self.dados_valores['adicional_amarelo']
    @property
    def adicional_vermelho(self) -> float:
        return self.dados_valores['adicional_vermelho']
    @property
    def verde(self) -> float:
        return self.preco_base
    @property
    def amarelo(self) -> float:
        return self.preco_base + self.adicional_amarelo
    @ property
    def vermelho(self) -> float:
        return self.preco_base + self.adicional_vermelho



    chaves_alteraveis = Literal['preco_base', 'adicional_amarelo', 'adicional_vermelho']
    def definir_valores(self, tipo: chaves_alteraveis, valor:  float) -> None:
        with open("valoreskwr.json", "r", encoding="utf-8") as f:
            dados = json.load(f)
        dados[tipo] = valor
        with open("valoreskwr.json", "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
        self.dados_valores = self.carregar_dados()


class Consumo:
    def __init__(self) -> None:
        self.dados_consumo: TipoConsumo = self.carregar_dados()

    def carregar_dados(self):
        with open('consumo.json') as file:
            return json.load(file)

    @property
    def total_consumo(self) -> float:
        return self.dados_consumo['total_consumo']
    
    @property
    def consumo_verde(self) -> float:
        return self.dados_consumo['consumo_verde']
    @property
    def consumo_amarelo(self) -> float:
        return self.dados_consumo['consumo_amarelo']

    @property
    def consumo_vermelho(self) -> float:
        return self.dados_consumo['consumo_vermelho']        

    chaves_alteraveis = Literal['total_consumo',
                                'consumo_verde',
                                'consumo_amarelo',
                                'consumo_vermelho']
    def definir_valores(self, tipo: chaves_alteraveis, valor:  float) -> None:
        with open("consumo.json", "r", encoding="utf-8") as f:
            dados = json.load(f)
        dados[tipo] = valor
        with open("consumo.json", "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
        self.dados_consumo = self.carregar_dados()







if __name__ == '__main__':
    print('Testando')
    consumo_app = Consumo()
    print(consumo_app.total_consumo)
    print(consumo_app.consumo_verde)
    print(consumo_app.consumo_amarelo)
    print(consumo_app.consumo_vermelho)

    consumo_app.definir_valores(tipo='total_consumo', valor = 100)
    consumo_app.definir_valores(tipo='consumo_verde', valor = 45)
    consumo_app.definir_valores(tipo='consumo_amarelo', valor = 98)
    consumo_app.definir_valores(tipo='consumo_vermelho', valor=34)
    print(consumo_app.total_consumo)
    print(consumo_app.consumo_verde)
    print(consumo_app.consumo_amarelo)
    print(consumo_app.consumo_vermelho)
