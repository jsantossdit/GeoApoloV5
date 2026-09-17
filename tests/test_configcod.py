"""
Testes Unitários para o Módulo de Manutenção de Códigos do Sistema (Sequenciais).
GeoApolo V5
Clean Architecture: DTOs, Repositório SQLite em memória e Regras de Negócio do Service.
"""

import sqlite3
import unittest
from unittest.mock import MagicMock

from configcod.models import ConfigCodDTO, ResultadoConfigCodDTO
from configcod.repository import ConfigCodRepository
from configcod.service import ConfigCodService


class TestConfigCodModels(unittest.TestCase):
    """Testes dos DTOs de Manutenção de Códigos."""

    def test_config_cod_dto_defaults_and_properties(self):
        dto = ConfigCodDTO(geotabela="USER_geoapolo_entidades", proximo_codigo=10, tabela_ativa="S")
        self.assertTrue(dto.is_ativa)
        self.assertIn("USER_geoapolo_entidades", dto.display)
        self.assertIn("10", dto.display)
        self.assertIn("Ativa", dto.display)

        dto_inativa = ConfigCodDTO(geotabela="USER_geoapolo_old", proximo_codigo=5, tabela_ativa="N")
        self.assertFalse(dto_inativa.is_ativa)
        self.assertIn("Inativa", dto_inativa.display)

    def test_resultado_config_cod_dto(self):
        res = ResultadoConfigCodDTO(sucesso=True, mensagem="OK", geotabela="TAB1", proximo_codigo=20)
        self.assertTrue(res.sucesso)
        self.assertEqual(res.proximo_codigo, 20)


class TestConfigCodRepository(unittest.TestCase):
    """Testes do Repositório com SQLite em memória."""

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
            CREATE TABLE USER_geoapolo_empresas (
                empcod VARCHAR(10) PRIMARY KEY,
                empnome VARCHAR(100)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE USER_geoapolo_configcod (
                geotabela VARCHAR(50) PRIMARY KEY,
                proximo_codigo INTEGER,
                tabela_ativa VARCHAR(1),
                empcod VARCHAR(10)
            )
        """)

        self.cursor.execute("INSERT INTO USER_geoapolo_empresas VALUES ('01', 'EMPRESA MATRIZ')")
        self.conn.commit()

        self.repo = ConfigCodRepository(connection=self.conn)

    def tearDown(self):
        self.conn.close()

    def test_salvar_e_listar_tabelas(self):
        c1 = ConfigCodDTO("USER_geoapolo_entidades", 100, "S", "01")
        c2 = ConfigCodDTO("USER_geoapolo_produtos", 50, "N", "01")
        self.repo.salvar_config_cod(c1)
        self.repo.salvar_config_cod(c2)

        todas = self.repo.listar_tabelas()
        self.assertEqual(len(todas), 2)
        self.assertEqual(todas[0].geotabela, "USER_geoapolo_entidades")
        self.assertEqual(todas[0].empnome, "EMPRESA MATRIZ")

        # Filtro
        filtradas = self.repo.listar_tabelas("produtos")
        self.assertEqual(len(filtradas), 1)
        self.assertEqual(filtradas[0].geotabela, "USER_geoapolo_produtos")

    def test_atualizar_proximo_codigo(self):
        c1 = ConfigCodDTO("USER_geoapolo_ocorrencias", 1, "S", "01")
        self.repo.salvar_config_cod(c1)

        self.repo.atualizar_proximo_codigo("USER_geoapolo_ocorrencias", 25, "S")
        recuperado = self.repo.obter_config_cod("USER_geoapolo_ocorrencias")
        self.assertIsNotNone(recuperado)
        self.assertEqual(recuperado.proximo_codigo, 25)

    def test_gerar_e_incrementar_codigo(self):
        # Tabela inexistente: cria com 1 e avança para 2
        cod1 = self.repo.gerar_e_incrementar_codigo("USER_geoapolo_nova")
        self.assertEqual(cod1, 1)

        # Próxima chamada deve retornar 2 e avançar para 3
        cod2 = self.repo.gerar_e_incrementar_codigo("USER_geoapolo_nova")
        self.assertEqual(cod2, 2)


class TestConfigCodService(unittest.TestCase):
    """Testes de Regras de Negócio do ConfigCodService."""

    def setUp(self):
        self.mock_repo = MagicMock(spec=ConfigCodRepository)
        self.service = ConfigCodService(self.mock_repo)

    def test_atualizar_validacoes(self):
        # Tabela vazia
        res1 = self.service.atualizar_config_cod("", 10, "S")
        self.assertFalse(res1.sucesso)
        self.assertIn("obrigatório", res1.mensagem)

        # Código negativo
        res2 = self.service.atualizar_config_cod("TABELA", -1, "S")
        self.assertFalse(res2.sucesso)
        self.assertIn("negativo", res2.mensagem)

        # Sucesso
        res3 = self.service.atualizar_config_cod("TABELA", 15, "S")
        self.assertTrue(res3.sucesso)
        self.mock_repo.atualizar_proximo_codigo.assert_called_with("TABELA", 15, "S")

    def test_salvar_config_cod_validacoes(self):
        res_vazia = self.service.salvar_config_cod(ConfigCodDTO("", 5))
        self.assertFalse(res_vazia.sucesso)

        res_neg = self.service.salvar_config_cod(ConfigCodDTO("TABELA", -5))
        self.assertFalse(res_neg.sucesso)

        res_ok = self.service.salvar_config_cod(ConfigCodDTO("TABELA", 20, "S"))
        self.assertTrue(res_ok.sucesso)
        self.mock_repo.salvar_config_cod.assert_called_once()

    def test_obter_proximo_codigo(self):
        self.mock_repo.obter_config_cod.return_value = ConfigCodDTO("TAB", 42)
        self.mock_repo.gerar_e_incrementar_codigo.return_value = 42

        # Apenas leitura
        cod = self.service.obter_proximo_codigo("TAB", auto_incrementar=False)
        self.assertEqual(cod, 42)

        # Com incremento
        cod_inc = self.service.obter_proximo_codigo("TAB", auto_incrementar=True)
        self.assertEqual(cod_inc, 42)
        self.mock_repo.gerar_e_incrementar_codigo.assert_called_with("TAB")


if __name__ == "__main__":
    unittest.main()
