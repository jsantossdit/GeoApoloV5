"""
Testes unitários para os 5 ajustes da Gestão de Usuários, Grupos, Permissões e Nomes Amigáveis:
1. Modalidade e retenção de foco nos diálogos
2. Padronização de maiúsculas na aba de grupos
3. geoapolo_configcod com chave primária correta (codigo_grupo) e navegação com Enter
4. Auto-seeding de objetos em bases novas
5. Resiliência e migração da coluna categoria / nome_amigavel em USER_geoapolo_objetos
"""

import sqlite3
import unittest
from unittest.mock import MagicMock, patch

from core.recursos import geoapolo_configcod, configurar_navegacao_enter, vincular_maiusculo
from usuarios.repository import UsuariosRepository, CATALOGO_OBJETOS_SISTEMA
from usuarios.models import UsuarioDTO
from usuarios.service import UsuariosService
from nomesamigaveis.repository import NomesAmigaveisRepository
from nomesamigaveis.models import ObjetoSistemaDTO


class TestAjustesUsuariosPermissoes(unittest.TestCase):
    """Bateria de testes unitários para as novas funcionalidades implementadas."""

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.cur = self.conn.cursor()

        # Criação das tabelas base
        self.cur.execute("""
            CREATE TABLE USER_geoapolo_configcod (
                empcod TEXT,
                geotabela TEXT,
                tabela_ativa TEXT,
                proximo_codigo INTEGER,
                ultimo_numero_utilizado INTEGER,
                PRIMARY KEY (empcod, geotabela)
            )
        """)

        self.cur.execute("""
            CREATE TABLE USER_geoapolo_departamentos (
                codigo_departamento TEXT PRIMARY KEY,
                nome_departamento TEXT,
                empcod TEXT,
                flagativo TEXT
            )
        """)

        self.cur.execute("""
            CREATE TABLE USER_geoapolo_grupo (
                codigo_grupo INTEGER PRIMARY KEY,
                descricao TEXT
            )
        """)

        self.cur.execute("""
            CREATE TABLE USER_geoapolo_usuarios (
                codigo_usuario TEXT PRIMARY KEY,
                usucod TEXT,
                nome_completo TEXT,
                flagativo TEXT,
                login TEXT,
                email TEXT,
                data_nascimento TEXT,
                codigo_departamento TEXT,
                usucod_apolo TEXT,
                senha_alvo TEXT,
                senha TEXT
            )
        """)

        self.cur.execute("""
            CREATE TABLE USER_geoapolo_grupousuario (
                codigo_grupo TEXT,
                usucod TEXT,
                PRIMARY KEY (codigo_grupo, usucod)
            )
        """)

        self.cur.execute("""
            CREATE TABLE USER_geoapolo_grupobjetos (
                codigo_grupo TEXT,
                codigo_objeto TEXT,
                statusacesso TEXT,
                PRIMARY KEY (codigo_grupo, codigo_objeto)
            )
        """)

        # Tabela de objetos criada INICIALMENTE no formato antigo do Delphi (sem categoria nem nome_amigavel)
        self.cur.execute("""
            CREATE TABLE USER_geoapolo_objetos (
                codigo_objeto TEXT PRIMARY KEY,
                nome_objeto TEXT,
                nome_oficial TEXT
            )
        """)

        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def test_geoapolo_configcod_grupo_detecta_codigo_grupo(self):
        """Testa geração de próximo código sequencial para USER_geoapolo_grupo."""
        # Insere grupos existentes 1 e 5
        self.cur.execute("INSERT INTO USER_geoapolo_grupo VALUES (1, 'ADMINISTRADORES')")
        self.cur.execute("INSERT INTO USER_geoapolo_grupo VALUES (5, 'FINANCEIRO')")
        self.conn.commit()

        # Sem registro em USER_geoapolo_configcod: deve pegar MAX(codigo_grupo) + 1 = 6
        prox = geoapolo_configcod(empresa="1", tabela="USER_geoapolo_grupo", atualiza="Sim", connection=self.conn)
        self.assertEqual(prox, "6")

        # Verifica se gravou em USER_geoapolo_configcod com proximo_codigo=7
        self.cur.execute("SELECT proximo_codigo, ultimo_numero_utilizado FROM USER_geoapolo_configcod WHERE geotabela = 'USER_geoapolo_grupo'")
        row = self.cur.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 7)
        self.assertEqual(row[1], 6)

        # Próxima chamada deve retornar 7
        prox2 = geoapolo_configcod(empresa="1", tabela="USER_geoapolo_grupo", atualiza="Sim", connection=self.conn)
        self.assertEqual(prox2, "7")

    def test_seeding_em_base_nova_e_migracao_colunas(self):
        """Testa auto-seeding quando USER_geoapolo_objetos está vazia e migração de categoria."""
        self.cur.execute("INSERT INTO USER_geoapolo_grupo VALUES (1, 'ADMIN')")
        self.cur.execute("INSERT INTO USER_geoapolo_grupo VALUES (2, 'OPERADORES')")
        self.conn.commit()

        repo = UsuariosRepository(self.conn)

        # A tabela não tinha 'categoria' nem 'nome_amigavel'
        # Ao sincronizar/listar, deve adicionar as colunas e popular o catálogo completo
        qtd_inseridos = repo.sincronizar_ou_inicializar_objetos("1")
        self.assertEqual(qtd_inseridos, len(CATALOGO_OBJETOS_SISTEMA))

        # Verifica se as colunas foram criadas na tabela
        cols = repo._obter_colunas("USER_geoapolo_objetos")
        self.assertIn("categoria", cols)
        self.assertIn("nome_amigavel", cols)

        # Verifica se os objetos e categorias foram carregados
        categorias = repo.listar_categorias_objetos()
        self.assertIn("Menu Principal", categorias)
        self.assertIn("Barra de Ferramentas", categorias)
        self.assertIn("Configurações", categorias)

        # Verifica se grupo ADMIN recebe status 'A' (Liberado) por padrão
        objetos_admin = repo.listar_objetos_perfil("1")
        self.assertEqual(len(objetos_admin), len(CATALOGO_OBJETOS_SISTEMA))
        for item in objetos_admin:
            self.assertEqual(item.statusacesso, "A")

        # Verifica se grupo OPERADORES recebe status 'N' (Bloqueado) por padrão
        objetos_oper = repo.listar_objetos_perfil("2")
        self.assertEqual(len(objetos_oper), len(CATALOGO_OBJETOS_SISTEMA))
        for item in objetos_oper:
            self.assertEqual(item.statusacesso, "N")

    def test_sincronizacao_incremental_atualiza_nomes_genericos_e_insere_novos(self):
        """Testa que sincronização incremental atualiza classes Delphi genéricas para nomes amigáveis oficiais."""
        repo = UsuariosRepository(self.conn)
        repo._garantir_estrutura_tabela_objetos()

        # Cria objeto pré-existente com classe Delphi genérica
        self.cur.execute("""
            INSERT INTO USER_geoapolo_objetos (codigo_objeto, nome_objeto, nome_amigavel, categoria)
            VALUES ('1', 'pnlmenuprincipal', 'TPanel', 'TPanel')
        """)
        self.conn.commit()

        repo.sincronizar_ou_inicializar_objetos("1", apenas_se_vazia=False)

        # Verifica que pnlmenuprincipal foi atualizado com o nome amigável e categoria oficiais
        self.cur.execute("SELECT nome_amigavel, categoria FROM USER_geoapolo_objetos WHERE UPPER(nome_objeto) = 'PNLMENUPRINCIPAL'")
        row = self.cur.fetchone()
        self.assertEqual(row[0], "Barra de Ferramentas Principal")
        self.assertEqual(row[1], "Barra de Ferramentas")

        # Verifica que mnuprincipal foi inserido
        self.cur.execute("SELECT nome_amigavel, categoria FROM USER_geoapolo_objetos WHERE UPPER(nome_objeto) = 'MNUPRINCIPAL'")
        row_mnu = self.cur.fetchone()
        self.assertIsNotNone(row_mnu)
        self.assertEqual(row_mnu[0], "Menu Principal")
        self.assertEqual(row_mnu[1], "Menu Principal")


    def test_nomesamigaveis_resiliencia_coluna_categoria(self):
        """Testa que NomesAmigaveisRepository funciona mesmo em tabela que inicialmente não possui categoria."""
        repo_nom = NomesAmigaveisRepository(connection=self.conn)

        # Salva um objeto novo
        dto = ObjetoSistemaDTO(nome_objeto="frmClientes", nome_amigavel="Cadastro de Clientes", categoria="Cadastros")
        sucesso = repo_nom.salvar_objeto(dto)
        self.assertTrue(sucesso)

        # Lista objetos e valida recuperação correta
        objs = repo_nom.listar_objetos()
        self.assertEqual(len(objs), 1)
        self.assertEqual(objs[0].nome_objeto, "frmClientes")
        self.assertEqual(objs[0].nome_amigavel, "Cadastro de Clientes")
        self.assertEqual(objs[0].categoria, "Cadastros")

        # Lista categorias
        cats = repo_nom.listar_categorias()
        self.assertIn("Cadastros", cats)

    def test_configurar_navegacao_enter(self):
        """Testa encadeamento da tecla Enter entre widgets."""
        mock_w1 = MagicMock()
        mock_w2 = MagicMock()
        mock_w3 = MagicMock()

        configurar_navegacao_enter([mock_w1, mock_w2, mock_w3])

        # Verifica se bind foi chamado com <Return> e <KP_Enter> em w1 e w2
        self.assertEqual(mock_w1.bind.call_count, 2)
        self.assertEqual(mock_w2.bind.call_count, 2)

    def test_salvar_usuario_sanitiza_numericos_e_gera_codigo_usuario(self):
        """Valida que novo usuário tem codigo_usuario gerado como int e departamento vazio salvo como None."""
        repo = UsuariosRepository(self.conn)

        # Inserção de usuário com codigo_usuario vazio e departamento vazio
        u = UsuarioDTO(
            usucod="NOVOUSER",
            nome_completo="Novo Usuario de Teste",
            login="novouser",
            codigo_usuario="",
            codigo_departamento="",
            data_nascimento="",
        )
        ok = repo.salvar_usuario(u)
        self.assertTrue(ok)

        # Verifica dados gravados
        self.cur.execute("SELECT codigo_usuario, usucod, codigo_departamento, data_nascimento FROM USER_geoapolo_usuarios WHERE usucod = 'NOVOUSER'")
        row = self.cur.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(int(row[0]), 1)  # Gerado como 1
        self.assertEqual(row[1], "NOVOUSER")
        self.assertIsNone(row[2])    # codigo_departamento vazio -> None/NULL
        self.assertIsNone(row[3])    # data_nascimento vazia -> None/NULL

        # Atualização mantendo codigo_usuario
        u.nome_completo = "Novo Usuario Alterado"
        u.codigo_departamento = "5"
        ok_upd = repo.salvar_usuario(u)
        self.assertTrue(ok_upd)

        self.cur.execute("SELECT codigo_usuario, nome_completo, codigo_departamento FROM USER_geoapolo_usuarios WHERE usucod = 'NOVOUSER'")
        row_upd = self.cur.fetchone()
        self.assertEqual(int(row_upd[0]), 1)
        self.assertEqual(row_upd[1], "Novo Usuario Alterado")
        self.assertEqual(int(row_upd[2]), 5)

    def test_usuarios_view_novo_usuario_reseta_foco_e_codigo(self):
        """Valida que o método _novo_usuario reseta estado e posiciona foco no primeiro campo."""
        from usuarios.view import UsuariosView
        mock_master = MagicMock()
        with patch.object(UsuariosView, "_setup_ui"), patch.object(UsuariosView, "_carregar_dados_iniciais"):
            view = UsuariosView(mock_master)
            view.ent_usucod = MagicMock()
            view.ent_login = MagicMock()
            view.ent_nome = MagicMock()
            view.ent_email = MagicMock()
            view.ent_senha = MagicMock()
            view.cbo_departamento = MagicMock()
            view.var_user_ativo = MagicMock()
            view.tree_users = MagicMock()
            view.tree_users.selection.return_value = ()
            view.tree_sistemas_user = MagicMock()
            view.tree_sistemas_user.get_children.return_value = []
            view._atualizar_visibilidade_btn_decript = MagicMock()
            view._codigo_usuario_atual = "99"

            view._novo_usuario()

            self.assertEqual(view._codigo_usuario_atual, "")
            view.ent_usucod.focus_set.assert_called_once()


if __name__ == "__main__":
    unittest.main()
