import json
import os

class GerenciadorDados:
    def __init__(self) -> None:
        self.diretorio = 'dados'
        self.path = os.path.join(self.diretorio, 'data.json')
        self._configurar_base()
        self._dados = self._carregar_arquivo()

    def _configurar_base(self):
        if not os.path.exists(self.diretorio):
            os.makedirs(self.diretorio)
        
        if not os.path.exists(self.path):
            default = {
                "preco_base": 0.0, "adicional_amarelo": 0.0, "adicional_vermelho": 0.0,
                "total_consumo": 0.0, "consumo_verde": 0.0, "consumo_amarelo": 0.0,
                "consumo_vermelho": 0.0, "iluminacao_publica": 0.0
            }
            self._salvar_arquivo(default)

    def _carregar_arquivo(self) -> dict:
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _salvar_arquivo(self, dados: dict):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)

    def _atualizar(self, chave: str, valor: float):
        self._dados[chave] = float(valor)
        self._salvar_arquivo(self._dados)
        self._dados = self._carregar_arquivo()

    @property
    def preco_base(self) -> float:
        return self._dados.get("preco_base", 0.0)

    @preco_base.setter
    def preco_base(self, valor) -> None:
        self._atualizar("preco_base", valor)

    @property
    def adicional_amarelo(self) -> float:
        return self._dados.get("adicional_amarelo", 0.0)

    @adicional_amarelo.setter
    def adicional_amarelo(self, valor) -> None:
        self._atualizar("adicional_amarelo", valor)

    @property
    def adicional_vermelho(self) -> float:
        return self._dados.get("adicional_vermelho", 0.0)

    @adicional_vermelho.setter
    def adicional_vermelho(self, valor) -> None:
        self._atualizar("adicional_vermelho", valor)

    @property
    def valor_total_amarelo(self) -> float:
        return self.preco_base + self.adicional_amarelo

    @property
    def valor_total_vermelho(self) -> float:
        return self.preco_base + self.adicional_vermelho

    @property
    def total_consumo(self) -> float:
        return self._dados.get("total_consumo", 0.0)

    @total_consumo.setter
    def total_consumo(self, valor) -> None:
        self._atualizar("total_consumo", valor)

    @property
    def consumo_verde(self) -> float:
        return self._dados.get("consumo_verde", 0.0)

    @consumo_verde.setter
    def consumo_verde(self, valor) -> None:
        self._atualizar("consumo_verde", valor)

    @property
    def consumo_amarelo(self) -> float:
        return self._dados.get("consumo_amarelo", 0.0)

    @consumo_amarelo.setter
    def consumo_amarelo(self, valor) -> None:
        self._atualizar("consumo_amarelo", valor)

    @property
    def consumo_vermelho(self) -> float:
        return self._dados.get("consumo_vermelho", 0.0)

    @consumo_vermelho.setter
    def consumo_vermelho(self, valor) -> None:
        self._atualizar("consumo_vermelho", valor)

    @property
    def iluminacao_publica(self) -> float:
        return self._dados.get("iluminacao_publica", 0.0)

    @iluminacao_publica.setter
    def iluminacao_publica(self, valor) -> None:
        self._atualizar("iluminacao_publica", valor)

