from decimal import Decimal
from pathlib import Path

from reportlab.lib.colors import HexColor, black, white  # type: ignore
from reportlab.lib.pagesizes import A4  # type: ignore
from reportlab.lib.units import mm  # type: ignore
from reportlab.pdfgen import canvas  # type: ignore

from energia.exceptions import ValidationError
from energia.gerenciador_de_dados import GerenciadorDados
from energia.paths import FATURAS_DIR


def gerar_faturas_pdf(gerenciador: GerenciadorDados | None = None, pasta_saida: str | Path | None = None) -> list[Path]:
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


def _gerar_pdf_cliente(cliente: str, valores: dict, pasta_saida: Path) -> Path:
    arquivo_pdf = pasta_saida / f"fatura_{cliente}.pdf"

    pdf = canvas.Canvas(str(arquivo_pdf), pagesize=A4)
    largura, altura = A4

    cor_principal = HexColor("#1f4fd8")
    cinza_claro = HexColor("#f2f2f2")
    cinza_escuro = HexColor("#555555")

    pdf.setFillColor(cor_principal)
    pdf.rect(0, altura - 40 * mm, largura, 40 * mm, fill=1)

    pdf.setFillColor(white)
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(25 * mm, altura - 25 * mm, "FATURA DE ENERGIA")

    pdf.setFont("Helvetica", 10)
    pdf.drawString(25 * mm, altura - 32 * mm, "Resumo mensal de consumo")

    y = altura - 55 * mm
    pdf.setFillColor(black)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(25 * mm, y, f"Cliente: {cliente.capitalize()}")
    y -= 10 * mm

    pdf.setFillColor(cinza_claro)
    pdf.rect(25 * mm, y - 28 * mm, largura - 50 * mm, 28 * mm, fill=1)

    pdf.setFillColor(black)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(30 * mm, y - 8 * mm, "Leitura do Medidor (kWh)")

    pdf.setFont("Helvetica", 11)
    pdf.drawString(30 * mm, y - 16 * mm, f"Anterior: {valores['registro_kwh_anterior']}")
    pdf.drawString(30 * mm, y - 23 * mm, f"Atual: {valores['registro_kwh_atual']}")
    pdf.drawRightString(
        largura - 30 * mm,
        y - 20 * mm,
        f"Consumo do mes: {Decimal(valores['kwh_consumido_mes']):.2f} kWh",
    )

    y -= 38 * mm

    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(25 * mm, y, "Detalhamento do Consumo por Bandeira")
    y -= 8 * mm

    pdf.setFillColor(cinza_claro)
    pdf.rect(25 * mm, y - 40 * mm, largura - 50 * mm, 40 * mm, fill=1)

    pdf.setFillColor(black)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(30 * mm, y - 8 * mm, "Bandeira")
    pdf.drawRightString(95 * mm, y - 8 * mm, "Consumo (kWh)")
    pdf.drawRightString(135 * mm, y - 8 * mm, "R$/kWh")
    pdf.drawRightString(largura - 30 * mm, y - 8 * mm, "Total (R$)")

    y_linha = y - 16 * mm
    pdf.setFont("Helvetica", 10)

    def linha_bandeira(nome: str, consumo: str, valor_kwh: str, total: str) -> None:
        nonlocal y_linha
        pdf.drawString(30 * mm, y_linha, nome)
        pdf.drawRightString(95 * mm, y_linha, f"{Decimal(consumo):.2f}")
        pdf.drawRightString(135 * mm, y_linha, f"{Decimal(valor_kwh):.4f}")
        pdf.drawRightString(largura - 30 * mm, y_linha, f"{Decimal(total):.2f}")
        y_linha -= 8 * mm

    linha_bandeira("Verde", valores["consumo_kwh_verde"], valores["valor_kwh_verde"], valores["valor_verde"])
    linha_bandeira("Amarela", valores["consumo_kwh_amarelo"], valores["valor_kwh_amarelo"], valores["valor_amarelo"])
    linha_bandeira("Vermelha", valores["consumo_kwh_vermelho"], valores["valor_kwh_vermelho"], valores["valor_vermelho"])

    y_final = y_linha - 10 * mm

    pdf.setFont("Helvetica", 11)
    pdf.drawString(30 * mm, y_final, "Iluminacao Publica")
    pdf.drawRightString(largura - 30 * mm, y_final, f"R$ {Decimal(valores['iluminacao_publica']):.2f}")

    pdf.setFillColor(cor_principal)
    pdf.rect(largura - 110 * mm, y_final - 20 * mm, 85 * mm, 15 * mm, fill=1)

    pdf.setFillColor(white)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawCentredString(
        largura - 67 * mm,
        y_final - 14 * mm,
        f"TOTAL A PAGAR: R$ {Decimal(valores['total']):.2f}",
    )

    y_explica = y_final - 40 * mm
    pdf.setStrokeColor(cor_principal)
    pdf.setLineWidth(0.5)
    pdf.line(25 * mm, y_explica + 5 * mm, largura - 25 * mm, y_explica + 5 * mm)

    pdf.setFillColor(cor_principal)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(25 * mm, y_explica, "ENTENDA SEU CALCULO:")

    pdf.setFillColor(cinza_escuro)
    pdf.setFont("Helvetica", 9)
    y_text = y_explica - 6 * mm

    linhas_explicacao = [
        f"1. Consumo: Leitura Atual ({valores['registro_kwh_atual']}) - Leitura Anterior ({valores['registro_kwh_anterior']}) = {valores['kwh_consumido_mes']} kWh.",
        "2. Bandeiras: O consumo e rateado proporcionalmente conforme a fatura da concessionaria.",
        f"   - Verde: {valores['consumo_kwh_verde']} kWh x R$ {valores['valor_kwh_verde']}",
        f"   - Amarela: {valores['consumo_kwh_amarelo']} kWh x R$ {valores['valor_kwh_amarelo']}",
        f"   - Vermelha: {valores['consumo_kwh_vermelho']} kWh x R$ {valores['valor_kwh_vermelho']}",
        "3. Iluminacao Publica: Valor total rateado igualmente entre os moradores.",
        f"Formula Final: (Soma das Bandeiras) + Iluminacao Publica = R$ {valores['total']}.",
    ]

    for linha in linhas_explicacao:
        pdf.drawString(25 * mm, y_text, linha)
        y_text -= 5 * mm

    pdf.showPage()
    pdf.save()
    return arquivo_pdf
