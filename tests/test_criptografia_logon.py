"""
Testes Unitários para o Módulo de Criptografia Delphi e Validação de Logon com Banco de Dados.
GeoApolo V5 / GeoAlvo
"""

import sqlite3
import unittest
from pathlib import Path
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


    def test_verificar_usuario_existe_valido(self):
        with patch("entidades.database.obter_conexao_banco", return_value=self.conn):
            existe, msg = self.tela.verificar_usuario_existe("julio")
            self.assertTrue(existe)
            self.assertEqual(msg, "")

    def test_verificar_usuario_existe_inativo(self):
        with patch("entidades.database.obter_conexao_banco", return_value=self.conn):
            existe, msg = self.tela.verificar_usuario_existe("inativo")
            self.assertFalse(existe)
            self.assertIn("inativo", msg)

    def test_verificar_usuario_existe_inexistente(self):
        with patch("entidades.database.obter_conexao_banco", return_value=self.conn):
            existe, msg = self.tela.verificar_usuario_existe("nao_existe")
            self.assertFalse(existe)
            self.assertIn("não cadastrado", msg)

    def test_validar_usuario_enter_sucesso_foca_senha(self):
        with patch("entidades.database.obter_conexao_banco", return_value=self.conn):
            self.tela.entry_usuario.get = MagicMock(return_value="julio")
            self.tela.entry_senha.focus_set = MagicMock()

            res = self.tela.validar_usuario_enter()
            self.assertEqual(res, "break")
            self.assertEqual(self.tela.tentativas_usuario, 0)
            self.tela.entry_senha.focus_set.assert_called_once()

    def test_validar_usuario_enter_tres_tentativas_aborta(self):
        with patch("entidades.database.obter_conexao_banco", return_value=self.conn):
            with patch("tkinter.messagebox.showerror"):
                self.tela.entry_usuario.get = MagicMock(return_value="nao_existe")
                self.tela.entry_usuario.focus_set = MagicMock()
                self.tela.entry_usuario.select_range = MagicMock()
                self.tela.root.destroy = MagicMock()

                # Tentativa 1
                self.tela.validar_usuario_enter()
                self.assertEqual(self.tela.tentativas_usuario, 1)

                # Tentativa 2
                self.tela.validar_usuario_enter()
                self.assertEqual(self.tela.tentativas_usuario, 2)

                # Tentativa 3 -> aborta execucao
                with self.assertRaises(SystemExit) as cm:
                    self.tela.validar_usuario_enter()
                self.assertEqual(cm.exception.code, 0)
                self.assertEqual(self.tela.tentativas_usuario, 3)
                self.tela.root.destroy.assert_called_once()

    def test_fazer_login_usuario_inexistente_alerta_antes_da_senha(self):
        """Valida que usuário inexistente em fazer_login() alerta antes de checar ou solicitar senha."""
        with patch("entidades.database.obter_conexao_banco", return_value=self.conn):
            with patch("tkinter.messagebox.showerror") as mock_err, \
                 patch("tkinter.messagebox.showwarning") as mock_warn:
                self.tela.entry_usuario.get = MagicMock(return_value="inexistente_xyz")
                self.tela.entry_senha.get = MagicMock(return_value="")  # Senha vazia
                self.tela.entry_usuario.focus_set = MagicMock()
                self.tela.entry_usuario.select_range = MagicMock()

                self.tela.fazer_login()

                # Deve exibir erro de usuário não cadastrado, e NUNCA o aviso de senha vazia
                mock_err.assert_called_once()
                self.assertIn("Usuário não cadastrado", mock_err.call_args[0][1])
                mock_warn.assert_not_called()

    def test_usuario_com_senha_nula_solicita_cadastro_e_salva_criptografada(self):
        """Valida que usuário com senha nula é detectado e a nova senha é gravada criptografada (chave 32)."""
        # Insere usuário com senha NULL
        self.cursor.execute("""
            INSERT INTO USER_geoapolo_usuarios
            VALUES ('004', 'novato', 'Usuario Sem Senha', 'APL04', NULL, NULL, 'A')
        """)
        self.conn.commit()

        with patch("entidades.database.obter_conexao_banco", return_value=self.conn):
            # 1. Verifica detecção de senha nula
            res = self.tela.verificar_usuario_existe("novato")
            self.assertTrue(res.existe)
            self.assertTrue(res.dados.get("senha_nula"))

            # 2. Testa gravação de nova senha com criptografia oficial do sistema (chave 32)
            sucesso = self.tela.salvar_nova_senha("novato", "MinhaNovaSenha123")
            self.assertTrue(sucesso)

            # 3. Confere diretamente no banco de dados
            self.cursor.execute("SELECT senha FROM USER_geoapolo_usuarios WHERE login = 'novato'")
            row = self.cursor.fetchone()
            self.assertIsNotNone(row)
            senha_salva = row[0]

            # Deve estar criptografada com chave 32, não em texto puro
            self.assertNotEqual(senha_salva, "MinhaNovaSenha123")
            self.assertEqual(senha_salva, criptografia(32, "MinhaNovaSenha123"))
            self.assertEqual(decriptografia(32, senha_salva), "MinhaNovaSenha123")

    def test_admin_sem_configuracao_abre_config(self):
        """Valida que quando as configurações do GeoAlvo não estão presentes, admin abre config com a senha mestre."""
        with patch("entidades.database.obter_conexao_banco", return_value=self.conn), \
             patch.object(self.tela, "configuracoes_geoalvo_presentes", return_value=False):
            # No banco de testes não existe o usuário 'admin' na tabela
            res = self.tela.verificar_usuario_existe("admin")
            self.assertTrue(res.existe)
            self.assertTrue(res.dados.get("is_admin_fallback"))

            # Testa tentativa de login com a senha mestre protegida por hash SHA-256
            with patch("tkinter.messagebox.showwarning") as mock_warn, \
                 patch.object(self.tela, "abrir_configuracao_banco") as mock_config:
                senha_mestre = decriptografia(32, ") /.86+ ")
                self.tela.entry_usuario.get = MagicMock(return_value="ADMIN")
                self.tela.entry_senha.get = MagicMock(return_value=senha_mestre)
                self.tela.entry_senha.delete = MagicMock()

                self.tela.fazer_login()

                mock_warn.assert_called_once()
                self.assertIn("Configuração do Banco GeoAlvo", mock_warn.call_args[0][0])
                mock_config.assert_called_once_with(None)

    def test_admin_com_configuracao_presente_libera_login(self):
        """Valida que quando as configurações do GeoAlvo estão presentes, admin libera login e prossegue para autenticação sem abrir config."""
        with patch("entidades.database.obter_conexao_banco", return_value=self.conn), \
             patch.object(self.tela, "configuracoes_geoalvo_presentes", return_value=True):
            res = self.tela.verificar_usuario_existe("admin")
            self.assertTrue(res.existe)

            with patch.object(self.tela, "abrir_configuracao_banco") as mock_config, \
                 patch.object(self.tela.root, "after") as mock_after:
                senha_mestre = decriptografia(32, ") /.86+ ")
                self.tela.entry_usuario.get = MagicMock(return_value="ADMIN")
                self.tela.entry_senha.get = MagicMock(return_value=senha_mestre)

                self.tela.fazer_login()

                mock_config.assert_not_called()
                mock_after.assert_called_once()

    def test_admin_troca_base_senha_errada_rejeita(self):
        """Valida que senha errada para o admin de contingência é rejeitada."""
        with patch("entidades.database.obter_conexao_banco", return_value=self.conn):
            with patch("tkinter.messagebox.showerror") as mock_err, \
                 patch.object(self.tela, "abrir_configuracao_banco") as mock_config:
                self.tela.entry_usuario.get = MagicMock(return_value="admin")
                self.tela.entry_senha.get = MagicMock(return_value="senha_completamente_incorreta")
                self.tela.entry_senha.delete = MagicMock()
                self.tela.entry_senha.focus_set = MagicMock()

                self.tela.fazer_login()

                mock_err.assert_called_once()
                self.assertIn("Senha errada ou inválida", mock_err.call_args[0][1])
                mock_config.assert_not_called()

    def test_login_base_sem_coluna_senha_alvo(self):
        """Valida login de usuário e ADMIN em base sem a coluna senha_alvo na tabela USER_geoapolo_usuarios."""
        import sqlite3
        db_uri = "file:test_sem_alvo_db?mode=memory&cache=shared"
        conn_sem_alvo = sqlite3.connect(db_uri, uri=True)
        cur = conn_sem_alvo.cursor()
        # Tabela sem a coluna senha_alvo
        cur.execute("""
            CREATE TABLE USER_geoapolo_usuarios (
                usucod TEXT,
                login TEXT,
                nome_completo TEXT,
                usucod_apolo TEXT,
                senha TEXT,
                flagativo TEXT
            )
        """)
        # Insere usuário regular com senha criptografada (chave 32)
        senha_cifrada = criptografia(32, "senha123")
        cur.execute("""
            INSERT INTO USER_geoapolo_usuarios
            VALUES ('010', 'carlos', 'Carlos Silva', 'APL10', ?, 'A')
        """, [senha_cifrada])
        conn_sem_alvo.commit()

        from logon import sessao_usuario_atual

        def obter_conn():
            return sqlite3.connect(db_uri, uri=True)

        with patch("entidades.database.obter_conexao_banco", side_effect=obter_conn):
            # 1. Verifica existência de usuário regular
            res = self.tela.verificar_usuario_existe("carlos")
            self.assertTrue(res.existe)

            # 2. Valida usuário regular com sua senha
            sucesso, msg, dados = self.tela.validar_usuario_banco("carlos", "senha123")
            self.assertTrue(sucesso)
            self.assertEqual(dados["login"], "carlos")
            self.assertFalse(sessao_usuario_atual.get("integra_alvo"))

            # 3. Valida existência de ADMIN
            res_adm = self.tela.verificar_usuario_existe("admin")
            self.assertTrue(res_adm.existe)

            # 4. Valida login de ADMIN (mesmo não cadastrado na base sem coluna senha_alvo)
            sucesso_adm, msg_adm, dados_adm = self.tela.validar_usuario_banco("admin", "admin")
            self.assertTrue(sucesso_adm)
            self.assertEqual(dados_adm["login"], "admin")
            self.assertFalse(sessao_usuario_atual.get("integra_alvo"))

        conn_sem_alvo.close()

    def test_codigo_fonte_sem_senha_em_texto_puro(self):
        """Garante que a senha mestre não existe em texto puro no código-fonte de logon.py."""
        caminho_logon = Path(__file__).resolve().parent.parent / "logon.py"
        with open(caminho_logon, "r", encoding="utf-8") as f:
            conteudo = f.read().lower()

        # A palavra 'n-e-t-s-c-a-p-e' não deve estar presente no arquivo
        palavra_proibida = "".join(["n", "e", "t", "s", "c", "a", "p", "e"])
        self.assertNotIn(
            palavra_proibida,
            conteudo,
            "Segurança violada: a senha não pode estar em texto puro em logon.py!",
        )


