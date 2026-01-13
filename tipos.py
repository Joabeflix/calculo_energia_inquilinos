from typing import TypedDict

class TipoValKwr(TypedDict):
    preco_base: float
    adicional_amarelo: float
    adicional_vermelho: float

class TipoConsumo(TypedDict):
    total_consumo: float
    consumo_verde: float
    consumo_amarelo: float
    consumo_vermelho: float
    ilumicacao_publica: float
class TipoInquilino(TypedDict):
    nome: str
    consumo_anterior: float
    consumo_atual: float
