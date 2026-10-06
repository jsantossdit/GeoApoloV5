"""
Testes Unitários para Alertas e Bloqueios por Vencimento de Lote (GeoApolo V5).
Regras:
- 10 a 30 dias: Alerta AMARELO
- 5 a 10 dias: Alerta VERMELHO
- 0 a 5 dias (ou vencido): Alerta ROXO com BLOQUEIO
"""

import sqlite3
import tkinter as tk
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from lotes.models import ProdutoLoteDTO
from lotes.repository import LotesRepository
from lotes.service import LotesService
from lotes.alerta_vencimento_view import exibir_alerta_vencimento_lote
from estoque.models import RequisicaoDTO, ItemRequisicaoDTO
from estoque.repository import EstoqueRepository
from estoque.service import EstoqueService


def criar_banco_teste_lotes():
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()

    # Tabela de produtos do GeoApolo
    cur.execute("""
        CREATE TABLE USER_geoapolo_produtos (
            prodcod INTEGER PRIMARY KEY,
            prodnome TEXT,
            codigo_lote TEXT
        )
    """)
    cur.execute("INSERT INTO USER_geoapolo_produtos VALUES (101, 'VACINA ANTIRRABICA', 'LOTE_PADRAO')")
    cur.execute("INSERT INTO USER_geoapolo_produtos VALUES (102, 'DIPIRONA GOTAS', '')")
    cur.execute("INSERT INTO USER_geoapolo_produtos VALUES (103, 'SERINGA DESCARTAVEL', NULL)")

    # Tabela de PRODUTO (Alvo)
    cur.execute("""
        CREATE TABLE PRODUTO (
            ProdCodEstr TEXT PRIMARY KEY,
            ProdNome TEXT,
            ProdCtrlEstqLote TEXT
        )
    """)
    cur.execute("INSERT INTO PRODUTO VALUES ('102', 'DIPIRONA GOTAS', 'Sim')")
    cur.execute("INSERT INTO PRODUTO VALUES ('103', 'SERINGA DESCARTAVEL', 'Nao')")

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

    # Garante tabelas de estoque
    estq_repo = EstoqueRepository(conn)
    estq_repo._garantir_tabelas_geoapolo()

    cur.execute("INSERT OR REPLACE INTO USER_geoapolo_estoque (codigo_empresa, prodcod, saldo_atual, saldo_disponivel) VALUES ('1.01', 101, 100.0, 100.0)")
    cur.execute("INSERT OR REPLACE INTO USER_geoapolo_estoque (codigo_empresa, prodcod, saldo_atual, saldo_disponivel) VALUES ('1.01', 102, 50.0, 50.0)")

    conn.commit()
    return conn


