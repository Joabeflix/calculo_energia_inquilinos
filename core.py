from class_dados import Consumo, ValoresKwh, Inquilinos
from tipos import TipoInquilino, TipoConsumo, TipoValKwr

inquilinos = Inquilinos()



class CalcularEnergia():
    def __init__(self, consumo_geral: TipoConsumo) -> None:
        self.consumo_total = consumo_geral["total_consumo"]
        self.consumo_verde = consumo_geral["consumo_verde"]
        self.consumo_amarelo = consumo_geral["consumo_amarelo"]
        self.consumo_vermelho = consumo_geral["consumo_vermelho"]
    
        self.porcentagem_verde: float = 0
        self.porcentagem_amarela: float = 0
        self.porcentagem_vermelha: float = 0
        self.carregar_porcentagens()
        
    def carregar_porcentagens(self):
        self.porcentagem_verde = self.consumo_verde / self.consumo_total
        self.porcentagem_amarela = self.consumo_amarelo / self.consumo_total
        self.porcentagem_vermelha = self.consumo_vermelho / self.consumo_total

    def teste(self):
        return self.porcentagem_amarela + self.porcentagem_verde + self.porcentagem_vermelha





if __name__ == "__main__":
    consumo_geral: TipoConsumo = {"total_consumo": 496,
                                "consumo_verde": 105.21,
                                "consumo_amarelo": 390.79,
                                "consumo_vermelho": 0,
                                "ilumicacao_publica": 43.93
                                }
    app = CalcularEnergia(consumo_geral=consumo_geral)
    print(app.teste())

    