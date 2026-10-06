"""
Testes automatizados para:
1. Consultas Imediatas com banco SAVIC (execução em background e mensagem quando não configurado).
2. Resolução e integração prévia de contatos vinculados para envio ao Alvo.
3. Payload de Contatos e Operação I vs A no Alvo.
"""

import unittest
from unittest.mock import MagicMock, patch
from consultas.repository import ConsultasRepository, ResultadoConsultaDTO
from entidades.service import EntidadeService
from entidades.repository import EntidadeRepository
from entidades.models import ResultadoOperacao


class TestSavicConsultasImediatas(unittest.TestCase):
    """Testes para suporte ao banco SAVIC no módulo de Consultas."""

    def setUp(self):
        self.mock_db = MagicMock()
        self.repo = ConsultasRepository(self.mock_db)

    def test_executar_sql_savic_nao_configurado(self):
        """Verifica se mensagem exata é retornada quando SAVIC não está configurado."""
        with patch("config_banco.ConfigManager.load_savic_settings", return_value={"host": "", "database": ""}), \
             patch("config_banco.ConfigManager.get_savic_credentials", return_value={"user": "", "password": ""}):
            res = self.repo._executar_sql_savic("SELECT * FROM teste")
            self.assertFalse(res.sucesso)
            self.assertEqual(res.mensagem, "Solicite ao Administrador a configuração de acesso aos dados do SAVIC")

    def test_executar_sql_dinamico_roteia_savic(self):
        """Verifica se executar_sql_dinamico direciona para SAVIC quando banco == 'SAVIC'."""
        ret_dto = ResultadoConsultaDTO(colunas=["id"], linhas=[{"id": 1}], total_registros=1, sucesso=True)
        with patch.object(self.repo, "_executar_sql_savic", return_value=ret_dto) as mock_savic:
            res = self.repo.executar_sql_dinamico("SELECT 1", banco="SAVIC")
            self.assertTrue(res.sucesso)
            mock_savic.assert_called_once_with("SELECT 1", None)

    def test_combo_bancos_inclui_savic(self):
        """Verifica se a lista de bancos aceita SAVIC nas views."""
        from consultas.imediatas_view import ConsultasImediatasView
        from consultas.view import ConsultasView
        import inspect
        src_imediatas = inspect.getsource(ConsultasImediatasView)
        src_consultas = inspect.getsource(ConsultasView)
        self.assertIn("SAVIC", src_imediatas)
        self.assertIn("SAVIC", src_consultas)


class TestContatosIntegracaoAlvo(unittest.TestCase):
    """Testes para resolução e integração prévia de contatos vinculados."""

    def setUp(self):
        self.mock_repo = MagicMock(spec=EntidadeRepository)
        self.service = EntidadeService(self.mock_repo)

    def test_entidade_sem_contato_vinculado(self):
        """Entidade sem contatos não falha nem chama integração de contato."""
        self.mock_repo.obter_contatos_vinculados_geoentcod.return_value = []
        sucesso, msg, cod = self.service.garantir_contato_integrado_alvo("100")
        self.assertTrue(sucesso)
        self.assertIsNone(cod)

    def test_contato_ja_possui_entcod_local(self):
        """Contato vinculado já possui entcod no Alvo registrado localmente."""
        self.mock_repo.obter_contatos_vinculados_geoentcod.return_value = [
            {"EntCodContato": "200", "entcod_relacao": "ALVO_999", "entcod_contato_alvo": "ALVO_999"}
        ]
        sucesso, msg, cod = self.service.garantir_contato_integrado_alvo("100")
        self.assertTrue(sucesso)
        self.assertEqual(cod, "ALVO_999")
        self.mock_repo.vincular_entcod.assert_called_with("200", "ALVO_999")
        self.mock_repo.vincular_entcod_contato_relacao.assert_called_with("100", "200", "ALVO_999")

    def test_contato_encontrado_no_alvo_via_cpf(self):
        """Contato não possui entcod local, mas é localizado no Alvo pelo CPF."""
        self.mock_repo.obter_contatos_vinculados_geoentcod.return_value = [
            {"EntCodContato": "200", "entcod_relacao": "", "entcod_contato_alvo": ""}
        ]
        self.mock_repo.obter_entcod_entidade.return_value = ""
        self.mock_repo.atualizar_entcod_alvo_via_cpf.return_value = "ALVO_CPF_777"

        sucesso, msg, cod = self.service.garantir_contato_integrado_alvo("100")
        self.assertTrue(sucesso)
        self.assertEqual(cod, "ALVO_CPF_777")
        self.mock_repo.vincular_entcod.assert_called_with("200", "ALVO_CPF_777")
        self.mock_repo.vincular_entcod_contato_relacao.assert_called_with("100", "200", "ALVO_CPF_777")

    def test_contato_nao_encontrado_no_alvo_integra_primeiro(self):
        """Contato não existe no Alvo: sistema integra o contato primeiro e vincula o entcod."""
        self.mock_repo.obter_contatos_vinculados_geoentcod.return_value = [
            {"EntCodContato": "200", "entcod_relacao": "", "entcod_contato_alvo": ""}
        ]
        self.mock_repo.obter_entcod_entidade.return_value = ""
        self.mock_repo.atualizar_entcod_alvo_via_cpf.return_value = None

        mock_api = MagicMock()
        with patch.object(self.service, "exportar_entidade_para_alvo") as mock_exp:
            mock_exp.return_value = ResultadoOperacao(sucesso=True, mensagem="Contato inserido", codigo="ALVO_NOVO_888")
            sucesso, msg, cod = self.service.garantir_contato_integrado_alvo("100", api_client=mock_api)
            self.assertTrue(sucesso)
            self.assertEqual(cod, "ALVO_NOVO_888")
            mock_exp.assert_called_once_with(
                geoentcod="200",
                usuario_alvo="",
                senha_alvo_plana="",
                api_client=mock_api,
                _integrando_contato_filho=True,
            )
            self.mock_repo.vincular_entcod.assert_called_with("200", "ALVO_NOVO_888")
            self.mock_repo.vincular_entcod_contato_relacao.assert_called_with("100", "200", "ALVO_NOVO_888")

    def test_montar_payload_inclui_entcod_contato_resolvido(self):
        """Verifica se o payload no modo delphi embute o entcod do contato vinculado."""
        self.mock_repo.carregar_dados_completos_entidade_geoapolo.return_value = {
            "geoentcod": "100",
            "geoentnome": "Entidade Pai",
            "entcpfcgc": "12345678901",
        }
        self.mock_repo.obter_cpf_rg_documentos.return_value = ("12345678901", "")
        self.mock_repo.listar_categorias_entidade.return_value = [{"categcodestr": "03.001.001"}]
        self.mock_repo.listar_telefones_entidade.return_value = []
        self.mock_repo.listar_webcontatos_entidade.return_value = []
        self.mock_repo.carregar_contatos_entidade.return_value = [
            {
                "EntCodContato": "200",
                "entCod": "ALVO_RESOLVIDO_555",
                "geoentnome": "Contato Filho",
                "EntContatoCelular": "11999998888",
            }
        ]

        payload = self.service.montar_payload_entidade_alvo("100", operacao="I", modo="delphi")
        self.assertEqual(len(payload["Contatos"]), 1)
        self.assertEqual(payload["Contatos"][0]["Codigo"], "ALVO_RESOLVIDO_555")
        self.assertEqual(payload["Contatos"][0]["Nome"], "Contato Filho")


if __name__ == "__main__":
    unittest.main()
