from typing import TypedDict

class TipoValKwr(TypedDict):
    preco_base: float
    adicional_amarelo: float
    adicional_vermelho: float

class TipoConsumo(TypedDict):
    total_consumido: int
    consumido_verde: int
    consumido_amarelo: int
    consumido_vermelho: int

class TipoInquilino(TypedDict):
    nome: str
    consumo_anterior: int
    consumo_atual: int
