from class_dados import Consumo, ValoresKwh, Inquilinos
from tipos import TipoInquilino, TipoConsumo, TipoValKwr

inquilinos = Inquilinos()

consumo_geral: TipoConsumo = {"total_consumo": 496,
                              "consumo_verde": 105.21,
                              "consumo_amarelo": 390.79,
                              "consumo_vermelho": 0,
                              "ilumicacao_publica": 43.93
                              }

class CalcularEnergia():
    def __init__(self) -> None:
        self.porcentagem_amarela: None | float = None
        
    




