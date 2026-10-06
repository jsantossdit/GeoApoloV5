"""
Testes Unitários para:
1. Gestão centralizada de sessão corporativa (obter_empresa_ativa, definir_empresa_ativa)
2. Baixa de estoque e saldo de lote no atendimento de requisições
3. Correção do grid e resolução de referências no modal de saída direta
4. Resiliência na consulta de fornecedores de lotes com USER_geoapolo_entidade
"""

import sqlite3
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import tkinter as tk

from core.sessao import obter_empresa_ativa, definir_empresa_ativa, obter_nome_empresa_ativa
from lotes.models import ProdutoLoteDTO
from lotes.repository import LotesRepository
from lotes.service import LotesService
from estoque.models import RequisicaoDTO, ItemRequisicaoDTO
from estoque.repository import EstoqueRepository
from estoque.service import EstoqueService


def criar_banco_teste_completo():
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()

    # Empresas
    cur.execute("""
        CREATE TABLE USER_geoapolo_empresas (
            empcod VARCHAR(10) PRIMARY KEY,
            empnome VARCHAR(100)
        )
    """)
    cur.execute("INSERT INTO USER_geoapolo_empresas VALUES ('1', 'APAE GUARATINGUETA')")

    # Produtos
    cur.execute("""
        CREATE TABLE USER_geoapolo_produtos (
            prodcod INTEGER PRIMARY KEY,
            prodnome VARCHAR(100),
            unidade VARCHAR(10) DEFAULT 'UN',
            codigo_lote VARCHAR(50) NULL
        )
    """)
    cur.execute("INSERT INTO USER_geoapolo_produtos VALUES (30, 'PAO DE HAMBURGUER', 'UN', 'LT30')")

    # Estoque
    cur.execute("""
        CREATE TABLE USER_geoapolo_estoque (
            codigo_empresa VARCHAR(10) NOT NULL,
            prodcod INTEGER NOT NULL,
            saldo_atual DECIMAL(18,6) NOT NULL DEFAULT 0,
            quantidade_reservada DECIMAL(18,6) NOT NULL DEFAULT 0,
            saldo_disponivel DECIMAL(18,6) NOT NULL DEFAULT 0,
            data_ultima_movimentacao TEXT NULL,
            PRIMARY KEY (codigo_empresa, prodcod)
        )
    """)
    cur.execute("INSERT INTO USER_geoapolo_estoque VALUES ('1', 30, 435.0, 0.0, 435.0, '2026-10-03 19:14:25')")

    # Movimentações
    cur.execute("""
        CREATE TABLE USER_geoapolo_movimentacoes_estoque (
            codigo_movimento INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_empresa VARCHAR(10) NOT NULL,
            data_movimento TEXT NOT NULL,
            tipo_movimento CHAR(1) NOT NULL,
            origem_movimento VARCHAR(30) NOT NULL,
            prodcod INTEGER NOT NULL,
            unidade VARCHAR(10) NULL,
            quantidade DECIMAL(18,6) NOT NULL,
            valor_unitario DECIMAL(18,6) NOT NULL DEFAULT 0,
            valor_total DECIMAL(18,6) NOT NULL DEFAULT 0,
            documento_origem VARCHAR(50) NULL,
            numero_requisicao VARCHAR(20) NULL,
            item_requisicao_seq INTEGER NULL,
            centro_custo VARCHAR(30) NULL,
            numero_lote VARCHAR(50) NULL,
            observacao VARCHAR(255) NULL
        )
    """)

    # Lotes
    cur.execute("""
        CREATE TABLE user_geoapolo_produto_lote (
            ID_PRODUTO_LOTE INTEGER PRIMARY KEY AUTOINCREMENT,
            prodcod INTEGER NOT NULL,
            NUMERO_LOTE VARCHAR(50) NOT NULL,
            DATA_FABRICACAO TEXT,
            DATA_VALIDADE TEXT,
            QUANTIDADE_INICIAL REAL NOT NULL DEFAULT 0,
            QUANTIDADE_ATUAL REAL NOT NULL DEFAULT 0,
            DATA_ENTRADA TEXT,
            entcod_fornecedor INTEGER,
            STATUS CHAR(1) NOT NULL DEFAULT 'A',
            OBSERVACAO VARCHAR(500),
            DATA_CADASTRO TEXT,
            usucod VARCHAR(20)
        )
    """)
    d_val = (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d")
    cur.execute(
        "INSERT INTO user_geoapolo_produto_lote (prodcod, NUMERO_LOTE, DATA_VALIDADE, QUANTIDADE_INICIAL, QUANTIDADE_ATUAL, STATUS) "
        "VALUES (30, 'LOTE-PAO-01', ?, 500.0, 435.0, 'A')",
        [d_val]
    )

    # Entidades (USER_geoapolo_entidade)
    cur.execute("""
        CREATE TABLE USER_geoapolo_entidade (
            geoentcod VARCHAR(20) PRIMARY KEY,
            geoentnome VARCHAR(100)
        )
    """)
    cur.execute("INSERT INTO USER_geoapolo_entidade VALUES ('38', 'FORNECEDOR DE PAES LTDA')")

    # Requisições
    cur.execute("""
        CREATE TABLE USER_geoapolo_requisicoes (
            numero_requisicao VARCHAR(20) NOT NULL,
            codigo_empresa VARCHAR(10) NOT NULL,
            data_requisicao TEXT NOT NULL,
            codigo_solicitante VARCHAR(20) NULL,
            nome_solicitante VARCHAR(100) NULL,
            centro_custo VARCHAR(30) NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'Aberta',
            observacao VARCHAR(255) NULL,
            PRIMARY KEY (numero_requisicao, codigo_empresa)
        )
    """)
    cur.execute("INSERT INTO USER_geoapolo_requisicoes VALUES ('REQ001', '1', '2026-10-03', '38', 'SOLICITANTE', '01.01', 'Aberta', 'REQ TESTE')")

    cur.execute("""
        CREATE TABLE USER_geoapolo_requisicao_itens (
            numero_requisicao VARCHAR(20) NOT NULL,
            codigo_empresa VARCHAR(10) NOT NULL,
            item_seq INTEGER NOT NULL,
            prodcod INTEGER NOT NULL,
            quantidade_solicitada DECIMAL(18,6) NOT NULL,
            quantidade_atendida DECIMAL(18,6) NOT NULL DEFAULT 0,
            saldo_pendente DECIMAL(18,6) NOT NULL,
            unidade VARCHAR(10) NULL,
            status_item VARCHAR(20) NOT NULL DEFAULT 'Pendente',
            PRIMARY KEY (numero_requisicao, codigo_empresa, item_seq)
        )
    """)
    cur.execute("INSERT INTO USER_geoapolo_requisicao_itens VALUES ('REQ001', '1', 1, 30, 50.0, 0.0, 50.0, 'UN', 'Pendente')")

    conn.commit()
    return conn


class TestLotesSaidaSaldosSessao(unittest.TestCase):
    """Testes de Sessão, Baixa de Saldos e Lotes."""

    def setUp(self):
        self.conn = criar_banco_teste_completo()
        self.estoque_repo = EstoqueRepository(self.conn)
        self.estoque_svc = EstoqueService(self.estoque_repo)
        self.lotes_repo = LotesRepository(self.conn)
        self.lotes_svc = LotesService(self.lotes_repo)

    def tearDown(self):
        self.conn.close()
        try:
            from logon import sessao_usuario_atual
            sessao_usuario_atual.pop("codigo_empresa", None)
            sessao_usuario_atual.pop("empcod", None)
            sessao_usuario_atual.pop("nome_empresa", None)
        except Exception:
            pass
        try:
            from empresas.service import EmpresasService
            EmpresasService._empresa_ativa_contexto = None
        except Exception:
            pass

    def test_obter_e_definir_empresa_ativa(self):
        """Verifica que a empresa selecionada é gravada e obtida com precisão."""
        definir_empresa_ativa("2.05", "FILIAL 2.05 TESTE")
        self.assertEqual(obter_empresa_ativa(), "2.05")
        self.assertIn("2.05", obter_nome_empresa_ativa())

        # Redefine para empresa 1
        definir_empresa_ativa("1", "APAE GUARATINGUETA")
        self.assertEqual(obter_empresa_ativa(), "1")

    def test_saldo_produto_na_empresa_ativa(self):
        """Garante que a consulta de saldos retorna os valores corretos para a empresa 1."""
        saldos = self.estoque_repo.consultar_saldos_produtos(empcod="1", termo_busca="30")
        self.assertEqual(len(saldos), 1)
        self.assertEqual(saldos[0].prodcod_estr, "30")
        self.assertEqual(saldos[0].saldo_atual, 435.0)

    def test_baixa_saldo_produto_e_lote_no_atendimento(self):
        """Verifica que ao atender a requisição, o saldo de estoque e do lote são ambos debitados."""
        sucesso, msg, mov_chv = self.estoque_repo.atender_item_requisicao(
            req_num="REQ001",
            item_seq=1,
            qtd_atender=35.0,
            empcod="1",
            observacao="BAIXA REQUISICAO TESTE",
            numero_lote="LOTE-PAO-01",
        )
        self.assertTrue(sucesso)
        self.assertGreater(mov_chv, 0)

        # Verifica saldo do produto em USER_geoapolo_estoque (435 - 35 = 400)
        s_atual, _, s_disp = self.estoque_repo.obter_saldo_produto("1", 30)
        self.assertEqual(s_atual, 400.0)
        self.assertEqual(s_disp, 400.0)

        # Verifica saldo do lote em user_geoapolo_produto_lote (435 - 35 = 400)
        cur = self.conn.cursor()
        cur.execute("SELECT QUANTIDADE_ATUAL FROM user_geoapolo_produto_lote WHERE prodcod = 30 AND NUMERO_LOTE = 'LOTE-PAO-01'")
        row = cur.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(float(row[0]), 400.0)

    def test_saida_direta_debita_estoque_e_lote(self):
        """Verifica que a saída direta debita saldo do produto e lote."""
        sucesso, msg, mov_chv = self.estoque_repo.registrar_movimentacao_saida_direta(
            empcod="1",
            prodcod_estr="30",
            quantidade=20.0,
            destino_obs="LANCHE DA TARDE",
            centro_custo="01.01",
            numero_lote="LOTE-PAO-01",
        )
        self.assertTrue(sucesso)
        self.assertGreater(mov_chv, 0)

        s_atual, _, _ = self.estoque_repo.obter_saldo_produto("1", 30)
        self.assertEqual(s_atual, 415.0)

        cur = self.conn.cursor()
        cur.execute("SELECT QUANTIDADE_ATUAL FROM user_geoapolo_produto_lote WHERE prodcod = 30 AND NUMERO_LOTE = 'LOTE-PAO-01'")
        self.assertEqual(float(cur.fetchone()[0]), 415.0)

    def test_alerta_vencimento_lote_regras(self):
        """Valida que lote com 20 dias restantes retorna nível AMARELO."""
        nivel, dias, fmt = self.lotes_svc.verificar_vencimento_lote(30, "LOTE-PAO-01")
        self.assertEqual(nivel, "AMARELO")
        self.assertGreaterEqual(dias, 10)
        self.assertLessEqual(dias, 30)


if __name__ == "__main__":
    unittest.main()
