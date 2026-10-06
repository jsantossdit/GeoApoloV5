import unittest
import sqlite3
from core.schema_checker import (
    verificar_sanidade_estoque_produtos,
    gerar_script_sql_tabelas_faltantes,
    aplicar_correcao_tabelas_faltantes,
    TABELAS_ESTOQUE_PRODUTOS,
)


class TestSchemaChecker(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")

    def tearDown(self):
        self.conn.close()

    def test_todas_tabelas_definidas(self):
        self.assertGreaterEqual(len(TABELAS_ESTOQUE_PRODUTOS), 15)

    def test_verificar_sanidade_banco_vazio(self):
        diag = verificar_sanidade_estoque_produtos(self.conn)
        self.assertFalse(diag["todas_ok"])
        self.assertEqual(len(diag["tabelas_faltando"]), len(TABELAS_ESTOQUE_PRODUTOS))
        self.assertIn("O catálogo de produtos", diag["avisos"][0])

    def test_gerar_script_sql(self):
        faltando = [
            {"nome": "USER_geoapolo_marca_produtos", "descricao": "Vínculo Marca", "ddl": "CREATE TABLE A;"},
            {"nome": "USER_geoapolo_produto_cor", "descricao": "Vínculo Cor", "ddl": "CREATE TABLE B;"},
        ]
        sql = gerar_script_sql_tabelas_faltantes(faltando)
        self.assertIn("USER_geoapolo_marca_produtos", sql)
        self.assertIn("USER_geoapolo_produto_cor", sql)
        self.assertIn("CREATE TABLE A;", sql)

    def test_verificar_sanidade_com_tabela_existente(self):
        cur = self.conn.cursor()
        cur.execute("CREATE TABLE USER_geoapolo_produtos (prodcod INT PRIMARY KEY, prodnome TEXT)")
        cur.execute("INSERT INTO USER_geoapolo_produtos VALUES (1, 'PRODUTO TESTE')")
        self.conn.commit()

        diag = verificar_sanidade_estoque_produtos(self.conn)
        nomes_ok = [t["nome"] for t in diag["tabelas_ok"]]
        self.assertIn("USER_geoapolo_produtos", nomes_ok)
        self.assertEqual(diag["total_produtos"], 1)
        self.assertEqual(len(diag["avisos"]), 0)


if __name__ == "__main__":
    unittest.main()
