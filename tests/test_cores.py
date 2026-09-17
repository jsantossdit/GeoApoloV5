"""
Testes Unitários para o Módulo de Cores de Produtos e Estoque Auxiliar.
GeoApolo V5
Clean Architecture: DTOs, Repositório SQLite em memória e Regras de Negócio do Service.
"""

import sqlite3
import unittest
from unittest.mock import MagicMock

from cores.models import CorDTO, ResultadoCorDTO
from cores.repository import CoresRepository
from cores.service import CoresService


class TestCoresModels(unittest.TestCase):
    """Testes dos DTOs do cadastro de cores."""

    def test_cor_dto_defaults(self):
        dto = CorDTO()
        self.assertEqual(dto.codigo_cor, 0)
        self.assertEqual(dto.descricao_cor, "")
        self.assertEqual(dto.display, "000 - ")

    def test_cor_dto_display_formatting(self):
        dto = CorDTO(codigo_cor=5, descricao_cor="AZUL ROYAL")
        self.assertEqual(dto.display, "005 - AZUL ROYAL")

    def test_resultado_cor_dto(self):
        res_ok = ResultadoCorDTO(sucesso=True, mensagem="OK", codigo=1)
        self.assertTrue(res_ok.sucesso)
        self.assertEqual(res_ok.codigo, 1)

        res_err = ResultadoCorDTO(sucesso=False, mensagem="Erro")
        self.assertFalse(res_err.sucesso)
        self.assertIsNone(res_err.codigo)


class TestCoresRepository(unittest.TestCase):
    """Testes do repositório de cores usando banco SQLite em memória."""

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE USER_geoapolo_produto_cores (
                codigo_cor INTEGER PRIMARY KEY,
                descricao_cor VARCHAR(50)
            )
        """)
        self.conn.commit()
        self.repo = CoresRepository(connection=self.conn)

    def tearDown(self):
        self.conn.close()

    def test_obter_proximo_codigo_tabela_vazia(self):
        prox = self.repo.obter_proximo_codigo()
        self.assertEqual(prox, 1)

    def test_obter_proximo_codigo_com_registros(self):
        self.cursor.execute("INSERT INTO USER_geoapolo_produto_cores VALUES (1, 'AZUL')")
        self.cursor.execute("INSERT INTO USER_geoapolo_produto_cores VALUES (5, 'VERDE')")
        self.conn.commit()

        prox = self.repo.obter_proximo_codigo()
        self.assertEqual(prox, 6)

    def test_salvar_e_listar_cores(self):
        c1 = CorDTO(codigo_cor=1, descricao_cor="BRANCO")
        c2 = CorDTO(codigo_cor=2, descricao_cor="PRETO")
        self.repo.salvar_cor(c1)
        self.repo.salvar_cor(c2)

        cores = self.repo.listar_cores()
        self.assertEqual(len(cores), 2)
        self.assertEqual(cores[0].codigo_cor, 1)
        self.assertEqual(cores[0].descricao_cor, "BRANCO")
        self.assertEqual(cores[1].codigo_cor, 2)
        self.assertEqual(cores[1].descricao_cor, "PRETO")

    def test_salvar_atualizacao_cor(self):
        c1 = CorDTO(codigo_cor=1, descricao_cor="AZUL CLARO")
        self.repo.salvar_cor(c1)

        c1_up = CorDTO(codigo_cor=1, descricao_cor="AZUL CELESTE")
        self.repo.salvar_cor(c1_up)

        cor_db = self.repo.obter_cor(1)
        self.assertIsNotNone(cor_db)
        self.assertEqual(cor_db.descricao_cor, "AZUL CELESTE")

    def test_obter_cor_inexistente(self):
        self.assertIsNone(self.repo.obter_cor(999))

    def test_existe_descricao(self):
        self.repo.salvar_cor(CorDTO(codigo_cor=1, descricao_cor="VERMELHO"))

        self.assertTrue(self.repo.existe_descricao("VERMELHO"))
        self.assertTrue(self.repo.existe_descricao("  vermelho  "))
        self.assertFalse(self.repo.existe_descricao("VERMELHO", codigo_ignorar=1))
        self.assertFalse(self.repo.existe_descricao("AMARELO"))

    def test_excluir_cor(self):
        self.repo.salvar_cor(CorDTO(codigo_cor=1, descricao_cor="CINZA"))
        self.assertIsNotNone(self.repo.obter_cor(1))

        self.repo.excluir_cor(1)
        self.assertIsNone(self.repo.obter_cor(1))


class TestCoresService(unittest.TestCase):
    """Testes de regras de negócio do CoresService."""

    def setUp(self):
        self.mock_repo = MagicMock(spec=CoresRepository)
        self.service = CoresService(self.mock_repo)

    def test_listar_e_obter_cores(self):
        self.mock_repo.listar_cores.return_value = [CorDTO(1, "AZUL")]
        self.mock_repo.obter_cor.return_value = CorDTO(1, "AZUL")

        res_list = self.service.listar_cores()
        self.assertEqual(len(res_list), 1)

        cor = self.service.obter_cor(1)
        self.assertIsNotNone(cor)
        self.assertEqual(cor.descricao_cor, "AZUL")

        # Código <= 0
        self.assertIsNone(self.service.obter_cor(0))
        self.assertIsNone(self.service.obter_cor(-5))

    def test_salvar_cor_descricao_vazia(self):
        res = self.service.salvar_cor(CorDTO(codigo_cor=1, descricao_cor="   "))
        self.assertFalse(res.sucesso)
        self.assertIn("obrigatória", res.mensagem)

    def test_salvar_cor_descricao_duplicada(self):
        self.mock_repo.existe_descricao.return_value = True
        res = self.service.salvar_cor(CorDTO(codigo_cor=1, descricao_cor="AMARELO"))
        self.assertFalse(res.sucesso)
        self.assertIn("já está cadastrada", res.mensagem)

    def test_salvar_cor_nova_gera_codigo(self):
        self.mock_repo.obter_proximo_codigo.return_value = 10
        self.mock_repo.existe_descricao.return_value = False

        cor = CorDTO(codigo_cor=0, descricao_cor="DOURADO")
        res = self.service.salvar_cor(cor)
        self.assertTrue(res.sucesso)
        self.assertEqual(res.codigo, 10)
        self.mock_repo.salvar_cor.assert_called_once()

    def test_excluir_cor_codigo_invalido(self):
        res = self.service.excluir_cor(0)
        self.assertFalse(res.sucesso)
        self.assertIn("inválido", res.mensagem)

    def test_excluir_cor_sucesso(self):
        res = self.service.excluir_cor(5)
        self.assertTrue(res.sucesso)
        self.mock_repo.excluir_cor.assert_called_once_with(5)


if __name__ == "__main__":
    unittest.main()
