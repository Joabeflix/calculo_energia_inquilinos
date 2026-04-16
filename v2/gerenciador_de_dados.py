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
    def _adicional_amarelo(self) -> float:
        return self._dados.get("adicional_amarelo", 0.0)

    @_adicional_amarelo.setter
    def _adicional_amarelo(self, valor) -> None:
        self._atualizar("adicional_amarelo", valor)

    @property
    def _adicional_vermelho(self) -> float:
        return self._dados.get("adicional_vermelho", 0.0)

    @_adicional_vermelho.setter
    def _adicional_vermelho(self, valor) -> None:
        self._atualizar("adicional_vermelho", valor)

    @property
    def valor_total_amarelo(self) -> float:
        return self.preco_base + self._adicional_amarelo

    @property
    def valor_total_vermelho(self) -> float:
        return self.preco_base + self._adicional_vermelho

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

    @property
    def dados_inquilinos(self) -> dict: 
        return self._dados.get("inquilinos", {})

    @property
    def inquilinos_cadastrados(self) -> list: 
        return list(self.dados_inquilinos.keys())

    @property
    def quantidade_inquilinos(self) -> int: 
        return len(self.dados_inquilinos)

    def cadastrar_atualizar_inquilino(self, inquilino: dict) -> None:
        nome = inquilino['nome']

        if "inquilinos" not in self._dados:
            self._dados["inquilinos"] = {}

        self._dados["inquilinos"][nome] = {
            "consumo_anterior": float(inquilino['consumo_anterior']),
            "consumo_atual": float(inquilino['consumo_atual']),
        }

        self._salvar_arquivo(self._dados)


    def remover_inquilino(self, nome: str) -> bool:
        if "inquilinos" in self._dados and nome in self._dados["inquilinos"]:
            del self._dados["inquilinos"][nome]
            self._salvar_arquivo(self._dados)
            return True
        return False

    def salvar_calculo_inquilino(self, nome: str, dados: dict) -> None:
        if "calculos_inquilinos" not in self._dados["inquilinos"][nome]:
            self._dados["inquilinos"][nome]["calculo_inquilino"] = {}

        self._dados["inquilinos"][nome]["calculo_inquilino"] = dados
        self._salvar_arquivo(self._dados)
        print(f"Calculo do inquilino {nome} salvo com sucesso!")

    




if __name__ == "__main__":
    gd = GerenciadorDados()
    print(gd.inquilinos_cadastrados)
    print(gd.quantidade_inquilinos)
    
