import json
import os
from kivy.config import Config
from gerar_faturas_pdf import gerar_faturas_pdf

# Ajuste de Janela Desktop
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

# --- FUNÇÃO AUXILIAR DE SEGURANÇA ---
def safe_float(value):
    """Converte string para float com segurança, tratando erros de digitação."""
    try:
        # Limpa espaços e troca vírgula por ponto
        clean_val = str(value).strip().replace(',', '.')
        return float(clean_val) if clean_val else 0.0
    except ValueError:
        print(f"AVISO: Valor inválido '{value}' convertido para 0.0")
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
    height: "160dp"
    padding: "15dp"
    spacing: "10dp"
    elevation: 2
    radius: [12, ]

    MDBoxLayout:
        adaptive_height: True
        spacing: "15dp"
        MDTextField:
            id: txt_nome
            hint_text: "Inquilino"
            icon_left: "account"
        MDIconButton:
            icon: "trash-can-outline"
            theme_text_color: "Error"
            on_release: app.root.get_screen('inquilinos').ids.lista_inquilinos.remove_widget(root)

    MDGridLayout:
        cols: 2
        spacing: "20dp"
        adaptive_height: True
        MDTextField:
            id: txt_anterior
            hint_text: "Kwh Anterior"
            input_filter: "float"
        MDTextField:
            id: txt_atual
            hint_text: "Kwh Atual"
            input_filter: "float"

<MainScreen>:
    name: 'main'
    MDBoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: "Gestão de Energia 2024"
            elevation: 2

        MDAnchorLayout:
            MDCard:
                orientation: 'vertical'
                size_hint: None, None
                size: "450dp", "380dp"
                padding: "30dp"
                spacing: "20dp"
                radius: [20, ]
                elevation: 4

                MDLabel:
                    text: "Painel de Controle"
                    halign: "center"
                    font_style: "H5"
                    bold: True

                MDRaisedButton:
                    text: "1. CONFIGURAR TARIFAS"
                    icon: "cog"
                    size_hint_x: 1
                    on_release: root.manager.current = 'config'

                MDRaisedButton:
                    text: "2. GERENCIAR INQUILINOS"
                    icon: "account-group"
                    size_hint_x: 1
                    on_release: root.manager.current = 'inquilinos'

                MDRectangleFlatIconButton:
                    text: "3. EXECUTAR CÁLCULOS"
                    icon: "calculator-variant"
                    size_hint_x: 1
                    on_release: root.executar_calculo_geral()

<ConfigScreen>:
    name: 'config'
    on_enter: root.carregar_dados() 
    MDBoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: "Configuração de Bandeiras"
            left_action_items: [["arrow-left", lambda x: setattr(root.manager, 'current', 'main')]]

        ScrollView:
            MDBoxLayout:
                orientation: 'vertical'
                padding: "40dp"
                spacing: "20dp"
                adaptive_height: True
                size_hint_x: None
                width: "700dp"
                pos_hint: {"center_x": .5}

                MDLabel:
                    text: "Dados da Fatura"
                    font_style: "H6"

                MDGridLayout:
                    cols: 2
                    spacing: "20dp"
                    adaptive_height: True
                    MDTextField:
                        id: total_consumo
                        hint_text: "Total kWh Geral"
                        mode: "rectangle"
                        input_filter: "float"
                    MDTextField:
                        id: ilumicacao_publica
                        hint_text: "Ilum. Pública (R$)"
                        mode: "rectangle"
                        input_filter: "float"

                MDGridLayout:
                    cols: 3
                    spacing: "15dp"
                    adaptive_height: True
                    MDTextField:
                        id: consumo_verde
                        hint_text: "kWh Verde"
                        mode: "fill"
                        input_filter: "float"
                    MDTextField:
                        id: consumo_amarelo
                        hint_text: "kWh Amarelo"
                        mode: "fill"
                        input_filter: "float"
                    MDTextField:
                        id: consumo_vermelho
                        hint_text: "kWh Vermelho"
                        mode: "fill"
                        input_filter: "float"

                MDSeparator:

                MDLabel:
                    text: "Preços por kWh"
                    font_style: "H6"

                MDGridLayout:
                    cols: 3
                    spacing: "15dp"
                    adaptive_height: True
                    MDTextField:
                        id: preco_base
                        hint_text: "kWh Base"
                        input_filter: "float"
                    MDTextField:
                        id: adicional_amarelo
                        hint_text: "Add. Amarelo"
                        input_filter: "float"
                    MDTextField:
                        id: adicional_vermelho
                        hint_text: "Add. Vermelho"
                        input_filter: "float"

                MDRaisedButton:
                    text: "SALVAR TUDO"
                    size_hint_x: 1
                    on_release: root.salvar_dados()

