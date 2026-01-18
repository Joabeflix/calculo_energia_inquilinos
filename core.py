from class_dados import Consumo, ValoresKwh, Inquilinos
from tipos import TipoInquilino, TipoConsumo, TipoValKwr


class CalcularEnergia():
    def __init__(self) -> None:
        consumo = Consumo()
        self.consumo_total = consumo.total_consumo
        self.consumo_verde = consumo.consumo_verde
        self.consumo_amarelo = consumo.consumo_amarelo
        self.consumo_vermelho = consumo.consumo_vermelho
        self.iluminacao_publica = consumo.iluminacao_publica
    
        self.porcentagem_verde: float = 0
        self.porcentagem_amarela: float = 0
        self.porcentagem_vermelha: float = 0
        self.carregar_porcentagens()
        
    def carregar_porcentagens(self):
        self.porcentagem_verde = self.consumo_verde / self.consumo_total
        self.porcentagem_amarela = self.consumo_amarelo / self.consumo_total
        self.porcentagem_vermelha = self.consumo_vermelho / self.consumo_total

    
    def calcular_energia(self):
        inquilinos = Inquilinos()
        valoreskwh = ValoresKwh()
        iluminacao_publica = self.iluminacao_publica / inquilinos.quantidade_inquilinos

        valores = {}
        for inq, dados in zip(
            inquilinos.inquilinos_cadastrados, 
            inquilinos.dados_inquilinos.values()):
            consumo = dados["consumo_atual"] - dados["consumo_anterior"]
            consumo_verde = consumo * self.porcentagem_verde
            consumo_amarelo = consumo * self.porcentagem_amarela
            consumo_vermelho = consumo * self.porcentagem_vermelha
            valor_verde = consumo_verde * valoreskwh.verde
            valor_amarelo = consumo_amarelo * valoreskwh.amarelo
            valor_vermelho = consumo_vermelho * valoreskwh.vermelho

            total = iluminacao_publica + valor_verde + valor_amarelo + valor_vermelho

            valores[inq] = {"valor_verde": f"{valor_verde:.2f}",
                            "valor_amarelo": f"{valor_amarelo:.2f}",
                            "valor_vermelho": f"{valor_vermelho:.2f}",
                            "iluminacao_publica": f"{iluminacao_publica:.2f}",
                            "total": f"{total:.2f}"}
            
        
        return valores
    
    
if __name__ == "__main__":
    consumo_geral: TipoConsumo = {"total_consumo": 496,
                                "consumo_verde": 105.21,
                                "consumo_amarelo": 390.79,
                                "consumo_vermelho": 0,
                                "ilumicacao_publica": 43.93
                                }
    app = CalcularEnergia()
    print(app.calcular_energia())

