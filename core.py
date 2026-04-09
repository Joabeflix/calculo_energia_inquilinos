import json
import os
from class_dados import Consumo, ValoresKwh, Inquilinos, get_data_path

class CalcularEnergia():
    def __init__(self) -> None:
        # Inicializamos os caminhos e porcentagens base
        self.atualizar_bases()

    def atualizar_bases(self):
        """Recarrega os dados globais de consumo e recalcula as porcentagens."""
        consumo_global = Consumo()
        self.consumo_total = consumo_global.total_consumo
        self.consumo_verde = consumo_global.consumo_verde
        self.consumo_amarelo = consumo_global.consumo_amarelo
        self.consumo_vermelho = consumo_global.consumo_vermelho
        self.iluminacao_total = consumo_global.iluminacao_publica

        self.porcentagem_verde = 0.0
        self.porcentagem_amarela = 0.0
        self.porcentagem_vermelha = 0.0

        if self.consumo_total > 0:
            self.porcentagem_verde = self.consumo_verde / self.consumo_total
            self.porcentagem_amarela = self.consumo_amarelo / self.consumo_total
            self.porcentagem_vermelha = self.consumo_vermelho / self.consumo_total

    def calcular_energia(self):
        # Sempre atualiza as bases antes de calcular para pegar mudanças recentes
        self.atualizar_bases()
        
        inquilinos_db = Inquilinos()
        valores_kwh = ValoresKwh()
        
        qtd = inquilinos_db.quantidade_inquilinos
        iluminacao_por_inq = self.iluminacao_total / qtd if qtd > 0 else 0

        resultado_final = {}

        for inq, dados in inquilinos_db.dados.items():
            consumo = dados["consumo_atual"] - dados["consumo_anterior"]
            
            c_verde = consumo * self.porcentagem_verde
            c_amarelo = consumo * self.porcentagem_amarela
            c_vermelho = consumo * self.porcentagem_vermelha
            
            # Cálculo financeiro
            v_verde = c_verde * valores_kwh.verde
            v_amarelo = c_amarelo * valores_kwh.amarelo
            v_vermelho = c_vermelho * valores_kwh.vermelho

            total = iluminacao_por_inq + v_verde + v_amarelo + v_vermelho

            # Estrutura preparada para exibição e geração de PDF
            resultado_final[inq] = {
                "registro_kwh_anterior": dados["consumo_anterior"],
                "registro_kwh_atual": dados["consumo_atual"],
                "kwh_consumido_mes": f'{consumo:.2f}',
                "valor_kwh_verde": f'{valores_kwh.verde:.4f}',
                "valor_kwh_amarelo": f'{valores_kwh.amarelo:.4f}',
                "valor_kwh_vermelho": f'{valores_kwh.vermelho:.4f}',
                "consumo_kwh_verde": f'{c_verde:.2f}',
                "consumo_kwh_amarelo": f'{c_amarelo:.2f}',
                "consumo_kwh_vermelho": f'{c_vermelho:.2f}',
                "valor_verde": f"{v_verde:.2f}",
                "valor_amarelo": f"{v_amarelo:.2f}",
                "valor_vermelho": f"{v_vermelho:.2f}",
                "iluminacao_publica": f"{iluminacao_por_inq:.2f}",
                "total": f"{total:.2f}"
            }
            
        # Salva o resultado final na pasta /dados/
        path_final = get_data_path('calculo_final.json')
        with open(path_final, "w", encoding="utf-8") as f:
            json.dump(resultado_final, f, indent=4, ensure_ascii=False)
            
        return resultado_final

if __name__ == "__main__":
    # Teste rápido de execução
    calculo = CalcularEnergia()
    res = calculo.calcular_energia()
    print("Cálculo realizado e salvo com sucesso.")
