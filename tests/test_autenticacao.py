"""
Testes Unitários para o Módulo de Autenticação, Logon e Sessão.
GeoApolo V5
Clean Architecture: DTOs, Repositório SQLite em memória e Regras de Negócio do Service.
"""

import sqlite3
import unittest
from unittest.mock import MagicMock

from autenticacao.models import CredenciaisDTO, UsuarioSessaoDTO, ResultadoAutenticacaoDTO
from autenticacao.repository import AutenticacaoRepository
from autenticacao.service import AutenticacaoService, SENHA_MESTRA_DEV
from licenciamento.models import ResultadoValidacaoLicencaDTO


class TestAutenticacaoModels(unittest.TestCase):
    """Testes dos DTOs de Autenticação."""

    def test_usuario_sessao_dto_display(self):
        sessao = UsuarioSessaoDTO(
            usucod="ADMIN",
            login="admin",
            nome_usuario="Administrador do Sistema",
            empcod="01",
            empnome="MATRIZ",
            perfil_admin=True,
        )
        self.assertTrue(sessao.perfil_admin)
        self.assertIn("Administrador do Sistema", sessao.display)
        self.assertIn("MATRIZ", sessao.display)

    def test_resultado_autenticacao_dto(self):
        res = ResultadoAutenticacaoDTO(sucesso=True, mensagem="Logon efetuado")
        self.assertTrue(res.sucesso)
        self.assertFalse(res.bloqueio_licenca)


class TestAutenticacaoRepository(unittest.TestCase):
    """Testes do Repositório com SQLite em memória."""

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
            CREATE TABLE USER_geoapolo_usuarios (
                usucod VARCHAR(20) PRIMARY KEY,
                login VARCHAR(50),
                nome_completo VARCHAR(100),
                flagativo VARCHAR(1),
                senha VARCHAR(100),
                senha_alvo VARCHAR(100)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE USER_geoapolo_empresas (
                empcod VARCHAR(10) PRIMARY KEY,
                empnome VARCHAR(100),
                empcod_apolo VARCHAR(20),
                flagativo VARCHAR(1)
            )
        """)

        self.cursor.execute("""
            INSERT INTO USER_geoapolo_usuarios
            VALUES ('ADMIN', 'admin', 'Administrador Master', 'A', 'senha123', 'senha123')
        """)
        self.cursor.execute("""
            INSERT INTO USER_geoapolo_usuarios
            VALUES ('USER2', 'inativo', 'Usuario Desativado', 'I', '123456', '123456')
        """)
        self.cursor.execute("""
            INSERT INTO USER_geoapolo_empresas
            VALUES ('01', 'MATRIZ SEDE', 'EMP01', 'S')
        """)
        self.conn.commit()

        self.repo = AutenticacaoRepository(connection=self.conn)

    def tearDown(self):
        self.conn.close()

    def test_obter_usuario_login(self):
        # Busca por login
        u1 = self.repo.obter_usuario_login("admin")
        self.assertIsNotNone(u1)
        self.assertEqual(u1["nome_completo"], "Administrador Master")
        self.assertEqual(u1["flagativo"], "A")

        # Busca por usucod
        u2 = self.repo.obter_usuario_login("ADMIN")
        self.assertIsNotNone(u2)

        # Inexistente
        self.assertIsNone(self.repo.obter_usuario_login("desconhecido"))

    def test_listar_empresas_ativas(self):
        emps = self.repo.listar_empresas_ativas()
        self.assertEqual(len(emps), 1)
        self.assertEqual(emps[0]["empcod"], "01")
        self.assertEqual(emps[0]["empnome"], "MATRIZ SEDE")


class TestAutenticacaoService(unittest.TestCase):
    """Testes de Regras de Negócio do AutenticacaoService."""

    def setUp(self):
        self.mock_repo = MagicMock(spec=AutenticacaoRepository)
        self.mock_lic = MagicMock()
        self.service = AutenticacaoService(self.mock_repo, licenciamento_service=self.mock_lic)

        # Licença OK por padrão
        self.mock_lic.validar_licenca_atual.return_value = ResultadoValidacaoLicencaDTO(
            sucesso=True, status="OK", dias_restantes=30
        )

    def test_autenticar_login_vazio(self):
        res = self.service.autenticar(CredenciaisDTO("", "123"))
        self.assertFalse(res.sucesso)
        self.assertIn("informe o usuário", res.mensagem)

    def test_autenticar_bloqueio_licenca(self):
        self.mock_lic.validar_licenca_atual.return_value = ResultadoValidacaoLicencaDTO(
            sucesso=False, status="BLOQUEADA", mensagem="Licença vencida"
        )
        res = self.service.autenticar(CredenciaisDTO("admin", "senha"))
        self.assertFalse(res.sucesso)
        self.assertTrue(res.bloqueio_licenca)
        self.assertIn("Acesso negado", res.mensagem)

    def test_autenticar_usuario_inexistente(self):
        self.mock_repo.obter_usuario_login.return_value = None
        res = self.service.autenticar(CredenciaisDTO("naoexiste", "123"))
        self.assertFalse(res.sucesso)
        self.assertIn("não encontrado", res.mensagem)

    def test_autenticar_usuario_inativo(self):
        self.mock_repo.obter_usuario_login.return_value = {
            "usucod": "U2", "login": "inativo", "flagativo": "I", "senha": "123"
        }
        res = self.service.autenticar(CredenciaisDTO("inativo", "123"))
        self.assertFalse(res.sucesso)
        self.assertIn("desativado", res.mensagem)

    def test_autenticar_senha_incorreta(self):
        self.mock_repo.obter_usuario_login.return_value = {
            "usucod": "ADMIN", "login": "admin", "flagativo": "A", "senha": "correta"
        }
        res = self.service.autenticar(CredenciaisDTO("admin", "errada"))
        self.assertFalse(res.sucesso)
        self.assertIn("Senha incorreta", res.mensagem)

    def test_autenticar_sucesso_senha_correta(self):
        self.mock_repo.obter_usuario_login.return_value = {
            "usucod": "ADMIN", "login": "admin", "nome_completo": "Admin", "flagativo": "A", "senha": "123"
        }
        self.mock_repo.obter_empresa.return_value = {"empcod": "01", "empnome": "SEDE"}

        res = self.service.autenticar(CredenciaisDTO("admin", "123", "01"))
        self.assertTrue(res.sucesso)
        self.assertIsNotNone(res.sessao)
        self.assertEqual(res.sessao.empcod, "01")
        self.assertEqual(res.sessao.nome_usuario, "Admin")
        self.assertTrue(res.sessao.perfil_admin)

    def test_obter_info_sistema(self):
        info = self.service.obter_info_sistema()
        self.assertIn("sistema", info)
        self.assertIn("versao", info)
        self.assertEqual(info["versao"], "5.0.0")
        self.assertIn("estacao", info)
        self.assertIn("ip", info)


if __name__ == "__main__":
    unittest.main()
