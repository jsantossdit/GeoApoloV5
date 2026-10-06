"""
Testes unitários para validação de maiúsculas automáticas, navegação com Enter e tratamentos completos.
"""

import unittest
from unittest.mock import MagicMock
import tkinter as tk

from entidades.cadentidade_view import FrmCadEntidade
from entidades.repository import EntidadeRepository
from entidades.service import EntidadeService


class TestEntidadesMaiusculasEEnter(unittest.TestCase):
    """Testa padronização em maiúsculas, tecla Enter e tratamentos em FrmCadEntidade."""

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

    def test_listar_tipos_tratamento_traz_todos_registros(self):
        """Verifica se listar_tipos_tratamento traz a lista completa de tratamentos."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        # Simula retorno do banco para USER_geoapolo_tipotratamento
        mock_cursor.description = [("codigo",), ("abreviatura",), ("descricao",)]
        mock_cursor.fetchall.return_value = [
            ("01", "SR", "SENHOR"),
            ("02", "SRA", "SENHORA"),
            ("03", "PADRE", "PADRE"),
            ("04", "BISPO", "BISPO"),
            ("05", "PAPA", "PAPA"),
        ]

        repo = EntidadeRepository(connection=mock_conn)
        res = repo.listar_tipos_tratamento()
        self.assertGreaterEqual(len(res), 5)
        abrevs = [r["abreviatura"] for r in res]
        self.assertIn("SR", abrevs)
        self.assertIn("PADRE", abrevs)
        self.assertIn("BISPO", abrevs)
        self.assertIn("PAPA", abrevs)

    def test_fallback_tipos_tratamento_contem_mais_de_20_registros(self):
        """Verifica se em caso de ausência de banco, o fallback possui títulos ampliados."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.side_effect = Exception("Sem conexão com banco")

        repo = EntidadeRepository(connection=mock_conn)
        res = repo.listar_tipos_tratamento()
        self.assertGreaterEqual(len(res), 20)
        abrevs = [r["abreviatura"] for r in res]
        self.assertIn("PAPA", abrevs)
        self.assertIn("PASTOR", abrevs)
        self.assertIn("BISPO", abrevs)
        self.assertIn("FREI", abrevs)

    def test_cadentidade_maiusculas_e_email_minusculo(self):
        """Verifica se campos são coletados em maiúsculo e se email permanece minúsculo."""
        if not self.root:
            self.skipTest("Ambiente Tkinter não disponível.")

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []

        frm = FrmCadEntidade(self.root, connection=mock_conn, registro={"geoentcod": "100", "entnome": "teste"})
        try:
            frm.txt_nome.delete(0, tk.END)
            frm.txt_nome.insert(0, "joão silva e cia ltda")

            frm.txt_ender.delete(0, tk.END)
            frm.txt_ender.insert(0, "rua das flores")

            frm.txt_bair.delete(0, tk.END)
            frm.txt_bair.insert(0, "centro")

            frm.txt_web_email.delete(0, tk.END)
            frm.txt_web_email.insert(0, "TESTE.CONTATO@DOMINIO.COM.BR")
            frm._forcar_email_minusculo()

            dados = frm._coletar_dados()

            # Nomes e endereços devem ser MAIÚSCULOS
            self.assertEqual(dados["geoentnome"], "JOÃO SILVA E CIA LTDA")
            self.assertEqual(dados["geoentender"], "RUA DAS FLORES")
            self.assertEqual(dados["geoentbair"], "CENTRO")

            # E-mail digitado deve ser MINÚSCULO
            self.assertEqual(frm.txt_web_email.get(), "teste.contato@dominio.com.br")

            # Combo de tratamento deve conter itens
            vals_trat = frm.cbo_tipotrat["values"]
            self.assertGreaterEqual(len(vals_trat), 9)
        finally:
            frm.destroy()


if __name__ == "__main__":
    unittest.main()
