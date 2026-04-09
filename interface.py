import json
import os
from kivy.config import Config
from gerar_faturas_pdf import gerar_faturas_pdf

# Configurações de Janela
Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '750')
Config.set('graphics', 'resizable', '1')

from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.factory import Factory
from kivymd.app import MDApp
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel

from class_dados import get_data_path
from core import CalcularEnergia

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