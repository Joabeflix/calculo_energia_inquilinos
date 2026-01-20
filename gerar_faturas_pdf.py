import json
from decimal import Decimal
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, white


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def gerar_faturas_pdf(nome_arquivo_json: str, pasta_saida: str = "faturas"):
    caminho_json = os.path.join(BASE_DIR, nome_arquivo_json)
    pasta_saida = os.path.join(BASE_DIR, pasta_saida)

    os.makedirs(pasta_saida, exist_ok=True)

    with open(caminho_json, "r", encoding="utf-8") as f:
        dados = json.load(f)

    for cliente, valores in dados.items():
        _gerar_pdf_cliente(cliente, valores, pasta_saida)


def _gerar_pdf_cliente(cliente: str, v: dict, pasta_saida: str):
    arquivo_pdf = os.path.join(pasta_saida, f"fatura_{cliente}.pdf")

    c = canvas.Canvas(arquivo_pdf, pagesize=A4)
    largura, altura = A4

    cor_principal = HexColor("#1f4fd8")
    cinza = HexColor("#f2f2f2")

    # ===== CABEÇALHO =====
    c.setFillColor(cor_principal)
    c.rect(0, altura - 40 * mm, largura, 40 * mm, fill=1)

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(25 * mm, altura - 25 * mm, "FATURA DE ENERGIA")

    c.setFont("Helvetica", 10)
    c.drawString(25 * mm, altura - 32 * mm, "Resumo mensal de consumo")

    # ===== CLIENTE =====
    y = altura - 55 * mm
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(25 * mm, y, f"Cliente: {cliente.capitalize()}")
    y -= 10 * mm

    c.setFillColor(cinza)
    c.rect(25 * mm, y - 28 * mm, largura - 50 * mm, 28 * mm, fill=1)

    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(30 * mm, y - 8 * mm, "Leitura do Medidor (kWh)")

    c.setFont("Helvetica", 11)
    c.drawString(30 * mm, y - 16 * mm, f"Anterior: {v['registro_kwh_anterior']}")
    c.drawString(30 * mm, y - 23 * mm, f"Atual: {v['registro_kwh_atual']}")

    c.drawRightString(
        largura - 30 * mm,
        y - 20 * mm,
        f"Consumo do mês: {Decimal(v['kwh_consumido_mes']):.2f} kWh"
    )

    y -= 38 * mm

    # ===== DETALHAMENTO POR BANDEIRA =====
    c.setFont("Helvetica-Bold", 11)
    c.drawString(25 * mm, y, "Detalhamento do Consumo por Bandeira")
    y -= 8 * mm

    c.setFillColor(cinza)
    c.rect(25 * mm, y - 40 * mm, largura - 50 * mm, 40 * mm, fill=1)

    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 10)

    # Cabeçalho da tabela
    c.drawString(30 * mm, y - 8 * mm, "Bandeira")
    c.drawRightString(95 * mm, y - 8 * mm, "Consumo (kWh)")
    c.drawRightString(135 * mm, y - 8 * mm, "R$/kWh")
    c.drawRightString(largura - 30 * mm, y - 8 * mm, "Total (R$)")

    y_linha = y - 16 * mm
    c.setFont("Helvetica", 10)

    def linha_bandeira(nome, consumo, valor_kwh, total):
        nonlocal y_linha
        c.drawString(30 * mm, y_linha, nome)
        c.drawRightString(95 * mm, y_linha, f"{Decimal(consumo):.2f}")
        c.drawRightString(135 * mm, y_linha, f"{Decimal(valor_kwh):.4f}")
        c.drawRightString(largura - 30 * mm, y_linha, f"{Decimal(total):.2f}")
        y_linha -= 8 * mm

    linha_bandeira("Verde", v["consumo_kwh_verde"], v["valor_kwh_verde"], v["valor_verde"])
    linha_bandeira("Amarela", v["consumo_kwh_amarelo"], v["valor_kwh_amarelo"], v["valor_amarelo"])
    linha_bandeira("Vermelha", v["consumo_kwh_vermelho"], v["valor_kwh_vermelho"], v["valor_vermelho"])

    # ===== ILUMINAÇÃO + TOTAL =====
    y_final = y_linha - 10 * mm

    c.setFont("Helvetica", 11)
    c.drawString(30 * mm, y_final, "Iluminação Pública")
    c.drawRightString(
        largura - 30 * mm,
        y_final,
        f"R$ {Decimal(v['iluminacao_publica']):.2f}"
    )

    # TOTAL EM DESTAQUE
    c.setFillColor(cor_principal)
    c.rect(
        largura - 110 * mm,
        y_final - 20 * mm,
        85 * mm,
        15 * mm,
        fill=1
    )

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(
        largura - 67 * mm,
        y_final - 14 * mm,
        f"TOTAL A PAGAR: R$ {Decimal(v['total']):.2f}"
    )

    c.showPage()
    c.save()


gerar_faturas_pdf('calculo_final.json')

