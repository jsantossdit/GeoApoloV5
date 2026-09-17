"""
Teste headless de inicialização das telas Tkinter (RelatoriosView e EntidadesView).
Garante integridade de widgets, layout, bindings e inicialização sem travar loop.
"""

import os
import sys
import unittest
import tkinter as tk
from unittest.mock import MagicMock

PASTA_RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PASTA_RAIZ not in sys.path:
    sys.path.insert(0, PASTA_RAIZ)

from relatorios.view import RelatoriosView
from entidades.view import EntidadesView


class TestViewsHeadless(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Não exibe a janela principal

        # Mock de conexão de banco de dados
        self.mock_cursor = MagicMock()
        self.mock_cursor.description = [("Código",), ("Nome",), ("Documento",), ("Cidade",)]
        self.mock_cursor.fetchall.return_value = [
            ("001", "ENTIDADE MODELO", "12345678900", "SAO PAULO")
        ]
        self.mock_conn = MagicMock()
        self.mock_conn.cursor.return_value = self.mock_cursor

    def tearDown(self):
        try:
            self.root.destroy()
        except Exception:
            pass

    def test_relatorios_view_instantiation(self):
        """Verifica se a tela de Relatórios inicializa todos os componentes com sucesso."""
        view = RelatoriosView(parent=self.root, connection=self.mock_conn)
        self.assertIsNotNone(view.tree)
        self.assertIsNotNone(view.combo_tipo)
        self.assertIsNotNone(view.btn_excel)
        self.assertIsNotNone(view.btn_html)
        self.assertIsNotNone(view.btn_csv)

        # Testa filtro local
        view.entry_filtro.insert(0, "MODELO")
        view._aplicar_filtro_local()
        self.assertGreaterEqual(len(view._dados_filtrados), 1)

        view.destroy()

    def test_entidades_view_instantiation(self):
        """Verifica se a tela de Gestão de Entidades inicializa todos os componentes com sucesso."""
        view = EntidadesView(parent=self.root, connection=self.mock_conn)
        self.assertIsNotNone(view.tree)
        self.assertIsNotNone(view.combo_base)
        self.assertIsNotNone(view.entry_busca)
        view.destroy()

    def test_novas_views_headless(self):
        """Verifica se todas as novas views criadas inicializam sem erro."""
        from permissoes import UsuarioContasFinView, DesligamentoUsuarioView, PermissoesService, PermissoesRepository
        from contabilidade import ExclusaoContabilView, DebxCredView, ContabilidadeService, ContabilidadeRepository
        from eventos import ImportarInscritosEventosView, EventosService, EventosRepository

        # 1. Permissoes
        mock_perm_repo = MagicMock(spec=PermissoesRepository)
        mock_perm_repo.listar_usuarios_ativos.return_value = [{"codigo": "ADMIN", "nome": "Administrador"}]
        mock_perm_repo.listar_contas_disponiveis.return_value = []
        mock_perm_repo.listar_contas_usuario.return_value = []
        mock_perm_repo.listar_usuarios_por_status.return_value = []
        mock_perm_repo.pesquisar_usuarios.return_value = []
        perm_service = PermissoesService(mock_perm_repo)

        view_contas = UsuarioContasFinView(self.root, service=perm_service)
        self.assertIsNotNone(view_contas.cbo_usuario)
        view_contas.window.destroy()

        view_desliga = DesligamentoUsuarioView(self.root, service=perm_service)
        self.assertIsNotNone(view_desliga.tree)
        view_desliga.window.destroy()

        # 2. Contabilidade
        mock_contab_repo = MagicMock(spec=ContabilidadeRepository)
        mock_contab_repo.pesquisar_lancamentos.return_value = []
        mock_contab_repo.pesquisar_por_modulo.return_value = []
        mock_contab_repo.conciliar_debxcred.return_value = []
        mock_contab_repo.obter_nome_conta_contabil.return_value = ""
        contab_service = ContabilidadeService(mock_contab_repo)

        view_exclui = ExclusaoContabilView(self.root, service=contab_service)
        self.assertIsNotNone(view_exclui.tree_indiv)
        view_exclui.window.destroy()

        view_debxcred = DebxCredView(self.root, service=contab_service)
        self.assertIsNotNone(view_debxcred.tree)
        view_debxcred.window.destroy()

        # 3. Eventos
        mock_evt_repo = MagicMock(spec=EventosRepository)
        mock_evt_repo.listar_eventos_cadastrados.return_value = []
        mock_evt_repo.listar_inscricoes_evento.return_value = []
        evt_service = EventosService(mock_evt_repo)

        view_evt = ImportarInscritosEventosView(self.root, service=evt_service)
        self.assertIsNotNone(view_evt.tree)
        view_evt.window.destroy()

    def test_ciclo2_views_headless(self):
        """Verifica a inicialização das views do Ciclo 2 (Fiscal, Vindi, Localidades, Dioceses)."""
        from fiscal import AuditoriaCuponsView, AuditoriaCuponsService, AuditoriaCuponsRepository
        from vindi import ConciliacaoVindiView, VindiService, VindiRepository
        from localidades import CorrecaoCidadesDistritosView, LocalidadesService, LocalidadesRepository
        from dioceses import RelacionaDioceseEntidadeView, DiocesesService, DiocesesRepository

        # 1. Fiscal - Auditoria de Cupons
        mock_fisc_repo = MagicMock(spec=AuditoriaCuponsRepository)
        mock_fisc_repo.listar_cupons_pdv.return_value = []
        fisc_service = AuditoriaCuponsService(mock_fisc_repo)
        view_fisc = AuditoriaCuponsView(self.root, service=fisc_service)
        self.assertIsNotNone(view_fisc.tree)
        view_fisc.window.destroy()

        # 2. Vindi - Conciliação Recorrente
        mock_vindi_repo = MagicMock(spec=VindiRepository)
        mock_vindi_repo.listar_transacoes.return_value = []
        vindi_service = VindiService(mock_vindi_repo)
        view_vindi = ConciliacaoVindiView(self.root, service=vindi_service)
        self.assertIsNotNone(view_vindi.tree)
        view_vindi.window.destroy()

        # 3. Localidades - Correção Cidades/Distritos
        mock_loc_repo = MagicMock(spec=LocalidadesRepository)
        mock_loc_repo.listar_cidades.return_value = []
        loc_service = LocalidadesService(mock_loc_repo)
        view_loc = CorrecaoCidadesDistritosView(self.root, service=loc_service)
        self.assertIsNotNone(view_loc.tree_cid)
        view_loc.window.destroy()

        # 4. CRM Eclesial - Relaciona Entidade x Diocese
        mock_dio_repo = MagicMock(spec=DiocesesRepository)
        mock_dio_repo.listar_entidades.return_value = []
        mock_dio_repo.listar_dioceses.return_value = []
        dio_service = DiocesesService(mock_dio_repo)
        view_dio = RelacionaDioceseEntidadeView(self.root, service=dio_service)
        self.assertIsNotNone(view_dio.grid_entidades)
        view_dio.window.destroy()

    def test_usuarios_view_headless(self):
        """Verifica a inicialização da tela unificada de Gestão de Usuários, Grupos e Perfis."""
        from usuarios import UsuariosView, UsuariosService, UsuariosRepository

        mock_repo = MagicMock(spec=UsuariosRepository)
        mock_repo.listar_departamentos.return_value = []
        mock_repo.listar_sistemas.return_value = []
        mock_repo.listar_usuarios.return_value = []
        mock_repo.listar_grupos.return_value = []
        mock_repo.listar_categorias_objetos.return_value = []
        mock_repo.listar_sistemas_usuario.return_value = []
        mock_repo.listar_usuarios_grupo.return_value = []
        mock_repo.listar_objetos_perfil.return_value = []

        service = UsuariosService(mock_repo)
        view = UsuariosView(self.root, service=service)

        self.assertIsNotNone(view.tree_users)
        self.assertIsNotNone(view.tree_grupos)
        self.assertIsNotNone(view.tree_perfis)
        view.destroy()

    def test_consultas_e_matchcode_views_headless(self):
        """Verifica a inicialização das views de Consultas Dinâmicas e MatchCode."""
        from consultas import ConsultasView, ConsultasService, ConsultasRepository
        from matchcode import MatchCodeView, MatchCodeService, MatchCodeRepository

        # Consultas
        mock_c_repo = MagicMock(spec=ConsultasRepository)
        mock_c_repo.listar_consultas.return_value = []
        mock_c_repo.executar_sql_dinamico.return_value = MagicMock(sucesso=True, colunas=["A"], linhas=[["1"]], total_registros=1)
        c_service = ConsultasService(mock_c_repo)
        view_c = ConsultasView(self.root, service=c_service)
        self.assertIsNotNone(view_c.tree_resultados)
        self.assertIsNotNone(view_c.tree_consultas)
        view_c.destroy()

        # MatchCode
        mock_m_repo = MagicMock(spec=MatchCodeRepository)
        mock_m_repo.obter_usuario.return_value = ("U1", "Usuario 1", "A")
        mock_m_repo.obter_entidade.return_value = ("E1", "Entidade 1")
        m_service = MatchCodeService(mock_m_repo)
        view_m = MatchCodeView(self.root, service=m_service)
        self.assertIsNotNone(view_m.ent_user_orig)
        self.assertIsNotNone(view_m.ent_ent_orig)
        view_m.destroy()

    def test_empresas_view_headless(self):
        """Verifica a inicialização da tela de Multi-Empresas e Contexto Corporativo."""
        from empresas import EmpresasView, EmpresasService, EmpresasRepository

        mock_repo = MagicMock(spec=EmpresasRepository)
        mock_repo.listar_empresas.return_value = []
        mock_repo.sincronizar_empresas_apolo.return_value = 0
        service = EmpresasService(mock_repo)

        view = EmpresasView(self.root, service=service)
        self.assertIsNotNone(view.tree_selecao)
        self.assertIsNotNone(view.tree_cad)
        view.destroy()

    def test_crm_view_headless(self):
        """Verifica a inicialização da tela unificada de CRM (Ocorrências, Campanhas, Tratamentos)."""
        from crm import CRMView, CRMService, CRMRepository

        mock_repo = MagicMock(spec=CRMRepository)
        mock_repo.listar_ocorrencias.return_value = []
        mock_repo.listar_tipos_campanha.return_value = []
        mock_repo.listar_tipos_tratamento.return_value = []
        mock_repo.listar_areas_disponiveis.return_value = []
        mock_repo.listar_motivos_por_area.return_value = []
        mock_repo.listar_origens.return_value = []
        mock_repo.listar_solicitantes.return_value = []

        service = CRMService(mock_repo)
        view = CRMView(self.root, service=service, codigo_empresa="01")

        self.assertIsNotNone(view.tree_ocor)
        self.assertIsNotNone(view.tree_camp)
        self.assertIsNotNone(view.tree_trat)
        view.destroy()

    def test_cores_view_headless(self):
        """Verifica a inicialização da tela de Cores de Produtos."""
        from cores import CoresView, CoresService, CoresRepository, CorDTO

        mock_repo = MagicMock(spec=CoresRepository)
        mock_repo.listar_cores.return_value = [CorDTO(1, "BRANCO"), CorDTO(2, "PRETO")]
        mock_repo.obter_proximo_codigo.return_value = 3
        service = CoresService(mock_repo)

        view = CoresView(self.root, service=service)
        self.assertIsNotNone(view.tree)
        self.assertIsNotNone(view.ent_cod)
        self.assertIsNotNone(view.ent_desc)

        # Testa seleção e novo registro
        view._novo_registro()
        self.assertEqual(view.ent_cod.get(), "003")
        view.destroy()

    def test_licenciamento_e_versoes_views_headless(self):
        """Verifica a inicialização das telas de Licenciamento, Versões e Novidades."""
        from datetime import date
        from licenciamento import (
            ValidacaoLicencaView,
            ManutencaoVersoesView,
            NovidadesVersaoDialog,
            LicenciamentoService,
            LicenciamentoRepository,
            LicencaDTO,
            VersaoSistemaDTO,
        )

        mock_repo = MagicMock(spec=LicenciamentoRepository)
        mock_repo.buscar_licenca_mes.return_value = LicencaDTO(
            id_palavra="TEST_PALAVRA",
            data_inicial=date(2026, 9, 1),
            data_final=date(2026, 9, 30),
            flag_bloqueia="N",
            flag_ativar="S",
            tempo_bloqueio_dias=10,
        )
        mock_repo.listar_versoes.return_value = [
            VersaoSistemaDTO("5.0.0", "17/09/2026", "Changelog", "S")
        ]
        mock_repo.obter_versao.return_value = VersaoSistemaDTO("5.0.0", "17/09/2026", "Changelog", "S")
        mock_repo.usuario_ja_viu_versao.return_value = False

        service = LicenciamentoService(mock_repo)

        # 1. ValidacaoLicencaView
        view_lic = ValidacaoLicencaView(self.root, service=service)
        self.assertIsNotNone(view_lic.ent_chave)
        self.assertIsNotNone(view_lic.lbl_status)
        view_lic.destroy()

        # 2. ManutencaoVersoesView
        view_ver = ManutencaoVersoesView(self.root, service=service)
        self.assertIsNotNone(view_ver.tree)
        self.assertIsNotNone(view_ver.ent_versao)
        self.assertIsNotNone(view_ver.txt_novidades)
        view_ver._novo_registro()
        view_ver.destroy()

        # 3. NovidadesVersaoDialog
        dialog = NovidadesVersaoDialog(
            self.root,
            idversao="5.0.0",
            usucod="ADMIN",
            texto_novidades="Notas de teste",
            service=service,
        )
        self.assertIsNotNone(dialog)
        dialog._confirmar()

    def test_configcod_view_headless(self):
        """Verifica a inicialização da tela de Manutenção de Códigos do Sistema."""
        from configcod import ManutencaoCodigosView, ConfigCodService, ConfigCodRepository, ConfigCodDTO

        mock_repo = MagicMock(spec=ConfigCodRepository)
        mock_repo.listar_tabelas.return_value = [
            ConfigCodDTO("USER_geoapolo_entidades", 10, "S", "01", "MATRIZ")
        ]
        mock_repo.obter_config_cod.return_value = ConfigCodDTO("USER_geoapolo_entidades", 10, "S", "01", "MATRIZ")
        service = ConfigCodService(mock_repo)

        view = ManutencaoCodigosView(self.root, service=service)
        self.assertIsNotNone(view.tree)
        self.assertIsNotNone(view.ent_tabela)
        self.assertIsNotNone(view.ent_proximo)
        self.assertIsNotNone(view.chk_ativa)

        # Testa seleção e limpeza
        view._limpar_campos()
        self.assertEqual(view.ent_tabela.get(), "")
        view.destroy()

    def test_nomesamigaveis_view_headless(self):
        """Verifica a inicialização da tela de Dicionário de Nomes Amigáveis."""
        from nomesamigaveis import NomesAmigaveisView, NomesAmigaveisService, NomesAmigaveisRepository, ObjetoSistemaDTO

        mock_repo = MagicMock(spec=NomesAmigaveisRepository)
        mock_repo.listar_categorias.return_value = ["Geral", "Fiscal"]
        mock_repo.listar_objetos.return_value = [
            ObjetoSistemaDTO("frmprincipal.btnEmitirNFe", "Emitir NF-e", "Fiscal")
        ]
        service = NomesAmigaveisService(mock_repo)

        view = NomesAmigaveisView(self.root, service=service)
        self.assertIsNotNone(view.tree)
        self.assertIsNotNone(view.cbo_filtro_cat)
        self.assertIsNotNone(view.ent_busca)
        self.assertIsNotNone(view.ent_objeto)
        self.assertIsNotNone(view.ent_amigavel)

        # Testa sugestão para objeto atual
        view.ent_objeto.insert(0, "btnSalvarCupom")
        view._sugerir_nome_atual()
        self.assertEqual(view.ent_amigavel.get(), "Salvar Cupom")

        view.destroy()

    def test_departamentos_view_headless(self):
        """Verifica a inicialização da tela de Departamentos e Seções."""
        from departamentos import DepartamentosView, DepartamentosService, DepartamentosRepository, DepartamentoDTO

        mock_repo = MagicMock(spec=DepartamentosRepository)
        mock_repo.listar_departamentos.return_value = [
            DepartamentoDTO(1, "FINANCEIRO", "01", "MATRIZ", "A", "1.01", "ADM")
        ]
        mock_repo.obter_departamento.return_value = DepartamentoDTO(1, "FINANCEIRO", "01", "MATRIZ", "A")
        mock_repo.obter_proximo_codigo.return_value = 2
        service = DepartamentosService(mock_repo)

        view = DepartamentosView(self.root, service=service)
        self.assertIsNotNone(view.tree)
        self.assertIsNotNone(view.ent_cod)
        self.assertIsNotNone(view.ent_nome)
        self.assertIsNotNone(view.ent_empresa)

        # Testa novo registro
        view._novo_registro()
        self.assertEqual(view.ent_cod.get(), "002")
        view.destroy()

    def test_autenticacao_e_sobre_views_headless(self):
        """Verifica a inicialização da tela de Login e do diálogo Sobre o Sistema."""
        from autenticacao import LoginView, SobreSistemaDialog, AutenticacaoService, AutenticacaoRepository

        mock_repo = MagicMock(spec=AutenticacaoRepository)
        mock_repo.listar_empresas_ativas.return_value = [{"empcod": "01", "empnome": "MATRIZ SEDE"}]
        mock_repo.obter_usuario_login.return_value = {
            "usucod": "ADMIN",
            "login": "admin",
            "nome_completo": "Administrador",
            "flagativo": "A",
            "senha": "123",
        }
        mock_repo.obter_empresa.return_value = {"empcod": "01", "empnome": "MATRIZ SEDE"}

        service = AutenticacaoService(mock_repo)

        # 1. LoginView
        login_view = LoginView(self.root, service=service)
        self.assertIsNotNone(login_view.ent_login)
        self.assertIsNotNone(login_view.ent_senha)
        self.assertIsNotNone(login_view.cbo_empresa)
        login_view.destroy()

        # 2. SobreSistemaDialog
        sobre = SobreSistemaDialog(self.root, service=service)
        self.assertIsNotNone(sobre)
        sobre.destroy()


if __name__ == "__main__":
    unittest.main()





