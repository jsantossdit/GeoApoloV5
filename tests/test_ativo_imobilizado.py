"""
Testes automatizados para o módulo de Ativo Imobilizado e Depreciação.
Execução headless e desacoplada.
"""

import os
import sys
import unittest
import tkinter as tk
from datetime import date
from unittest.mock import MagicMock, patch

PASTA_RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PASTA_RAIZ not in sys.path:
    sys.path.insert(0, PASTA_RAIZ)

from ativo_imobilizado.models import (
    AtivoImobilizadoDTO,
    CalculoDepreciacaoDTO,
    LookupItemDTO,
    ResultadoOperacaoAtivo,
)
from ativo_imobilizado.service import AtivoImobilizadoService
from ativo_imobilizado.repository import AtivoImobilizadoRepository
from ativo_imobilizado.view import AtivoImobilizadoView


class TestAtivoImobilizadoService(unittest.TestCase):

    def setUp(self):
        self.mock_repo = MagicMock()
        self.service = AtivoImobilizadoService(self.mock_repo)

    def test_calcular_depreciacao_valida(self):
        calc = self.service.calcular_depreciacao(
            data_aquisicao="01/01/2020",
            valor_compra=10000.0,
            taxa_depreciacao_anual=10.0,
            data_referencia="01/01/2024",
        )
        self.assertTrue(calc.valido)
        self.assertAlmostEqual(calc.anos_em_uso, 4.0, delta=0.05)
        self.assertEqual(calc.depreciacao_anual, 1000.0)
        self.assertAlmostEqual(calc.depreciacao_acumulada, 4000.0, delta=50.0)
        self.assertAlmostEqual(calc.valor_atual, 6000.0, delta=50.0)

    def test_calcular_depreciacao_totalmente_depreciado(self):
        # 15 anos a 10% anuais -> 150% de depreciação -> valor atual deve ser 0.0, nunca negativo
        calc = self.service.calcular_depreciacao(
            data_aquisicao="01/01/2000",
            valor_compra=5000.0,
            taxa_depreciacao_anual=10.0,
            data_referencia="01/01/2020",
        )
        self.assertTrue(calc.valido)
        self.assertEqual(calc.valor_atual, 0.0)

    def test_calcular_depreciacao_validacoes(self):
        # Data inválida
        c1 = self.service.calcular_depreciacao("data_invalida", 1000, 10)
        self.assertFalse(c1.valido)

        # Valor compra zero ou negativo
        c2 = self.service.calcular_depreciacao("01/01/2020", 0, 10)
        self.assertFalse(c2.valido)

        # Taxa anual zero ou negativa
        c3 = self.service.calcular_depreciacao("01/01/2020", 1000, 0)
        self.assertFalse(c3.valido)

        # Data referência anterior à aquisição
        c4 = self.service.calcular_depreciacao("01/01/2024", 1000, 10, "01/01/2020")
        self.assertFalse(c4.valido)

    def test_validar_bem_campos_obrigatorios(self):
        dados_base = {
            "numero_do_bem": "100",
            "empcod": "001",
            "geocctrlcodestr": "CC01",
            "codigo_categoria_bem": "CAT01",
            "descricao_do_bem": "Servidor Dell PowerEdge",
            "codigo_classificacaoativoimobilizado": "INF01",
            "codigo_localizacao": "LOC01",
        }

        # Válido com todos os campos
        res = self.service.validar_bem(dados_base)
        self.assertTrue(res.sucesso)

        # Sem número do bem
        dados_sem_num = dict(dados_base, numero_do_bem="")
        self.assertFalse(self.service.validar_bem(dados_sem_num).sucesso)

        # Sem centro de custo
        dados_sem_cc = dict(dados_base, geocctrlcodestr="")
        self.assertFalse(self.service.validar_bem(dados_sem_cc).sucesso)

        # Sem categoria
        dados_sem_cat = dict(dados_base, codigo_categoria_bem="")
        self.assertFalse(self.service.validar_bem(dados_sem_cat).sucesso)

        # Sem descrição
        dados_sem_descr = dict(dados_base, descricao_do_bem="")
        self.assertFalse(self.service.validar_bem(dados_sem_descr).sucesso)

        # Sem localização
        dados_sem_loc = dict(dados_base, codigo_localizacao="")
        self.assertFalse(self.service.validar_bem(dados_sem_loc).sucesso)

    def test_salvar_bem(self):
        dados = {
            "numero_do_bem": "101",
            "empcod": "001",
            "geocctrlcodestr": "CC01",
            "codigo_categoria_bem": "CAT01",
            "descricao_do_bem": "Notebook Lenovo",
            "codigo_classificacaoativoimobilizado": "INF01",
            "codigo_localizacao": "LOC01",
            "data_aquisicao": "15/05/2023",
            "valor_compra": 4500.0,
            "taxa_depreciacao_anual": 20.0,
        }

        # Inclusão
        res_inc = self.service.salvar_bem(dados, modo_inclusao=True)
        self.assertTrue(res_inc.sucesso)
        self.mock_repo.inserir_bem.assert_called_once()

        # Alteração
        res_alt = self.service.salvar_bem(dados, modo_inclusao=False)
        self.assertTrue(res_alt.sucesso)
        self.mock_repo.atualizar_bem.assert_called_once()

    def test_excluir_bem(self):
        res = self.service.excluir_bem("101")
        self.assertTrue(res.sucesso)
        self.mock_repo.excluir_bem.assert_called_once_with("101")


