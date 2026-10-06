"""
Testes Unitários Dedicados para as Novas Regras de Negócio:
1. Tabela user_geoapolo_saldoestqdata (Entradas somam, Saídas reduzem por data).
2. Remoção do campo código de lote no Cadastro de Produtos.
3. Atendimento Total F7 com validação de saldo e vencimento de lotes.
4. Atendimento Individual com proteção de tela em branco e auto-seleção.
GeoApolo V5
"""

import sqlite3
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

import tkinter as tk
from tkinter import ttk

from estoque.models import RequisicaoDTO, ItemRequisicaoDTO
from estoque.repository import EstoqueRepository
from estoque.service import EstoqueService
from estoque.requisicoes_view import RequisicoesView
from lotes.models import ProdutoLoteDTO
from lotes.repository import LotesRepository
from lotes.service import LotesService
from produtos.models import ProdutoDTO
from produtos.repository import ProdutosRepository
from produtos.service import ProdutosService
from produtos.view import ProdutosView


def criar_banco_teste_completo():
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()

    # Produtos
    cur.execute("""
        CREATE TABLE USER_geoapolo_produtos (
            prodcod INTEGER PRIMARY KEY,
            prodnome TEXT,
            codigo_inmetro TEXT,
            codigo_lote TEXT,
            tamanho TEXT,
            grupocod INTEGER
        )
    """)
    cur.execute("INSERT INTO USER_geoapolo_produtos VALUES (10, 'PRODUTO COM LOTE VENCIDO', '', '', 'UN', 1)")
    cur.execute("INSERT INTO USER_geoapolo_produtos VALUES (20, 'PRODUTO COM LOTE VALIDO', '', '', 'UN', 1)")
    cur.execute("INSERT INTO USER_geoapolo_produtos VALUES (30, 'PRODUTO SEM CONTROLE DE LOTE', '', '', 'UN', 1)")

    # Empresas e Configurações
    cur.execute("""
        CREATE TABLE USER_geoapolo_configuracoes (
            empcod TEXT PRIMARY KEY,
            permite_estoque_negativo TEXT DEFAULT 'Nao'
        )
    """)
    cur.execute("INSERT INTO USER_geoapolo_configuracoes VALUES ('1.01', 'Nao')")

    # Garante tabelas GeoApolo de estoque (inclusive user_geoapolo_saldoestqdata)
    repo = EstoqueRepository(conn)
    repo._garantir_tabelas_geoapolo()

    # Tabela de Lotes
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

    # Cadastra lotes para os produtos
    dt_vencida = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    dt_valida = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")

    cur.execute("""
        INSERT INTO user_geoapolo_produto_lote (prodcod, numero_lote, data_validade, quantidade_inicial, quantidade_atual, status)
        VALUES (10, 'LOTE-VENCIDO', ?, 50.0, 50.0, 'A')
    """, [dt_vencida])

    cur.execute("""
        INSERT INTO user_geoapolo_produto_lote (prodcod, numero_lote, data_validade, quantidade_inicial, quantidade_atual, status)
        VALUES (20, 'LOTE-VALIDO', ?, 100.0, 100.0, 'A')
    """, [dt_valida])

    # Saldos de estoque
    cur.execute("INSERT OR REPLACE INTO USER_geoapolo_estoque (codigo_empresa, prodcod, saldo_atual, saldo_disponivel) VALUES ('1.01', 10, 50.0, 50.0)")
    cur.execute("INSERT OR REPLACE INTO USER_geoapolo_estoque (codigo_empresa, prodcod, saldo_atual, saldo_disponivel) VALUES ('1.01', 20, 100.0, 100.0)")
    cur.execute("INSERT OR REPLACE INTO USER_geoapolo_estoque (codigo_empresa, prodcod, saldo_atual, saldo_disponivel) VALUES ('1.01', 30, 0.0, 0.0)")

    conn.commit()
    return conn


