import json
import os

def get_data_path(filename: str) -> str:
    """
    Retorna o caminho absoluto para o arquivo dentro da pasta 'dados'
    localizada no mesmo diretório deste script.
    """
    # Pega a pasta onde este arquivo (class_dados.py) está salvo
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define o caminho da pasta 'dados'
    data_dir = os.path.join(base_dir, 'dados')
    
    # Cria a pasta 'dados' se ela não existir
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
        
    return os.path.join(data_dir, filename)

def garantir_json_base(path: str, default_content: dict):
    """Cria um arquivo JSON com conteúdo padrão se ele não existir."""
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default_content, f, indent=4, ensure_ascii=False)

class ValoresKwh:
    def __init__(self) -> None:
        self.path = get_data_path('valoreskwr.json')
        garantir_json_base(self.path, {
            "preco_base": 0.0, 
            "adicional_amarelo": 0.0, 
            "adicional_vermelho": 0.0
        })
        self.dados_valores = self.carregar_dados()

    def carregar_dados(self):
        with open(self.path, "r", encoding="utf-8") as file:
            return json.load(file)

    @property
    def preco_base(self) -> float: return float(self.dados_valores.get('preco_base', 0))
    
    @property
    def adicional_amarelo(self) -> float: return float(self.dados_valores.get('adicional_amarelo', 0))
    
    @property
    def adicional_vermelho(self) -> float: return float(self.dados_valores.get('adicional_vermelho', 0))

    @property
    def verde(self) -> float: return self.preco_base

    @property
    def amarelo(self) -> float: return self.preco_base + self.adicional_amarelo

    @property
    def vermelho(self) -> float: return self.preco_base + self.adicional_vermelho

    def definir_valores(self, tipo: str, valor: float) -> None:
        dados = self.carregar_dados()
        dados[tipo] = valor
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
        self.dados_valores = dados

class Consumo:
    def __init__(self) -> None:
        self.path = get_data_path('consumo.json')
        garantir_json_base(self.path, {
            "total_consumo": 0.0, 
            "consumo_verde": 0.0, 
            "consumo_amarelo": 0.0, 
            "consumo_vermelho": 0.0, 
            "ilumicacao_publica": 0.0
        })
        self.dados_consumo = self.carregar_dados()

    def carregar_dados(self):
        with open(self.path, "r", encoding="utf-8") as file:
            return json.load(file)

    @property
    def total_consumo(self) -> float: return float(self.dados_consumo.get('total_consumo', 0))
    
    @property
    def consumo_verde(self) -> float: return float(self.dados_consumo.get('consumo_verde', 0))
        
    @property
    def consumo_amarelo(self) -> float: return float(self.dados_consumo.get('consumo_amarelo', 0))

    @property
    def consumo_vermelho(self) -> float: return float(self.dados_consumo.get('consumo_vermelho', 0))        
        
    @property
    def iluminacao_publica(self) -> float: return float(self.dados_consumo.get("ilumicacao_publica", 0))

    def definir_valores(self, tipo: str, valor: float) -> None:
        dados = self.carregar_dados()
        dados[tipo] = valor
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
        self.dados_consumo = dados

class Inquilinos:
    def __init__(self) -> None:
        self.path = get_data_path('inquilinos.json')
        garantir_json_base(self.path, {})
        self.dados = self.carregar_dados()

    def carregar_dados(self) -> dict:
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    @property
    def dados_inquilinos(self) -> dict: return self.dados

    @property
    def inquilinos_cadastrados(self) -> list: return list(self.dados.keys())

    @property
    def quantidade_inquilinos(self) -> int: return len(self.dados)

    def cadastrar_atualizar_inquilino(self, inquilino: dict) -> None:
        dados_atuais = self.carregar_dados()
        nome = inquilino['nome']
        dados_atuais[nome] = {
            "consumo_anterior": float(inquilino['consumo_anterior']),
            "consumo_atual": float(inquilino['consumo_atual'])
        }
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(dados_atuais, f, indent=4, ensure_ascii=False)
        self.dados = dados_atuais

    def remover_inquilino(self, nome: str) -> bool:
        dados = self.carregar_dados()
        if nome in dados:
            del dados[nome]
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
            self.dados = dados
            return True
        return False
