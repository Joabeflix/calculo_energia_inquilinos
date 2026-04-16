import os
from v2.gerenciador_de_dados import GerenciadorDados
import json


class CalcularEnergia():
    def __init__(self) -> None:
        self.diretorio = 'dados'
        self.path = os.path.join(self.diretorio, 'data.json')
        self.atualizar_bases()

    def atualizar_bases(self):
        self.dados = GerenciadorDados()
        self.consumo_total = self.dados.total_consumo
        self.consumo_verde = self.dados.consumo_verde
        self.consumo_amarelo = self.dados.consumo_amarelo
        self.consumo_vermelho = self.dados.consumo_vermelho
        self.iluminacao_total = self.dados.iluminacao_publica

        self.porcentagem_verde = 0.0
        self.porcentagem_amarela = 0.0
        self.porcentagem_vermelha = 0.0

        if self.consumo_total > 0:
            self.porcentagem_verde = self.consumo_verde / self.consumo_total
            self.porcentagem_amarela = self.consumo_amarelo / self.consumo_total
            self.porcentagem_vermelha = self.consumo_vermelho / self.consumo_total

        self.qtd_inquilinos = self.dados.quantidade_inquilinos
        self.dados_inquilinos = self.dados.dados_inquilinos

        self.taxa_verde = self.dados.preco_base
        self.taxa_amarelo = self.dados.valor_total_amarelo
        self.taxa_vermelho = self.dados.valor_total_vermelho


    def calcular_energia(self):
        # Sempre atualiza as bases antes de calcular para pegar mudanças recentes
        self.atualizar_bases()
        
        # inquilinos_db = Inquilinos()
        # valores_kwh = ValoresKwh()
        
        # qtd_inquilinos = ...
        iluminacao_por_inq = self.iluminacao_total / self.qtd_inquilinos if self.qtd_inquilinos > 0 else 0

        resultado_final = {}

        for inq, dados in self.dados_inquilinos.items():
            consumo = dados["consumo_atual"] - dados["consumo_anterior"]
            
            c_verde = consumo * self.porcentagem_verde
            c_amarelo = consumo * self.porcentagem_amarela
            c_vermelho = consumo * self.porcentagem_vermelha
            

            v_verde = c_verde * self.taxa_verde
            v_amarelo = c_amarelo * self.taxa_amarelo
            v_vermelho = c_vermelho * self.taxa_vermelho
            total = iluminacao_por_inq + v_verde + v_amarelo + v_vermelho

            # Estrutura preparada para exibição e geração de PDF
            resultado_final = {
                "registro_kwh_anterior": dados["consumo_anterior"],
                "registro_kwh_atual": dados["consumo_atual"],
                "kwh_consumido_mes": f'{consumo:.2f}',
                "valor_kwh_verde": f'{self.taxa_verde:.4f}',
                "valor_kwh_amarelo": f'{self.taxa_amarelo:.4f}',
                "valor_kwh_vermelho": f'{self.taxa_vermelho:.4f}',
                "consumo_kwh_verde": f'{c_verde:.2f}',
                "consumo_kwh_amarelo": f'{c_amarelo:.2f}',
                "consumo_kwh_vermelho": f'{c_vermelho:.2f}',
                "valor_verde": f"{v_verde:.2f}",
                "valor_amarelo": f"{v_amarelo:.2f}",
                "valor_vermelho": f"{v_vermelho:.2f}",
                "iluminacao_publica": f"{iluminacao_por_inq:.2f}",
                "total": f"{total:.2f}"
            }
            self.dados.salvar_calculo_inquilino(inq, resultado_final)
            
        # # Salva o resultado final na pasta /dados/
        # path_final = os.path.join('dados', 'calculo_final.json')
        # with open(path_final, "w", encoding="utf-8") as f:
        #     json.dump(resultado_final, f, indent=4, ensure_ascii=False)
            
        # return resultado_final

