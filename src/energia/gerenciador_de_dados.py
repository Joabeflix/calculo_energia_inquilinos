import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from energia.exceptions import DataStoreError, ValidationError
from energia.paths import DATA_FILE
from energia.validators import (
    to_float,
    validate_meter_readings,
    validate_name,
    validate_non_negative,
)


DEFAULT_DATA = {
    "preco_base": 0.0,
    "adicional_amarelo": 0.0,
    "adicional_vermelho": 0.0,
    "total_consumo": 0.0,
    "consumo_verde": 0.0,
    "consumo_amarelo": 0.0,
    "consumo_vermelho": 0.0,
    "iluminacao_publica": 0.0,
    "inquilinos": {},
}


class GerenciadorDados:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else DATA_FILE
        self.diretorio = self.path.parent
        self._configurar_base()
        self._dados = self._carregar_arquivo()

    def _configurar_base(self) -> None:
        self.diretorio.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._salvar_arquivo(deepcopy(DEFAULT_DATA))

    def _normalizar_estrutura(self, dados: dict[str, Any]) -> dict[str, Any]:
        normalizado = deepcopy(DEFAULT_DATA)
        normalizado.update(dados)
        normalizado["inquilinos"] = dados.get("inquilinos", {}) or {}
        return normalizado

    def _carregar_arquivo(self) -> dict[str, Any]:
        try:
            with self.path.open("r", encoding="utf-8") as file:
                dados = json.load(file)
        except FileNotFoundError as exc:
            raise DataStoreError(f"Arquivo de dados nao encontrado: {self.path}") from exc
        except json.JSONDecodeError as exc:
            raise DataStoreError(f"Arquivo de dados invalido: {self.path}") from exc

        return self._normalizar_estrutura(dados)

    def _salvar_arquivo(self, dados: dict[str, Any]) -> None:
        try:
            with self.path.open("w", encoding="utf-8") as file:
                json.dump(dados, file, indent=4, ensure_ascii=False)
        except OSError as exc:
            raise DataStoreError(f"Nao foi possivel salvar os dados em {self.path}.") from exc

    def recarregar(self) -> None:
        self._dados = self._carregar_arquivo()

    def _atualizar(self, chave: str, valor: Any) -> None:
        self._dados[chave] = validate_non_negative(to_float(valor, chave), chave)
        self._salvar_arquivo(self._dados)
        self.recarregar()

    @property
    def preco_base(self) -> float:
        return self._dados.get("preco_base", 0.0)

    @preco_base.setter
    def preco_base(self, valor: Any) -> None:
        self._atualizar("preco_base", valor)

    @property
    def adicional_amarelo(self) -> float:
        return self._dados.get("adicional_amarelo", 0.0)

    @adicional_amarelo.setter
    def adicional_amarelo(self, valor: Any) -> None:
        self._atualizar("adicional_amarelo", valor)

    @property
    def _adicional_amarelo(self) -> float:
        return self.adicional_amarelo

    @_adicional_amarelo.setter
    def _adicional_amarelo(self, valor: Any) -> None:
        self.adicional_amarelo = valor

    @property
    def adicional_vermelho(self) -> float:
        return self._dados.get("adicional_vermelho", 0.0)

    @adicional_vermelho.setter
    def adicional_vermelho(self, valor: Any) -> None:
        self._atualizar("adicional_vermelho", valor)

    @property
    def _adicional_vermelho(self) -> float:
        return self.adicional_vermelho

    @_adicional_vermelho.setter
    def _adicional_vermelho(self, valor: Any) -> None:
        self.adicional_vermelho = valor

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
    def total_consumo(self, valor: Any) -> None:
        self._atualizar("total_consumo", valor)

    @property
    def consumo_verde(self) -> float:
        return self._dados.get("consumo_verde", 0.0)

    @consumo_verde.setter
    def consumo_verde(self, valor: Any) -> None:
        self._atualizar("consumo_verde", valor)

    @property
    def consumo_amarelo(self) -> float:
        return self._dados.get("consumo_amarelo", 0.0)

    @consumo_amarelo.setter
    def consumo_amarelo(self, valor: Any) -> None:
        self._atualizar("consumo_amarelo", valor)

    @property
    def consumo_vermelho(self) -> float:
        return self._dados.get("consumo_vermelho", 0.0)

    @consumo_vermelho.setter
    def consumo_vermelho(self, valor: Any) -> None:
        self._atualizar("consumo_vermelho", valor)

    @property
    def iluminacao_publica(self) -> float:
        return self._dados.get("iluminacao_publica", 0.0)

    @iluminacao_publica.setter
    def iluminacao_publica(self, valor: Any) -> None:
        self._atualizar("iluminacao_publica", valor)

    @property
    def dados_inquilinos(self) -> dict[str, dict[str, Any]]:
        return self._dados.get("inquilinos", {})

    @property
    def inquilinos_cadastrados(self) -> list[str]:
        return list(self.dados_inquilinos.keys())

    @property
    def quantidade_inquilinos(self) -> int:
        return len(self.dados_inquilinos)

    def atualizar_configuracoes(self, configuracoes: dict[str, Any]) -> None:
        for campo in (
            "preco_base",
            "adicional_amarelo",
            "adicional_vermelho",
            "total_consumo",
            "consumo_verde",
            "consumo_amarelo",
            "consumo_vermelho",
            "iluminacao_publica",
        ):
            if campo in configuracoes:
                self._dados[campo] = validate_non_negative(
                    to_float(configuracoes[campo], campo), campo
                )

        self._salvar_arquivo(self._dados)
        self.recarregar()

    def cadastrar_atualizar_inquilino(self, inquilino: dict[str, Any]) -> None:
        nome = validate_name(inquilino["nome"])
        consumo_anterior, consumo_atual = validate_meter_readings(
            inquilino["consumo_anterior"], inquilino["consumo_atual"]
        )

        self._dados.setdefault("inquilinos", {})
        calculo_existente = self._dados["inquilinos"].get(nome, {}).get("calculo_inquilino")
        self._dados["inquilinos"][nome] = {
            "consumo_anterior": consumo_anterior,
            "consumo_atual": consumo_atual,
        }
        if calculo_existente:
            self._dados["inquilinos"][nome]["calculo_inquilino"] = calculo_existente

        self._salvar_arquivo(self._dados)
        self.recarregar()

    def remover_inquilino(self, nome: str) -> bool:
        if nome in self._dados.get("inquilinos", {}):
            del self._dados["inquilinos"][nome]
            self._salvar_arquivo(self._dados)
            self.recarregar()
            return True
        return False

    def salvar_calculo_inquilino(self, nome: str, dados: dict[str, Any]) -> None:
        if nome not in self._dados.get("inquilinos", {}):
            raise ValidationError(f"Inquilino '{nome}' nao encontrado para salvar calculo.")

        self._dados["inquilinos"][nome]["calculo_inquilino"] = dados
        self._salvar_arquivo(self._dados)
        self.recarregar()
