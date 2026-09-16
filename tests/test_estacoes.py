"""
Suite de Testes Automatizados para o Módulo de Estações de Trabalho e Inventário de TI.
Execução headless e desacoplada.
"""

import os
import sys
import unittest
import tkinter as tk
from datetime import datetime, timedelta
from unittest.mock import MagicMock

PASTA_RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PASTA_RAIZ not in sys.path:
    sys.path.insert(0, PASTA_RAIZ)

from estacoes.models import EstacaoDTO, HardwareDTO, SoftwareDTO, EstacaoFiltro, ResultadoOperacao
from estacoes.service import EstacoesService
from estacoes.repository import EstacoesRepository
from estacoes.view import EstacoesView


class TestEstacoesService(unittest.TestCase):
    """Testa regras de negócio e validações de estações, hardware e garantias."""

    def setUp(self):
        self.mock_repo = MagicMock()
        self.service = EstacoesService(self.mock_repo)

    def test_validar_ip(self):
        self.assertTrue(self.service.validar_ip("192.168.0.1"))
        self.assertTrue(self.service.validar_ip("10.1.1.250"))
        self.assertTrue(self.service.validar_ip(""))  # Opcional
        self.assertFalse(self.service.validar_ip("999.999.999.999"))
        self.assertFalse(self.service.validar_ip("192.168.1"))
        self.assertFalse(self.service.validar_ip("abc.def.ghi.jkl"))

    def test_validar_estacao_campos_obrigatorios(self):
        # Sem código
        valido, msg = self.service.validar_estacao({"descricao": "DESKTOP ADM"})
        self.assertFalse(valido)
        self.assertIn("código", msg.lower())

        # Sem descrição
        valido, msg = self.service.validar_estacao({"codigo_estacao": "EST001"})
        self.assertFalse(valido)
        self.assertIn("descrição", msg.lower())

        # IP inválido
        valido, msg = self.service.validar_estacao({
            "codigo_estacao": "EST001",
            "descricao": "DESKTOP ADM",
            "enderecoip": "invalido",
        })
        self.assertFalse(valido)
        self.assertIn("ip", msg.lower())

        # Válido
        valido, msg = self.service.validar_estacao({
            "codigo_estacao": "EST001",
            "descricao": "DESKTOP ADM",
            "enderecoip": "192.168.1.50",
        })
        self.assertTrue(valido)

    def test_validar_hardware(self):
        # Sem código
        valido, msg = self.service.validar_hardware({"descricao": "MONITOR 24"})
        self.assertFalse(valido)

        # Sem estação vinculada
        valido, msg = self.service.validar_hardware({
            "codigo_hardware": "H001",
            "descricao": "MONITOR 24",
        })
        self.assertFalse(valido)
        self.assertIn("vinculado", msg.lower())

        # Valor negativo
        valido, msg = self.service.validar_hardware({
            "codigo_hardware": "H001",
            "descricao": "MONITOR 24",
            "codigo_estacao": "EST001",
            "valor": -50.0,
        })
        self.assertFalse(valido)

        # Válido
        valido, msg = self.service.validar_hardware({
            "codigo_hardware": "H001",
            "descricao": "MONITOR 24 DELL",
            "codigo_estacao": "EST001",
            "valor": 850.0,
        })
        self.assertTrue(valido)

    def test_calcular_dias_garantia_restante(self):
        hoje = datetime.now()
        # Comprado há 30 dias com garantia de 365 dias -> ~335 dias restantes
        compra_recente = (hoje - timedelta(days=30)).strftime("%d/%m/%Y")
        dias = self.service.calcular_dias_garantia_restante(compra_recente, 365)
        self.assertGreater(dias, 300)

        # Comprado há 400 dias com garantia de 365 dias -> garantia expirada (< 0)
        compra_antiga = (hoje - timedelta(days=400)).strftime("%d/%m/%Y")
        dias_exp = self.service.calcular_dias_garantia_restante(compra_antiga, 365)
        self.assertLess(dias_exp, 0)


class TestEstacoesRepository(unittest.TestCase):
    """Testa as consultas e hints WITH (NOLOCK) do repositório."""

    def test_queries_with_nolock(self):
        mock_cursor = MagicMock()
        mock_cursor.description = [("codigo_estacao",), ("descricao",)]
        mock_cursor.fetchall.return_value = [("001", "ESTACAO TESTE")]

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        repo = EstacoesRepository(connection=mock_conn)

        # 1. listar_estacoes
        repo.listar_estacoes(EstacaoFiltro())
        sql = mock_cursor.execute.call_args[0][0]
        self.assertIn("WITH (NOLOCK)", sql)
        self.assertIn("USER_geoapolo_satfi_estacao", sql)

        # 2. listar_hardware
        repo.listar_hardware("001")
        sql_h = mock_cursor.execute.call_args[0][0]
        self.assertIn("WITH (NOLOCK)", sql_h)
        self.assertIn("USER_geoapolo_satfi_hardware", sql_h)

        # 3. listar_software
        repo.listar_software("001")
        sql_s = mock_cursor.execute.call_args[0][0]
        self.assertIn("WITH (NOLOCK)", sql_s)
        self.assertIn("USER_geoapolo_satfi_software", sql_s)


class TestEstacoesViewHeadless(unittest.TestCase):
    """Testa instanciação gráfica sem travar loop."""

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

        self.mock_cursor = MagicMock()
        self.mock_cursor.description = [
            ("codigo_estacao",),
            ("descricao",),
            ("nome_departamento",),
            ("tag_servico",),
            ("enderecoip",),
            ("modelo_estacao",),
            ("usuario_responsavel",),
            ("data_cadastro",),
        ]
        self.mock_cursor.fetchall.return_value = [
            ("001", "DESKTOP TI 01", "TECNOLOGIA", "TAG123", "192.168.1.10", "OPTIPLEX", "JULIO", "14/09/2026")
        ]
        self.mock_conn = MagicMock()
        self.mock_conn.cursor.return_value = self.mock_cursor

    def tearDown(self):
        try:
            self.root.destroy()
        except Exception:
            pass

    def test_estacoes_view_instantiation(self):
        view = EstacoesView(parent=self.root, connection=self.mock_conn)
        self.assertIsNotNone(view.tree_estacoes)
        self.assertIsNotNone(view.tree_hardware)
        self.assertIsNotNone(view.tree_software)
        self.assertIsNotNone(view.tree_usuarios)
        self.assertIsNotNone(view.notebook)
        view.destroy()


if __name__ == "__main__":
    unittest.main()
