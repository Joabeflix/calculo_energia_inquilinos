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
    @property
    def iluminacao_publica(self) -> float:
        return self.dados_consumo["ilumicacao_publica"]

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

class Inquilinos:
    def __init__(self) -> None:
        self.dados = self.carregar_dados()

    def carregar_dados(self) -> dict:
        with open('inquilinos.json', encoding="utf-8") as file:
            return json.load(file)
    
    @property
    def dados_inquilinos(self):
        return self.dados

    @property
    def inquilinos_cadastrados(self) -> list:
        return list(self.dados.keys())

    @property
    def quantidade_inquilinos(self) -> int:
        return len(self.dados)
    
    def limpar_inquilinos(self) -> None:
        dados = {}

        with open("inquilinos.json", "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)

        self.dados = self.carregar_dados()


    def cadastrar_atualizar_inquilino(self, inquilino):
        with open("inquilinos.json", "r", encoding="utf-8") as f:
            dados = json.load(f)

        dados[inquilino['nome']] = {
            "consumo_anterior": inquilino['consumo_anterior'],
            "consumo_atual": inquilino['consumo_atual']
        }

        with open("inquilinos.json", "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)

        self.dados = self.carregar_dados()

if __name__ == '__main__':
    inq = Inquilinos()
    # inq.limpar_inquilinos()
    # print(inq.inquilinos_cadastrados)
    # print(inq.quantidade_inquilinos)
    x: TipoInquilino = {"nome": "suellen",
                        "consumo_anterior": 231.8,
                        "consumo_atual": 416.5}
    y: TipoInquilino = {"nome": "milly",
                        "consumo_anterior": 248.3,
                        "consumo_atual": 472.2}
    z: TipoInquilino = {"nome": "wanderson",
                        "consumo_anterior": 103.2,
                        "consumo_atual": 177.4} 
    inq.cadastrar_atualizar_inquilino(inquilino=x)
    inq.cadastrar_atualizar_inquilino(inquilino=y)
    inq.cadastrar_atualizar_inquilino(inquilino=z)

    print(inq.inquilinos_cadastrados)
    print(inq.quantidade_inquilinos)
    # print('Testando')
    # consumo_app = Consumo()
    # print(consumo_app.total_consumo)
    # print(consumo_app.consumo_verde)
    # print(consumo_app.consumo_amarelo)
    # print(consumo_app.consumo_vermelho)

    # consumo_app.definir_valores(tipo='total_consumo', valor = 100)
    # consumo_app.definir_valores(tipo='consumo_verde', valor = 45)
    # consumo_app.definir_valores(tipo='consumo_amarelo', valor = 98)
    # consumo_app.definir_valores(tipo='consumo_vermelho', valor=34)
    # print(consumo_app.total_consumo)
    # print(consumo_app.consumo_verde)
    # print(consumo_app.consumo_amarelo)
    # print(consumo_app.consumo_vermelho)
