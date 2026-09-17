"""
Testes Unitários para o Módulo de Gestão de Usuários, Grupos e Perfis de Acesso.
GeoApolo V5
"""

import sqlite3
import unittest
from unittest.mock import MagicMock

from usuarios.models import (
    UsuarioDTO,
    DepartamentoDTO,
    SistemaDTO,
    GrupoUsuarioDTO,
    VinculoGrupoUsuarioDTO,
    ObjetoAcessoDTO,
    PerfilAcessoItemDTO,
    ResultadoOperacaoUsuario,
)
from usuarios.repository import UsuariosRepository
from usuarios.service import UsuariosService


class TestUsuarioModels(unittest.TestCase):
    """Testes dos DTOs e propriedades de Usuários, Grupos e Perfis."""

    def test_usuario_dto_propriedades(self):
        u_ativo = UsuarioDTO(usucod="USR01", login="julio", nome_completo="Julio Santos", flagativo="A")
        self.assertTrue(u_ativo.ativo)
        self.assertEqual(u_ativo.status_display, "Ativo")

        u_inativo = UsuarioDTO(usucod="USR02", login="pedro", nome_completo="Pedro Silva", flagativo="I")
        self.assertFalse(u_inativo.ativo)
        self.assertEqual(u_inativo.status_display, "Inativo")

    def test_perfil_item_dto_propriedades(self):
        item_lib = PerfilAcessoItemDTO(
            codigo_objeto="OBJ01",
            nome_objeto="frmUsuarios",
            nome_amigavel="Tela de Usuários",
            statusacesso="A"
        )
        self.assertTrue(item_lib.liberado)
        self.assertEqual(item_lib.status_display, "Liberado")

        item_bloq = PerfilAcessoItemDTO(
            codigo_objeto="OBJ02",
            nome_objeto="frmAuditoria",
            nome_amigavel="Auditoria Fiscal",
            statusacesso="N"
        )
        self.assertFalse(item_bloq.liberado)
        self.assertEqual(item_bloq.status_display, "Bloqueado")


