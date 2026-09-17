"""
Testes Unitários para o Motor de Consultas Dinâmicas e Gestão de Permissões SQL.
GeoApolo V5
"""

import sqlite3
import unittest
from unittest.mock import MagicMock

from consultas.models import (
    ConsultaConfigDTO,
    PermissaoConsultaDTO,
    FiltroConsultaDTO,
    ResultadoConsultaDTO,
)
from consultas.repository import ConsultasRepository
from consultas.service import ConsultasService


class TestConsultasModels(unittest.TestCase):
    """Testes dos DTOs e propriedades de consultas e permissões."""

    def test_permissao_consulta_dto(self):
        p_aut = PermissaoConsultaDTO(usucod="USER1", codigo_consulta="CONS01", autorizacao="S")
        self.assertTrue(p_aut.autorizado)
        self.assertEqual(p_aut.status_display, "Autorizado")

        p_bloq = PermissaoConsultaDTO(usucod="USER2", codigo_consulta="CONS01", autorizacao="N")
        self.assertFalse(p_bloq.autorizado)
        self.assertEqual(p_bloq.status_display, "Bloqueado")


class TestConsultasRepositorySQLite(unittest.TestCase):
    """Testes do repositório de consultas com banco SQLite em memória."""

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self._criar_schema()
        self._popular_dados()
        self.repo = ConsultasRepository(self.conn)

    def tearDown(self):
        self.conn.close()

    def _criar_schema(self):
        cur = self.conn.cursor()
        cur.executescript("""
            CREATE TABLE USER_geoapolo_consultas (
                codigo_consulta TEXT PRIMARY KEY,
                descricao_consulta TEXT,
                sql_consulta TEXT,
                tipo_consulta TEXT,
                banco_consulta TEXT
            );

            CREATE TABLE USER_geoapolo_permissaoconsulta (
                usucod TEXT,
                codigo_consulta TEXT,
                autorizacao TEXT,
                PRIMARY KEY (usucod, codigo_consulta)
            );

            CREATE TABLE user_geoapolo_cidades (
                geocidcod TEXT PRIMARY KEY,
                cidnomecomp TEXT,
                ufsigla TEXT
            );

            CREATE TABLE USER_geoapolo_contasfinanceiras (
                contafincod TEXT PRIMARY KEY,
                contafinnome TEXT
            );

            CREATE TABLE USER_geoapolo_departamentos (
                codigo_departamento TEXT PRIMARY KEY,
                nome_departamento TEXT
            );

            CREATE TABLE USER_geoapolo_categoria (
                geocategcodestr TEXT PRIMARY KEY,
                geocategnome TEXT
            );

            CREATE TABLE USER_geoapolo_tipologradouro (
                tipolograd TEXT PRIMARY KEY,
                tipologradabrev TEXT
            );

            CREATE TABLE USER_geoapolo_entidade (
                geoentcod TEXT PRIMARY KEY,
                geoentnome TEXT,
                geocidcod TEXT
            );
        """)
        self.conn.commit()

    def _popular_dados(self):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO user_geoapolo_cidades VALUES ('01', 'SAO PAULO', 'SP')")
        cur.execute("INSERT INTO user_geoapolo_cidades VALUES ('02', 'LORENA', 'SP')")

        cur.execute("INSERT INTO USER_geoapolo_contasfinanceiras VALUES ('CF01', 'BANCO DO BRASIL')")
        cur.execute("INSERT INTO USER_geoapolo_departamentos VALUES ('D01', 'CONTABILIDADE')")
        cur.execute("INSERT INTO USER_geoapolo_categoria VALUES ('CAT01', 'FORNECEDOR')")
        cur.execute("INSERT INTO USER_geoapolo_tipologradouro VALUES ('RUA', 'R.')")
        cur.execute("INSERT INTO USER_geoapolo_entidade VALUES ('E01', 'EMPRESA ALVO LTDA', '01')")

        cur.execute("""
            INSERT INTO USER_geoapolo_consultas VALUES
            ('CONS_CIDADES', 'Consulta de Cidades', 'SELECT * FROM user_geoapolo_cidades', 'T', 'Apolo')
        """)
        cur.execute("""
            INSERT INTO USER_geoapolo_permissaoconsulta VALUES ('ADMIN', 'CONS_CIDADES', 'S')
        """)
        self.conn.commit()

    def test_listar_consultas(self):
        consultas = self.repo.listar_consultas()
        self.assertEqual(len(consultas), 1)
        self.assertEqual(consultas[0].codigo_consulta, "CONS_CIDADES")

    def test_salvar_e_obter_consulta(self):
        c = ConsultaConfigDTO(
            codigo_consulta="CONS_CONTAS",
            descricao_consulta="Consulta de Contas",
            sql_consulta="SELECT * FROM USER_geoapolo_contasfinanceiras",
            banco_consulta="Apolo"
        )
        self.repo.salvar_consulta(c)

        buscado = self.repo.obter_consulta("CONS_CONTAS")
        self.assertIsNotNone(buscado)
        self.assertEqual(buscado.descricao_consulta, "Consulta de Contas")

    def test_excluir_consulta(self):
        self.repo.excluir_consulta("CONS_CIDADES")
        self.assertIsNone(self.repo.obter_consulta("CONS_CIDADES"))

    def test_permissoes_consulta(self):
        perms = self.repo.listar_permissoes_consulta("CONS_CIDADES")
        self.assertEqual(len(perms), 1)
        self.assertEqual(perms[0].usucod, "ADMIN")
        self.assertTrue(perms[0].autorizado)

        # Atualizar para N
        self.repo.atualizar_permissao_consulta("ADMIN", "CONS_CIDADES", "N")
        perms_att = self.repo.listar_permissoes_consulta("CONS_CIDADES")
        self.assertFalse(perms_att[0].autorizado)

    def test_executar_sql_dinamico(self):
        sql = "SELECT cidnomecomp, ufsigla FROM user_geoapolo_cidades WHERE cidnomecomp LIKE ? ORDER BY cidnomecomp"
        res = self.repo.executar_sql_dinamico(sql, ["%LORENA%"])
        self.assertTrue(res.sucesso)
        self.assertEqual(res.total_registros, 1)
        self.assertEqual(res.colunas, ["cidnomecomp", "ufsigla"])
        self.assertEqual(res.linhas[0][0], "LORENA")


