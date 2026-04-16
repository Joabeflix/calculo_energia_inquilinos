from v2.gerenciador_de_dados import GerenciadorDados
from v2.calculadora import CalcularEnergia

gd = GerenciadorDados()

gd.preco_base = 1
gd._adicional_amarelo = 0.3
gd._adicional_vermelho = 0.5

gd.total_consumo = 100

gd.consumo_verde = 50
gd.consumo_amarelo = 25
gd.consumo_vermelho = 25
gd.iluminacao_publica = 45.92

gd.cadastrar_atualizar_inquilino({
    "nome": "jojo",
    "consumo_anterior": 50,
    "consumo_atual": 100
})
gd.cadastrar_atualizar_inquilino({
    "nome": "maria",
    "consumo_anterior": 0,
    "consumo_atual": 50
})

calculadora = CalcularEnergia()
calculadora.calcular_energia()

from v2.gerador_pdf import gerar_faturas_pdf
gerar_faturas_pdf()
