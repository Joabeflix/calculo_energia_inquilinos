import os
import json
from decimal import Decimal
from typing import TypedDict

from reportlab.lib.units import mm   # type: ignore
from reportlab.pdfgen import canvas # type: ignore
from reportlab.lib.pagesizes import A4 # type: ignore
from reportlab.lib.colors import HexColor, black, white # type: ignore

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.config import Config
from kivy.factory import Factory
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import MDSnackbar
from kivy.uix.screenmanager import Screen

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



class CalcularEnergia():
    def __init__(self) -> None:
        # Inicializamos os caminhos e porcentagens base
        self.atualizar_bases()

    def atualizar_bases(self):
        consumo_global = Consumo()
        self.consumo_total = consumo_global.total_consumo
        self.consumo_verde = consumo_global.consumo_verde
        self.consumo_amarelo = consumo_global.consumo_amarelo
        self.consumo_vermelho = consumo_global.consumo_vermelho
        self.iluminacao_total = consumo_global.iluminacao_publica

        self.porcentagem_verde = 0.0
        self.porcentagem_amarela = 0.0
        self.porcentagem_vermelha = 0.0

        if self.consumo_total > 0:
            self.porcentagem_verde = self.consumo_verde / self.consumo_total
            self.porcentagem_amarela = self.consumo_amarelo / self.consumo_total
            self.porcentagem_vermelha = self.consumo_vermelho / self.consumo_total

    def calcular_energia(self):
        # Sempre atualiza as bases antes de calcular para pegar mudanças recentes
        self.atualizar_bases()
        
        inquilinos_db = Inquilinos()
        valores_kwh = ValoresKwh()
        
        qtd = inquilinos_db.quantidade_inquilinos
        iluminacao_por_inq = self.iluminacao_total / qtd if qtd > 0 else 0

        resultado_final = {}

        for inq, dados in inquilinos_db.dados.items():
            consumo = dados["consumo_atual"] - dados["consumo_anterior"]
            
            c_verde = consumo * self.porcentagem_verde
            c_amarelo = consumo * self.porcentagem_amarela
            c_vermelho = consumo * self.porcentagem_vermelha
            
            # Cálculo financeiro
            v_verde = c_verde * valores_kwh.verde
            v_amarelo = c_amarelo * valores_kwh.amarelo
            v_vermelho = c_vermelho * valores_kwh.vermelho

            total = iluminacao_por_inq + v_verde + v_amarelo + v_vermelho

            # Estrutura preparada para exibição e geração de PDF
            resultado_final[inq] = {
                "registro_kwh_anterior": dados["consumo_anterior"],
                "registro_kwh_atual": dados["consumo_atual"],
                "kwh_consumido_mes": f'{consumo:.2f}',
                "valor_kwh_verde": f'{valores_kwh.verde:.4f}',
                "valor_kwh_amarelo": f'{valores_kwh.amarelo:.4f}',
                "valor_kwh_vermelho": f'{valores_kwh.vermelho:.4f}',
                "consumo_kwh_verde": f'{c_verde:.2f}',
                "consumo_kwh_amarelo": f'{c_amarelo:.2f}',
                "consumo_kwh_vermelho": f'{c_vermelho:.2f}',
                "valor_verde": f"{v_verde:.2f}",
                "valor_amarelo": f"{v_amarelo:.2f}",
                "valor_vermelho": f"{v_vermelho:.2f}",
                "iluminacao_publica": f"{iluminacao_por_inq:.2f}",
                "total": f"{total:.2f}"
            }
            
        # Salva o resultado final na pasta /dados/
        path_final = get_data_path('calculo_final.json')
        with open(path_final, "w", encoding="utf-8") as f:
            json.dump(resultado_final, f, indent=4, ensure_ascii=False)
            
        return resultado_final





# Configurações de Janela
Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '750')
Config.set('graphics', 'resizable', '1')

def safe_float(value):
    """Converte para float com suporte a alta precisão e troca de vírgula por ponto."""
    try:
        clean_val = str(value).strip().replace(',', '.')
        return float(clean_val) if clean_val else 0.0
    except ValueError:
        return 0.0