class TestLotesVencimento(unittest.TestCase):

    def setUp(self):
        self.conn = criar_banco_teste_lotes()
        self.lote_repo = LotesRepository(self.conn)
        self.lote_svc = LotesService(self.lote_repo)
        self.estq_repo = EstoqueRepository(self.conn)
        self.estq_svc = EstoqueService(self.estq_repo)
        self.hoje = datetime.now()

    def tearDown(self):
        self.conn.close()

    def test_01_produto_controla_lote_geoapolo(self):
        # Produto 101 tem codigo_lote preenchido em USER_geoapolo_produtos
        self.assertTrue(self.lote_svc.produto_controla_lote(101))

    def test_02_produto_controla_lote_alvo(self):
        # Produto 102 tem ProdCtrlEstqLote = 'Sim' em PRODUTO
        self.assertTrue(self.lote_svc.produto_controla_lote(102))

    def test_03_produto_nao_controla_lote(self):
        # Produto 103 tem ProdCtrlEstqLote = 'Nao' e sem lote cadastrado
        self.assertFalse(self.lote_svc.produto_controla_lote(103))

    def test_04_produto_controla_lote_por_ter_lotes_cadastrados(self):
        # Se cadastrar lote para 103, ele passa a ter controle
        dto = ProdutoLoteDTO(prodcod=103, numero_lote="LOTE103", data_validade="2027-12-31")
        self.lote_svc.salvar_lote(dto)
        self.assertTrue(self.lote_svc.produto_controla_lote(103))

    def test_05_faixa_normal_mais_de_30_dias(self):
        dt_val = (self.hoje + timedelta(days=45)).strftime("%Y-%m-%d")
        dto = ProdutoLoteDTO(prodcod=101, numero_lote="LOTE_OK", data_validade=dt_val)
        self.lote_svc.salvar_lote(dto)

        nivel, dias, fmt = self.lote_svc.verificar_vencimento_lote(101, "LOTE_OK", data_base=self.hoje)
        self.assertEqual(nivel, "NORMAL")
        self.assertGreater(dias, 30)

    def test_06_faixa_amarela_entre_10_e_30_dias(self):
        dt_val = (self.hoje + timedelta(days=20)).strftime("%Y-%m-%d")
        dto = ProdutoLoteDTO(prodcod=101, numero_lote="LOTE_AMARELO", data_validade=dt_val)
        self.lote_svc.salvar_lote(dto)

        nivel, dias, fmt = self.lote_svc.verificar_vencimento_lote(101, "LOTE_AMARELO", data_base=self.hoje)
        self.assertEqual(nivel, "AMARELO")
        self.assertTrue(10 < dias <= 30)

    def test_07_faixa_vermelha_entre_5_e_10_dias(self):
        dt_val = (self.hoje + timedelta(days=7)).strftime("%Y-%m-%d")
        dto = ProdutoLoteDTO(prodcod=101, numero_lote="LOTE_VERMELHO", data_validade=dt_val)
        self.lote_svc.salvar_lote(dto)

        nivel, dias, fmt = self.lote_svc.verificar_vencimento_lote(101, "LOTE_VERMELHO", data_base=self.hoje)
        self.assertEqual(nivel, "VERMELHO")
        self.assertTrue(5 < dias <= 10)

    def test_08_faixa_roxa_entre_0_e_5_dias_bloqueio(self):
        dt_val = (self.hoje + timedelta(days=3)).strftime("%Y-%m-%d")
        dto = ProdutoLoteDTO(prodcod=101, numero_lote="LOTE_ROXO", data_validade=dt_val)
        self.lote_svc.salvar_lote(dto)

        nivel, dias, fmt = self.lote_svc.verificar_vencimento_lote(101, "LOTE_ROXO", data_base=self.hoje)
        self.assertEqual(nivel, "ROXO")
        self.assertTrue(0 <= dias <= 5)

    def test_09_faixa_roxa_lote_vencido_bloqueio(self):
        dt_val = (self.hoje - timedelta(days=2)).strftime("%Y-%m-%d")
        dto = ProdutoLoteDTO(prodcod=101, numero_lote="LOTE_VENCIDO", data_validade=dt_val)
        self.lote_svc.salvar_lote(dto)

        nivel, dias, fmt = self.lote_svc.verificar_vencimento_lote(101, "LOTE_VENCIDO", data_base=self.hoje)
        self.assertEqual(nivel, "ROXO")
        self.assertLess(dias, 0)

    def test_10_atender_item_requisicao_com_lote(self):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO USER_geoapolo_requisicoes (codigo_empresa, numero_requisicao, data_requisicao, solicitante, centro_custo, status, observacao)
            VALUES ('1.01', 'REQ-001', '2026-10-03', 'JOAO', 'CC01', 'Aberta', '')
        """)
        cur.execute("""
            INSERT INTO USER_geoapolo_requisicao_itens (codigo_empresa, numero_requisicao, item_seq, prodcod, unidade, quantidade_solicitada, quantidade_atendida, saldo_pendente, status_item, observacao)
            VALUES ('1.01', 'REQ-001', 1, 101, 'UN', 10.0, 0.0, 10.0, 'Pendente', '')
        """)
        self.conn.commit()

        res = self.estq_svc.atender_item_requisicao(
            req_num="REQ-001",
            item_seq=1,
            qtd_atender=5.0,
            empcod="1.01",
            observacao="BAIXA PARCIAL COM LOTE",
            numero_lote="LOTE12345",
        )
        self.assertTrue(res.sucesso)

        # Checa se o lote foi salvo na movimentação
        cur.execute("SELECT numero_lote, quantidade, tipo_movimento FROM USER_geoapolo_movimentacoes_estoque WHERE numero_requisicao = 'REQ-001'")
        r = cur.fetchone()
        self.assertIsNotNone(r)
        self.assertEqual(r[0], "LOTE12345")
        self.assertEqual(r[1], 5.0)
        self.assertEqual(r[2], "S")

    def test_11_saida_direta_com_lote(self):
        res = self.estq_svc.registrar_saida_direta(
            empcod="1.01",
            prodcod_estr="101",
            quantidade=3.0,
            destino_obs="TESTE SAIDA",
            centro_custo="CC01",
            numero_lote="LOTE_SAIDA",
        )
        self.assertTrue(res.sucesso)

        cur = self.conn.cursor()
        cur.execute("SELECT numero_lote, quantidade, tipo_movimento FROM USER_geoapolo_movimentacoes_estoque WHERE origem_movimento = 'SAIDA_DIRETA'")
        r = cur.fetchone()
        self.assertIsNotNone(r)
        self.assertEqual(r[0], "LOTE_SAIDA")
        self.assertEqual(r[1], 3.0)

    def test_12_alerta_vencimento_modal_headless(self):
        root = tk.Tk()
        root.withdraw()
        try:
            # Testa se o modal ROXO retorna False e não bloqueia a aplicação
            def _fechar_modal():
                for w in root.winfo_children():
                    if isinstance(w, tk.Toplevel):
                        w.destroy()
            root.after(100, _fechar_modal)
            res_roxo = exibir_alerta_vencimento_lote(
                root,
                nivel="ROXO",
                numero_lote="LOTE_ROXO",
                prodnome="MATERIAL TESTE",
                data_validade="05/10/2026",
                dias_restantes=2,
            )
            self.assertFalse(res_roxo)
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