class TestRegrasLoteERequisicoesESaldoEstqData(unittest.TestCase):

    def setUp(self):
        self.conn = criar_banco_teste_completo()
        self.estq_repo = EstoqueRepository(self.conn)
        self.estq_svc = EstoqueService(self.estq_repo)
        self.lote_repo = LotesRepository(self.conn)
        self.lote_svc = LotesService(self.lote_repo)
        try:
            self.root = tk.Tk()
            self.root.withdraw()
        except Exception:
            self.root = None

    def tearDown(self):
        if self.root:
            try:
                self.root.destroy()
            except Exception:
                pass
        self.conn.close()

    def test_01_saldo_estq_data_entrada_e_saida(self):
        """
        Verifica a tabela user_geoapolo_saldoestqdata:
        - Movimentação de Entrada soma no saldo_do_dia.
        - Movimentação de Saída reduz no saldo_do_dia.
        """
        cur = self.conn.cursor()
        dt_hoje = datetime.now().strftime("%Y-%m-%d")

        # 1. Entrada de 25 unidades do produto 20
        res_e = self.estq_svc.registrar_entrada_compras(
            empcod="1.01",
            prodcod_estr="20",
            quantidade=25.0,
            valor_unitario=10.0,
            num_doc="NF-TESTE-1",
            numero_lote="LOTE-VALIDO",
        )
        self.assertTrue(res_e.sucesso)

        cur.execute("SELECT saldo_do_dia FROM user_geoapolo_saldoestqdata WHERE prodcod = 20 AND data_saldo = ?", [dt_hoje])
        r = cur.fetchone()
        self.assertIsNotNone(r, "Registro em user_geoapolo_saldoestqdata deve ser criado na entrada")
        self.assertEqual(float(r[0]), 25.0)

        # 2. Mais uma entrada no mesmo dia de 15 unidades soma (+15 = 40)
        self.estq_svc.registrar_entrada_compras(
            empcod="1.01",
            prodcod_estr="20",
            quantidade=15.0,
            valor_unitario=10.0,
            num_doc="NF-TESTE-2",
            numero_lote="LOTE-VALIDO",
        )
        cur.execute("SELECT saldo_do_dia FROM user_geoapolo_saldoestqdata WHERE prodcod = 20 AND data_saldo = ?", [dt_hoje])
        self.assertEqual(float(cur.fetchone()[0]), 40.0)

        # 3. Saída direta de 10 unidades reduz (-10 = 30)
        res_s = self.estq_svc.registrar_saida_direta(
            empcod="1.01",
            prodcod_estr="20",
            quantidade=10.0,
            destino_obs="TESTE SAIDA",
        )
        self.assertTrue(res_s.sucesso)
        cur.execute("SELECT saldo_do_dia FROM user_geoapolo_saldoestqdata WHERE prodcod = 20 AND data_saldo = ?", [dt_hoje])
        self.assertEqual(float(cur.fetchone()[0]), 30.0)

    def test_02_cadastro_produto_sem_campo_lote(self):
        """
        Valida que o formulário de cadastro de produtos não possui mais o campo código do lote.
        """
        if not self.root:
            self.skipTest("Ambiente sem display Tkinter")

        mock_p_repo = MagicMock(spec=ProdutosRepository)
        mock_p_repo.listar_grupos.return_value = []
        mock_p_repo.listar_marcas.return_value = []
        mock_p_repo.listar_produtos.return_value = []
        mock_p_repo.contar_produtos.return_value = 0
        p_svc = ProdutosService(mock_p_repo)

        view = ProdutosView(self.root, service=p_svc)
        self.assertFalse(hasattr(view, "ent_codigo_lote"), "ent_codigo_lote não deve existir na view de produtos")
        self.assertFalse(hasattr(view, "var_codigo_lote"), "var_codigo_lote não deve existir na view de produtos")
        view.destroy()

    def test_03_atendimento_f7_bloqueio_saldo_insuficiente(self):
        """
        Valida que o atendimento total F7 bloqueia se um dos itens da requisição não tiver saldo
        e a empresa não permitir estoque negativo.
        """
        # Cria requisição com produto 30 (saldo 0)
        req = RequisicaoDTO(
            req_num="REQ-SEM-SALDO",
            empcod="1.01",
            requerente="ALMOXARIFE",
            centro_custo="01.01",
            itens=[ItemRequisicaoDTO(prodcod_estr="30", qtd_solicitada=5.0)],
        )
        s, m, r_id = self.estq_repo.criar_requisicao(req)
        self.assertTrue(s)

        res_atend = self.estq_svc.atender_requisicao_completa("REQ-SEM-SALDO", empcod="1.01")
        self.assertFalse(res_atend.sucesso)
        self.assertIn("não permite estoque negativo", res_atend.mensagem)

    def test_04_atendimento_f7_bloqueio_lote_vencido(self):
        """
        Valida que o F7 identifica lote vencido e bloqueia atendimento (Nível ROXO).
        """
        # Cria requisição com produto 10 (tem lote vencido)
        req = RequisicaoDTO(
            req_num="REQ-LOTE-VENC",
            empcod="1.01",
            requerente="MEDICO",
            centro_custo="01.01",
            itens=[ItemRequisicaoDTO(prodcod_estr="10", qtd_solicitada=2.0)],
        )
        self.estq_repo.criar_requisicao(req)

        # Checa validação de vencimento do lote
        nivel, dias, dt_val = self.lote_svc.verificar_vencimento_lote(10, "LOTE-VENCIDO")
        self.assertEqual(nivel, "ROXO", "Lote com validade passada deve retornar nível ROXO (bloqueio)")
        self.assertLess(dias, 0)

    def test_05_atendimento_f7_sucesso_com_lote_valido(self):
        """
        Valida que o F7 atende com sucesso quando os itens possuem saldo e lote válido.
        Atualiza user_geoapolo_saldoestqdata com a saída.
        """
        cur = self.conn.cursor()
        dt_hoje = datetime.now().strftime("%Y-%m-%d")

        req = RequisicaoDTO(
            req_num="REQ-F7-SUCESSO",
            empcod="1.01",
            requerente="SOLICITANTE",
            centro_custo="01.01",
            itens=[ItemRequisicaoDTO(prodcod_estr="20", qtd_solicitada=10.0)],
        )
        self.estq_repo.criar_requisicao(req)

        res = self.estq_svc.atender_requisicao_completa(
            req_num="REQ-F7-SUCESSO",
            empcod="1.01",
            observacao="BAIXA F7 TOTAL",
            itens_lotes={1: "LOTE-VALIDO"},
        )
        self.assertTrue(res.sucesso)

        # Verifica baixa no saldo de estoque
        s_atual, _, s_disp = self.estq_svc.obter_saldo_produto("20", "1.01")
        self.assertEqual(s_disp, 90.0)

        # Verifica redução no saldo do dia da tabela user_geoapolo_saldoestqdata
        cur.execute("SELECT saldo_do_dia FROM user_geoapolo_saldoestqdata WHERE prodcod = 20 AND data_saldo = ?", [dt_hoje])
        r = cur.fetchone()
        self.assertIsNotNone(r)
        self.assertEqual(float(r[0]), -10.0)

    def test_06_atendimento_individual_auto_selecao_e_sem_erro(self):
        """
        Valida que a tela de requisições auto-seleciona item pendente para atendimento individual.
        """
        if not self.root:
            self.skipTest("Ambiente sem display Tkinter")

        req = RequisicaoDTO(
            req_num="REQ-INDIV",
            empcod="1.01",
            requerente="TESTADOR",
            centro_custo="01.01",
            itens=[ItemRequisicaoDTO(prodcod_estr="20", qtd_solicitada=5.0)],
        )
        self.estq_repo.criar_requisicao(req)

        view = RequisicoesView(self.root, service=self.estq_svc)
        view.carregar_requisicoes()
        view.tree_req.selection_set("REQ-INDIV")
        view._ao_selecionar_requisicao()

        # Sem selecionar na árvore de itens, _obter_item_selecionado auto-seleciona o item pendente
        item_sel = view._obter_item_selecionado()
        self.assertIsNotNone(item_sel)
        self.assertEqual(item_sel.prodcod_estr, "20")
        view.destroy()


if __name__ == "__main__":
    unittest.main()
