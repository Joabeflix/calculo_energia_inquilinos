from decimal import Decimal
from pathlib import Path

from reportlab.lib.colors import HexColor, black, white  # type: ignore
from reportlab.lib.pagesizes import A4  # type: ignore
from reportlab.lib.units import mm  # type: ignore
from reportlab.pdfgen import canvas  # type: ignore

from energia.exceptions import ValidationError
from energia.gerenciador_de_dados import GerenciadorDados
from energia.paths import FATURAS_DIR


def gerar_faturas_pdf(
    gerenciador: GerenciadorDados | None = None,
    pasta_saida: str | Path | None = None,
) -> list[Path]:
    dados = gerenciador or GerenciadorDados()
    dados.recarregar()

    destino = Path(pasta_saida) if pasta_saida else FATURAS_DIR
    destino.mkdir(parents=True, exist_ok=True)

    arquivos_gerados: list[Path] = []
    for cliente, valores in dados.dados_inquilinos.items():
        calculo = valores.get("calculo_inquilino")
        if not calculo:
            raise ValidationError(
                f"O inquilino '{cliente}' nao possui calculo gerado. Execute o calculo antes de emitir a fatura."
            )
        arquivos_gerados.append(_gerar_pdf_cliente(cliente, calculo, destino))

    return arquivos_gerados


def _money(value: str | float | Decimal) -> str:
    return f"R$ {Decimal(str(value)):.2f}"


def _number(value: str | float | Decimal, digits: int = 2) -> str:
    return f"{Decimal(str(value)):.{digits}f}"


def _draw_section_title(pdf: canvas.Canvas, x: float, y: float, titulo: str, cor: HexColor) -> None:
    pdf.setFillColor(cor)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(x, y, titulo.upper())


def _draw_label_value(
    pdf: canvas.Canvas,
    x: float,
    y: float,
    label: str,
    value: str,
    label_color: HexColor,
    value_color: HexColor = black,
) -> None:
    pdf.setFillColor(label_color)
    pdf.setFont("Helvetica", 9)
    pdf.drawString(x, y, label)
    pdf.setFillColor(value_color)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(x, y - 5 * mm, value)


def _draw_metric_card(
    pdf: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    h: float,
    titulo: str,
    valor: str,
    cor_fundo: HexColor,
    cor_texto: HexColor,
) -> None:
    pdf.setFillColor(cor_fundo)
    pdf.roundRect(x, y - h, w, h, 4 * mm, fill=1, stroke=0)
    pdf.setFillColor(cor_texto)
    pdf.setFont("Helvetica", 9)
    pdf.drawString(x + 4 * mm, y - 7 * mm, titulo)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(x + 4 * mm, y - 15 * mm, valor)


