"""
Testes Unitários para o Módulo Multi-Empresas e Contexto Corporativo.
GeoApolo V5
"""

import sqlite3
import unittest
from unittest.mock import MagicMock

from empresas.models import EmpresaDTO, ResultadoEmpresaDTO
from empresas.repository import EmpresasRepository
from empresas.service import EmpresasService


class TestEmpresasModels(unittest.TestCase):
    """Testes dos DTOs de Empresas."""

    def test_empresa_display_completo(self):
        e = EmpresaDTO(empcod="01", empnome="MATRIZ SAO PAULO")
        self.assertEqual(e.display_completo, "01 - MATRIZ SAO PAULO")


class TestEmpresasRepositorySQLite(unittest.TestCase):
    """Testes de repositório com banco SQLite em memória."""

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self._criar_schema()
        self._popular_dados()
        self.repo = EmpresasRepository(self.conn)

    def tearDown(self):
        self.conn.close()

    def _criar_schema(self):
        cur = self.conn.cursor()
        cur.executescript("""
            CREATE TABLE USER_geoapolo_empresas (
                empcod TEXT PRIMARY KEY,
                empnome TEXT
            );

            CREATE TABLE empresa_filial (
                empcod TEXT PRIMARY KEY,
                empnome TEXT
            );
        """)
        self.conn.commit()

    def _popular_dados(self):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO USER_geoapolo_empresas VALUES ('01', 'SEDE LORENA')")
        cur.execute("INSERT INTO empresa_filial VALUES ('01', 'SEDE LORENA')")
        cur.execute("INSERT INTO empresa_filial VALUES ('02', 'FILIAL APARECIDA')")
        self.conn.commit()

    def test_listar_empresas(self):
        lista = self.repo.listar_empresas()
        self.assertEqual(len(lista), 1)
        self.assertEqual(lista[0].empcod, "01")

    def test_obter_empresa(self):
        e = self.repo.obter_empresa("01")
        self.assertIsNotNone(e)
        self.assertEqual(e.empnome, "SEDE LORENA")

        inex = self.repo.obter_empresa("99")
        self.assertIsNone(inex)

    def test_salvar_empresa_insert_e_update(self):
        # Insert
        nova = EmpresaDTO(empcod="03", empnome="FILIAL GUARATINGUETA")
        self.repo.salvar_empresa(nova)
        self.assertEqual(len(self.repo.listar_empresas()), 2)

        # Update
        nova.empnome = "FILIAL GUARATINGUETA ATUALIZADA"
        self.repo.salvar_empresa(nova)
        buscado = self.repo.obter_empresa("03")
        self.assertEqual(buscado.empnome, "FILIAL GUARATINGUETA ATUALIZADA")

    def test_excluir_empresa(self):
        self.repo.excluir_empresa("01")
        self.assertIsNone(self.repo.obter_empresa("01"))

    def test_sincronizar_empresas_apolo(self):
        # '01' já existe; '02' deve ser importada
        novas = self.repo.sincronizar_empresas_apolo()
        self.assertEqual(novas, 1)

        todas = self.repo.listar_empresas()
        self.assertEqual(len(todas), 2)
        cods = [e.empcod for e in todas]
        self.assertIn("01", cods)
        self.assertIn("02", cods)


class TestEmpresasService(unittest.TestCase):
    """Testes de negócio e contexto de sessão do EmpresasService."""

    def setUp(self):
        self.mock_repo = MagicMock(spec=EmpresasRepository)
        self.service = EmpresasService(self.mock_repo)
        EmpresasService._empresa_ativa_contexto = None

    def test_salvar_validacoes(self):
        r1 = self.service.salvar_empresa(EmpresaDTO(empcod="", empnome="Nome"))
        self.assertFalse(r1.sucesso)
        self.assertIn("código da empresa", r1.mensagem)

        r2 = self.service.salvar_empresa(EmpresaDTO(empcod="01", empnome=""))
        self.assertFalse(r2.sucesso)
        self.assertIn("razão social/nome", r2.mensagem)

    def test_selecionar_empresa_ativa(self):
        self.mock_repo.obter_empresa.return_value = EmpresaDTO(empcod="01", empnome="MATRIZ")

        res = self.service.selecionar_empresa_ativa("01")
        self.assertTrue(res.sucesso)

        ativa = EmpresasService.obter_empresa_ativa()
        self.assertIsNotNone(ativa)
        self.assertEqual(ativa.empcod, "01")

    def test_nao_permite_excluir_empresa_ativa(self):
        EmpresasService._empresa_ativa_contexto = EmpresaDTO(empcod="01", empnome="MATRIZ")

        res = self.service.excluir_empresa("01")
        self.assertFalse(res.sucesso)
        self.assertIn("atualmente selecionada como ativa", res.mensagem)
        self.mock_repo.excluir_empresa.assert_not_called()


if __name__ == "__main__":
    unittest.main()