MAPA_DINAMICO = {
    "total_consumo": {"file": "consumo.json", "key": "total_consumo"},
    "consumo_verde": {"file": "consumo.json", "key": "consumo_verde"},
    "consumo_amarelo": {"file": "consumo.json", "key": "consumo_amarelo"},
    "consumo_vermelho": {"file": "consumo.json", "key": "consumo_vermelho"},
    "ilumicacao_publica": {"file": "consumo.json", "key": "ilumicacao_publica"},
    "preco_base": {"file": "valoreskwr.json", "key": "preco_base"},
    "adicional_amarelo": {"file": "valoreskwr.json", "key": "adicional_amarelo"},
    "adicional_vermelho": {"file": "valoreskwr.json", "key": "adicional_vermelho"},
}

KV = '''
ScreenManager:
    MainScreen:
    ConfigScreen:
    InquilinosScreen:

<ItemInquilino@MDCard>:
    orientation: "vertical"
    size_hint_y: None
    height: "180dp"
    padding: "20dp"
    spacing: "15dp"
    elevation: 3
    radius: [20, ]
    md_bg_color: 0.15, 0.15, 0.2, 1 

    MDBoxLayout:
        adaptive_height: True
        spacing: "15dp"
        MDTextField:
            id: txt_nome
            hint_text: "Nome do Inquilino"
            icon_left: "account"
            mode: "line"
        MDIconButton:
            icon: "close-circle-outline"
            theme_text_color: "Error"
            pos_hint: {"center_y": .5}
            on_release: app.root.get_screen('inquilinos').ids.lista_inquilinos.remove_widget(root)

    MDGridLayout:
        cols: 2
        spacing: "25dp"
        adaptive_height: True
        MDTextField:
            id: txt_anterior
            hint_text: "Leitura Anterior (kWh)"
            input_filter: "float"
            icon_left: "history"
        MDTextField:
            id: txt_atual
            hint_text: "Leitura Atual (kWh)"
            input_filter: "float"
            icon_left: "flash"

<MainScreen>:
    name: 'main'
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 0.1, 0.1, 0.12, 1
        
        MDTopAppBar:
            title: "Energy Master v2.0"
            elevation: 4
            md_bg_color: 0.2, 0.2, 0.3, 1

        MDAnchorLayout:
            MDCard:
                orientation: 'vertical'
                size_hint: None, None
                size: "400dp", "480dp"
                padding: "30dp"
                spacing: "20dp"
                radius: [25, ]
                elevation: 4
                md_bg_color: 0.15, 0.15, 0.2, 1

                MDIcon:
                    icon: "lightning-bolt-circle"
                    halign: "center"
                    font_size: "80sp"
                    theme_text_color: "Custom"
                    text_color: app.theme_cls.primary_color

                MDLabel:
                    text: "Gestão Residencial"
                    halign: "center"
                    font_style: "H5"
                    bold: True
                    theme_text_color: "Primary"

                MDFillRoundFlatIconButton:
                    text: "Configurar Tarifas"
                    icon: "tune"
                    size_hint_x: 1
                    on_release: root.manager.current = 'config'

                MDFillRoundFlatIconButton:
                    text: "Gerenciar Inquilinos"
                    icon: "account-group"
                    size_hint_x: 1
                    on_release: root.manager.current = 'inquilinos'

                MDRectangleFlatIconButton:
                    text: "Gerar Relatórios e PDF"
                    icon: "file-pdf-box"
                    size_hint_x: 1
                    text_color: 1, 1, 1, 1
                    line_color: app.theme_cls.primary_color
                    on_release: root.executar_calculo_geral()

<ConfigScreen>:
    name: 'config'
    on_enter: root.carregar_dados() 
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 0.1, 0.1, 0.12, 1
        
        MDTopAppBar:
            title: "Configurações"
            left_action_items: [["arrow-left", lambda x: setattr(root.manager, 'current', 'main')]]

        ScrollView:
            MDBoxLayout:
                orientation: 'vertical'
                padding: "30dp"
                spacing: "20dp"
                adaptive_height: True
                size_hint_x: None
                width: "600dp"
                pos_hint: {"center_x": .5}

                # --- CALCULADORA ---
                MDCard:
                    orientation: 'vertical'
                    adaptive_height: True
                    padding: "15dp"
                    spacing: "10dp"
                    radius: [15, ]
                    md_bg_color: 0.2, 0.2, 0.25, 1
                    
                    MDLabel:
                        text: "Cálculo do Preço Base (Até 9 casas)"
                        font_style: "Caption"
                        theme_text_color: "Secondary"
                    
                    MDBoxLayout:
                        spacing: "15dp"
                        adaptive_height: True
                        MDTextField:
                            id: calc_val1
                            hint_text: "Valor 1"
                            on_text: root.somar_auxiliar()
                        MDLabel:
                            text: "+"
                            adaptive_size: True
                            pos_hint: {"center_y": .5}
                        MDTextField:
                            id: calc_val2
                            hint_text: "Valor 2"
                            on_text: root.somar_auxiliar()
                        MDLabel:
                            id: lbl_calc_result
                            text: "0.000000000"
                            bold: True
                            theme_text_color: "Primary"

                MDLabel:
                    text: "Consumo por Bandeira (kWh)"
                    font_style: "Subtitle1"

                MDGridLayout:
                    cols: 2
                    spacing: "15dp"
                    adaptive_height: True
                    MDTextField:
                        id: total_consumo
                        hint_text: "Consumo Total Fatura"
                        input_filter: "float"
                        mode: "rectangle"
                    MDTextField:
                        id: ilumicacao_publica
                        hint_text: "Ilum. Pública (R$)"
                        input_filter: "float"
                        mode: "rectangle"
                    MDTextField:
                        id: consumo_verde
                        hint_text: "kWh na Verde"
                        input_filter: "float"
                        mode: "rectangle"
                    MDTextField:
                        id: consumo_amarelo
                        hint_text: "kWh na Amarela"
                        input_filter: "float"
                        mode: "rectangle"
                    MDTextField:
                        id: consumo_vermelho
                        hint_text: "kWh na Vermelha"
                        input_filter: "float"
                        mode: "rectangle"

                MDSeparator:

                MDLabel:
                    text: "Preços das Tarifas"
                    font_style: "Subtitle1"

                MDGridLayout:
                    cols: 3
                    spacing: "10dp"
                    adaptive_height: True
                    MDTextField:
                        id: preco_base
                        hint_text: "Preço kWh"
                        icon_left: "currency-usd"
                    MDTextField:
                        id: adicional_amarelo
                        hint_text: "Add. Amarela"
                    MDTextField:
                        id: adicional_vermelho
                        hint_text: "Add. Vermelha"

                MDFillRoundFlatButton:
                    text: "SALVAR CONFIGURAÇÕES"
                    size_hint_x: 1
                    on_release: root.salvar_dados()

<InquilinosScreen>:
    name: 'inquilinos'
    on_enter: root.carregar_dados()
    on_leave: lista_inquilinos.clear_widgets()
    
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 0.1, 0.1, 0.12, 1
        
        MDTopAppBar:
            title: "Moradores"
            left_action_items: [["arrow-left", lambda x: setattr(root.manager, 'current', 'main')]]
            right_action_items: [["plus-circle", lambda x: root.adicionar_card_vazio()]]

        ScrollView:
            MDBoxLayout:
                id: lista_inquilinos
                orientation: 'vertical'
                padding: "20dp"
                spacing: "20dp"
                adaptive_height: True
                size_hint_x: None
                width: "500dp"
                pos_hint: {"center_x": .5}

        MDBoxLayout:
            adaptive_height: True
            padding: "20dp"
            MDFillRoundFlatIconButton:
                text: "SALVAR LISTA"
                icon: "content-save-check"
                size_hint_x: 1
                on_release: root.salvar_dados()
'''

