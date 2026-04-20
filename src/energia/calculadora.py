from typing import Any

from energia.exceptions import ValidationError
from energia.gerenciador_de_dados import GerenciadorDados


class CalcularEnergia:
    def __init__(self, gerenciador: GerenciadorDados | None = None) -> None:
        self.dados = gerenciador or GerenciadorDados()
        self.atualizar_bases()

    def atualizar_bases(self) -> None:
        self.dados.recarregar()
        self.consumo_total = self.dados.total_consumo
        self.consumo_verde = self.dados.consumo_verde
        self.consumo_amarelo = self.dados.consumo_amarelo
        self.consumo_vermelho = self.dados.consumo_vermelho
        self.iluminacao_total = self.dados.iluminacao_publica
        self.qtd_inquilinos = self.dados.quantidade_inquilinos
        self.dados_inquilinos = self.dados.dados_inquilinos
        self.taxa_verde = self.dados.preco_base
        self.taxa_amarelo = self.dados.valor_total_amarelo
        self.taxa_vermelho = self.dados.valor_total_vermelho
        self.percentuais_bandeiras = self._calcular_percentuais_bandeiras()

    def _calcular_percentuais_bandeiras(self) -> dict[str, float]:
        if self.consumo_total <= 0:
            return {"verde": 0.0, "amarela": 0.0, "vermelha": 0.0}

        return {
            "verde": self.consumo_verde / self.consumo_total,
            "amarela": self.consumo_amarelo / self.consumo_total,
            "vermelha": self.consumo_vermelho / self.consumo_total,
        }

    def _validar_estado_calculo(self) -> None:
        if self.qtd_inquilinos <= 0:
            raise ValidationError("Cadastre ao menos um inquilino antes de calcular.")

        soma_bandeiras = self.consumo_verde + self.consumo_amarelo + self.consumo_vermelho
        if self.consumo_total > 0 and abs(soma_bandeiras - self.consumo_total) > 0.01:
            raise ValidationError(
                "A soma dos consumos por bandeira deve ser igual ao consumo total."
            )

    @staticmethod
    def _montar_resultado(
        consumo_anterior: float,
        consumo_atual: float,
        consumo: float,
        consumo_verde: float,
        consumo_amarelo: float,
        consumo_vermelho: float,
        taxa_verde: float,
        taxa_amarelo: float,
        taxa_vermelho: float,
        valor_verde: float,
        valor_amarelo: float,
        valor_vermelho: float,
        iluminacao_publica: float,
        total: float,
    ) -> dict[str, Any]:
        return {
            "registro_kwh_anterior": consumo_anterior,
            "registro_kwh_atual": consumo_atual,
            "kwh_consumido_mes": f"{consumo:.2f}",
            "valor_kwh_verde": f"{taxa_verde:.4f}",
            "valor_kwh_amarelo": f"{taxa_amarelo:.4f}",
            "valor_kwh_vermelho": f"{taxa_vermelho:.4f}",
            "consumo_kwh_verde": f"{consumo_verde:.2f}",
            "consumo_kwh_amarelo": f"{consumo_amarelo:.2f}",
            "consumo_kwh_vermelho": f"{consumo_vermelho:.2f}",
            "valor_verde": f"{valor_verde:.2f}",
            "valor_amarelo": f"{valor_amarelo:.2f}",
            "valor_vermelho": f"{valor_vermelho:.2f}",
            "iluminacao_publica": f"{iluminacao_publica:.2f}",
            "total": f"{total:.2f}",
        }

    def calcular_energia(self) -> dict[str, dict[str, Any]]:
        self.atualizar_bases()
        self._validar_estado_calculo()

        iluminacao_por_inquilino = self.iluminacao_total / self.qtd_inquilinos
        resultados: dict[str, dict[str, Any]] = {}

        for nome, dados in self.dados_inquilinos.items():
            consumo = dados["consumo_atual"] - dados["consumo_anterior"]
            consumo_verde = consumo * self.percentuais_bandeiras["verde"]
            consumo_amarelo = consumo * self.percentuais_bandeiras["amarela"]
            consumo_vermelho = consumo * self.percentuais_bandeiras["vermelha"]

            valor_verde = consumo_verde * self.taxa_verde
            valor_amarelo = consumo_amarelo * self.taxa_amarelo
            valor_vermelho = consumo_vermelho * self.taxa_vermelho
            total = iluminacao_por_inquilino + valor_verde + valor_amarelo + valor_vermelho

            resultado = self._montar_resultado(
                consumo_anterior=dados["consumo_anterior"],
                consumo_atual=dados["consumo_atual"],
                consumo=consumo,
                consumo_verde=consumo_verde,
                consumo_amarelo=consumo_amarelo,
                consumo_vermelho=consumo_vermelho,
                taxa_verde=self.taxa_verde,
                taxa_amarelo=self.taxa_amarelo,
                taxa_vermelho=self.taxa_vermelho,
                valor_verde=valor_verde,
                valor_amarelo=valor_amarelo,
                valor_vermelho=valor_vermelho,
                iluminacao_publica=iluminacao_por_inquilino,
                total=total,
            )
            self.dados.salvar_calculo_inquilino(nome, resultado)
            resultados[nome] = resultado

        return resultados
