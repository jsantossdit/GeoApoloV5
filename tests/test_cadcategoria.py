"""
Testes unitários para o módulo de cadastro de categorias (cadcategoria_view, repository e service).
"""

import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk

from categorias.cadcategoria_view import FrmCadCategoria
from categorias.repository import CategoriaEntidadeRepository
from categorias.service import CategoriaEntidadeService
from categorias.view import CategoriasEntidadeView


class TestCadCategoria(unittest.TestCase):
    """Testes do módulo de categorias e formulário FrmCadCategoria."""

    @classmethod
    def setUpClass(cls):
        try:
            cls.root = tk.Tk()
            cls.root.withdraw()
        except Exception:
            cls.root = None

    @classmethod
    def tearDownClass(cls):
        if cls.root:
            try:
                cls.root.destroy()
            except Exception:
                pass

    def test_repository_salvar_e_listar_categorias(self):
        """Testa salvar_categoria e listar_todas_categorias com mock de conexão."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        # Simula retorno do banco para listar_todas_categorias
        mock_cursor.description = [("geocategcodestr",), ("geocategnome",), ("geocateggrupo",), ("geocategcodalt",)]
        mock_cursor.fetchall.return_value = [
            ("01", "DIOCESE", "S", "1"),
            ("01.001", "PARÓQUIA SANTO ANTÔNIO", "N", "2"),
        ]

        repo = CategoriaEntidadeRepository(connection=mock_conn)
        lista = repo.listar_todas_categorias()

        self.assertEqual(len(lista), 2)
        self.assertEqual(lista[0]["codigo"], "01")
        self.assertEqual(lista[0]["descricao"], "DIOCESE")
        self.assertEqual(lista[1]["codigo"], "01.001")

        # Teste de salvar inclusão
        dados_nova = {
            "codigo": "02",
            "descricao": "FORANIA",
            "codigo_alternativo": "3",
            "grupo": "S",
        }
        res_salvar = repo.salvar_categoria(dados_nova, modo_inclusao=True)
        self.assertTrue(res_salvar)
        self.assertTrue(mock_cursor.execute.called)
        self.assertTrue(mock_conn.commit.called)

    def test_service_validacoes_categoria(self):
        """Testa regras de negócio e validações de categoria no serviço."""
        mock_repo = MagicMock()
        mock_repo.obter_categoria.return_value = None
        mock_repo.salvar_categoria.return_value = True

        service = CategoriaEntidadeService(mock_repo)

        # Sem código -> erro
        res_sem_cod = service.salvar_categoria({"descricao": "TESTE"})
        self.assertFalse(res_sem_cod.sucesso)
        self.assertIn("Código Categoria", res_sem_cod.mensagem)

        # Sem descrição -> erro
        res_sem_desc = service.salvar_categoria({"codigo": "01"})
        self.assertFalse(res_sem_desc.sucesso)
        self.assertIn("Nome da Categoria", res_sem_desc.mensagem)

        # Dados válidos
        res_ok = service.salvar_categoria({"codigo": "01.005", "descricao": "COMUNIDADE SANTA LUZIA"}, modo_inclusao=True)
        self.assertTrue(res_ok.sucesso)

        # Código duplicado em inclusão
        mock_repo.obter_categoria.return_value = {"codigo": "01.005"}
        res_dup = service.salvar_categoria({"codigo": "01.005", "descricao": "COMUNIDADE SANTA LUZIA"}, modo_inclusao=True)
        self.assertFalse(res_dup.sucesso)
        self.assertIn("já está em uso", res_dup.mensagem)

    def test_formulario_cadcategoria_headless(self):
        """Testa instanciação e preenchimento de campos em FrmCadCategoria."""
        if not self.root:
            self.skipTest("Ambiente Tkinter não disponível para teste de GUI.")

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.description = [("geocategcodestr",), ("geocategnome",), ("geocateggrupo",), ("geocategcodalt",)]
        mock_cursor.fetchall.return_value = []

        frm = FrmCadCategoria(self.root, connection=mock_conn)
        try:
            self.assertIsNotNone(frm.txt_codigo_estrutural)
            self.assertIsNotNone(frm.txt_nome)
            self.assertIsNotNone(frm.txt_codigo_alternativo)
            self.assertIsNotNone(frm.chk_grupo)

            # Preenchimento e novo registro
            frm.novo_registro()
            self.assertEqual(frm.txt_codigo_estrutural.get(), "")
            self.assertEqual(frm.txt_nome.get(), "")

            frm.txt_codigo_estrutural.insert(0, "03.001")
            frm.txt_nome.insert(0, "GRUPO DE ORAÇÃO JOVENS")
            self.assertEqual(frm.txt_codigo_estrutural.get(), "03.001")
            self.assertEqual(frm.txt_nome.get(), "GRUPO DE ORAÇÃO JOVENS")
        finally:
            frm.destroy()


if __name__ == "__main__":
    unittest.main()
