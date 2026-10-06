"""
Testes Unitários para o Módulo de Controle de Lotes de Produtos (GeoApolo V5).
Cobertura: ProdutoLoteDTO, LotesRepository, LotesService e LotesView (headless).
"""

import sqlite3
import tkinter as tk
import unittest
from unittest.mock import patch
from datetime import datetime

from lotes.models import ProdutoLoteDTO, ResultadoLoteDTO
from lotes.repository import LotesRepository
from lotes.service import LotesService
from lotes.view import LotesView, abrir_janela_lotes


def criar_banco_teste():
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    # Tabela de produtos para joins
    cur.execute("""
        CREATE TABLE USER_geoapolo_produtos (
            prodcod INTEGER PRIMARY KEY,
            prodnome TEXT,
            grupocod INTEGER
        )
    """)
    cur.execute("INSERT INTO USER_geoapolo_produtos (prodcod, prodnome) VALUES (101, 'CABO DE FIBRA OPTICA 12FO')")
    cur.execute("INSERT INTO USER_geoapolo_produtos (prodcod, prodnome) VALUES (102, 'CONECTOR SC/APC FAST')")

    # Tabela de entidades/fornecedores para joins
    cur.execute("""
        CREATE TABLE USER_geoapolo_entidades (
            entcod INTEGER PRIMARY KEY,
            entnome TEXT
        )
    """)
    cur.execute("INSERT INTO USER_geoapolo_entidades (entcod, entnome) VALUES (1, 'FORNECEDOR BRASIL LTDA')")

    # Tabela de lotes
    cur.execute("""
        CREATE TABLE user_geoapolo_produto_lote (
            id_produto_lote INTEGER PRIMARY KEY AUTOINCREMENT,
            prodcod NUMERIC(8,0) NOT NULL,
            numero_lote VARCHAR(50) NOT NULL,
            data_fabricacao DATE NULL,
            data_validade DATE NULL,
            quantidade_inicial DECIMAL(18,6) NOT NULL DEFAULT 0,
            quantidade_atual DECIMAL(18,6) NOT NULL DEFAULT 0,
            data_entrada TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            entcod_fornecedor NUMERIC(8,0) NULL,
            status CHAR(1) NOT NULL DEFAULT 'A',
            observacao VARCHAR(500) NULL,
            data_cadastro TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            usucod VARCHAR(20) NULL
        )
    """)

    cur.execute("""
        INSERT INTO user_geoapolo_produto_lote
        (prodcod, numero_lote, data_fabricacao, data_validade, quantidade_inicial, quantidade_atual, entcod_fornecedor, status, observacao)
        VALUES (101, 'LT-2026-001', '2026-01-10', '2027-01-10', 1000.0, 1000.0, 1, 'A', 'PRIMEIRO LOTE')
    """)
    cur.execute("""
        INSERT INTO user_geoapolo_produto_lote
        (prodcod, numero_lote, data_fabricacao, data_validade, quantidade_inicial, quantidade_atual, entcod_fornecedor, status, observacao)
        VALUES (101, 'LT-2026-002', '2026-02-15', '2027-02-15', 500.0, 500.0, 1, 'I', 'LOTE BLOQUEADO')
    """)
    conn.commit()
    return conn


class TestProdutoLoteModels(unittest.TestCase):

    def test_dto_properties(self):
        lote = ProdutoLoteDTO(
            id_produto_lote=1,
            prodcod=101,
            numero_lote="LT-001",
            quantidade_inicial=100.0,
            quantidade_atual=60.0,
            status="A",
            data_validade="2099-12-31",
        )
        self.assertEqual(lote.display, "LT-001 (Saldo: 60.00)")
        self.assertTrue(lote.is_ativo)
        self.assertEqual(lote.display_status, "Ativo")

    def test_resultado_lote_dto(self):
        res = ResultadoLoteDTO(sucesso=True, mensagem="Criado", codigo=10)
        self.assertTrue(res.sucesso)
        self.assertEqual(res.codigo, 10)


