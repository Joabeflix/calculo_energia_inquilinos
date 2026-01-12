import json
from typing import TypedDict

class TipoValKwr(TypedDict):
    preco_base: float
    amarelo: float
    vermelho: float



class ValoresKwh:
    def __init__(self) -> None:
        with open('valoreskwr.json') as file:
            self.dados_valores: TipoValKwr = json.load(file)
    @property
    def preco_base(self) -> float:
        return self.dados_valores['preco_base']
    @property
    def adicional_amarelo(self) -> float:
        return self.dados_valores['amarelo']
    @property
    def adiconal_vermelho(self) -> float:
        return self.dados_valores['vermelho']

    @property
    def verde(self) -> float:
        return self.preco_base
    @property
    def amarelo(self) -> float:
        return self.preco_base + self.adicional_amarelo
    @ property
    def vermelho(self) -> float:
        return self.preco_base + self.adiconal_vermelho

x = ValoresKwh()
print(x.preco_base)
print(x.adicional_amarelo)
print(x.adiconal_vermelho)
print('-   - ' * 5)


print(x.verde)
print(x.amarelo)
print(x.vermelho)