class MainScreen(Screen):
    def executar_calculo_geral(self):
        try:
            calculo = CalcularEnergia()
            calculo.calcular_energia()
            caminho_json = get_data_path('calculo_final.json')
            gerar_faturas_pdf(caminho_json)
            mostrar_snackbar("Processado com sucesso!", (0.1, 0.6, 0.3, 1))
        except Exception as e:
            mostrar_snackbar(f"Erro ao processar: {e}", (0.7, 0.1, 0.1, 1))

class ConfigScreen(Screen):
    def somar_auxiliar(self):
        v1 = safe_float(self.ids.calc_val1.text)
        v2 = safe_float(self.ids.calc_val2.text)
        resultado = v1 + v2
        str_resultado = f"{resultado:.9f}"
        self.ids.lbl_calc_result.text = str_resultado
        self.ids.preco_base.text = str_resultado

    def carregar_dados(self):
        for widget_id, info in MAPA_DINAMICO.items():
            path = get_data_path(info["file"])
            if os.path.exists(path):
                with open(path, 'r', encoding="utf-8") as f:
                    try:
                        dados = json.load(f)
                        if info["key"] in dados and widget_id in self.ids:
                            val = dados[info["key"]]
                            if widget_id == "preco_base":
                                self.ids[widget_id].text = f"{float(val):.9f}"
                            else:
                                self.ids[widget_id].text = str(val)
                    except: pass

    def salvar_dados(self):
        dados_por_arquivo = {}
        for widget_id, info in MAPA_DINAMICO.items():
            if widget_id in self.ids:
                filename = info["file"]
                if filename not in dados_por_arquivo: dados_por_arquivo[filename] = {}
                dados_por_arquivo[filename][info["key"]] = safe_float(self.ids[widget_id].text)

        for filename, novos_valores in dados_por_arquivo.items():
            path = get_data_path(filename)
            conteudo = {}
            if os.path.exists(path):
                with open(path, 'r', encoding="utf-8") as f:
                    try: conteudo = json.load(f)
                    except: conteudo = {}
            conteudo.update(novos_valores)
            with open(path, 'w', encoding="utf-8") as f:
                json.dump(conteudo, f, indent=4, ensure_ascii=False)
        mostrar_snackbar("Configurações Salvas!", (0.1, 0.4, 0.8, 1))