class TestAtivoImobilizadoRepository(unittest.TestCase):

    def test_queries_with_nolock_and_params(self):
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        repo = AtivoImobilizadoRepository(connection=mock_conn)

        # 1. listar_bens
        mock_cursor.description = [
            ("numero_do_bem",), ("descricao_do_bem",), ("geocctrlcodestr",),
            ("geocctrlnome",), ("codigo_barrasativo",), ("codigo_categoria_bem",),
            ("categoria_bem",), ("codigo_classificacaoativoimobilizado",),
            ("classificacao",), ("codigo_localizacao",), ("localizacao",),
            ("codigo_func_responsavel",), ("nome_func_responsavel",),
            ("codigo_da_marca",), ("marca",), ("codigo_status_bem",),
            ("descricao_status_bem",), ("empcod",), ("data_aquisicao",),
            ("valor_compra",), ("taxa_depreciacao_anual",), ("data_ultima_revisao",),
            ("caminho_foto",), ("observacoes",),
        ]
        mock_cursor.fetchall.return_value = [
            (
                "1", "Servidor", "CC01", "TI", "PLA01", "CAT01", "Informática",
                "CL01", "Hardware", "LOC01", "CPD", "USR01", "Admin",
                "M01", "Dell", "ST01", "Ativo", "001", "01/01/2022",
                12000.0, 20.0, "01/01/2023", "", "Em produção"
            )
        ]
        bens = repo.listar_bens("001")
        self.assertEqual(len(bens), 1)
        sql1 = mock_cursor.execute.call_args[0][0]
        self.assertIn("WITH (NOLOCK)", sql1)
        self.assertIn("USER_geoapolo_satfi_ativoimobilizado", sql1)

        # 2. excluir_bem
        repo.excluir_bem("1")
        sql2 = mock_cursor.execute.call_args[0][0]
        self.assertIn("DELETE FROM USER_geoapolo_satfi_ativoimobilizado", sql2)
        mock_conn.commit.assert_called()

        # 3. listar_centros_controle
        mock_cursor.fetchall.return_value = [("CC01", "TI")]
        cctrls = repo.listar_centros_controle()
        self.assertEqual(len(cctrls), 1)
        sql3 = mock_cursor.execute.call_args[0][0]
        self.assertIn("WITH (NOLOCK)", sql3)
        self.assertIn("USER_geoapolo_centrocontrole", sql3)


class TestAtivoImobilizadoViewHeadless(unittest.TestCase):

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
        mock_cursor.fetchone.return_value = (1,)
        mock_conn.cursor.return_value = mock_cursor

        view = AtivoImobilizadoView(self.root, connection=mock_conn, empresa_codigo="001")
        self.assertIsNotNone(view)
        self.assertTrue(view._modo_inclusao)
        self.assertEqual(view.lbl_modo.cget("text"), "MODO: INCLUSÃO")
        view.destroy()


if __name__ == "__main__":
    unittest.main()
