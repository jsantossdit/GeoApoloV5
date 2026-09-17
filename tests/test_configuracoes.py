"""
Testes automatizados para o módulo de Configurações Gerais e Parâmetros do Sistema.
Execução headless e desacoplada.
"""

import os
import sys
import shutil
import tempfile
import unittest
import tkinter as tk
from unittest.mock import MagicMock

PASTA_RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PASTA_RAIZ not in sys.path:
    sys.path.insert(0, PASTA_RAIZ)

from configuracoes.models import (
    ConfiguracaoSistemaDTO,
    ServidorEmailDTO,
    ResultadoOperacao,
    ConfiguracaoBancoDTO,
    ResultadoTesteConexaoDTO,
)

from configuracoes.service import ConfiguracoesService
from configuracoes.repository import ConfiguracoesRepository
from configuracoes.view import ConfiguracoesView


class TestConfiguracoesService(unittest.TestCase):

    def setUp(self):
        self.mock_repo = MagicMock()
        self.service = ConfiguracoesService(self.mock_repo)
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_normalizar_caminho(self):
        # Substitui $ por barra
        cam = self.service.normalizar_caminho(r"C:$temp$backup$")
        self.assertEqual(cam, os.path.normpath(r"C:\temp\backup"))

        # Substitui # por traço
        cam2 = self.service.normalizar_caminho(r"C:\pasta#teste")
        self.assertEqual(cam2, os.path.normpath(r"C:\pasta-teste"))

        # Caminho vazio
        self.assertEqual(self.service.normalizar_caminho(""), "")

    def test_validar_diretorio(self):
        # Diretório temporário existente
        self.assertTrue(self.service.validar_diretorio(self.temp_dir))

        # Subdiretório inexistente
        sub = os.path.join(self.temp_dir, "nova_pasta")
        self.assertFalse(self.service.validar_diretorio(sub, criar_se_nao_existir=False))

        # Criar se não existir
        self.assertTrue(self.service.validar_diretorio(sub, criar_se_nao_existir=True))
        self.assertTrue(os.path.exists(sub))

    def test_salvar_parametros_validacao(self):
        # Sem empresa
        res = self.service.salvar_parametros({}, empresa_codigo="")
        self.assertFalse(res.sucesso)
        self.assertIn("empresa", res.mensagem.lower())

        # Com empresa
        self.mock_repo.salvar_configuracoes.return_value = True
        res_ok = self.service.salvar_parametros({"caminhobackupsistema": "C:$backup"}, empresa_codigo="001")
        self.assertTrue(res_ok.sucesso)
        self.mock_repo.salvar_configuracoes.assert_called_once()


class TestConfiguracoesRepository(unittest.TestCase):

    def test_queries_with_nolock(self):
        mock_cursor = MagicMock()
        mock_cursor.description = [("caminhobackupsistema",), ("instalacaolocal",)]
        mock_cursor.fetchone.return_value = ("C:\\backup", "C:\\local")

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        repo = ConfiguracoesRepository(connection=mock_conn)

        # 1. obter_configuracoes
        config = repo.obter_configuracoes("001")
        self.assertEqual(config["caminhobackupsistema"], "C:\\backup")
        sql = mock_cursor.execute.call_args[0][0]
        self.assertIn("WITH (NOLOCK)", sql)
        self.assertIn("USER_geoapolo_configuracoes", sql)

        # 2. listar_servidores_email
        mock_cursor.fetchall.return_value = [("001", "SMTP", "smtp.office365.com", 587, "", 993)]
        mock_cursor.description = [
            ("codigo_servidor",),
            ("protocolo",),
            ("servidor_envio",),
            ("porta_envio",),
            ("servidor_recebimento",),
            ("porta_recebimento",),
        ]
        servidores = repo.listar_servidores_email()
        self.assertEqual(len(servidores), 1)
        sql_email = mock_cursor.execute.call_args[0][0]
        self.assertIn("WITH (NOLOCK)", sql_email)
        self.assertIn("USER_geoapolo_mail_server", sql_email)