def _gerar_pdf_cliente(cliente: str, valores: dict, pasta_saida: Path) -> Path:
    arquivo_pdf = pasta_saida / f"fatura_{cliente}.pdf"

    pdf = canvas.Canvas(str(arquivo_pdf), pagesize=A4)
    largura, altura = A4

    margem_x = 18 * mm
    largura_util = largura - (2 * margem_x)

    azul_principal = HexColor("#2F5FD0")
    azul_secundario = HexColor("#EAF1FF")
    cinza_fundo = HexColor("#F5F7FA")
    cinza_borda = HexColor("#D9E2EC")
    cinza_texto = HexColor("#52606D")
    cinza_texto_escuro = HexColor("#243B53")
    verde_suave = HexColor("#E8F8F1")
    amarelo_suave = HexColor("#FFF6DE")
    vermelho_suave = HexColor("#FDECEC")

    total_bandeiras = (
        Decimal(valores["valor_verde"])
        + Decimal(valores["valor_amarelo"])
        + Decimal(valores["valor_vermelho"])
    )

    pdf.setFillColor(azul_principal)
    pdf.rect(0, altura - 44 * mm, largura, 44 * mm, fill=1, stroke=0)

    pdf.setFillColor(white)
    pdf.setFont("Helvetica-Bold", 19)
    pdf.drawString(margem_x, altura - 21 * mm, "FATURA DE ENERGIA")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(margem_x, altura - 29 * mm, "Resumo individual do rateio de consumo")
    pdf.drawRightString(largura - margem_x, altura - 21 * mm, f"Cliente: {cliente.upper()}")

    y = altura - 58 * mm
    _draw_section_title(pdf, margem_x, y, "Leituras e consumo", azul_principal)
    y -= 5 * mm

    pdf.setFillColor(cinza_fundo)
    pdf.roundRect(margem_x, y - 24 * mm, largura_util, 24 * mm, 4 * mm, fill=1, stroke=0)

    _draw_label_value(
        pdf,
        margem_x + 6 * mm,
        y - 5 * mm,
        "Leitura anterior",
        f"{_number(valores['registro_kwh_anterior'])} kWh",
        cinza_texto,
        cinza_texto_escuro,
    )
    _draw_label_value(
        pdf,
        margem_x + 54 * mm,
        y - 5 * mm,
        "Leitura atual",
        f"{_number(valores['registro_kwh_atual'])} kWh",
        cinza_texto,
        cinza_texto_escuro,
    )
    _draw_label_value(
        pdf,
        margem_x + 102 * mm,
        y - 5 * mm,
        "Consumo no mes",
        f"{_number(valores['kwh_consumido_mes'])} kWh",
        cinza_texto,
        azul_principal,
    )

    y -= 34 * mm
    _draw_section_title(pdf, margem_x, y, "Resumo financeiro", azul_principal)
    y -= 6 * mm

    card_w = (largura_util - 10 * mm) / 2
    _draw_metric_card(
        pdf,
        margem_x,
        y,
        card_w,
        20 * mm,
        "Total das bandeiras",
        _money(total_bandeiras),
        azul_secundario,
        cinza_texto_escuro,
    )
    _draw_metric_card(
        pdf,
        margem_x + card_w + 10 * mm,
        y,
        card_w,
        20 * mm,
        "Total a pagar",
        _money(valores["total"]),
        azul_principal,
        white,
    )

    y -= 30 * mm
    _draw_section_title(pdf, margem_x, y, "Detalhamento por bandeira", azul_principal)
    y -= 6 * mm

    tabela_y = y
    tabela_h = 42 * mm
    pdf.setStrokeColor(cinza_borda)
    pdf.setFillColor(white)
    pdf.roundRect(margem_x, tabela_y - tabela_h, largura_util, tabela_h, 4 * mm, fill=1, stroke=1)

    pdf.setFillColor(cinza_fundo)
    pdf.roundRect(margem_x + 1, tabela_y - 10 * mm, largura_util - 2, 10 * mm, 3 * mm, fill=1, stroke=0)

    col_nome = margem_x + 6 * mm
    col_consumo = margem_x + 86 * mm
    col_tarifa = margem_x + 118 * mm
    col_total = margem_x + largura_util - 6 * mm

    pdf.setFillColor(cinza_texto_escuro)
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(col_nome, tabela_y - 6.5 * mm, "Bandeira")
    pdf.drawRightString(col_consumo, tabela_y - 6.5 * mm, "Consumo (kWh)")
    pdf.drawRightString(col_tarifa, tabela_y - 6.5 * mm, "Tarifa")
    pdf.drawRightString(col_total, tabela_y - 6.5 * mm, "Subtotal")

    linhas = [
        ("Verde", valores["consumo_kwh_verde"], valores["valor_kwh_verde"], valores["valor_verde"], verde_suave),
        ("Amarela", valores["consumo_kwh_amarelo"], valores["valor_kwh_amarelo"], valores["valor_amarelo"], amarelo_suave),
        ("Vermelha", valores["consumo_kwh_vermelho"], valores["valor_kwh_vermelho"], valores["valor_vermelho"], vermelho_suave),
    ]

    y_linha = tabela_y - 15 * mm
    for nome, consumo, tarifa, subtotal, cor_linha in linhas:
        pdf.setFillColor(cor_linha)
        pdf.roundRect(margem_x + 3 * mm, y_linha - 4.5 * mm, largura_util - 6 * mm, 7 * mm, 2 * mm, fill=1, stroke=0)
        pdf.setFillColor(cinza_texto_escuro)
        pdf.setFont("Helvetica-Bold", 9)
        pdf.drawString(col_nome, y_linha, nome)
        pdf.setFont("Helvetica", 9)
        pdf.drawRightString(col_consumo, y_linha, _number(consumo))
        pdf.drawRightString(col_tarifa, y_linha, _money(tarifa))
        pdf.drawRightString(col_total, y_linha, _money(subtotal))
        y_linha -= 9 * mm

    y -= 54 * mm
    _draw_section_title(pdf, margem_x, y, "Composicao do total", azul_principal)
    y -= 5 * mm

    pdf.setFillColor(cinza_fundo)
    pdf.roundRect(margem_x, y - 20 * mm, largura_util, 20 * mm, 4 * mm, fill=1, stroke=0)
    pdf.setFillColor(cinza_texto_escuro)
    pdf.setFont("Helvetica", 10)
    pdf.drawString(margem_x + 6 * mm, y - 7 * mm, "Soma das bandeiras")
    pdf.drawRightString(margem_x + largura_util - 6 * mm, y - 7 * mm, _money(total_bandeiras))
    pdf.drawString(margem_x + 6 * mm, y - 14 * mm, "Iluminacao publica")
    pdf.drawRightString(margem_x + largura_util - 6 * mm, y - 14 * mm, _money(valores["iluminacao_publica"]))

    y -= 28 * mm
    pdf.setFillColor(azul_principal)
    pdf.roundRect(margem_x, y - 14 * mm, largura_util, 14 * mm, 4 * mm, fill=1, stroke=0)
    pdf.setFillColor(white)
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(margem_x + 6 * mm, y - 8.5 * mm, "TOTAL A PAGAR")
    pdf.drawRightString(margem_x + largura_util - 6 * mm, y - 8.5 * mm, _money(valores["total"]))

    y -= 24 * mm
    _draw_section_title(pdf, margem_x, y, "Memoria de calculo", azul_principal)
    y -= 5 * mm

    explicacao = [
        f"1. Consumo individual: {_number(valores['registro_kwh_atual'])} - {_number(valores['registro_kwh_anterior'])} = {_number(valores['kwh_consumido_mes'])} kWh.",
        "2. O consumo do morador e distribuido proporcionalmente entre as bandeiras verde, amarela e vermelha.",
        f"3. Total das bandeiras: {_money(valores['valor_verde'])} + {_money(valores['valor_amarelo'])} + {_money(valores['valor_vermelho'])} = {_money(total_bandeiras)}.",
        f"4. Rateio final: {_money(total_bandeiras)} + {_money(valores['iluminacao_publica'])} = {_money(valores['total'])}.",
    ]

    pdf.setFillColor(cinza_texto)
    pdf.setFont("Helvetica", 9)
    y_texto = y - 2 * mm
    for linha in explicacao:
        pdf.drawString(margem_x, y_texto, linha)
        y_texto -= 5.5 * mm

    pdf.setStrokeColor(cinza_borda)
    pdf.line(margem_x, 18 * mm, largura - margem_x, 18 * mm)
    pdf.setFillColor(cinza_texto)
    pdf.setFont("Helvetica", 8)
    pdf.drawString(margem_x, 14 * mm, "Documento gerado automaticamente pelo sistema de rateio de energia.")
    pdf.drawRightString(largura - margem_x, 14 * mm, f"Arquivo: {arquivo_pdf.name}")

    pdf.showPage()
    pdf.save()
    return arquivo_pdf