<InquilinosScreen>:
    name: 'inquilinos'
    on_enter: root.carregar_dados()
    on_leave: lista_inquilinos.clear_widgets()
    
    MDBoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: "Cadastro de Inquilinos"
            left_action_items: [["arrow-left", lambda x: setattr(root.manager, 'current', 'main')]]
            right_action_items: [["account-plus", lambda x: root.adicionar_card_vazio()]]

        ScrollView:
            MDBoxLayout:
                id: lista_inquilinos
                orientation: 'vertical'
                padding: "30dp"
                spacing: "20dp"
                adaptive_height: True
                size_hint_x: None
                width: "600dp"
                pos_hint: {"center_x": .5}

        MDBoxLayout:
            adaptive_height: True
            padding: "20dp"
            MDRaisedButton:
                text: "SALVAR LISTA"
                size_hint_x: 1
                on_release: root.salvar_dados()
'''

def mostrar_snackbar(texto, cor=(0.1, 0.1, 0.1, 1)):
    snackbar = MDSnackbar(
        MDLabel(text=texto, theme_text_color="Custom", text_color=(1,1,1,1)),
        md_bg_color=cor,
        radius=[10, 10, 10, 10],
    )
    snackbar.size_hint_x = None
    snackbar.width = "400dp"
    snackbar.open()

class MainScreen(Screen):
    def executar_calculo_geral(self):
        try:
            # 1. Realiza os cálculos matemáticos e gera o calculo_final.json
            calculo = CalcularEnergia()
            calculo.calcular_energia()
            
            # 2. Chama sua função de PDF apontando para o arquivo gerado
            # O prefixo 'rf' trata a string como bruta para evitar problemas com backslashes no Windows
            caminho_json = get_data_path('calculo_final.json')
            gerar_faturas_pdf(caminho_json)
            
            mostrar_snackbar("Cálculo concluído e PDFs gerados!", (0, .4, .2, 1))
            
        except Exception as e:
            # Exibe o erro real no console para debug e avisa o usuário
            print(f"Erro detalhado: {e}")
            mostrar_snackbar("Erro: Verifique os dados ou o gerador de PDF.", (.7, .1, .1, 1))
class ConfigScreen(Screen):
    def carregar_dados(self):
        for widget_id, info in MAPA_DINAMICO.items():
            path = get_data_path(info["file"])
            if os.path.exists(path):
                with open(path, 'r', encoding="utf-8") as f:
                    dados = json.load(f)
                    if info["key"] in dados and widget_id in self.ids:
                        self.ids[widget_id].text = str(dados[info["key"]])

    def salvar_dados(self):
        dados_por_arquivo = {}
        for widget_id, info in MAPA_DINAMICO.items():
            if widget_id in self.ids:
                filename = info["file"]
                if filename not in dados_por_arquivo: 
                    dados_por_arquivo[filename] = {}
                
                # Uso do safe_float para evitar crash
                val = self.ids[widget_id].text
                dados_por_arquivo[filename][info["key"]] = safe_float(val)

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
        
        mostrar_snackbar("Tarifas atualizadas!", (0, .4, .2, 1))

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
            
            # Conversão segura para os valores do inquilino
            ant = safe_float(card.ids.txt_anterior.text)
            atu = safe_float(card.ids.txt_atual.text)
            
            novos_dados[nome] = {"consumo_anterior": ant, "consumo_atual": atu}
        
        path = get_data_path("inquilinos.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(novos_dados, f, indent=4, ensure_ascii=False)
        mostrar_snackbar("Lista de inquilinos salva!", (0, .4, .2, 1))

class MyApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.theme_style = "Dark" 
        return Builder.load_string(KV)

if __name__ == '__main__':
    MyApp().run()