class InquilinosScreen(Screen):
    def carregar_dados(self):
        self.ids.lista_inquilinos.clear_widgets()
        path = get_data_path("inquilinos.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                try: dados = json.load(f)
                except: dados = {}
                for nome, info in dados.items():
                    self.criar_card(nome, info.get("consumo_anterior", 0), info.get("consumo_atual", 0))

    def criar_card(self, nome="", anterior=0.0, atual=0.0):
        card = Factory.ItemInquilino()
        card.ids.txt_nome.text = nome
        card.ids.txt_anterior.text = str(anterior)
        card.ids.txt_atual.text = str(atual)
        self.ids.lista_inquilinos.add_widget(card)

    def adicionar_card_vazio(self):
        self.criar_card()

    def salvar_dados(self):
        novos_dados = {}
        for card in self.ids.lista_inquilinos.children:
            nome = card.ids.txt_nome.text.strip()
            if not nome: continue
            novos_dados[nome] = {
                "consumo_anterior": safe_float(card.ids.txt_anterior.text),
                "consumo_atual": safe_float(card.ids.txt_atual.text)
            }
        path = get_data_path("inquilinos.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(novos_dados, f, indent=4, ensure_ascii=False)
        mostrar_snackbar("Lista Salva!", (0.1, 0.4, 0.8, 1))

class MyApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.theme_style = "Dark" 
        return Builder.load_string(KV)

def mostrar_snackbar(texto, cor):
    snackbar = MDSnackbar(
        MDLabel(text=texto, theme_text_color="Custom", text_color=(1,1,1,1)),
        md_bg_color=cor,
        radius=[10, 10, 10, 10],
    )
    snackbar.size_hint_x = None
    snackbar.width = "300dp"
    snackbar.open()

if __name__ == '__main__':
    MyApp().run()