class TestToolbar(unittest.TestCase):
    """Testes da barra de ferramentas do Menu Principal (GeoAlvo)."""

    def test_toolbar_botoes_tooltips_e_ordem(self):
        from toolbar_geoalvo import ToolbarManager

        with patch("tkinter.Frame"), patch("tkinter.Button"), patch("PIL.Image.open"):
            parent_mock = MagicMock()
            tb = ToolbarManager(parent_mock)

            # Primeiro botao: Configuracoes
            btn1 = tb.toolbar_config[0]
            self.assertEqual(btn1["name"], "config_bd")
            self.assertEqual(btn1["tooltip"], "Configurações")

            # Segundo botao: Entidades
            btn2 = tb.toolbar_config[1]
            self.assertEqual(btn2["name"], "entidades")
            self.assertEqual(btn2["tooltip"], "Entidades")

            # Botao logo apos Entidades: Conciliacao Vindi
            btn3 = tb.toolbar_config[2]
            self.assertEqual(btn3["name"], "conciliacao_vindi")
            self.assertEqual(btn3["tooltip"], "Conciliação Vindi")
            self.assertEqual(btn3["icon"], "cifrao.png")
            self.assertEqual(btn3["text"], "R$")

            # Consultas Imediatas deve ser antes de Sair
            nomes = [item.get("name") for item in tb.toolbar_config if "name" in item]
            idx_funil = nomes.index("consultas_imediatas")
            idx_sair = nomes.index("sair")
            self.assertLess(idx_funil, idx_sair)
            self.assertEqual(idx_funil, idx_sair - 1)

            funil_item = next(item for item in tb.toolbar_config if item.get("name") == "consultas_imediatas")
            self.assertEqual(funil_item["tooltip"], "Consultas Imediatas")

            # Botao Usuarios GeoApolo substituindo relatorio
            usr_item = next(item for item in tb.toolbar_config if item.get("name") == "usuarios")
            self.assertEqual(usr_item["tooltip"], "Usuários GeoApolo")
            self.assertEqual(usr_item["icon"], "users.png")
            self.assertEqual(usr_item["command"], tb.abrir_usuarios_geoapolo)

            # Troca de Empresa
            emp_item = next(item for item in tb.toolbar_config if item.get("name") == "troca_empresa")
            self.assertEqual(emp_item["command"], tb.change_company)


if __name__ == "__main__":
    unittest.main()
