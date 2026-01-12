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



    chaves_alteraveis = Literal['preco_base', 'adicional_amarelo', 'adicional_vermelho', 'tet']
    def definir_valores(self, tipo: chaves_alteraveis, valor:  float) -> None:
        with open("valoreskwr.json", "r", encoding="utf-8") as f:
            dados = json.load(f)
        dados[tipo] = valor
        with open("valoreskwr.json", "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
        self.dados_valores = self.carregar_dados()







if __name__ == '__main__':
    print('Testando')


    valor = ValoresKwh()
    print(valor.amarelo)
    valor.definir_valores('adicional_amarelo', 0.02395161)
    print(valor.amarelo)




# x = ValoresKwh()
# print(x.preco_base)
# print(x.adicional_amarelo)
# print(x.adiconal_vermelho)
# print('-   - ' * 5)


# print(x.verde)
# print(x.amarelo)
# print(x.vermelho)



