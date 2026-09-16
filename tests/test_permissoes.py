"""
Testes automatizados para o módulo de Clonagem de Permissões e Segurança.
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

from permissoes.models import (
    OpcoesClonagemDTO,
    UsuarioResumoDTO,
    RelatorioClonagemDTO,
    ResultadoClonagemDTO,
)
from permissoes.service import PermissoesService
from permissoes.repository import PermissoesRepository
from permissoes.view import ClonarPermissoesView


class TestPermissoesService(unittest.TestCase):

    def setUp(self):
        self.mock_repo = MagicMock()
        self.service = PermissoesService(self.mock_repo)

    def test_validar_clonagem(self):
        # 1. Origem vazia
        r1 = self.service.validar_clonagem("", "DEST")
        self.assertFalse(r1.sucesso)
        self.assertIn("origem", r1.mensagem.lower())

        # 2. Destino vazio
        r2 = self.service.validar_clonagem("ORIG", "")
        self.assertFalse(r2.sucesso)
        self.assertIn("destino", r2.mensagem.lower())

        # 3. Origem e destino iguais
        r3 = self.service.validar_clonagem("USER1", "user1")
        self.assertFalse(r3.sucesso)
        self.assertIn("mesmos", r3.mensagem.lower())

        # 4. Origem sem direitos
        self.mock_repo.usuario_tem_direitos.return_value = False
        r4 = self.service.validar_clonagem("ORIG", "DEST")
        self.assertFalse(r4.sucesso)
        self.assertIn("direitos", r4.mensagem.lower())

        # 5. Válido
        self.mock_repo.usuario_tem_direitos.return_value = True
        r5 = self.service.validar_clonagem("ORIG", "DEST")
        self.assertTrue(r5.sucesso)

    def test_clonar_permissoes_sucesso(self):
        self.mock_repo.usuario_tem_direitos.return_value = True
        self.mock_repo.clonar_direitos_sistema.return_value = 10
        self.mock_repo.clonar_relatorios.return_value = 5
        self.mock_repo.clonar_contas_financeiras.return_value = 2
        self.mock_repo.clonar_formularios.return_value = 8
        self.mock_repo.clonar_categorias_entidades.return_value = 15
        self.mock_repo.clonar_tipo_pagar_receber.return_value = 3
        self.mock_repo.clonar_grupos_usuario.return_value = 1
        self.mock_repo.clonar_favoritos.return_value = 4
        self.mock_repo.clonar_tour_usuario.return_value = 1
        self.mock_repo.clonar_empresas_filiais.return_value = 2

        res = self.service.clonar_permissoes("ORIG", "DEST")

        self.assertTrue(res.sucesso)
        self.assertEqual(res.total_itens, 51)
        self.assertEqual(res.relatorio.total_geral, 51)
        self.assertEqual(res.relatorio.total_direitos_sistema, 10)
        self.mock_repo.commit.assert_called_once()

    def test_clonar_permissoes_com_falha(self):
        self.mock_repo.usuario_tem_direitos.return_value = True
        self.mock_repo.clonar_direitos_sistema.side_effect = RuntimeError("Erro de banco")

        res = self.service.clonar_permissoes("ORIG", "DEST")

        self.assertFalse(res.sucesso)
        self.assertIn("Falha", res.mensagem)
        self.mock_repo.rollback.assert_called_once()

    def test_clonagem_modular_selecionada(self):
        self.mock_repo.usuario_tem_direitos.return_value = True
        self.mock_repo.clonar_direitos_sistema.return_value = 5

        # Clonar apenas direitos do sistema
        opcoes = OpcoesClonagemDTO(
            direitos_sistema=True,
            relatorios=False,
            contas_financeiras=False,
            formularios=False,
            categorias_entidades=False,
            tipo_pagar_receber=False,
            grupos_usuario=False,
            favoritos=False,
            tour_usuario=False,
            empresas_filiais=False,
        )

        res = self.service.clonar_permissoes("ORIG", "DEST", opcoes)

        self.assertTrue(res.sucesso)
        self.assertEqual(res.total_itens, 5)
        self.mock_repo.clonar_direitos_sistema.assert_called_once()
        self.mock_repo.clonar_relatorios.assert_not_called()
        self.mock_repo.clonar_contas_financeiras.assert_not_called()


class TestPermissoesRepository(unittest.TestCase):

    def test_queries_with_nolock_and_safe_inserts(self):
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        repo = PermissoesRepository(connection=mock_conn)

        # 1. listar_usuarios_ativos
        mock_cursor.fetchall.return_value = [("USR01", "Admin")]
        usuarios = repo.listar_usuarios_ativos()
        self.assertEqual(len(usuarios), 1)
        sql1 = mock_cursor.execute.call_args[0][0]
        self.assertIn("WITH (NOLOCK)", sql1)
        self.assertIn("usuario", sql1)

        # 2. clonar_direitos_sistema
        mock_cursor.rowcount = 4
        total_dir = repo.clonar_direitos_sistema("U1", "U2")
        self.assertEqual(total_dir, 4)
        sql2 = mock_cursor.execute.call_args[0][0]
        self.assertIn("WITH (NOLOCK)", sql2)
        self.assertIn("NOT EXISTS", sql2)
        self.assertIn("dir_usuario", sql2)

        # 3. clonar_categorias_entidades
        mock_cursor.rowcount = 3
        total_cat = repo.clonar_categorias_entidades("U1", "U2")
        self.assertEqual(total_cat, 6) # 3 categorias + 3 entidades
        sql3 = mock_cursor.execute.call_args[0][0]
        self.assertIn("WITH (NOLOCK)", sql3)
        self.assertIn("NOT EXISTS", sql3)


class TestClonarPermissoesViewHeadless(unittest.TestCase):

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
        mock_cursor.fetchall.return_value = [("U1", "Admin"), ("U2", "Operador")]
        mock_conn.cursor.return_value = mock_cursor

        view = ClonarPermissoesView(self.root, connection=mock_conn)
        self.assertIsNotNone(view)

        # Testar marcar/desmarcar todos
        self.assertTrue(view.chk_direitos.get())
        view._desmarcar_todos()
        self.assertFalse(view.chk_direitos.get())
        self.assertFalse(view.chk_relatorios.get())

        view._marcar_todos()
        self.assertTrue(view.chk_direitos.get())
        self.assertTrue(view.chk_relatorios.get())

        view.destroy()


if __name__ == "__main__":
    unittest.main()
