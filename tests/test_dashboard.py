"""
Testes Unitários para o Módulo de Dashboard de Doações & Inteligência Analítica (Empresa 1.01).
Cobre integração com Dashboard-menuprincipal.sql, USERPerfilFinanceiro_de_Doador,
status de doadores (Novos, Recorrentes, Retorno), formas de contribuição e motor de IA.
GeoApolo V5
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

from dashboard.models import (
    FiltroDashboardDTO,
    DoadorPerfilDTO,
    StatusDoadorMetricaDTO,
    DioceseMetricaDTO,
    TipoCobrancaMetricaDTO,
    EvolucaoMesDTO,
    EvolucaoAnoDTO,
    HistoricoAnoMetodoDTO,
    InsightIADTO,
    ResumoDoacoesDTO,
)
from dashboard.repository import DashboardRepository
from dashboard.service import DashboardService
from dashboard.view import DashboardDoacoesFrame, DashboardDoacoesView, abrir_dashboard_doacoes
from geoalvo import atualizar_painel_principal


class TestDashboardModels(unittest.TestCase):

    def test_filtro_dashboard_defaults(self):
        filtro = FiltroDashboardDTO()
        self.assertEqual(filtro.empresa, "1.01")
        self.assertEqual(filtro.ano, 2026)
        self.assertEqual(filtro.mes, 9)
        self.assertEqual(filtro.status_filtro, "TODOS")
        self.assertEqual(filtro.forma_filtro, "TODAS")
        self.assertIn("02.001", filtro.subgrupos)
        self.assertIn("03.005", filtro.subgrupos)

    def test_doador_perfil_dto(self):
        d = DoadorPerfilDTO(
            entcod="0000012",
            entnome="NATALIA SUELI",
            uf="RJ",
            codigo_dio="46",
            diocese="Arquidiocese de Niterói",
            categcodestr="03.001.001",
            categnome="SVE-DOADOR ATIVO",
            tipocobcod="0000011",
            forma_contribuicao="VND",
            data_doacao_mescorrente=date(2026, 9, 21),
            valor_doado=23.66,
            data_doacao_anterior=date(2026, 8, 21),
            valor_doado_mesanterior=23.66,
            docfinchv="1671237",
            status_doador="Doador Recorrente"
        )
        self.assertEqual(d.entcod, "0000012")
        self.assertEqual(d.forma_contribuicao, "VND")
        self.assertEqual(d.status_doador, "Doador Recorrente")
        self.assertEqual(d.valor_doado, 23.66)

    def test_status_doador_metrica_dto(self):
        s = StatusDoadorMetricaDTO("Doador Recorrente", 1306, 42370.18, 80.0, 32.44, "#10B981")
        self.assertEqual(s.status, "Doador Recorrente")
        self.assertEqual(s.qtd, 1306)
        self.assertEqual(s.percentual, 80.0)

    def test_diocese_metrica_dto(self):
        dio = DioceseMetricaDTO("46", "ARQUIDIOCESE DO RIO DE JANEIRO", "RJ", 74, 2885.97, 5.4, 39.00)
        self.assertEqual(dio.codigo, "46")
        self.assertEqual(dio.uf, "RJ")
        self.assertEqual(dio.qtd, 74)

    def test_resumo_doacoes_dto_defaults(self):
        r = ResumoDoacoesDTO()
        self.assertEqual(r.total_arrecadado, 0.0)
        self.assertEqual(r.qtd_doacoes, 0)
        self.assertEqual(r.status_metricas, [])
        self.assertEqual(r.doadores, [])


class TestDashboardRepository(unittest.TestCase):

    def setUp(self):
        self.repo = DashboardRepository()

    def test_montar_clausula_subgrupos(self):
        subgrupos = ("02.001", "02.002", "03.001")
        clausula = self.repo._montar_clausula_subgrupos(subgrupos)
        self.assertEqual(
            clausula,
            "(upfd.categcodestr LIKE '02.001%' OR upfd.categcodestr LIKE '02.002%' OR upfd.categcodestr LIKE '03.001%')"
        )
        self.assertEqual(
            self.repo._montar_clausula_subgrupos(("02.001",), alias="u"),
            "(u.categcodestr LIKE '02.001%')"
        )
        self.assertEqual(self.repo._montar_clausula_subgrupos([]), "(1=1)")

    def test_dados_fallback_completos(self):
        filtro = FiltroDashboardDTO(empresa="1.01", ano=2026, mes=9, tipo_periodo="MES")
        resumo = self.repo._gerar_dados_fallback(filtro)

        self.assertGreater(resumo.total_arrecadado, 40000.0)
        self.assertGreater(resumo.qtd_doacoes, 1000)
        self.assertEqual(len(resumo.status_metricas), 3)
        self.assertGreater(len(resumo.doadores), 5)
        self.assertGreater(len(resumo.evolucao_anos), 5)
        self.assertGreater(len(resumo.evolucao_meses), 5)

        # Verifica identificadores de status
        status_nomes = [s.status for s in resumo.status_metricas]
        self.assertIn("Doador Recorrente", status_nomes)
        self.assertIn("Retorno Doador", status_nomes)
        self.assertIn("Novo Doador", status_nomes)

    def test_dados_fallback_ultimos_10_dias(self):
        filtro = FiltroDashboardDTO(empresa="1.01", tipo_periodo="10_DIAS")
        resumo = self.repo._gerar_dados_fallback(filtro)

        self.assertEqual(resumo.tipo_periodo, "10_DIAS")
        self.assertIn("Últimos 10 Dias", resumo.periodo_descricao)
        self.assertGreater(resumo.total_arrecadado, 10000.0)
        self.assertEqual(resumo.qtd_doacoes, 534)
        self.assertEqual(resumo.qtd_doadores, 520)

    def test_obter_dados_perfil_doadores_mock(self):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (
                "0000012", "NATALIA LEITAO", "RJ", "46", "Diocese Niteroi",
                "03.001.001", "SVE-DOADOR ATIVO", "0000011", "VND",
                date(2026, 9, 21), 25.0, date(2026, 8, 21), 25.0,
                "1671237", "Doador Recorrente"
            ),
            (
                "0000034", "CELINA SILVA", "RJ", "53", "Diocese Volta Redonda",
                "03.001.000", "SVE-DOADOR", "0000020", "BOL",
                date(2026, 9, 13), 30.0, date(2026, 7, 16), 30.0,
                "1637742", "Retorno Doador"
            ),
            (
                "0000088", "MARIA APARECIDA", "SP", "240", "Arquidiocese SP",
                "03.001.001", "SVE-NOVO", "0000025", "PIX",
                date(2026, 9, 5), 50.0, None, 0.0,
                "1672301", "Novo Doador"
            ),
        ]
        mock_conn.cursor.return_value = mock_cursor

        repo = DashboardRepository(connection=mock_conn)
        filtro = FiltroDashboardDTO(empresa="1.01", ano=2026, mes=9)
        resumo = repo._obter_dados_perfil_doadores(mock_conn, filtro)

        self.assertEqual(resumo.qtd_doacoes, 3)
        self.assertEqual(resumo.total_arrecadado, 105.0)
        self.assertEqual(resumo.qtd_recorrentes, 1)
        self.assertEqual(resumo.qtd_retorno, 1)
        self.assertEqual(resumo.qtd_novos, 1)
        self.assertEqual(len(resumo.doadores), 3)

    def test_sincronizar_perfil_mes_mock(self):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        repo = DashboardRepository(connection=mock_conn)
        sucesso = repo.sincronizar_perfil_mes(ano=2026, mes=9, empcod="1.01")
        self.assertTrue(sucesso)
        self.assertEqual(mock_cursor.execute.call_count, 2)
        mock_conn.commit.assert_called_once()


class TestDashboardService(unittest.TestCase):

    def setUp(self):
        self.mock_repo = MagicMock(spec=DashboardRepository)
        self.mock_repo.carregar_dados_completos.return_value = ResumoDoacoesDTO(qtd_doacoes=10, total_arrecadado=100.0, doadores=[])
        self.service = DashboardService(repository=self.mock_repo)

    def test_filtrar_doadores_por_status(self):
        d1 = DoadorPerfilDTO("1", "D1", "SP", "1", "D1", "03", "C1", "1", "BOL", None, 10.0, None, 0.0, "1", "Novo Doador")
        d2 = DoadorPerfilDTO("2", "D2", "RJ", "2", "D2", "03", "C2", "2", "DEB", None, 20.0, None, 0.0, "2", "Doador Recorrente")
        d3 = DoadorPerfilDTO("3", "D3", "MG", "3", "D3", "03", "C3", "3", "VND", None, 30.0, None, 0.0, "3", "Retorno Doador")
        lista = [d1, d2, d3]

        filtrados = self.service._filtrar_doadores(lista, status_filtro="Novo Doador")
        self.assertEqual(len(filtrados), 1)
        self.assertEqual(filtrados[0].entcod, "1")

        filtrados_rec = self.service._filtrar_doadores(lista, status_filtro="Doador Recorrente")
        self.assertEqual(len(filtrados_rec), 1)
        self.assertEqual(filtrados_rec[0].entcod, "2")

    def test_filtrar_doadores_por_forma_e_busca(self):
        d1 = DoadorPerfilDTO("101", "CARLOS EDUARDO", "SP", "1", "Diocese Santos", "03", "C1", "1", "BOL", None, 10.0, None, 0.0, "1", "Recorrente")
        d2 = DoadorPerfilDTO("102", "MARIA EDUARDA", "RJ", "2", "Diocese Rio", "03", "C2", "2", "PIX", None, 20.0, None, 0.0, "2", "Recorrente")
        lista = [d1, d2]

        # Filtro por forma
        self.assertEqual(len(self.service._filtrar_doadores(lista, forma_filtro="PIX")), 1)

        # Filtro por termo de busca
        self.assertEqual(len(self.service._filtrar_doadores(lista, termo_busca="santos")), 1)
        self.assertEqual(len(self.service._filtrar_doadores(lista, termo_busca="eduarda")), 1)
        self.assertEqual(len(self.service._filtrar_doadores(lista, termo_busca="101")), 1)

    def test_gerar_insights_sem_dados(self):
        resumo = ResumoDoacoesDTO()
        insights = self.service.gerar_insights_ia(resumo)
        self.assertEqual(len(insights), 1)
        self.assertEqual(insights[0].tipo, "ALERTA")

    def test_gerar_insights_com_perfil_completo(self):
        resumo = ResumoDoacoesDTO(
            ano=2026,
            mes=9,
            total_arrecadado=50000.0,
            total_mes_anterior=45000.0,
            variacao_mes_anterior_pct=11.1,
            qtd_doacoes=1500,
            qtd_doadores=1480,
            ticket_medio=33.33,
            qtd_recorrentes=1200,
            total_recorrentes=40000.0,
            qtd_retorno=250,
            total_retorno=8000.0,
            qtd_novos=50,
            total_novos=2000.0,
            tipos_cobranca=[
                TipoCobrancaMetricaDTO("DEB", "DEB - Débito em Conta", 600, 20000.0, 40.0, 33.33, 1),
            ],
            top_dioceses=[
                DioceseMetricaDTO("46", "ARQUIDIOCESE DO RIO DE JANEIRO", "RJ", 70, 2800.0, 5.6, 40.0),
            ],
            doadores=[DoadorPerfilDTO("1", "TESTE", "RJ", "46", "Rio", "03", "CAT", "1", "DEB", None, 10.0, None, 0.0, "1", "Doador Recorrente")],
        )

        insights = self.service.gerar_insights_ia(resumo)
        tipos = [i.tipo for i in insights]
        self.assertIn("FIDELIZACAO", tipos)
        self.assertIn("OPORTUNIDADE", tipos)
        self.assertIn("DESTAQUE", tipos)
        self.assertIn("TENDENCIA", tipos)
        self.assertIn("FORECAST", tipos)

    def test_cache_resumo_e_limpeza(self):
        filtro = FiltroDashboardDTO(ano=2026, mes=9)
        resumo1 = self.service.obter_dashboard(filtro)
        self.assertEqual(self.mock_repo.carregar_dados_completos.call_count, 1)

        # Segunda chamada para o mesmo período deve utilizar o cache
        resumo2 = self.service.obter_dashboard(filtro)
        self.assertEqual(self.mock_repo.carregar_dados_completos.call_count, 1)

        # Forçar atualização deve invalidar o cache e chamar repositório novamente
        resumo3 = self.service.obter_dashboard(filtro, forcar_atualizacao=True)
        self.assertEqual(self.mock_repo.carregar_dados_completos.call_count, 2)

        # Limpar cache
        self.service.limpar_cache()
        self.assertEqual(len(self.service._cache_resumo), 0)


class TestDashboardViewHeadless(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        # Mock do repository para respostas instantâneas em ambiente de teste
        self.mock_repo = MagicMock(spec=DashboardRepository)
        filtro_padrao = FiltroDashboardDTO()
        self.mock_repo.carregar_dados_completos.return_value = DashboardRepository()._gerar_dados_fallback(filtro_padrao)
        self.service = DashboardService(repository=self.mock_repo)

    def tearDown(self):
        try:
            self.root.destroy()
        except Exception:
            pass

    def test_instanciacao_dashboard_frame(self):
        frame = DashboardDoacoesFrame(self.root, service=self.service, empresa="1.01", assincrono_inicial=False)
        self.assertIsNotNone(frame.cbo_ano)
        self.assertIsNotNone(frame.cbo_mes)
        self.assertIsNotNone(frame.cbo_status)
        self.assertIsNotNone(frame.cbo_forma)
        self.assertIsNotNone(frame.notebook)

        # Aba 1
        self.assertIsNotNone(frame.canvas_status)
        self.assertIsNotNone(frame.canvas_formas)
        self.assertIsNotNone(frame.tree_dioceses)

        # Aba 2
        self.assertIsNotNone(frame.tree_doadores)
        self.assertIsNotNone(frame.txt_busca)
        itens_doadores = frame.tree_doadores.get_children()
        self.assertGreater(len(itens_doadores), 0)

        # Aba 3
        self.assertIsNotNone(frame.tree_historico)
        self.assertIsNotNone(frame.canvas_evolucao_meses)

        # Testa controles de parâmetros dinâmicos
        self.assertIsNotNone(frame.cbo_tipo_periodo)
        self.assertIsNotNone(frame.txt_data_ini)
        self.assertIsNotNone(frame.txt_data_fim)
        self.assertIsNotNone(frame.btn_filtrar)
        self.assertIsNotNone(frame.gauge_overlay)

        # Testa troca dinâmica de período
        frame.cbo_tipo_periodo.set("Últimos 15 Dias")
        frame._on_tipo_periodo_changed()
        self.assertEqual(frame.txt_data_fim.get(), "20/09/2026")
        self.assertEqual(frame.txt_data_ini.get(), "05/09/2026")

        # Testa filtro por busca
        frame.txt_busca.insert(0, "NATALIA")
        frame._aplicar_filtros_tabela()
        itens_apos_busca = frame.tree_doadores.get_children()
        self.assertEqual(len(itens_apos_busca), 1)

        frame.destroy()

    def test_dashboard_toplevel_singleton(self):
        with patch("dashboard.view.DashboardService", return_value=self.service):
            top1 = DashboardDoacoesView(self.root, empresa="1.01")
            top2 = DashboardDoacoesView(self.root, empresa="1.01")
            self.assertIs(top1, top2)
            top1.destroy()
            self.assertIsNone(DashboardDoacoesView._instancia_ativa)

    def test_abrir_dashboard_helper(self):
        with patch("dashboard.view.DashboardService", return_value=self.service):
            janela = abrir_dashboard_doacoes(self.root, empresa="1.01")
            self.assertIsInstance(janela, DashboardDoacoesView)
            janela.destroy()

    def test_atualizar_painel_principal_empresa_1_01(self):
        self.root.empresa_ativa = "1.01"
        self.root.nome_empresa_ativa = "RCC BRASIL MATRIZ"
        self.root.main_frame = tk.Frame(self.root)
        self.root.main_frame.pack()

        with patch("dashboard.view.DashboardService", return_value=self.service):
            atualizar_painel_principal(self.root)
            # Painel sob demanda montado instantaneamente para não bloquear o login
            self.assertTrue(hasattr(self.root, "btn_abrir_dashboard"))
            self.assertTrue(hasattr(self.root, "btn_sincronizar_banco"))
            self.assertIn("RCC BRASIL MATRIZ", self.root.welcome_label.cget("text"))
            # Ao acionar o botão de ação, monta o Dashboard sob demanda
            self.root.btn_abrir_dashboard.invoke()
            self.assertTrue(hasattr(self.root, "dashboard_ativo"))
            self.assertIsInstance(self.root.dashboard_ativo, DashboardDoacoesFrame)

    def test_atualizar_painel_principal_outra_empresa(self):
        self.root.empresa_ativa = "02.01"
        self.root.nome_empresa_ativa = "EDITORA RCC"
        self.root.main_frame = tk.Frame(self.root)
        self.root.main_frame.pack()

        atualizar_painel_principal(self.root)
        self.assertTrue(hasattr(self.root, "welcome_label"))
        self.assertIn("EDITORA RCC", self.root.welcome_label.cget("text"))


class TestDashboardGauge(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        try:
            self.root.destroy()
        except Exception:
            pass

    def test_gauge_widget_progresso_e_reset(self):
        from dashboard.gauge import DashboardGaugeWidget
        gauge = DashboardGaugeWidget(self.root, width=200, height=120)
        self.assertEqual(gauge.percentual, 0.0)

        gauge.definir_progresso(50.0, "Carregando 50%...")
        self.assertEqual(gauge.percentual, 50.0)
        self.assertEqual(gauge.texto_status, "Carregando 50%...")

        gauge.definir_progresso(120.0)  # Deve limitar em 100%
        self.assertEqual(gauge.percentual, 100.0)

        gauge.resetar()
        self.assertEqual(gauge.percentual, 0.0)
        gauge.destroy()

    def test_gauge_overlay_exibir_e_ocultar(self):
        from dashboard.gauge import GaugeOverlay
        parent = tk.Frame(self.root)
        parent.pack()
        overlay = GaugeOverlay(parent, titulo="Testando Overlay...")
        overlay.exibir()
        overlay.atualizar(45.0, "Processando 45%...")
        self.assertEqual(overlay.gauge.percentual, 45.0)
        self.assertEqual(overlay.prog_bar["value"], 45.0)
        overlay.ocultar()
        overlay.destroy()


if __name__ == "__main__":
    unittest.main()
