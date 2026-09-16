"""
Testes automatizados para o módulo de Relacionamento de Categorias, Entidades e Usuários.
Execução headless e desacoplada.
"""

import os
import sys
import unittest
import tkinter as tk
from unittest.mock import MagicMock, patch

PASTA_RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PASTA_RAIZ not in sys.path:
    sys.path.insert(0, PASTA_RAIZ)

from categorias.models import (
    CategoriaResumoDTO,
    UsuarioItemDTO,
    GrupoItemDTO,
    ResultadoOperacao,
)
from categorias.service import CategoriaEntidadeService
from categorias.repository import CategoriaEntidadeRepository
from categorias.view import CategoriasEntidadeView


class TestCategoriaEntidadeService(unittest.TestCase):

    def setUp(self):
        self.mock_repo = MagicMock()
        self.service = CategoriaEntidadeService(self.mock_repo)

    def test_obter_usuarios_e_grupos(self):
        self.mock_repo.listar_usuarios_ativos.return_value = [
            {"codigo": "USR01", "nome": "Administrador"}
        ]
        self.mock_repo.listar_grupos.return_value = [
            {"codigo": "GRP01", "descricao": "Diretoria"}
        ]

        usuarios = self.service.obter_usuarios()
        self.assertEqual(len(usuarios), 1)
        self.assertEqual(usuarios[0]["codigo"], "USR01")

        grupos = self.service.obter_grupos()
        self.assertEqual(len(grupos), 1)
        self.assertEqual(grupos[0]["descricao"], "Diretoria")

    def test_obter_categorias_usuario(self):
        self.mock_repo.listar_categorias_usuario.return_value = [
            {"codigo_categoria": "01", "descricao": "Associados", "total_entidades": 10, "vinculada": 1}
        ]
        cats = self.service.obter_categorias("Usuario", "USR01")
        self.assertEqual(len(cats), 1)
        self.assertEqual(cats[0]["codigo_categoria"], "01")
        self.mock_repo.listar_categorias_usuario.assert_called_with("USR01")

    def test_obter_categorias_grupo(self):
        self.mock_repo.listar_usuarios_do_grupo.return_value = ["USR01", "USR02"]
        self.mock_repo.listar_categorias_usuario.return_value = [
            {"codigo_categoria": "02", "descricao": "Benfeitores", "total_entidades": 5, "vinculada": 0}
        ]
        cats = self.service.obter_categorias("Grupo", "GRP01")
        self.assertEqual(len(cats), 1)
        self.mock_repo.listar_usuarios_do_grupo.assert_called_with("GRP01")
        self.mock_repo.listar_categorias_usuario.assert_called_with("USR01")

    def test_vincular_categoria_usuario(self):
        res = self.service.vincular_categoria("Usuario", "USR01", "CAT01")
        self.assertTrue(res.sucesso)
        self.mock_repo.vincular_categoria_usuario.assert_called_once_with("USR01", "CAT01")

    def test_vincular_categoria_grupo(self):
        self.mock_repo.listar_usuarios_do_grupo.return_value = ["U1", "U2"]
        res = self.service.vincular_categoria("Grupo", "GRP1", "CAT01")
        self.assertTrue(res.sucesso)
        self.assertEqual(self.mock_repo.vincular_categoria_usuario.call_count, 2)

    def test_relacionar_entidades_usuario(self):
        res = self.service.relacionar_entidades("Usuario", "USR01", "CAT01")
        self.assertTrue(res.sucesso)
        self.mock_repo.relacionar_entidades_categoria_usuario.assert_called_once_with("USR01", "CAT01")

    def test_remover_relacionamento(self):
        res = self.service.remover_relacionamento("Usuario", "USR01", "CAT01")
        self.assertTrue(res.sucesso)
        self.mock_repo.remover_categoria_usuario.assert_called_once_with("USR01", "CAT01")


class TestCategoriaEntidadeRepository(unittest.TestCase):

    def test_queries_with_nolock_and_params(self):
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        repo = CategoriaEntidadeRepository(connection=mock_conn)

        # 1. listar_usuarios_ativos
        mock_cursor.fetchall.return_value = [("USR01", "Admin")]
        users = repo.listar_usuarios_ativos()
        self.assertEqual(len(users), 1)
        sql1 = mock_cursor.execute.call_args[0][0]
        self.assertIn("WITH (NOLOCK)", sql1)
        self.assertIn("usuario", sql1)

        # 2. listar_grupos
        mock_cursor.fetchall.return_value = [("GRP01", "Diretoria")]
        grupos = repo.listar_grupos()
        self.assertEqual(len(grupos), 1)
        sql2 = mock_cursor.execute.call_args[0][0]
        self.assertIn("WITH (NOLOCK)", sql2)
        self.assertIn("grp_usuario", sql2)

        # 3. listar_categorias_usuario
        mock_cursor.description = [("codigo_categoria",), ("descricao",), ("total_entidades",), ("vinculada",)]
        mock_cursor.fetchall.return_value = [("01", "Cat 1", 5, 1)]
        repo.listar_categorias_usuario("USR01")
        sql3 = mock_cursor.execute.call_args[0][0]
        args3 = mock_cursor.execute.call_args[0][1]
        self.assertIn("WITH (NOLOCK)", sql3)
        self.assertEqual(args3, ["USR01"])

        # 4. vincular_categoria_usuario
        mock_cursor.fetchone.return_value = (0,)
        repo.vincular_categoria_usuario("USR01", "CAT01")
        self.assertEqual(mock_cursor.execute.call_count, 5)
        mock_conn.commit.assert_called()


class TestCategoriasViewHeadless(unittest.TestCase):

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
            cls.root.destroy()

    def test_view_instantiation_headless(self):
        if not self.root:
            self.skipTest("Ambiente sem display/Tk")

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn.cursor.return_value = mock_cursor

        view = CategoriasEntidadeView(self.root, connection=mock_conn)
        self.assertIsNotNone(view)
        self.assertEqual(view.var_modo.get(), "Usuario")
        view.destroy()


if __name__ == "__main__":
    unittest.main()
