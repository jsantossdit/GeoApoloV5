"""
Testes Unitários para o Módulo de Departamentos e Seções.
GeoApolo V5
Clean Architecture: DTOs, Repositório SQLite em memória e Regras de Negócio do Service.
"""

import sqlite3
import unittest
from unittest.mock import MagicMock

from departamentos.models import DepartamentoDTO, ResultadoDepartamentoDTO
from departamentos.repository import DepartamentosRepository
from departamentos.service import DepartamentosService


class TestDepartamentosModels(unittest.TestCase):
    """Testes dos DTOs de Departamentos."""

    def test_departamento_dto_display_and_properties(self):
        d1 = DepartamentoDTO(1, "FINANCEIRO", "01", "MATRIZ", "A")
        self.assertTrue(d1.is_ativo)
        self.assertIn("001 - FINANCEIRO", d1.display)
        self.assertIn("Ativo", d1.display)

        d2 = DepartamentoDTO(2, "ARQUIVO MORTO", "01", "MATRIZ", "I")
        self.assertFalse(d2.is_ativo)
        self.assertIn("Inativo", d2.display)

    def test_resultado_departamento_dto(self):
        res = ResultadoDepartamentoDTO(sucesso=True, mensagem="OK", codigo=1)
        self.assertTrue(res.sucesso)
        self.assertEqual(res.codigo, 1)


class TestDepartamentosRepository(unittest.TestCase):
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
            CREATE TABLE USER_geoapolo_departamentos (
                codigo_departamento INTEGER PRIMARY KEY,
                nome_departamento VARCHAR(100),
                empcod VARCHAR(10),
                flagativo VARCHAR(1)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE centro_ctrl (
                cctrlcodestr VARCHAR(20) PRIMARY KEY,
                cctrlnome VARCHAR(100)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE geoapolo_secoescctrlapolo (
                codigo_secao INTEGER,
                cctrlcodestr VARCHAR(20)
            )
        """)

        self.cursor.execute("INSERT INTO USER_geoapolo_empresas VALUES ('01', 'MATRIZ')")
        self.cursor.execute("INSERT INTO centro_ctrl VALUES ('1.01.001', 'ADMINISTRACAO')")
        self.conn.commit()

        self.repo = DepartamentosRepository(connection=self.conn)

    def tearDown(self):
        self.conn.close()

    def test_obter_proximo_codigo(self):
        self.assertEqual(self.repo.obter_proximo_codigo(), 1)
        self.repo.salvar_departamento(DepartamentoDTO(1, "DEPTO 1", "01"))
        self.assertEqual(self.repo.obter_proximo_codigo(), 2)

    def test_salvar_e_listar_departamentos(self):
        d1 = DepartamentoDTO(1, "TI", "01", flagativo="A", cctrlcodestr="1.01.001")
        d2 = DepartamentoDTO(2, "RECURSOS HUMANOS", "01", flagativo="A")
        self.repo.salvar_departamento(d1)
        self.repo.salvar_departamento(d2)

        todos = self.repo.listar_departamentos()
        self.assertEqual(len(todos), 2)
        self.assertEqual(todos[0].nome_departamento, "TI")
        self.assertEqual(todos[0].cctrlcodestr, "1.01.001")
        self.assertEqual(todos[0].cctrlnome, "ADMINISTRACAO")

        # Filtro por nome
        filtrados = self.repo.listar_departamentos(filtro="HUMANOS")
        self.assertEqual(len(filtrados), 1)
        self.assertEqual(filtrados[0].codigo_departamento, 2)

    def test_obter_e_excluir_departamento(self):
        d = DepartamentoDTO(5, "EXPEDICAO", "01", cctrlcodestr="1.01.001")
        self.repo.salvar_departamento(d)

        rec = self.repo.obter_departamento(5)
        self.assertIsNotNone(rec)
        self.assertEqual(rec.nome_departamento, "EXPEDICAO")

        self.repo.excluir_departamento(5)
        self.assertIsNone(self.repo.obter_departamento(5))


class TestDepartamentosService(unittest.TestCase):
    """Testes de Regras de Negócio do DepartamentosService."""

    def setUp(self):
        self.mock_repo = MagicMock(spec=DepartamentosRepository)
        self.service = DepartamentosService(self.mock_repo)

    def test_salvar_validacoes(self):
        # Nome vazio
        res1 = self.service.salvar_departamento(DepartamentoDTO(1, "", "01"))
        self.assertFalse(res1.sucesso)
        self.assertIn("obrigatório", res1.mensagem)

        # Empresa vazia
        res2 = self.service.salvar_departamento(DepartamentoDTO(1, "COMPRAS", ""))
        self.assertFalse(res2.sucesso)
        self.assertIn("obrigatória", res2.mensagem)

        # Sucesso com auto incremento de código
        self.mock_repo.obter_proximo_codigo.return_value = 10
        dto_novo = DepartamentoDTO(0, "MARKETING", "01")
        res3 = self.service.salvar_departamento(dto_novo)
        self.assertTrue(res3.sucesso)
        self.assertEqual(res3.codigo, 10)
        self.mock_repo.salvar_departamento.assert_called_once()

    def test_excluir_validacoes(self):
        res_inv = self.service.excluir_departamento(0)
        self.assertFalse(res_inv.sucesso)

        res_ok = self.service.excluir_departamento(5)
        self.assertTrue(res_ok.sucesso)
        self.mock_repo.excluir_departamento.assert_called_once_with(5)


if __name__ == "__main__":
    unittest.main()
