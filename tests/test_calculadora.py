import tempfile
import unittest
from pathlib import Path

from tests import _path_setup  # noqa: F401

from energia.calculadora import CalcularEnergia
from energia.exceptions import ValidationError
from energia.gerenciador_de_dados import GerenciadorDados


class CalculadoraTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_file = Path(self.temp_dir.name) / "data.json"
        self.gd = GerenciadorDados(path=self.data_file)
        self.gd.atualizar_configuracoes(
            {
                "preco_base": 1.0,
                "adicional_amarelo": 0.3,
                "adicional_vermelho": 0.5,
                "total_consumo": 100,
                "consumo_verde": 50,
                "consumo_amarelo": 25,
                "consumo_vermelho": 25,
                "iluminacao_publica": 40,
            }
        )
        self.gd.cadastrar_atualizar_inquilino(
            {"nome": "joao", "consumo_anterior": 0, "consumo_atual": 40}
        )
        self.gd.cadastrar_atualizar_inquilino(
            {"nome": "maria", "consumo_anterior": 10, "consumo_atual": 50}
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_calcula_resultados_e_salva_por_inquilino(self) -> None:
        calculadora = CalcularEnergia(self.gd)
        resultados = calculadora.calcular_energia()

        self.assertEqual(set(resultados.keys()), {"joao", "maria"})
        self.assertEqual(resultados["joao"]["kwh_consumido_mes"], "40.00")
        self.assertEqual(resultados["joao"]["iluminacao_publica"], "20.00")
        self.assertEqual(resultados["joao"]["total"], "68.00")
        self.assertIn("calculo_inquilino", self.gd.dados_inquilinos["joao"])

    def test_bloqueia_calculo_quando_bandeiras_nao_fecham_total(self) -> None:
        self.gd.total_consumo = 120
        calculadora = CalcularEnergia(self.gd)

        with self.assertRaises(ValidationError):
            calculadora.calcular_energia()