class TestUsuariosRepositorySQLite(unittest.TestCase):
    """Testes de repositório com banco SQLite em memória."""

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self._criar_schema()
        self._popular_dados()
        self.repo = UsuariosRepository(self.conn)

    def tearDown(self):
        self.conn.close()

    def _criar_schema(self):
        cur = self.conn.cursor()
        cur.executescript("""
            CREATE TABLE USER_geoapolo_empresas (
                empcod TEXT PRIMARY KEY,
                empnome TEXT
            );

            CREATE TABLE USER_geoapolo_departamentos (
                codigo_departamento TEXT PRIMARY KEY,
                nome_departamento TEXT,
                empcod TEXT,
                flagativo TEXT
            );

            CREATE TABLE USER_geoapolo_usuarios (
                codigo_usuario TEXT,
                usucod TEXT PRIMARY KEY,
                nome_completo TEXT,
                flagativo TEXT,
                login TEXT,
                email TEXT,
                data_nascimento TEXT,
                codigo_departamento TEXT,
                usucod_apolo TEXT,
                senha_alvo TEXT,
                senha TEXT
            );

            CREATE TABLE USER_geoapolo_sistemas (
                codigo_sistema TEXT PRIMARY KEY,
                descricao TEXT,
                sigla TEXT
            );

            CREATE TABLE USER_geoapolo_usuariossistemas (
                usucod TEXT,
                codigo_sistema TEXT,
                PRIMARY KEY (usucod, codigo_sistema)
            );

            CREATE TABLE USER_geoapolo_grupo (
                codigo_grupo TEXT PRIMARY KEY,
                descricao TEXT
            );

            CREATE TABLE USER_geoapolo_grupousuario (
                codigo_grupo TEXT,
                usucod TEXT,
                PRIMARY KEY (codigo_grupo, usucod)
            );

            CREATE TABLE USER_geoapolo_objetos (
                codigo_objeto TEXT PRIMARY KEY,
                nome_objeto TEXT,
                nome_amigavel TEXT,
                categoria TEXT
            );

            CREATE TABLE USER_geoapolo_grupobjetos (
                codigo_grupo TEXT,
                codigo_objeto TEXT,
                statusacesso TEXT,
                PRIMARY KEY (codigo_grupo, codigo_objeto)
            );
        """)
        self.conn.commit()

    def _popular_dados(self):
        cur = self.conn.cursor()
        # Empresas e Deptos
        cur.execute("INSERT INTO USER_geoapolo_empresas VALUES ('EMP01', 'SEDE PRINCIPAL')")
        cur.execute("INSERT INTO USER_geoapolo_departamentos VALUES ('DEP01', 'TECNOLOGIA', 'EMP01', 'S')")
        cur.execute("INSERT INTO USER_geoapolo_departamentos VALUES ('DEP02', 'FINANCEIRO', 'EMP01', 'S')")

        # Usuários
        cur.execute("""
            INSERT INTO USER_geoapolo_usuarios VALUES
            ('1', 'USR01', 'JULIO CESAR', 'A', 'julio', 'julio@sdit.com.br', '1990-01-01', 'DEP01', 'APL01', 'HASH1', 'PWD1')
        """)
        cur.execute("""
            INSERT INTO USER_geoapolo_usuarios VALUES
            ('2', 'USR02', 'CARLOS EDUARDO', 'I', 'carlos', 'carlos@empresa.com', '1985-05-10', 'DEP02', '', 'HASH2', 'PWD2')
        """)

        # Sistemas
        cur.execute("INSERT INTO USER_geoapolo_sistemas VALUES ('SIS01', 'GeoApolo Desktop', 'GEO')")
        cur.execute("INSERT INTO USER_geoapolo_sistemas VALUES ('SIS02', 'GeoAlvo CRM', 'ALV')")
        cur.execute("INSERT INTO USER_geoapolo_usuariossistemas VALUES ('USR01', 'SIS01')")

        # Grupos
        cur.execute("INSERT INTO USER_geoapolo_grupo VALUES ('GRP01', 'ADMINISTRADORES')")
        cur.execute("INSERT INTO USER_geoapolo_grupo VALUES ('GRP02', 'OPERADORES')")
        cur.execute("INSERT INTO USER_geoapolo_grupousuario VALUES ('GRP01', 'USR01')")

        # Objetos & Permissões
        cur.execute("INSERT INTO USER_geoapolo_objetos VALUES ('OBJ01', 'frmUsuarios', 'Cadastro de Usuários', 'Segurança')")
        cur.execute("INSERT INTO USER_geoapolo_objetos VALUES ('OBJ02', 'frmConciliaVindi', 'Conciliação Vindi', 'Financeiro')")
        cur.execute("INSERT INTO USER_geoapolo_grupobjetos VALUES ('GRP01', 'OBJ01', 'A')")
        cur.execute("INSERT INTO USER_geoapolo_grupobjetos VALUES ('GRP01', 'OBJ02', 'N')")

        self.conn.commit()

    def test_listar_usuarios_ativos(self):
        users = self.repo.listar_usuarios(apenas_ativos=True)
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].usucod, "USR01")
        self.assertEqual(users[0].nome_departamento, "TECNOLOGIA")

    def test_listar_todos_usuarios(self):
        users = self.repo.listar_usuarios(apenas_ativos=False)
        self.assertEqual(len(users), 2)

    def test_obter_usuario_por_usucod_e_login(self):
        u1 = self.repo.obter_usuario_por_usucod("USR01")
        self.assertIsNotNone(u1)
        self.assertEqual(u1.login, "julio")

        u2 = self.repo.obter_usuario_por_login("carlos")
        self.assertIsNotNone(u2)
        self.assertEqual(u2.usucod, "USR02")

        inex = self.repo.obter_usuario_por_login("inexistente")
        self.assertIsNone(inex)

    def test_salvar_novo_usuario(self):
        novo = UsuarioDTO(
            codigo_usuario="3",
            usucod="USR03",
            nome_completo="MARIANA SOUZA",
            login="mariana",
            email="mariana@empresa.com",
            codigo_departamento="DEP01",
            flagativo="A"
        )
        sucesso = self.repo.salvar_usuario(novo)
        self.assertTrue(sucesso)

        buscado = self.repo.obter_usuario_por_usucod("USR03")
        self.assertIsNotNone(buscado)
        self.assertEqual(buscado.nome_completo, "MARIANA SOUZA")

    def test_atualizar_usuario(self):
        u = self.repo.obter_usuario_por_usucod("USR01")
        u.nome_completo = "JULIO CESAR DOS SANTOS"
        u.email = "novo_email@sdit.com.br"
        self.repo.salvar_usuario(u)

        atualizado = self.repo.obter_usuario_por_usucod("USR01")
        self.assertEqual(atualizado.nome_completo, "JULIO CESAR DOS SANTOS")
        self.assertEqual(atualizado.email, "novo_email@sdit.com.br")

    def test_excluir_usuario(self):
        sucesso = self.repo.excluir_usuario("USR01")
        self.assertTrue(sucesso)
        self.assertIsNone(self.repo.obter_usuario_por_usucod("USR01"))

        # Verifica limpeza de sistemas e grupos
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM USER_geoapolo_usuariossistemas WHERE usucod = 'USR01'")
        self.assertEqual(cur.fetchone()[0], 0)
        cur.execute("SELECT COUNT(*) FROM USER_geoapolo_grupousuario WHERE usucod = 'USR01'")
        self.assertEqual(cur.fetchone()[0], 0)

    def test_departamentos_e_sistemas(self):
        deptos = self.repo.listar_departamentos()
        self.assertEqual(len(deptos), 2)

        sistemas = self.repo.listar_sistemas()
        self.assertEqual(len(sistemas), 2)

        sis_user = self.repo.listar_sistemas_usuario("USR01")
        self.assertEqual(len(sis_user), 1)
        self.assertEqual(sis_user[0].codigo_sistema, "SIS01")

        # Vincular SIS02
        self.repo.vincular_sistema_usuario("USR01", "SIS02")
        sis_user2 = self.repo.listar_sistemas_usuario("USR01")
        self.assertEqual(len(sis_user2), 2)

        # Desvincular SIS01
        self.repo.desvincular_sistema_usuario("USR01", "SIS01")
        sis_user3 = self.repo.listar_sistemas_usuario("USR01")
        self.assertEqual(len(sis_user3), 1)
        self.assertEqual(sis_user3[0].codigo_sistema, "SIS02")

    def test_grupos_e_membros(self):
        grupos = self.repo.listar_grupos()
        self.assertEqual(len(grupos), 2)
        # GRP01 tem 1 usuário, GRP02 tem 0
        g1 = next(g for g in grupos if g.codigo_grupo == "GRP01")
        self.assertEqual(g1.total_usuarios, 1)

        # Adiciona USR02 no GRP01
        self.repo.vincular_usuario_grupo("GRP01", "USR02")
        membros = self.repo.listar_usuarios_grupo("GRP01")
        self.assertEqual(len(membros), 2)

        # Remove USR01 do GRP01
        self.repo.desvincular_usuario_grupo("GRP01", "USR01")
        membros_apos = self.repo.listar_usuarios_grupo("GRP01")
        self.assertEqual(len(membros_apos), 1)
        self.assertEqual(membros_apos[0].usucod, "USR02")

    def test_objetos_e_permissoes_perfil(self):
        perfis = self.repo.listar_objetos_perfil("GRP01")
        self.assertEqual(len(perfis), 2)
        p_obj1 = next(p for p in perfis if p.codigo_objeto == "OBJ01")
        self.assertTrue(p_obj1.liberado)

        p_obj2 = next(p for p in perfis if p.codigo_objeto == "OBJ02")
        self.assertFalse(p_obj2.liberado)

        # Liberar OBJ02 para GRP01
        self.repo.atualizar_status_acesso("GRP01", "OBJ02", "A")
        perfis_atualizados = self.repo.listar_objetos_perfil("GRP01")
        p_obj2_att = next(p for p in perfis_atualizados if p.codigo_objeto == "OBJ02")
        self.assertTrue(p_obj2_att.liberado)


