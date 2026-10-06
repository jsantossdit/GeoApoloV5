"""
Testes Unitários para o Módulo de Conciliação Vindi e Crédito Recorrente.
GeoApolo V5
"""

import unittest
import tkinter as tk
from unittest.mock import MagicMock, patch
from datetime import date
from vindi.models import (
    TransacaoVindiDTO,
    ResumoConciliacaoVindiDTO,
)
from vindi.repository import VindiRepository
from vindi.service import VindiService
from vindi.view import ConciliacaoVindiView
from vindi.dashboard_view import DashboardVindiView


class TestVindiModule(unittest.TestCase):

    def setUp(self):
        self.mock_repo = MagicMock(spec=VindiRepository)
        self.service = VindiService(self.mock_repo)

    def test_checar_integridade_sem_cpf(self):
        t = TransacaoVindiDTO(
            pedido_id="PED01",
            cpf_cnpj="",
            nome_cliente="Cliente Sem CPF",
            data_transacao=date(2025, 9, 1),
            valor_bruto=100.0,
            valor_tarifa=2.5,
            valor_liquido=97.5,
        )
        erros = self.service.checar_integridade(t)
        self.assertTrue(t.tem_erros)
        self.assertTrue(any("não informado" in e for e in erros))

    def test_checar_integridade_cpf_nao_localizado_menciona_alvo(self):
        t = TransacaoVindiDTO(
            pedido_id="PED02",
            cpf_cnpj="12345678901",
            nome_cliente="Cliente Nao Cadastrado",
            data_transacao=date(2025, 9, 1),
            valor_bruto=100.0,
            valor_tarifa=2.5,
            valor_liquido=97.5,
        )
        self.mock_repo.buscar_entidade_por_cpf.return_value = None
        erros = self.service.checar_integridade(t)
        self.assertTrue(t.tem_erros)
        self.assertTrue(any("Alvo" in e for e in erros))
        self.assertFalse(any("Apolo" in e for e in erros))

    def test_checar_integridade_valida(self):
        t = TransacaoVindiDTO(
            pedido_id="PED03",
            cpf_cnpj="12345678901",
            nome_cliente="Doador Fiel",
            data_transacao=date(2025, 9, 1),
            valor_bruto=150.0,
            valor_tarifa=3.5,
            valor_liquido=146.5,
            status_vindi="Paga",
        )
        self.mock_repo.buscar_entidade_por_cpf.return_value = ("ENT010", "Doador Fiel")
        self.mock_repo.buscar_categorias_entidade.return_value = ["02.001"]

        erros = self.service.checar_integridade(t)
        self.assertFalse(t.tem_erros)
        self.assertEqual(len(erros), 0)
        self.assertEqual(t.ent_cod, "ENT010")
        self.assertEqual(t.categoria_cod, "02.001")

    def test_checar_integridade_status_active(self):
        t = TransacaoVindiDTO(
            pedido_id="PED04",
            cpf_cnpj="12345678901",
            nome_cliente="Doador Recorrente Vindi",
            data_transacao=date(2025, 9, 1),
            valor_bruto=50.0,
            valor_tarifa=1.5,
            valor_liquido=48.5,
            status_vindi="active",
        )
        self.mock_repo.buscar_entidade_por_cpf.return_value = ("ENT020", "Doador Recorrente")
        self.mock_repo.buscar_categorias_entidade.return_value = ["03.001"]

        erros = self.service.checar_integridade(t)
        self.assertFalse(t.tem_erros)
        self.assertEqual(len(erros), 0)

    def test_checar_integridade_multiplas_categorias_validas(self):
        """Entidade com mais de uma categoria válida (02.001 e 03.004) não gera erro."""
        t = TransacaoVindiDTO(
            pedido_id="PED05",
            cpf_cnpj="12345678901",
            nome_cliente="Doador Multiplas Categorias",
            data_transacao=date(2025, 9, 1),
            valor_bruto=100.0,
            valor_tarifa=2.5,
            valor_liquido=97.5,
            status_vindi="Paga",
        )
        self.mock_repo.buscar_entidade_por_cpf.return_value = ("ENT030", "Doador Multiplas")
        self.mock_repo.buscar_categorias_entidade.return_value = ["02.001.0001", "03.004.0010"]

        erros = self.service.checar_integridade(t)
        self.assertFalse(t.tem_erros)
        self.assertEqual(len(erros), 0)
        self.assertIn("02.001.0001", t.categoria_cod)
        self.assertIn("03.004.0010", t.categoria_cod)

    def test_checar_integridade_todas_substrings_arrecadacao(self):
        """Valida que todas as 8 substrings dos subgrupos de arrecadação são aceitas."""
        substrings = ["02.001", "02.002", "03.001", "03.002", "03.003", "03.004", "03.005", "03.006"]
        for sub in substrings:
            self.assertTrue(self.service.validar_categoria_arrecadacao(f"CATEG.{sub}.001"))
            self.assertTrue(self.service.validar_categoria_arrecadacao(sub))

    def test_checar_integridade_nenhuma_categoria_arrecadacao(self):
        """Entidade sem nenhuma categoria do setor de arrecadação deve gerar inconsistência."""
        t = TransacaoVindiDTO(
            pedido_id="PED06",
            cpf_cnpj="12345678901",
            nome_cliente="Doador Sem Categ Arrecadacao",
            data_transacao=date(2025, 9, 1),
            valor_bruto=80.0,
            valor_tarifa=2.0,
            valor_liquido=78.0,
            status_vindi="Paga",
        )
        self.mock_repo.buscar_entidade_por_cpf.return_value = ("ENT040", "Doador Invalido")
        self.mock_repo.buscar_categorias_entidade.return_value = ["01.001.0005"]  # Somente outro grupo (não arrecadação)

        erros = self.service.checar_integridade(t)
        self.assertTrue(t.tem_erros)
        self.assertTrue(any("setor de arrecadação" in e for e in erros))

    def test_checar_integridade_mista_com_outros_grupos_permitida(self):
        """Entidade com categoria de arrecadação E de outros grupos é PERMITIDA sem erro."""
        t = TransacaoVindiDTO(
            pedido_id="PED07",
            cpf_cnpj="12345678901",
            nome_cliente="Doador e Fornecedor",
            data_transacao=date(2025, 9, 1),
            valor_bruto=80.0,
            valor_tarifa=2.0,
            valor_liquido=78.0,
            status_vindi="Paga",
        )
        self.mock_repo.buscar_entidade_por_cpf.return_value = ("ENT050", "Doador Misto")
        # 02.001 (arrecadação) + 99.001 (outro grupo qualquer): permitido!
        self.mock_repo.buscar_categorias_entidade.return_value = ["02.001.0001", "99.001.0001"]

        erros = self.service.checar_integridade(t)
        self.assertFalse(t.tem_erros)
        self.assertEqual(len(erros), 0)
        self.assertIn("02.001.0001", t.categoria_cod)

    def test_checar_integridade_duplicidade_no_mesmo_subgrupo(self):
        """Entidade com mais de uma categoria do MESMO subgrupo de arrecadação deve gerar inconsistência."""
        t = TransacaoVindiDTO(
            pedido_id="PED08",
            cpf_cnpj="12345678901",
            nome_cliente="Doador Duplicado Mesmo Subgrupo",
            data_transacao=date(2025, 9, 1),
            valor_bruto=120.0,
            valor_tarifa=3.0,
            valor_liquido=117.0,
            status_vindi="Paga",
        )
        self.mock_repo.buscar_entidade_por_cpf.return_value = ("ENT060", "Doador Duplo")
        # Duas categorias do mesmo subgrupo 02.001: PROIBIDO!
        self.mock_repo.buscar_categorias_entidade.return_value = ["02.001.0001", "02.001.0002", "03.003.0001"]

        erros = self.service.checar_integridade(t)
        self.assertTrue(t.tem_erros)
        self.assertTrue(any("mais de uma categoria no mesmo subgrupo" in e for e in erros))
        self.assertTrue(any("02.001" in e for e in erros))

    def test_filtrar_sem_consistencia_e_depois_checar(self):
        t1 = TransacaoVindiDTO("P1", "123", "Cli 1", date(2025, 9, 1), 100.0, 2.0, 98.0, "Paga", False)
        t2 = TransacaoVindiDTO("P2", "456", "Cli 2", date(2025, 9, 2), 200.0, 4.0, 196.0, "Paga", True)

        self.mock_repo.listar_transacoes.return_value = [t1, t2]

        # 1. Filtro sem checagem de integridade
        trans, resumo = self.service.filtrar_transacoes(date(2025, 9, 1), date(2025, 9, 30))
        self.assertEqual(len(trans), 2)
        self.assertEqual(resumo.total_com_inconsistencias, 0)
        self.assertEqual(len(t1.erros), 0)
        self.assertEqual(len(t2.erros), 0)

        # 2. Executa checagem de integridade separadamente
        self.mock_repo.buscar_entidade_por_cpf.return_value = None  # Gera erro de CPF
        resumo_pos = self.service.executar_checagem_integridade(trans)
        self.assertEqual(resumo_pos.total_com_inconsistencias, 2)
        self.assertTrue(t1.tem_erros)
        self.assertTrue(t2.tem_erros)

    def test_integrar_transacao(self):
        self.mock_repo.marcar_transacao_integrada.return_value = True
        self.assertTrue(self.service.integrar_transacao("PED100"))
        self.mock_repo.marcar_transacao_integrada.assert_called_once_with("PED100")


