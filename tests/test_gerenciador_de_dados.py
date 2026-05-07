import tempfile
import unittest
from pathlib import Path

from tests import _path_setup  # noqa: F401

from energia.exceptions import ValidationError
from energia.gerenciador_de_dados import GerenciadorDados
from energia.paths import BASE_DIR, DATA_FILE, DADOS_DIR


class GerenciadorDadosTestCase(unittest.TestCase):
    def test_caminho_padrao_aponta_para_dados_data_json_na_raiz(self) -> None:
        self.assertEqual(BASE_DIR, Path(__file__).resolve().parent.parent)
        self.assertEqual(DADOS_DIR, BASE_DIR / "dados")
        self.assertEqual(DATA_FILE, BASE_DIR / "dados" / "data.json")

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_file = Path(self.temp_dir.name) / "data.json"
        self.gd = GerenciadorDados(path=self.data_file)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_cria_arquivo_com_estrutura_padrao(self) -> None:
        self.assertTrue(self.data_file.exists())
        self.assertEqual(self.gd.quantidade_inquilinos, 0)
        self.assertEqual(self.gd.iluminacao_publica, 0.0)
        self.assertEqual(self.gd.desconto, 0.0)
        self.assertEqual(self.gd.motivo_desconto, "")

    def test_cadastra_inquilino_com_validacao(self) -> None:
        self.gd.cadastrar_atualizar_inquilino(
            {"nome": "Maria", "consumo_anterior": "10", "consumo_atual": "25"}
        )

        inquilino = self.gd.dados_inquilinos["Maria"]
        self.assertEqual(inquilino["consumo_anterior"], 10.0)
        self.assertEqual(inquilino["consumo_atual"], 25.0)

    def test_impede_leitura_atual_menor_que_anterior(self) -> None:
        with self.assertRaises(ValidationError):
            self.gd.cadastrar_atualizar_inquilino(
                {"nome": "Maria", "consumo_anterior": 30, "consumo_atual": 20}
            )

    def test_atualiza_configuracoes_em_lote(self) -> None:
        self.gd.atualizar_configuracoes(
            {
                "preco_base": 1.2,
                "adicional_amarelo": 0.1,
                "adicional_vermelho": 0.2,
                "total_consumo": 100,
                "consumo_verde": 50,
                "consumo_amarelo": 30,
                "consumo_vermelho": 20,
                "iluminacao_publica": 42,
                "desconto": 15,
                "motivo_desconto": "Ajuste da concessionaria",
            }
        )

        self.assertEqual(self.gd.preco_base, 1.2)
        self.assertEqual(self.gd.valor_total_amarelo, 1.3)
        self.assertEqual(self.gd.valor_total_vermelho, 1.4)
        self.assertEqual(self.gd.desconto, 15.0)
        self.assertEqual(self.gd.motivo_desconto, "Ajuste da concessionaria")
