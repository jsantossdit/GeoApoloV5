"""
Testes Unitários para o Módulo de Criptografia Delphi e Validação de Logon com Banco de Dados.
GeoApolo V5 / GeoAlvo
"""

import sqlite3
import unittest
from unittest.mock import MagicMock, patch

from core.criptografia import criptografia, decriptografia, preenche_vetor
from logon import TelaLogon


class TestCriptografiaDelphi(unittest.TestCase):
    """Testes de fidelidade da rotina criptográfica do Delphi (funcoes.pas)."""

    def test_preenche_vetor_tamanho(self):
        vetor = preenche_vetor()
        self.assertEqual(len(vetor), 94)
        self.assertEqual(vetor[1], "A")
        self.assertEqual(vetor[26], "Z")
        self.assertEqual(vetor[27], "a")
        self.assertEqual(vetor[52], "z")
        self.assertEqual(vetor[53], "0")
        self.assertEqual(vetor[62], "9")

    def test_criptografia_decriptografia_roundtrip(self):
        senhas = ["netscape", "123456", "admin@2026", "Apolo_V5", "senhaComEspaco 123"]
        for s in senhas:
            c = criptografia(32, s)
            d = decriptografia(32, c)
            self.assertEqual(s, d, f"Falha no roundtrip para a senha: {s}")

    def test_compatibilidade_senha_legada_delphi(self):
        # netscape cifrado com chave 32
        hash_delphi = criptografia(32, "netscape")
        self.assertEqual(decriptografia(32, hash_delphi), "netscape")


class TestLogonBancoDados(unittest.TestCase):
    """Testes da validação de logon contra base de dados."""

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE USER_geoapolo_usuarios (
                usucod VARCHAR(20) PRIMARY KEY,
                login VARCHAR(50),
                nome_completo VARCHAR(100),
                usucod_apolo VARCHAR(20),
                senha VARCHAR(100),
                senha_alvo VARCHAR(100),
                flagativo VARCHAR(1)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE USER_geoapolo_usuariossistemas (
                usucod VARCHAR(20),
                codigo_sistema INTEGER
            )
        """)

        # Usuário 1: Senha cifrada no padrão Delphi (chave 32)
        senha_cifrada = criptografia(32, "segredo123")
        self.cursor.execute("""
            INSERT INTO USER_geoapolo_usuarios
            VALUES ('001', 'julio', 'Julio Cesar', 'APL01', ?, '', 'A')
        """, [senha_cifrada])

        # Usuário 2: Desativado
        self.cursor.execute("""
            INSERT INTO USER_geoapolo_usuarios
            VALUES ('002', 'inativo', 'Usuario Inativo', 'APL02', '123', '', 'I')
        """)

        # Usuário 3: Sem permissão no sistema (usucod = '0' em usuariossistemas)
        self.cursor.execute("""
            INSERT INTO USER_geoapolo_usuarios
            VALUES ('003', 'bloqueado', 'Usuario Bloqueado', 'APL03', '123', '', 'A')
        """)
        self.cursor.execute("""
            INSERT INTO USER_geoapolo_usuariossistemas VALUES ('003', 1)
        """)
        self.conn.commit()

        # Cria instância do formulário de logon com mock do Tk
        with patch("tkinter.Tk"):
            self.tela = TelaLogon()

    def tearDown(self):
        self.conn.close()

    def test_validar_usuario_com_senha_cifrada_delphi(self):
        with patch("entidades.database.obter_conexao_banco", return_value=self.conn):
            sucesso, msg, dados = self.tela.validar_usuario_banco("julio", "segredo123")
            self.assertTrue(sucesso)
            self.assertIsNotNone(dados)
            self.assertEqual(dados["codigo_usuario"], "001")
            self.assertEqual(dados["nome_completo"], "Julio Cesar")

    def test_validar_usuario_com_senha_incorreta(self):
        with patch("entidades.database.obter_conexao_banco", return_value=self.conn):
            sucesso, msg, dados = self.tela.validar_usuario_banco("julio", "senha_errada")
            self.assertFalse(sucesso)
            self.assertIn("Senha errada ou inválida", msg)

    def test_validar_usuario_inativo(self):
        with patch("entidades.database.obter_conexao_banco", return_value=self.conn):
            sucesso, msg, dados = self.tela.validar_usuario_banco("inativo", "123")
            self.assertFalse(sucesso)
            self.assertIn("desativado ou desligado", msg)

    def test_validar_usuario_inexistente(self):
        with patch("entidades.database.obter_conexao_banco", return_value=self.conn):
            sucesso, msg, dados = self.tela.validar_usuario_banco("nao_existe", "123")
            self.assertFalse(sucesso)
            self.assertIn("não encontrado", msg)

    def test_validar_contingencia_local(self):
        sucesso, msg, dados = self.tela._validar_contingencia_local("admin", "admin")
        self.assertTrue(sucesso)
        self.assertEqual(dados["login"], "admin")


if __name__ == "__main__":
    unittest.main()