class TestConciliacaoVindiViewHeadless(unittest.TestCase):
    """Testes de inicialização headless da interface de conciliação Vindi."""

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.mock_service = MagicMock(spec=VindiService)
        self.view = ConciliacaoVindiView(self.root, service=self.mock_service)

    def tearDown(self):
        self.view.window.destroy()
        self.root.destroy()

    def test_formato_data_padrao(self):
        dt_ini = self.view.txt_dt_ini.get()
        dt_fim = self.view.txt_dt_fim.get()
        self.assertEqual(len(dt_ini), 10)
        self.assertEqual(len(dt_fim), 10)
        self.assertIn("/", dt_ini)
        self.assertIn("/", dt_fim)

        parsed_ini = self.view._parse_data(dt_ini)
        self.assertIsInstance(parsed_ini, date)

    def test_parse_data_flexivel(self):
        self.assertEqual(self.view._parse_data("18/09/2026"), date(2026, 9, 18))
        self.assertEqual(self.view._parse_data("2026-09-18"), date(2026, 9, 18))
        self.assertEqual(self.view._parse_data("18-09-2026"), date(2026, 9, 18))

    def test_validacao_datas_vazias_exibe_erro_e_foco_data_inicial(self):
        with patch("tkinter.messagebox.showerror") as mock_err:
            # Caso 1: Data inicial vazia
            self.view.txt_dt_ini.delete(0, tk.END)
            self.view._executar_filtro()
            mock_err.assert_called()
            self.assertIn("Data Inicial", mock_err.call_args[0][1])

            # Caso 2: Data final vazia
            self.view.txt_dt_ini.insert(0, "01/09/2026")
            self.view.txt_dt_fim.delete(0, tk.END)
            self.view._executar_filtro()
            mock_err.assert_called()
            self.assertIn("Data Final", mock_err.call_args[0][1])

    def test_checagem_integridade_marca_todas_linhas(self):
        t1 = TransacaoVindiDTO("P10", "111", "Doador 1", date(2026, 9, 1), 100.0, 2.0, 98.0, "Paga", False)
        t2 = TransacaoVindiDTO("P20", "222", "Doador 2", date(2026, 9, 2), 200.0, 4.0, 196.0, "Paga", False)
        resumo_filtro = ResumoConciliacaoVindiDTO(2, 300.0, 6.0, 294.0, 0, 0)

        self.mock_service.filtrar_transacoes.return_value = ([t1, t2], resumo_filtro)
        self.view._executar_filtro()

        # Antes da checagem: linhas devem conter "Não checado"
        item1 = self.view.tree.item("P10")["values"]
        self.assertIn("Não checado", item1[9])

        # Executar checagem de integridade
        t1.erros = []
        t2.erros = ["CPF não encontrado no Alvo"]
        resumo_check = ResumoConciliacaoVindiDTO(2, 300.0, 6.0, 294.0, 0, 1)
        self.mock_service.executar_checagem_integridade.return_value = resumo_check

        with patch("tkinter.messagebox.showinfo"):
            self.view._executar_checagem_integridade()

        # Depois da checagem: todas as linhas atualizadas
        item1_pos = self.view.tree.item("P10")["values"]
        item2_pos = self.view.tree.item("P20")["values"]
        self.assertIn("OK", item1_pos[9])
        self.assertIn("1 inconsistência", item2_pos[9])

    def test_botao_integracao_removido(self):
        # O botão de integração prematura foi removido conforme regra de negócio
        self.assertFalse(hasattr(self.view, "btn_integrar"))

    def test_dashboard_abertura(self):
        with patch.object(self.mock_service, "filtrar_transacoes", return_value=([], ResumoConciliacaoVindiDTO())):
            dash = DashboardVindiView(self.view.window, service=self.mock_service)
            self.assertIsNotNone(dash.window)
            self.assertIn("Dashboard", dash.window.title())
            dash.window.destroy()


if __name__ == "__main__":
    unittest.main()