class TestUsuariosService(unittest.TestCase):
    """Testes de regras de negócio do UsuariosService com Mocks."""

    def setUp(self):
        self.mock_repo = MagicMock(spec=UsuariosRepository)
        self.service = UsuariosService(self.mock_repo)

    def test_salvar_usuario_validacao_campos_obrigatorios(self):
        # usucod vazio
        u1 = UsuarioDTO(usucod="", login="teste", nome_completo="Nome")
        r1 = self.service.salvar_usuario(u1)
        self.assertFalse(r1.sucesso)
        self.assertIn("usucod", r1.mensagem)

        # login vazio
        u2 = UsuarioDTO(usucod="U1", login="", nome_completo="Nome")
        r2 = self.service.salvar_usuario(u2)
        self.assertFalse(r2.sucesso)
        self.assertIn("login", r2.mensagem)

        # nome vazio
        u3 = UsuarioDTO(usucod="U1", login="login", nome_completo="")
        r3 = self.service.salvar_usuario(u3)
        self.assertFalse(r3.sucesso)
        self.assertIn("nome completo", r3.mensagem)

    def test_salvar_usuario_login_duplicado(self):
        # Usuário existente com mesmo login mas outro usucod
        existente = UsuarioDTO(usucod="OUTRO_USER", login="julio", nome_completo="Outro Julio")
        self.mock_repo.obter_usuario_por_login.return_value = existente

        u_novo = UsuarioDTO(usucod="MEU_USER", login="julio", nome_completo="Novo Julio")
        res = self.service.salvar_usuario(u_novo)

        self.assertFalse(res.sucesso)
        self.assertIn("já está em uso por outro colaborador", res.mensagem)
        self.mock_repo.salvar_usuario.assert_not_called()

    def test_salvar_usuario_sucesso(self):
        self.mock_repo.obter_usuario_por_login.return_value = None
        self.mock_repo.salvar_usuario.return_value = True

        u = UsuarioDTO(usucod="U10", login="u10", nome_completo="Usuario Dez")
        res = self.service.salvar_usuario(u)

        self.assertTrue(res.sucesso)
        self.assertEqual(res.id_gerado, "U10")
        self.mock_repo.salvar_usuario.assert_called_once()

    def test_excluir_usuario_validacoes(self):
        # Código vazio
        r1 = self.service.excluir_usuario("")
        self.assertFalse(r1.sucesso)

        # Usuário inexistente
        self.mock_repo.obter_usuario_por_usucod.return_value = None
        r2 = self.service.excluir_usuario("INEX")
        self.assertFalse(r2.sucesso)
        self.assertIn("não localizado", r2.mensagem)

        # Exclusão com sucesso
        self.mock_repo.obter_usuario_por_usucod.return_value = UsuarioDTO(usucod="U1", login="u1", nome_completo="Nome")
        self.mock_repo.excluir_usuario.return_value = True
        r3 = self.service.excluir_usuario("U1")
        self.assertTrue(r3.sucesso)

    def test_salvar_grupo_validacao(self):
        r1 = self.service.salvar_grupo("", "Descricao")
        self.assertFalse(r1.sucesso)
        self.assertIn("código do grupo", r1.mensagem)

        r2 = self.service.salvar_grupo("G1", "")
        self.assertFalse(r2.sucesso)
        self.assertIn("descrição do grupo", r2.mensagem)

        self.mock_repo.salvar_grupo.return_value = True
        r3 = self.service.salvar_grupo("G1", "Diretoria")
        self.assertTrue(r3.sucesso)

    def test_atualizar_acesso_liberado_e_bloqueado(self):
        self.mock_repo.atualizar_status_acesso.return_value = True

        res_lib = self.service.atualizar_acesso("G1", "OBJ1", liberado=True)
        self.assertTrue(res_lib.sucesso)
        self.mock_repo.atualizar_status_acesso.assert_called_with("G1", "OBJ1", "A")

        res_bloq = self.service.atualizar_acesso("G1", "OBJ1", liberado=False)
        self.assertTrue(res_bloq.sucesso)
        self.mock_repo.atualizar_status_acesso.assert_called_with("G1", "OBJ1", "N")


if __name__ == "__main__":
    unittest.main()
