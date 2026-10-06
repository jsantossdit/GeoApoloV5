"""
Testes automatizados para o Cadastro de Classificação de Bens (USER_geoapolo_satfi_classificacaoativo)
e integração com o módulo de Ativo Fixo (GeoApolo V5).
"""

import os
import sys
import unittest
import sqlite3
import tkinter as tk
from unittest.mock import MagicMock

PASTA_RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PASTA_RAIZ not in sys.path:
    sys.path.insert(0, PASTA_RAIZ)

from ativo_imobilizado.repository import AtivoImobilizadoRepository
from ativo_imobilizado.service import AtivoImobilizadoService
from ativo_imobilizado.classificacao_bens_view import ClassificacaoBensView
from ativo_imobilizado.view import AtivoImobilizadoView


class TestClassificacaoBensRepository(unittest.TestCase):

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE USER_geoapolo_satfi_categorias (
                codigo_categoria INTEGER PRIMARY KEY,
                descricao VARCHAR(100)
            )
        """)
        cur.execute("""
            CREATE TABLE USER_geoapolo_satfi_classificacaoativo (
                codigoclasse INTEGER PRIMARY KEY,
                descricao VARCHAR(100) NOT NULL,
                codigo_categoria INTEGER NULL
            )
        """)
        # Insere dados de apoio para testes
        cur.execute("INSERT INTO USER_geoapolo_satfi_categorias VALUES (1, 'EQUIPAMENTOS DE TI')")
        cur.execute("INSERT INTO USER_geoapolo_satfi_categorias VALUES (2, 'VEÍCULOS')")
        self.conn.commit()
        self.repo = AtivoImobilizadoRepository(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_proximo_codigo_classificacao(self):
        prox = self.repo.obter_proximo_codigo_classificacao()
        self.assertEqual(prox, 1)

        self.repo.salvar_classificacao(1, "COMPUTADORES", 1)
        prox2 = self.repo.obter_proximo_codigo_classificacao()
        self.assertEqual(prox2, 2)

    def test_salvar_e_obter_classificacao(self):
        # Inserção
        ok = self.repo.salvar_classificacao(1, "microcomputadores", 1)
        self.assertTrue(ok)

        reg = self.repo.obter_classificacao(1)
        self.assertIsNotNone(reg)
        self.assertEqual(reg["codigoclasse"], 1)
        self.assertEqual(reg["descricao"], "MICROCOMPUTADORES")
        self.assertEqual(reg["codigo_categoria"], 1)
        self.assertEqual(reg["categoria"], "EQUIPAMENTOS DE TI")

        # Atualização
        ok_upd = self.repo.salvar_classificacao(1, "servidores e racks", 1)
        self.assertTrue(ok_upd)
        reg_upd = self.repo.obter_classificacao(1)
        self.assertEqual(reg_upd["descricao"], "SERVIDORES E RACKS")

    def test_listar_todas_classificacoes_e_filtros(self):
        self.repo.salvar_classificacao(1, "NOTEBOOKS", 1)
        self.repo.salvar_classificacao(2, "AUTOMÓVEIS", 2)
        self.repo.salvar_classificacao(3, "IMPRESSORAS", 1)

        todos = self.repo.listar_todas_classificacoes()
        self.assertEqual(len(todos), 3)

        filtrados = self.repo.listar_todas_classificacoes("NOTE")
        self.assertEqual(len(filtrados), 1)
        self.assertEqual(filtrados[0]["codigoclasse"], 1)

        # Filtro por código
        filtrados_cod = self.repo.listar_todas_classificacoes("2")
        self.assertEqual(len(filtrados_cod), 1)
        self.assertEqual(filtrados_cod[0]["descricao"], "AUTOMÓVEIS")

    def test_listar_classificacoes_por_categoria(self):
        self.repo.salvar_classificacao(1, "NOTEBOOKS", 1)
        self.repo.salvar_classificacao(2, "AUTOMÓVEIS", 2)
        self.repo.salvar_classificacao(3, "IMPRESSORAS", 1)

        # Categoria 1 (TI) deve retornar 2 itens
        classifs_ti = self.repo.listar_classificacoes("1")
        self.assertEqual(len(classifs_ti), 2)
        codigos = [c["codigo"] for c in classifs_ti]
        self.assertIn("1", codigos)
        self.assertIn("3", codigos)

        # Categoria 2 (Veículos) deve retornar 1 item
        classifs_veic = self.repo.listar_classificacoes("2")
        self.assertEqual(len(classifs_veic), 1)
        self.assertEqual(classifs_veic[0]["codigo"], "2")

        # Categoria vazia deve retornar todos
        classifs_todas = self.repo.listar_classificacoes("")
        self.assertEqual(len(classifs_todas), 3)

    def test_excluir_classificacao(self):
        self.repo.salvar_classificacao(1, "MONITORES", 1)
        self.assertIsNotNone(self.repo.obter_classificacao(1))

        self.repo.excluir_classificacao(1)
        self.assertIsNone(self.repo.obter_classificacao(1))


class TestClassificacaoBensService(unittest.TestCase):

    def setUp(self):
        self.mock_repo = MagicMock()
        self.service = AtivoImobilizadoService(self.mock_repo)

    def test_salvar_classificacao_sucesso(self):
        res = self.service.salvar_classificacao(1, "equipamento de rede", 1)
        self.assertTrue(res.sucesso)
        self.mock_repo.salvar_classificacao.assert_called_once_with(1, "EQUIPAMENTO DE REDE", 1)

    def test_salvar_classificacao_validacoes(self):
        # Código inválido
        r1 = self.service.salvar_classificacao("invalido", "TESTE")
        self.assertFalse(r1.sucesso)

        # Código negativo
        r2 = self.service.salvar_classificacao(-1, "TESTE")
        self.assertFalse(r2.sucesso)

        # Descrição vazia
        r3 = self.service.salvar_classificacao(1, "")
        self.assertFalse(r3.sucesso)

    def test_excluir_classificacao_sucesso(self):
        res = self.service.excluir_classificacao(5)
        self.assertTrue(res.sucesso)
        self.mock_repo.excluir_classificacao.assert_called_once_with(5)


class TestClassificacaoBensViewHeadless(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        try:
            cls.root = tk.Tk()
            cls.root.withdraw()
        except Exception:
            cls.root = None

    @classmethod
    def tearDownClass(cls):
        if cls.root:
            cls.root.destroy()

    def setUp(self):
        if not self.root:
            self.skipTest("Ambiente sem interface gráfica")

        self.conn = sqlite3.connect(":memory:")
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE USER_geoapolo_satfi_categorias (
                codigo_categoria INTEGER PRIMARY KEY,
                descricao VARCHAR(100)
            )
        """)
        cur.execute("""
            CREATE TABLE USER_geoapolo_satfi_classificacaoativo (
                codigoclasse INTEGER PRIMARY KEY,
                descricao VARCHAR(100) NOT NULL,
                codigo_categoria INTEGER NULL
            )
        """)
        cur.execute("INSERT INTO USER_geoapolo_satfi_categorias VALUES (1, 'EQUIPAMENTOS DE TI')")
        cur.execute("INSERT INTO USER_geoapolo_satfi_classificacaoativo VALUES (1, 'COMPUTADORES', 1)")
        self.conn.commit()
        self.repo = AtivoImobilizadoRepository(self.conn)

    def tearDown(self):
        if hasattr(self, "conn"):
            self.conn.close()

    def test_view_classificacao_instanciacao_e_componentes(self):
        view = ClassificacaoBensView(self.root, repo=self.repo)
        self.assertIsNotNone(view)

        # Verifica carregamento no treeview
        children = view.tree.get_children()
        self.assertEqual(len(children), 1)
        self.assertIn("1 classificação(ões)", view.lbl_total.cget("text"))

        # Verifica campos em maiúsculo (vincular_maiusculo)
        view.var_descricao.set("novo teste minúsculo")
        self.assertEqual(view.var_descricao.get(), "NOVO TESTE MINÚSCULO")

        # Verifica gravação via interface
        view.var_codigo.set("2")
        view.var_descricao.set("notebooks portáteis")
        view.var_categoria.set("1 - EQUIPAMENTOS DE TI")
        with unittest.mock.patch("ativo_imobilizado.classificacao_bens_view.messagebox") as mock_mb:
            view._gravar()
            self.assertTrue(mock_mb.showinfo.called)

        # Verifica que o segundo registro foi salvo
        self.assertIsNotNone(self.repo.obter_classificacao(2))
        view.destroy()

    def test_ativo_imobilizado_view_combos_e_maiusculo(self):
        # Cria tabelas necessárias para o módulo de ativo imobilizado
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE USER_geoapolo_satfi_ativoimobilizado (
                numero_do_bem VARCHAR(20) PRIMARY KEY,
                descricao_do_bem VARCHAR(100),
                geocctrlcodestr VARCHAR(20),
                codigo_barrasativo VARCHAR(50),
                codigo_categoria_bem VARCHAR(20),
                codigo_classificacaoativoimobilizado VARCHAR(20),
                codigo_localizacao VARCHAR(20),
                codigo_func_responsavel VARCHAR(20),
                codigo_da_marca VARCHAR(20),
                empcod VARCHAR(10),
                codigo_status_bem VARCHAR(20),
                data_aquisicao VARCHAR(20),
                valor_compra REAL,
                taxa_depreciacao_anual REAL,
                data_ultima_revisao VARCHAR(20),
                caminho_foto VARCHAR(200),
                observacoes TEXT
            )
        """)
        cur.execute("CREATE TABLE USER_geoapolo_centrocontrole (geocctrlcodestr VARCHAR(20), geocctrlnome VARCHAR(100))")
        cur.execute("CREATE TABLE USER_geoapolo_satfi_localizacao_fisica (codigo_localizacao VARCHAR(20), localizacao VARCHAR(100), codigo_departamento INT, grupo VARCHAR(5))")
        cur.execute("CREATE TABLE USER_geoapolo_departamentos (codigo_departamento INT, flagativo VARCHAR(1), nome_departamento VARCHAR(100))")
        cur.execute("CREATE TABLE USER_geoapolo_usuarios (usucod VARCHAR(20), flagativo VARCHAR(1), nome_completo VARCHAR(100), codigo_departamento INT)")
        cur.execute("CREATE TABLE USER_geoapolo_produto_marcas (codigo_marca VARCHAR(20), descricao_marca VARCHAR(100))")
        cur.execute("CREATE TABLE USER_geoapolo_satfi_status_imobilizado (codigo_status_bem VARCHAR(20), descricao_status_bem VARCHAR(100))")
        cur.execute("CREATE TABLE USER_geoapolo_empresas (empcod VARCHAR(10), empnome VARCHAR(100))")
        self.conn.commit()

        view_ativo = AtivoImobilizadoView(self.root, connection=self.conn, empresa_codigo="001")
        self.assertIsNotNone(view_ativo)

        # O combo de classificação deve estar inicializado com a opção cadastrada
        self.assertIn("1 - COMPUTADORES", view_ativo.combo_classif["values"])

        # Testa maiúsculo nos campos de texto
        view_ativo.txt_descricao.insert(0, "servidor dell")
        view_ativo.txt_descricao.event_generate("<KeyRelease>")
        view_ativo.update()
        self.assertEqual(view_ativo.txt_descricao.get(), "SERVIDOR DELL")

        view_ativo.destroy()


if __name__ == "__main__":
    unittest.main()