class TestConsultasService(unittest.TestCase):
    """Testes de negócio e proteção SQL do ConsultasService."""

    def setUp(self):
        self.mock_repo = MagicMock(spec=ConsultasRepository)
        self.mock_repo._nolock.return_value = ""
        self.service = ConsultasService(self.mock_repo)

    def test_montar_sql_cidades(self):
        filtro = FiltroConsultaDTO(controle="CIDADE_CIDADE", texto_busca="SAO", campo_busca="cidnomecomp")
        sql, params = self.service.montar_sql_consulta(filtro)
        self.assertIn("user_geoapolo_cidades", sql)
        self.assertIn("cidnomecomp LIKE ?", sql)
        self.assertEqual(params, ["%SAO%"])

    def test_montar_sql_sanitizacao_evita_sql_injection(self):
        # Campo de busca malicioso tentando injeção
        filtro = FiltroConsultaDTO(
            controle="CIDADE_CIDADE",
            campo_busca="cidnomecomp; DROP TABLE usuarios; --",
            texto_busca="teste"
        )
        sql, params = self.service.montar_sql_consulta(filtro)
        # Deve ter revertido para o padrão seguro
        self.assertNotIn("DROP TABLE", sql)
        self.assertIn("cidnomecomp LIKE ?", sql)

    def test_salvar_consulta_validacao(self):
        c_invalida = ConsultaConfigDTO(codigo_consulta="", descricao_consulta="Desc", sql_consulta="SELECT 1")
        with self.assertRaises(ValueError):
            self.service.salvar_consulta(c_invalida)

        c_valida = ConsultaConfigDTO(codigo_consulta="C01", descricao_consulta="Desc", sql_consulta="SELECT 1")
        self.mock_repo.salvar_consulta.return_value = True
        self.assertTrue(self.service.salvar_consulta(c_valida))

    def test_validar_seguranca_sql_leitura(self):
        # Validas
        ok1, _ = self.service.validar_seguranca_sql_leitura("SELECT * FROM user_geoapolo_cidades")
        self.assertTrue(ok1)

        ok2, _ = self.service.validar_seguranca_sql_leitura("WITH cte AS (SELECT 1 AS x) SELECT * FROM cte")
        self.assertTrue(ok2)

        # Inválidas: vazia
        inv_vazia, _ = self.service.validar_seguranca_sql_leitura("")
        self.assertFalse(inv_vazia)

        # Inválidas: comando proibido
        inv_drop, msg_drop = self.service.validar_seguranca_sql_leitura("DROP TABLE user_geoapolo_usuarios")
        self.assertFalse(inv_drop)

        inv_del, msg_del = self.service.validar_seguranca_sql_leitura("SELECT 1; DELETE FROM user_geoapolo_usuarios")
        self.assertFalse(inv_del)

        inv_upd, _ = self.service.validar_seguranca_sql_leitura("UPDATE user_geoapolo_grupo SET descricao = 'x'")
        self.assertFalse(inv_upd)

    def test_exportar_resultado_csv(self):
        import tempfile
        import os

        res = ResultadoConsultaDTO(
            sucesso=True,
            colunas=["codigo", "nome"],
            linhas=[["01", "TESTE 1"], ["02", "TESTE 2"]],
            total_registros=2
        )

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            total = self.service.exportar_resultado_csv(res, tmp_path, delimitador=";")
            self.assertEqual(total, 2)
            self.assertTrue(os.path.exists(tmp_path))

            with open(tmp_path, "r", encoding="utf-8-sig") as f:
                content = f.read()
                self.assertIn("codigo;nome", content)
                self.assertIn("01;TESTE 1", content)
                self.assertIn("02;TESTE 2", content)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


if __name__ == "__main__":
    unittest.main()

