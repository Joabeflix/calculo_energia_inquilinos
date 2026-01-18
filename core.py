from class_dados import Consumo, ValoresKwh, Inquilinos
from tipos import TipoInquilino, TipoConsumo, TipoValKwr
import json
import os

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

            valores[inq] = {"registro_kwh_anterior": dados["consumo_anterior"],
                            "registro_kwh_atual": dados["consumo_atual"],
                            "kwh_consumido_mes": f'{consumo:.2f}',
                            "valor_kwh_verde": valoreskwh.verde,
                            "valor_kwh_amarelo": valoreskwh.amarelo,
                            "valor_kwh_vermelho": valoreskwh.vermelho,
                            "consumo_kwh_verde": f'{consumo_verde:.2f}',
                            "consumo_kwh_amarelo": f'{consumo_amarelo:.2f}',
                            "consumo_kwh_vermelho": f'{consumo_vermelho:.2f}',
                            "valor_verde": f"{valor_verde:.2f}",
                            "valor_amarelo": f"{valor_amarelo:.2f}",
                            "valor_vermelho": f"{valor_vermelho:.2f}",
                            "iluminacao_publica": f"{iluminacao_publica:.2f}",
                            "total": f"{total:.2f}"}
            
        with open(os.path.join('dados', 'calculo_final.json'), "w", encoding="utf-8") as f:
            json.dump(valores, f, indent=4)
        return valores
    
    
if __name__ == "__main__":

    app = CalcularEnergia()
    print(app.calcular_energia())