class TestLotesRepository(unittest.TestCase):

    def setUp(self):
        self.conn = criar_banco_teste()
        self.repo = LotesRepository(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_listar_lotes(self):
        todos = self.repo.listar_lotes(prodcod=101)
        self.assertEqual(len(todos), 2)

        ativos = self.repo.listar_lotes(prodcod=101, apenas_ativos=True)
        self.assertEqual(len(ativos), 1)
        self.assertEqual(ativos[0].numero_lote, "LT-2026-001")

    def test_obter_lote_por_id_e_por_numero(self):
        lote = self.repo.obter_lote_por_id(1)
        self.assertIsNotNone(lote)
        self.assertEqual(lote.numero_lote, "LT-2026-001")
        self.assertEqual(lote.prodnome, "CABO DE FIBRA OPTICA 12FO")
        self.assertEqual(lote.nome_fornecedor, "FORNECEDOR BRASIL LTDA")

        lote2 = self.repo.obter_lote_por_numero(101, "LT-2026-001")
        self.assertIsNotNone(lote2)
        self.assertEqual(lote2.id_produto_lote, 1)

    def test_lote_existe(self):
        self.assertTrue(self.repo.lote_existe(101, "LT-2026-001"))
        self.assertTrue(self.repo.lote_existe(101, "lt-2026-001"))  # Case-insensitive
        self.assertFalse(self.repo.lote_existe(101, "LT-INEXISTENTE"))
        self.assertFalse(self.repo.lote_existe(102, "LT-2026-001"))  # Outro produto

    def test_salvar_novo_lote_e_atualizar(self):
        novo = ProdutoLoteDTO(
            prodcod=102,
            numero_lote="LT-SC-001",
            quantidade_inicial=200.0,
            quantidade_atual=200.0,
            status="A",
            observacao="CONECTORES NOVOS",
        )
        id_criado = self.repo.salvar_lote(novo)
        self.assertGreater(id_criado, 0)

        buscado = self.repo.obter_lote_por_id(id_criado)
        self.assertIsNotNone(buscado)
        self.assertEqual(buscado.numero_lote, "LT-SC-001")
        self.assertEqual(buscado.quantidade_atual, 200.0)

        # Atualizar
        buscado.observacao = "OBS ATUALIZADA"
        buscado.quantidade_atual = 180.0
        id_upd = self.repo.salvar_lote(buscado)
        self.assertEqual(id_upd, id_criado)

        atualizado = self.repo.obter_lote_por_id(id_criado)
        self.assertEqual(atualizado.observacao, "OBS ATUALIZADA")
        self.assertEqual(atualizado.quantidade_atual, 180.0)

    def test_atualizar_saldo_lote(self):
        # Aumentar saldo em 50
        ok = self.repo.atualizar_saldo_lote(1, 50.0)
        self.assertTrue(ok)
        lote = self.repo.obter_lote_por_id(1)
        self.assertEqual(lote.quantidade_atual, 1050.0)

        # Baixar saldo em 200
        ok2 = self.repo.atualizar_saldo_lote(1, -200.0)
        self.assertTrue(ok2)
        lote2 = self.repo.obter_lote_por_id(1)
        self.assertEqual(lote2.quantidade_atual, 850.0)

    def test_excluir_lote(self):
        ok = self.repo.excluir_lote(2)
        self.assertTrue(ok)
        self.assertIsNone(self.repo.obter_lote_por_id(2))


class TestLotesService(unittest.TestCase):

    def setUp(self):
        self.conn = criar_banco_teste()
        self.repo = LotesRepository(self.conn)
        self.service = LotesService(self.repo)

    def tearDown(self):
        self.conn.close()

    def test_validacao_produto_e_numero_lote_obrigatorios(self):
        # Sem produto
        res1 = self.service.salvar_lote(ProdutoLoteDTO(prodcod=0, numero_lote="LT-01"))
        self.assertFalse(res1.sucesso)
        self.assertIn("Código do Produto", res1.mensagem)

        # Sem número de lote
        res2 = self.service.salvar_lote(ProdutoLoteDTO(prodcod=101, numero_lote=""))
        self.assertFalse(res2.sucesso)
        self.assertIn("Número do Lote", res2.mensagem)

    def test_validacao_unicidade_lote_por_produto(self):
        # Lote já existente para prodcod 101
        res = self.service.salvar_lote(ProdutoLoteDTO(prodcod=101, numero_lote="LT-2026-001"))
        self.assertFalse(res.sucesso)
        self.assertIn("Já existe um lote", res.mensagem)

        # Mesmo número de lote para outro produto (102) deve ser permitido
        res_outro = self.service.salvar_lote(ProdutoLoteDTO(prodcod=102, numero_lote="LT-2026-001"))
        self.assertTrue(res_outro.sucesso)

    def test_validacao_datas_fabricacao_validade(self):
        # Validade anterior à fabricação
        dto = ProdutoLoteDTO(
            prodcod=101,
            numero_lote="LT-DATA-INV",
            data_fabricacao="2026-06-01",
            data_validade="2026-05-01",
        )
        res = self.service.salvar_lote(dto)
        self.assertFalse(res.sucesso)
        self.assertIn("não pode ser anterior", res.mensagem)

    def test_lote_existe(self):
        self.assertTrue(self.service.lote_existe(101, "LT-2026-001"))
        self.assertFalse(self.service.lote_existe(101, "INEXISTENTE"))
        self.assertFalse(self.service.lote_existe(0, "LT-2026-001"))


class TestLotesViewHeadless(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.conn = criar_banco_teste()
        self.repo = LotesRepository(self.conn)
        self.service = LotesService(self.repo)

    def tearDown(self):
        self.root.destroy()
        self.conn.close()

    def test_renderizacao_view_e_selecao(self):
        view = LotesView(self.root, service=self.service)
        self.assertTrue(hasattr(view, "tree"))
        self.assertTrue(hasattr(view, "var_numero_lote"))
        self.assertTrue(hasattr(view, "var_prodcod"))

        # Grade carregou registros (LT-2026-002 é o mais recente, vem primeiro)
        items = view.tree.get_children()
        self.assertEqual(len(items), 2)

        # Selecionar primeiro item
        view.tree.selection_set(items[0])
        view._ao_selecionar_lote()
        self.assertEqual(view.var_numero_lote.get(), "LT-2026-002")
        self.assertEqual(view.var_prodcod.get(), "101")
        view.destroy()

    def test_abrir_janela_com_preenchimento_e_callback(self):
        capturado = []

        def callback_teste(novo_num):
            capturado.append(novo_num)

        with patch("tkinter.messagebox.showinfo"), patch("tkinter.messagebox.showerror"):
            win = abrir_janela_lotes(
                self.root,
                prodcod=101,
                numero_lote="LT-NOVO-999",
                callback=callback_teste,
                service=self.service,
            )
            self.assertIsInstance(win, tk.Toplevel)

            # Acha a view dentro da janela
            view = [w for w in win.winfo_children() if isinstance(w, LotesView)][0]
            self.assertEqual(view.var_prodcod.get(), "101")
            self.assertEqual(view.var_numero_lote.get(), "LT-NOVO-999")

            # Salvar o novo lote via formulário
            view._salvar_lote()
            self.assertIn("LT-NOVO-999", capturado)

            try:
                win.destroy()
            except Exception:
                pass

    def test_selecao_duplo_clique_e_f3_fecham_janela(self):
        capturado = []

        def callback_teste(num):
            capturado.append(num)

        win = abrir_janela_lotes(
            self.root,
            prodcod=101,
            callback=callback_teste,
            service=self.service,
        )
        view = [w for w in win.winfo_children() if isinstance(w, LotesView)][0]
        items = view.tree.get_children()
        self.assertGreaterEqual(len(items), 1)

        # Seleciona o primeiro item na grade
        view.tree.selection_set(items[0])

        # Testa o duplo clique
        view._ao_duplo_clique_grade()
        self.assertGreaterEqual(len(capturado), 1)
        self.assertEqual(capturado[0], "LT-2026-002")

        # Testa F3 em nova janela
        capturado_f3 = []
        win2 = abrir_janela_lotes(
            self.root,
            prodcod=101,
            callback=lambda n: capturado_f3.append(n),
            service=self.service,
        )
        view2 = [w for w in win2.winfo_children() if isinstance(w, LotesView)][0]
        items2 = view2.tree.get_children()
        view2.tree.selection_set(items2[1])
        view2._confirmar_selecao_e_fechar()
        self.assertEqual(capturado_f3[0], "LT-2026-001")


if __name__ == "__main__":

    unittest.main()
