"""
Testes Unitários para o Módulo de Unificação de Cadastros (MatchCode).
GeoApolo V5
"""

import sqlite3
import unittest
from unittest.mock import MagicMock

from matchcode.models import (
    MatchCodeUsuarioDTO,
    MatchCodeEntidadeDTO,
    ResultadoMatchCodeDTO,
)
from matchcode.repository import MatchCodeRepository
from matchcode.service import MatchCodeService


class TestMatchCodeRepositorySQLite(unittest.TestCase):
    """Testes de fusão com banco SQLite em memória."""

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self._criar_schema()
        self._popular_dados()
        self.repo = MatchCodeRepository(self.conn)

    def tearDown(self):
        self.conn.close()

    def _criar_schema(self):
        cur = self.conn.cursor()
        cur.executescript("""
            CREATE TABLE USER_geoapolo_usuarios (
                usucod TEXT PRIMARY KEY,
                nome_completo TEXT,
                flagativo TEXT
            );

            CREATE TABLE USER_geoapolo_grupousuario (
                codigo_grupo TEXT,
                usucod TEXT,
                PRIMARY KEY (codigo_grupo, usucod)
            );

            CREATE TABLE USER_geoapolo_usuariossistemas (
                usucod TEXT,
                codigo_sistema TEXT,
                PRIMARY KEY (usucod, codigo_sistema)
            );

            CREATE TABLE USER_geoapolo_permissaoconsulta (
                usucod TEXT,
                codigo_consulta TEXT,
                autorizacao TEXT,
                PRIMARY KEY (usucod, codigo_consulta)
            );

            CREATE TABLE entidade (
                entcod TEXT PRIMARY KEY,
                entnome TEXT
            );

            CREATE TABLE ent_categ (
                entcod TEXT,
                categcodestr TEXT,
                PRIMARY KEY (entcod, categcodestr)
            );

            CREATE TABLE u_entidade (
                entcod TEXT PRIMARY KEY,
                USERDiocese_id TEXT
            );
        """)
        self.conn.commit()

    def _popular_dados(self):
        cur = self.conn.cursor()
        # Usuários
        cur.execute("INSERT INTO USER_geoapolo_usuarios VALUES ('ORIGEM', 'USUARIO DUPLICADO', 'A')")
        cur.execute("INSERT INTO USER_geoapolo_usuarios VALUES ('DESTINO', 'USUARIO PRINCIPAL', 'A')")

        cur.execute("INSERT INTO USER_geoapolo_grupousuario VALUES ('GRP1', 'ORIGEM')")
        cur.execute("INSERT INTO USER_geoapolo_grupousuario VALUES ('GRP2', 'ORIGEM')")
        cur.execute("INSERT INTO USER_geoapolo_grupousuario VALUES ('GRP2', 'DESTINO')")  # GRP2 já existe no destino

        cur.execute("INSERT INTO USER_geoapolo_usuariossistemas VALUES ('ORIGEM', 'SIS1')")
        cur.execute("INSERT INTO USER_geoapolo_permissaoconsulta VALUES ('ORIGEM', 'CONS1', 'S')")

        # Entidades
        cur.execute("INSERT INTO entidade VALUES ('E_ORIG', 'COLABORADOR DUPLICADO')")
        cur.execute("INSERT INTO entidade VALUES ('E_DEST', 'COLABORADOR OFICIAL')")

        cur.execute("INSERT INTO ent_categ VALUES ('E_ORIG', 'CAT_A')")
        cur.execute("INSERT INTO ent_categ VALUES ('E_DEST', 'CAT_B')")
        cur.execute("INSERT INTO u_entidade VALUES ('E_ORIG', 'DIO_01')")

        self.conn.commit()

    def test_obter_usuario_e_entidade(self):
        u = self.repo.obter_usuario("ORIGEM")
        self.assertIsNotNone(u)
        self.assertEqual(u[0], "ORIGEM")
        self.assertEqual(u[1], "USUARIO DUPLICADO")

        e = self.repo.obter_entidade("E_DEST")
        self.assertIsNotNone(e)
        self.assertEqual(e[1], "COLABORADOR OFICIAL")

    def test_matchcode_usuario(self):
        res = self.repo.executar_matchcode_usuario("ORIGEM", "DESTINO")
        self.assertTrue(res.sucesso)

        # Verifica que origem foi deletado
        self.assertIsNone(self.repo.obter_usuario("ORIGEM"))

        cur = self.conn.cursor()
        # Grupos no destino: deve ter GRP1 e GRP2 (sem erro de primary key)
        cur.execute("SELECT codigo_grupo FROM USER_geoapolo_grupousuario WHERE usucod = 'DESTINO' ORDER BY codigo_grupo")
        grupos = [r[0] for r in cur.fetchall()]
        self.assertEqual(grupos, ["GRP1", "GRP2"])

        # Sistemas no destino: deve ter SIS1
        cur.execute("SELECT codigo_sistema FROM USER_geoapolo_usuariossistemas WHERE usucod = 'DESTINO'")
        self.assertEqual(cur.fetchone()[0], "SIS1")

        # Permissão de consulta no destino
        cur.execute("SELECT codigo_consulta FROM USER_geoapolo_permissaoconsulta WHERE usucod = 'DESTINO'")
        self.assertEqual(cur.fetchone()[0], "CONS1")

    def test_matchcode_entidade(self):
        res = self.repo.executar_matchcode_entidade("E_ORIG", "E_DEST")
        self.assertTrue(res.sucesso)

        # Entidade de origem removida
        self.assertIsNone(self.repo.obter_entidade("E_ORIG"))

        # Destino possui CAT_A e CAT_B
        cur = self.conn.cursor()
        cur.execute("SELECT categcodestr FROM ent_categ WHERE entcod = 'E_DEST' ORDER BY categcodestr")
        cats = [r[0] for r in cur.fetchall()]
        self.assertEqual(cats, ["CAT_A", "CAT_B"])


class TestMatchCodeService(unittest.TestCase):
    """Testes das regras de validação do MatchCodeService."""

    def setUp(self):
        self.mock_repo = MagicMock(spec=MatchCodeRepository)
        self.service = MatchCodeService(self.mock_repo)

    def test_unificar_usuarios_mesmo_codigo(self):
        res = self.service.unificar_usuarios("USER1", "USER1")
        self.assertFalse(res.sucesso)
        self.assertIn("não podem ser iguais", res.mensagem)
        self.mock_repo.executar_matchcode_usuario.assert_not_called()

    def test_unificar_usuarios_origem_nao_encontrada(self):
        self.mock_repo.obter_usuario.side_effect = lambda cod: None if cod == "INEX" else ("DEST", "Nome", "A")
        res = self.service.unificar_usuarios("INEX", "DEST")
        self.assertFalse(res.sucesso)
        self.assertIn("não encontrado", res.mensagem)

    def test_unificar_usuarios_sucesso(self):
        self.mock_repo.obter_usuario.side_effect = lambda cod: (cod, f"Nome {cod}", "A")
        self.mock_repo.executar_matchcode_usuario.return_value = ResultadoMatchCodeDTO(
            sucesso=True, mensagem="Mesclado com sucesso", tabelas_afetadas=3, registros_migrados=5
        )

        res = self.service.unificar_usuarios("U_ORIG", "U_DEST")
        self.assertTrue(res.sucesso)
        self.assertEqual(res.registros_migrados, 5)
        self.mock_repo.executar_matchcode_usuario.assert_called_once_with("U_ORIG", "U_DEST")


if __name__ == "__main__":
    unittest.main()
