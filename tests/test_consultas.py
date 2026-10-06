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

    def test_listar_consultas_imediatas_e_por_descricao(self):
        # Cadastra consulta imediata
        c = ConsultaConfigDTO(
            codigo_consulta="CONS_IMED_1",
            descricao_consulta="Consulta Imediata Teste",
            sql_consulta="SELECT * FROM user_geoapolo_cidades",
            tipo_consulta="I",
            banco_consulta="ALVO"
        )
        self.repo.salvar_consulta(c)
        self.repo.atualizar_permissao_consulta("JULIO", "CONS_IMED_1", "A")

        # Busca por descricao
        buscada = self.repo.obter_consulta_por_descricao("Consulta Imediata Teste")
        self.assertIsNotNone(buscada)
        self.assertEqual(buscada.codigo_consulta, "CONS_IMED_1")

        # Lista imediatas para JULIO
        imediatas_julio = self.repo.listar_consultas_imediatas("JULIO", "ALVO")
        self.assertEqual(len(imediatas_julio), 1)
        self.assertEqual(imediatas_julio[0].codigo_consulta, "CONS_IMED_1")

        # Lista imediatas para ADMIN
        imediatas_admin = self.repo.listar_consultas_imediatas("ADMIN", "ALVO")
        self.assertGreaterEqual(len(imediatas_admin), 1)

    def test_aplicar_permissao_usuario_e_remover(self):
        qtd = self.repo.aplicar_permissao_grupo_ou_usuario("CONS_CIDADES", "A", usucod="TESTE_USER")
        self.assertEqual(qtd, 1)

        perms = self.repo.listar_permissoes_consulta("CONS_CIDADES")
        usuarios = [p.usucod for p in perms]
        self.assertIn("TESTE_USER", usuarios)

        # Remover permissao
        self.assertTrue(self.repo.remover_permissao_consulta("TESTE_USER", "CONS_CIDADES"))
        perms_depois = self.repo.listar_permissoes_consulta("CONS_CIDADES")
        usuarios_depois = [p.usucod for p in perms_depois]
        self.assertNotIn("TESTE_USER", usuarios_depois)

    def test_clonar_permissoes_consulta(self):
        self.repo.atualizar_permissao_consulta("USER_ORIGEM", "CONS_CIDADES", "A")
        clonadas = self.repo.clonar_permissoes_consulta("USER_ORIGEM", "USER_DESTINO")
        self.assertEqual(clonadas, 1)

        perms = self.repo.listar_permissoes_consulta("CONS_CIDADES")
        usuarios = [p.usucod for p in perms]
        self.assertIn("USER_DESTINO", usuarios)


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
        # Validas (SELECT, WITH, INSERT em temp, DROP temp, CREATE, etc.)
        ok1, _ = self.service.validar_seguranca_sql_leitura("SELECT * FROM user_geoapolo_cidades")
        self.assertTrue(ok1)

        ok2, _ = self.service.validar_seguranca_sql_leitura("WITH cte AS (SELECT 1 AS x) SELECT * FROM cte")
        self.assertTrue(ok2)

        ok_insert, _ = self.service.validar_seguranca_sql_leitura("INSERT INTO #temp_dados SELECT 1, 'teste'")
        self.assertTrue(ok_insert)

        ok_drop_temp, _ = self.service.validar_seguranca_sql_leitura("DROP TABLE #temp_dados")
        self.assertTrue(ok_drop_temp)

        # Inválidas: vazia
        inv_vazia, _ = self.service.validar_seguranca_sql_leitura("")
        self.assertFalse(inv_vazia)

        # Inválidas: comandos destrutivos (somente DELETE e UPDATE)
        inv_del, msg_del = self.service.validar_seguranca_sql_leitura("SELECT 1; DELETE FROM user_geoapolo_usuarios")
        self.assertFalse(inv_del)
        self.assertIn("DELETE", msg_del)

        inv_upd, msg_upd = self.service.validar_seguranca_sql_leitura("UPDATE user_geoapolo_grupo SET descricao = 'x'")
        self.assertFalse(inv_upd)
        self.assertIn("UPDATE", msg_upd)

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

    def test_analisar_e_substituir_parametros(self):
        sql_original = "SELECT * FROM t WHERE ano = |Ano^ AND dt >= {Data_Inicio} AND tipo = [01.001] AND obs = &?"

        def mock_input(nome, tipo):
            if nome == "Ano":
                return "2026"
            if nome == "Data_Inicio":
                return "18/09/2026"
            return ""

        sql_proc, sucesso = self.service.analisar_e_substituir_parametros(sql_original, callback_input=mock_input)
        self.assertTrue(sucesso)
        self.assertIn("ano = '2026'", sql_proc)
        self.assertIn("dt >= '2026-09-18'", sql_proc)
        self.assertIn("tipo = '01.001' ", sql_proc)
        self.assertIn("obs = ''", sql_proc)

    def test_analisar_parametros_cancelamento_usuario(self):
        sql_original = "SELECT * FROM t WHERE ano = |Ano^"

        def mock_input_cancela(nome, tipo):
            return None  # Usuário cancelou

        sql_proc, sucesso = self.service.analisar_e_substituir_parametros(sql_original, callback_input=mock_input_cancela)
        self.assertFalse(sucesso)
        self.assertEqual(sql_proc, "")

    def test_exportar_resultado_excel_xlsx(self):
        import tempfile
        import os

        res = ResultadoConsultaDTO(
            sucesso=True,
            colunas=["codigo", "descricao"],
            linhas=[["1", "CONSULTA 1"], ["2", "CONSULTA 2"]],
            total_registros=2
        )

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            total = self.service.exportar_resultado_excel(res, tmp_path)
            self.assertEqual(total, 2)
            self.assertTrue(os.path.exists(tmp_path))
            self.assertGreater(os.path.getsize(tmp_path), 0)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


if __name__ == "__main__":
    unittest.main()

