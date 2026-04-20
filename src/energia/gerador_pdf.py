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


def _money_per_kwh(value: str | float | Decimal, digits: int = 5) -> str:
    return f"R$ {Decimal(str(value)):.{digits}f}/kWh"


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


def _draw_info_box(
    pdf: canvas.Canvas,
    x: float,
    y_top: float,
    width: float,
    height: float,
    titulo: str,
    linhas: list[str],
    cor_titulo: HexColor,
    cor_fundo: HexColor,
    cor_texto: HexColor,
    font_size: float = 8.4,
) -> None:
    pdf.setFillColor(cor_fundo)
    pdf.roundRect(x, y_top - height, width, height, 4 * mm, fill=1, stroke=0)
    pdf.setFillColor(cor_titulo)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(x + 5 * mm, y_top - 7 * mm, titulo.upper())

    pdf.setFillColor(cor_texto)
    pdf.setFont("Helvetica", font_size)
    y_text = y_top - 13 * mm
    for linha in linhas:
        pdf.drawString(x + 5 * mm, y_text, linha)
        y_text -= 4.7 * mm


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
    pdf.rect(0, altura - 34 * mm, largura, 34 * mm, fill=1, stroke=0)

    pdf.setFillColor(white)
    pdf.setFont("Helvetica-Bold", 17)
    pdf.drawString(margem_x, altura - 17 * mm, "FATURA DE ENERGIA")
    pdf.setFont("Helvetica", 9)
    pdf.drawString(margem_x, altura - 24 * mm, "Resumo individual do rateio de consumo")
    pdf.drawRightString(largura - margem_x, altura - 17 * mm, f"Cliente: {cliente.upper()}")

    y = altura - 44 * mm
    _draw_section_title(pdf, margem_x, y, "Leituras e consumo", azul_principal)
    y -= 4 * mm

    pdf.setFillColor(cinza_fundo)
    pdf.roundRect(margem_x, y - 20 * mm, largura_util, 20 * mm, 4 * mm, fill=1, stroke=0)

    _draw_label_value(
        pdf,
        margem_x + 6 * mm,
        y - 4 * mm,
        "Leitura anterior",
        f"{_number(valores['registro_kwh_anterior'])} kWh",
        cinza_texto,
        cinza_texto_escuro,
    )
    _draw_label_value(
        pdf,
        margem_x + 54 * mm,
        y - 4 * mm,
        "Leitura atual",
        f"{_number(valores['registro_kwh_atual'])} kWh",
        cinza_texto,
        cinza_texto_escuro,
    )
    _draw_label_value(
        pdf,
        margem_x + 102 * mm,
        y - 4 * mm,
        "Consumo no mes",
        f"{_number(valores['kwh_consumido_mes'])} kWh",
        cinza_texto,
        azul_principal,
    )

    y -= 28 * mm
    _draw_section_title(pdf, margem_x, y, "Resumo financeiro", azul_principal)
    y -= 5 * mm

    card_w = (largura_util - 10 * mm) / 2
    _draw_metric_card(
        pdf,
        margem_x,
        y,
        card_w,
        18 * mm,
        "Total gasto",
        _money(total_bandeiras),
        azul_secundario,
        cinza_texto_escuro,
    )
    _draw_metric_card(
        pdf,
        margem_x + card_w + 10 * mm,
        y,
        card_w,
        18 * mm,
        "Total a pagar",
        _money(valores["total"]),
        azul_principal,
        white,
    )

    y -= 25 * mm
    _draw_section_title(pdf, margem_x, y, "Detalhamento por bandeira", azul_principal)
    y -= 5 * mm

    tabela_y = y
    tabela_h = 36 * mm
    pdf.setStrokeColor(cinza_borda)
    pdf.setFillColor(white)
    pdf.roundRect(margem_x, tabela_y - tabela_h, largura_util, tabela_h, 4 * mm, fill=1, stroke=1)

    pdf.setFillColor(cinza_fundo)
    pdf.roundRect(margem_x + 1, tabela_y - 9 * mm, largura_util - 2, 9 * mm, 3 * mm, fill=1, stroke=0)

    col_nome = margem_x + 6 * mm
    col_consumo = margem_x + 86 * mm
    col_tarifa = margem_x + 118 * mm
    col_total = margem_x + largura_util - 6 * mm

    pdf.setFillColor(cinza_texto_escuro)
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(col_nome, tabela_y - 5.8 * mm, "Bandeira")
    pdf.drawRightString(col_consumo, tabela_y - 5.8 * mm, "Consumo (kWh)")
    pdf.drawRightString(col_tarifa, tabela_y - 5.8 * mm, "Tarifa (R$/kWh)")
    pdf.drawRightString(col_total, tabela_y - 5.8 * mm, "Subtotal")

    linhas = [
        ("Verde", valores["consumo_kwh_verde"], valores["valor_kwh_verde"], valores["valor_verde"], verde_suave),
        ("Amarela", valores["consumo_kwh_amarelo"], valores["valor_kwh_amarelo"], valores["valor_amarelo"], amarelo_suave),
        ("Vermelha", valores["consumo_kwh_vermelho"], valores["valor_kwh_vermelho"], valores["valor_vermelho"], vermelho_suave),
    ]

    y_linha = tabela_y - 13 * mm
    for nome, consumo, tarifa, subtotal, cor_linha in linhas:
        pdf.setFillColor(cor_linha)
        pdf.roundRect(margem_x + 3 * mm, y_linha - 4.2 * mm, largura_util - 6 * mm, 6.5 * mm, 2 * mm, fill=1, stroke=0)
        pdf.setFillColor(cinza_texto_escuro)
        pdf.setFont("Helvetica-Bold", 9)
        y_texto_linha = y_linha - 2 * mm
        pdf.drawString(col_nome, y_texto_linha, nome)
        pdf.setFont("Helvetica", 9)
        pdf.drawRightString(col_consumo, y_texto_linha, _number(consumo))
        pdf.drawRightString(col_tarifa, y_texto_linha, _money_per_kwh(tarifa))
        pdf.drawRightString(col_total, y_texto_linha, _money(subtotal))
        y_linha -= 7.5 * mm

    y -= 45 * mm
    _draw_section_title(pdf, margem_x, y, "Composicao do total", azul_principal)
    y -= 4 * mm

    pdf.setFillColor(cinza_fundo)
    pdf.roundRect(margem_x, y - 17 * mm, largura_util, 17 * mm, 4 * mm, fill=1, stroke=0)
    pdf.setFillColor(cinza_texto_escuro)
    pdf.setFont("Helvetica", 9.5)
    pdf.drawString(margem_x + 6 * mm, y - 6 * mm, "Total gasto")
    pdf.drawRightString(margem_x + largura_util - 6 * mm, y - 6 * mm, _money(total_bandeiras))
    pdf.drawString(margem_x + 6 * mm, y - 12 * mm, "Iluminacao publica")
    pdf.drawRightString(margem_x + largura_util - 6 * mm, y - 12 * mm, _money(valores["iluminacao_publica"]))

    y -= 22 * mm
    pdf.setFillColor(azul_principal)
    pdf.roundRect(margem_x, y - 12 * mm, largura_util, 12 * mm, 4 * mm, fill=1, stroke=0)
    pdf.setFillColor(white)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(margem_x + 6 * mm, y - 7.3 * mm, "TOTAL A PAGAR")
    pdf.drawRightString(margem_x + largura_util - 6 * mm, y - 7.3 * mm, _money(valores["total"]))

    explicacao_bandeiras = [
        "No Brasil, a bandeira tarifaria indica o custo de geracao de energia no periodo.",
        "Bandeira verde: condicoes mais favoraveis, sem acrescimo extra relevante na tarifa.",
        "Bandeira amarela: custo de geracao maior, com aumento no valor cobrado por kWh.",
        "Bandeira vermelha: custo ainda mais alto, com acrescimo maior no valor por kWh.",
        "Por isso, nesta fatura o valor do kWh muda conforme a composicao da conta principal.",
    ]

    explicacao = [
        f"1. Consumo individual: {_number(valores['registro_kwh_atual'])} - {_number(valores['registro_kwh_anterior'])} = {_number(valores['kwh_consumido_mes'])} kWh.",
        "2. O consumo do morador e distribuido proporcionalmente entre as bandeiras verde, amarela e vermelha.",
        f"3. Total gasto: {_money(valores['valor_verde'])} + {_money(valores['valor_amarelo'])} + {_money(valores['valor_vermelho'])} = {_money(total_bandeiras)}.",
        f"4. Rateio final: {_money(total_bandeiras)} + {_money(valores['iluminacao_publica'])} = {_money(valores['total'])}.",
    ]

    y -= 18 * mm
    altura_box_memoria = 28 * mm
    altura_box_bandeiras = 33 * mm

    _draw_info_box(
        pdf,
        margem_x,
        y,
        largura_util,
        altura_box_memoria,
        "Memoria de calculo",
        explicacao,
        azul_principal,
        cinza_fundo,
        cinza_texto,
        font_size=8.4,
    )

    y -= altura_box_memoria + 6 * mm

    _draw_info_box(
        pdf,
        margem_x,
        y,
        largura_util,
        altura_box_bandeiras,
        "Entenda as bandeiras tarifarias",
        explicacao_bandeiras,
        azul_principal,
        azul_secundario,
        cinza_texto,
        font_size=8.3,
    )

    pdf.setStrokeColor(cinza_borda)
    pdf.line(margem_x, 18 * mm, largura - margem_x, 18 * mm)
    pdf.setFillColor(cinza_texto)
    pdf.setFont("Helvetica", 8)
    pdf.drawString(margem_x, 14 * mm, "Documento gerado automaticamente pelo sistema de rateio de energia.")
    pdf.drawRightString(largura - margem_x, 14 * mm, f"Arquivo: {arquivo_pdf.name}")

    pdf.showPage()
    pdf.save()
    return arquivo_pdf
