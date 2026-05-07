import importlib.util
import tempfile
import unittest
from pathlib import Path

from tests import _path_setup  # noqa: F401

from energia.calculadora import CalcularEnergia
from energia.gerenciador_de_dados import GerenciadorDados


REPORTLAB_DISPONIVEL = importlib.util.find_spec("reportlab") is not None

if REPORTLAB_DISPONIVEL:
    from energia.gerador_pdf import gerar_faturas_pdf


@unittest.skipUnless(REPORTLAB_DISPONIVEL, "reportlab nao esta instalado no ambiente de teste")
class GeradorPdfTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_dir = Path(self.temp_dir.name) / "faturas"
        self.data_file = Path(self.temp_dir.name) / "data.json"
        self.gd = GerenciadorDados(path=self.data_file)
        self.gd.atualizar_configuracoes(
            {
                "preco_base": 1.0,
                "adicional_amarelo": 0.2,
                "adicional_vermelho": 0.4,
                "total_consumo": 50,
                "consumo_verde": 25,
                "consumo_amarelo": 15,
                "consumo_vermelho": 10,
                "iluminacao_publica": 30,
                "desconto": 9,
                "motivo_desconto": "Credito aplicado",
            }
        )
        self.gd.cadastrar_atualizar_inquilino(
            {"nome": "carlos", "consumo_anterior": 5, "consumo_atual": 25}
        )
        CalcularEnergia(self.gd).calcular_energia()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_gera_arquivo_pdf(self) -> None:
        arquivos = gerar_faturas_pdf(self.gd, pasta_saida=self.output_dir)

        self.assertEqual(len(arquivos), 1)
        self.assertTrue(arquivos[0].exists())
        self.assertGreater(arquivos[0].stat().st_size, 0)