class TestConfiguracoesBanco(unittest.TestCase):
    """Testes para o subsistema de configuração de banco de dados e conectividade."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_json = os.path.join(self.temp_dir, "test_db.json")
        self.repo = ConfiguracoesRepository()
        self.service = ConfiguracoesService(self.repo)

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_connection_string_mssql_e_mysql(self):
        cfg_mssql = ConfiguracaoBancoDTO(
            tipo_banco="MSSQL",
            servidor="192.168.1.50",
            porta=1433,
            banco="ApoloProd",
            usuario="sa",
            senha="123",
        )
        self.assertIn("SERVER=192.168.1.50", cfg_mssql.connection_string)
        self.assertIn("DATABASE=ApoloProd", cfg_mssql.connection_string)

        cfg_mysql = ConfiguracaoBancoDTO(
            tipo_banco="MySQL",
            servidor="db.rcc.org.br",
            porta=3306,
            banco="app_rcc",
            usuario="admin",
            senha="456",
        )
        self.assertIn("host=db.rcc.org.br", cfg_mysql.connection_string)
        self.assertIn("port=3306", cfg_mysql.connection_string)

    def test_validar_config_banco(self):
        # Servidor vazio
        v, msg = self.service.validar_config_banco(ConfiguracaoBancoDTO(servidor=""))
        self.assertFalse(v)
        self.assertIn("servidor", msg.lower())

        # Banco vazio
        v, msg = self.service.validar_config_banco(ConfiguracaoBancoDTO(servidor="localhost", banco=""))
        self.assertFalse(v)

        # Porta inválida
        v, msg = self.service.validar_config_banco(ConfiguracaoBancoDTO(servidor="localhost", banco="Apolo", porta=99999))
        self.assertFalse(v)
        self.assertIn("porta", msg.lower())

        # Usuário vazio
        v, msg = self.service.validar_config_banco(ConfiguracaoBancoDTO(servidor="localhost", banco="Apolo", usuario=""))
        self.assertFalse(v)

        # Válido
        v, msg = self.service.validar_config_banco(ConfiguracaoBancoDTO(servidor="localhost", banco="Apolo", usuario="sa"))
        self.assertTrue(v)

    def test_salvar_e_carregar_config_banco_json(self):
        cfg = ConfiguracaoBancoDTO(
            tipo_banco="MSSQL",
            servidor="sql.empresa.com",
            porta=14330,
            banco="GeoApolo",
            usuario="apolo_user",
            senha="segredo_forte",
            timeout=25,
        )
        res = self.service.salvar_config_banco(cfg, arquivo_json=self.temp_json)
        self.assertTrue(res.sucesso)
        self.assertTrue(os.path.exists(self.temp_json))

        recup = self.service.obter_config_banco(arquivo_json=self.temp_json)
        self.assertEqual(recup.servidor, "sql.empresa.com")
        self.assertEqual(recup.porta, 14330)
        self.assertEqual(recup.banco, "GeoApolo")
        self.assertEqual(recup.usuario, "apolo_user")
        self.assertEqual(recup.senha, "segredo_forte")
        self.assertEqual(recup.timeout, 25)

    def test_testar_conexao_socket(self):
        import socket
        # Inicia um listener socket efêmero em localhost
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        port = server.getsockname()[1]

        try:
            cfg = ConfiguracaoBancoDTO(servidor="127.0.0.1", porta=port, timeout=2)
            res = self.service.testar_conexao_banco(cfg)
            self.assertTrue(res.sucesso)
            self.assertGreaterEqual(res.tempo_ms, 0)
        finally:
            server.close()

        # Testa porta fechada
        cfg_fechada = ConfiguracaoBancoDTO(servidor="127.0.0.1", porta=1, timeout=1)
        res_fail = self.service.testar_conexao_banco(cfg_fechada)
        self.assertFalse(res_fail.sucesso)


class TestConfiguracoesViewHeadless(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

        self.mock_cursor = MagicMock()
        self.mock_cursor.description = [("caminhobackupsistema",), ("instalacaolocal",)]
        self.mock_cursor.fetchone.return_value = ("C:\\backup", "C:\\local")

        self.mock_conn = MagicMock()
        self.mock_conn.cursor.return_value = self.mock_cursor

    def tearDown(self):
        try:
            self.root.destroy()
        except Exception:
            pass

    def test_view_instantiation(self):
        view = ConfiguracoesView(parent=self.root, connection=self.mock_conn, empresa_codigo="001")
        self.assertIsNotNone(view.notebook)
        self.assertIsNotNone(view.edt_backup)
        self.assertIsNotNone(view.edt_instalacao)
        self.assertIsNotNone(view.combo_integra)
        self.assertIsNotNone(view.tab_banco)
        self.assertIsNotNone(view.edt_db_servidor)
        view.destroy()


if __name__ == "__main__":
    unittest.main()

