"""
Testes Unitários para o Módulo de Estoque e Requisições (GeoApolo V5).
Cobertura: EstoqueRepository, EstoqueService, Atendimento, Cancelamento, Devolução, Entradas/Saídas, Kardex,
Emissão de Novas Requisições e Views Headless.
"""

import sqlite3
import tkinter as tk
from tkinter import ttk
import unittest
from datetime import datetime
from estoque.models import (
    RequisicaoDTO,
    ItemRequisicaoDTO,
    MovimentoEstoqueDTO,
    FichaEstoqueLinhaDTO,
    SaldoProdutoDTO,
    ResultadoEstoqueDTO,
)
from estoque.repository import EstoqueRepository
from estoque.service import EstoqueService
from estoque.requisicoes_view import RequisicoesView
from estoque.movimentacao_view import MovimentacaoView
from estoque.consultas_view import ConsultasEstoqueView
from estoque.nova_requisicao_view import NovaRequisicaoView


def criar_banco_teste():
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()

    # 1. Catálogo próprio de produtos do GeoApolo
    cur.execute("""
        CREATE TABLE USER_geoapolo_produtos (
            prodcod INTEGER PRIMARY KEY,
            prodnome TEXT,
            grupocod INTEGER
        )
    """)

    # 2. Centros de controle / custo do GeoApolo
    cur.execute("""
        CREATE TABLE USER_geoapolo_centro_controle (
            geocctrlcodestr TEXT PRIMARY KEY,
            geocctrlnome TEXT
        )
    """)

    # Carga inicial de produtos GeoApolo
    cur.execute("INSERT INTO USER_geoapolo_produtos (prodcod, prodnome, grupocod) VALUES (101, 'CABO DE FIBRA OPTICA 12FO', 1)")
    cur.execute("INSERT INTO USER_geoapolo_produtos (prodcod, prodnome, grupocod) VALUES (102, 'CONECTOR SC/APC FAST', 1)")
    cur.execute("INSERT INTO USER_geoapolo_produtos (prodcod, prodnome, grupocod) VALUES (9001, 'ONU GPON WIFI AC', 2)")

    # Centros de controle/custo
    cur.execute("INSERT INTO USER_geoapolo_centro_controle (geocctrlcodestr, geocctrlnome) VALUES ('01.01.001', 'DEPARTAMENTO DE TI')")
    cur.execute("INSERT INTO USER_geoapolo_centro_controle (geocctrlcodestr, geocctrlnome) VALUES ('01.01.002', 'ALMOXARIFADO CENTRAL')")

    # Configurações do sistema
    cur.execute("""
        CREATE TABLE IF NOT EXISTS USER_geoapolo_configuracoes (
            empcod TEXT PRIMARY KEY,
            permite_estoque_negativo TEXT DEFAULT 'Sim'
        )
    """)
    cur.execute("INSERT INTO USER_geoapolo_configuracoes (empcod, permite_estoque_negativo) VALUES ('1.01', 'Sim')")

    conn.commit()

    # 3. Inicialização automática das tabelas dedicadas de estoque GeoApolo
    repo = EstoqueRepository(conn)
    repo._garantir_tabelas_geoapolo()

    # 4. Inserção de Requisição Exemplo em USER_geoapolo_requisicoes e itens
    cur.execute("""
        INSERT INTO USER_geoapolo_requisicoes (codigo_empresa, numero_requisicao, data_requisicao, solicitante, centro_custo, status, observacao)
        VALUES ('1.01', 'REQ-1001', '2026-09-26 10:00:00', 'JOAO DA SILVA', '01.01.001', 'Aberta', 'MATERIAL PARA INSTALACAO')
    """)
    cur.execute("""
        INSERT INTO USER_geoapolo_requisicao_itens (codigo_empresa, numero_requisicao, item_seq, prodcod, unidade, quantidade_solicitada, quantidade_atendida, saldo_pendente, status_item, observacao)
        VALUES ('1.01', 'REQ-1001', 1, 101, 'MT', 100.0, 0.0, 100.0, 'Pendente', '')
    """)
    cur.execute("""
        INSERT INTO USER_geoapolo_requisicao_itens (codigo_empresa, numero_requisicao, item_seq, prodcod, unidade, quantidade_solicitada, quantidade_atendida, saldo_pendente, status_item, observacao)
        VALUES ('1.01', 'REQ-1001', 2, 102, 'UN', 10.0, 0.0, 10.0, 'Pendente', '')
    """)

    conn.commit()
    return conn


class TestEstoqueRepositoryEService(unittest.TestCase):

    def setUp(self):
        self.conn = criar_banco_teste()
        self.repo = EstoqueRepository(self.conn)
        self.service = EstoqueService(self.repo)

    def tearDown(self):
        self.conn.close()

    def test_isolamento_sem_tabelas_legadas_alvo(self):
        """Garante que as tabelas legadas do Alvo NÃO existem e o estoque opera 100% isolado."""
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = [r[0] for r in cur.fetchall()]

        # Verifica que tabelas do Alvo não existem
        for tab_alvo in ["REQ_MAT", "ITEM_REQ_MAT", "MOV_ESTQ", "ITEM_MOV_ESTQ", "PRODUTO"]:
            self.assertNotIn(tab_alvo, tabelas, f"Tabela legada {tab_alvo} não deve existir!")

        # Verifica que tabelas do GeoApolo existem
        for tab_geo in [
            "USER_geoapolo_produtos",
            "USER_geoapolo_estoque",
            "USER_geoapolo_requisicoes",
            "USER_geoapolo_requisicao_itens",
            "USER_geoapolo_movimentacoes_estoque",
        ]:
            self.assertIn(tab_geo, tabelas, f"Tabela dedicada {tab_geo} deve existir!")

    def test_listar_requisicoes(self):
        reqs = self.service.listar_requisicoes(empcod="1.01")
        self.assertEqual(len(reqs), 1)
        self.assertEqual(reqs[0].req_num, "REQ-1001")
        self.assertEqual(reqs[0].requerente, "JOAO DA SILVA")
        self.assertEqual(reqs[0].status, "Aberta")

    def test_obter_requisicao_com_itens(self):
        req = self.service.obter_requisicao("REQ-1001", "1.01")
        self.assertIsNotNone(req)
        self.assertEqual(len(req.itens), 2)
        self.assertEqual(req.itens[0].prodnome, "CABO DE FIBRA OPTICA 12FO")
        self.assertEqual(req.itens[0].qtd_solicitada, 100.0)
        self.assertEqual(req.itens[0].saldo_pendente, 100.0)

    def test_proximo_numero_requisicao_e_centros_custo(self):
        prox = self.service.obter_proximo_numero_requisicao("1.01")
        self.assertTrue(len(prox) > 0)

        centros = self.service.listar_centros_custo("1.01")
        self.assertGreaterEqual(len(centros), 2)
        self.assertEqual(centros[0][0], "01.01.001")

    def test_criar_nova_requisicao_sucesso(self):
        nova_req = RequisicaoDTO(
            req_num="REQ-2002",
            empcod="1.01",
            data_req="2026-09-26 15:30:00",
            requerente="MARIA OLIVEIRA",
            centro_custo="01.01.001",
            status="Aberta",
            observacao="EXPANSAO DE REDE",
            itens=[
                ItemRequisicaoDTO(
                    prodcod_estr="101",
                    prodnome="CABO DE FIBRA OPTICA 12FO",
                    unidade="MT",
                    qtd_solicitada=250.0,
                ),
                ItemRequisicaoDTO(
                    prodcod_estr="102",
                    prodnome="CONECTOR SC/APC FAST",
                    unidade="UN",
                    qtd_solicitada=50.0,
                ),
            ],
        )

        res = self.service.criar_requisicao(nova_req)
        self.assertTrue(res.sucesso)
        self.assertEqual(res.documento, "REQ-2002")

        # Verificar persistência no banco
        req_db = self.service.obter_requisicao("REQ-2002", "1.01")
        self.assertIsNotNone(req_db)
        self.assertEqual(req_db.requerente, "MARIA OLIVEIRA")
        self.assertEqual(req_db.centro_custo, "01.01.001")
        self.assertEqual(req_db.status, "Aberta")
        self.assertEqual(len(req_db.itens), 2)
        self.assertEqual(req_db.itens[0].qtd_solicitada, 250.0)
        self.assertEqual(req_db.itens[0].saldo_pendente, 250.0)
        self.assertEqual(req_db.itens[0].qtd_atendida, 0.0)

    def test_criar_nova_requisicao_validacoes(self):
        # 1. Sem requerente
        r1 = RequisicaoDTO(req_num="R1", requerente="", centro_custo="01.01", itens=[ItemRequisicaoDTO(prodcod_estr="101", qtd_solicitada=1)])
        res1 = self.service.criar_requisicao(r1)
        self.assertFalse(res1.sucesso)
        self.assertIn("solicitante", res1.mensagem)

        # 2. Sem centro de custo
        r2 = RequisicaoDTO(req_num="R2", requerente="USER", centro_custo="", itens=[ItemRequisicaoDTO(prodcod_estr="101", qtd_solicitada=1)])
        res2 = self.service.criar_requisicao(r2)
        self.assertFalse(res2.sucesso)
        self.assertIn("centro de custo", res2.mensagem)

        # 3. Sem itens
        r3 = RequisicaoDTO(req_num="R3", requerente="USER", centro_custo="01.01", itens=[])
        res3 = self.service.criar_requisicao(r3)
        self.assertFalse(res3.sucesso)
        self.assertIn("ao menos um item", res3.mensagem)

        # 4. Item com quantidade zerada
        r4 = RequisicaoDTO(req_num="R4", requerente="USER", centro_custo="01.01", itens=[ItemRequisicaoDTO(prodcod_estr="101", qtd_solicitada=0)])
        res4 = self.service.criar_requisicao(r4)
        self.assertFalse(res4.sucesso)
        self.assertIn("maior que zero", res4.mensagem)

    def test_atendimento_parcial_requisicao(self):
        res = self.service.atender_item_requisicao(
            req_num="REQ-1001",
            item_seq=1,
            qtd_atender=40.0,
            empcod="1.01",
            observacao="BAIXA PARCIAL TECNICO",
        )
        self.assertTrue(res.sucesso)
        self.assertGreater(res.codigo, 0)

        req = self.service.obter_requisicao("REQ-1001", "1.01")
        self.assertEqual(req.itens[0].qtd_atendida, 40.0)
        self.assertEqual(req.itens[0].saldo_pendente, 60.0)
        self.assertEqual(req.itens[0].status_item, "Atendido Parcial")
        self.assertEqual(req.status, "Atendida Parcial")

        movs = self.service.listar_movimentacoes(empcod="1.01", tipo_filtro="SAIDA")
        self.assertEqual(len(movs), 1)
        self.assertEqual(movs[0].tipo_movimento, "S")
        self.assertEqual(movs[0].quantidade, 40.0)
        self.assertEqual(movs[0].origem_movimento, "REQUISICAO")

    def test_atendimento_total_requisicao(self):
        res1 = self.service.atender_item_requisicao("REQ-1001", 1, 100.0, "1.01")
        self.assertTrue(res1.sucesso)

        res2 = self.service.atender_item_requisicao("REQ-1001", 2, 10.0, "1.01")
        self.assertTrue(res2.sucesso)

        req = self.service.obter_requisicao("REQ-1001", "1.01")
        self.assertEqual(req.status, "Atendida Total")
        self.assertEqual(req.itens[0].status_item, "Atendido")
        self.assertEqual(req.itens[1].status_item, "Atendido")

    def test_atendimento_validacoes_erro(self):
        res = self.service.atender_item_requisicao("REQ-1001", 1, 0, "1.01")
        self.assertFalse(res.sucesso)

        res2 = self.service.atender_item_requisicao("REQ-1001", 1, 150.0, "1.01")
        self.assertFalse(res2.sucesso)
        self.assertIn("ultrapassa o saldo", res2.mensagem)

        res3 = self.service.atender_item_requisicao("REQ-9999", 1, 10.0, "1.01")
        self.assertFalse(res3.sucesso)

    def test_bloqueio_estoque_negativo_atendimento(self):
        """Valida que quando permite_estoque_negativo é 'Nao', o atendimento sem saldo é bloqueado com a mensagem exata."""
        cur = self.conn.cursor()
        cur.execute("UPDATE USER_geoapolo_configuracoes SET permite_estoque_negativo = 'Nao' WHERE empcod = '1.01'")
        self.conn.commit()

        # Tenta atender item 1 da REQ-1001 (saldo atual em estoque é 0.0)
        res = self.service.atender_item_requisicao("REQ-1001", 1, 10.0, "1.01")
        self.assertFalse(res.sucesso)
        self.assertEqual(
            res.mensagem,
            "O sistema não permite estoque negativo, este produto não tem em estoque e não permite movimentação",
        )

    def test_bloqueio_estoque_negativo_atendimento_total(self):
        """Valida que quando permite_estoque_negativo é 'Nao', o atendimento total da requisição sem saldo é bloqueado."""
        cur = self.conn.cursor()
        cur.execute("UPDATE USER_geoapolo_configuracoes SET permite_estoque_negativo = 'Nao' WHERE empcod = '1.01'")
        self.conn.commit()

        # Tenta atendimento total da requisição sem saldo prévio
        res = self.service.atender_requisicao_completa("REQ-1001", "1.01")
        self.assertFalse(res.sucesso)
        self.assertEqual(
            res.mensagem,
            "O sistema não permite estoque negativo, este produto não tem em estoque e não permite movimentação",
        )

    def test_bloqueio_estoque_negativo_saida_direta(self):
        """Valida que quando permite_estoque_negativo é 'Nao', a saída direta sem saldo é bloqueada."""
        cur = self.conn.cursor()
        cur.execute("UPDATE USER_geoapolo_configuracoes SET permite_estoque_negativo = 'Nao' WHERE empcod = '1.01'")
        self.conn.commit()

        # Tenta saída direta de 5.0 unidades sem saldo
        res = self.service.registrar_saida_direta("1.01", "101", 5.0, "CONSUMO DIRETO")
        self.assertFalse(res.sucesso)
        self.assertEqual(
            res.mensagem,
            "O sistema não permite estoque negativo, este produto não tem em estoque e não permite movimentação",
        )

    def test_permissao_estoque_negativo_quando_sim(self):
        """Valida que quando permite_estoque_negativo é 'Sim', a movimentação sem saldo é permitida."""
        cur = self.conn.cursor()
        cur.execute("UPDATE USER_geoapolo_configuracoes SET permite_estoque_negativo = 'Sim' WHERE empcod = '1.01'")
        self.conn.commit()

        # Com 'Sim', deve permitir atender e movimentar
        res = self.service.atender_item_requisicao("REQ-1001", 1, 10.0, "1.01")
        self.assertTrue(res.sucesso)
        self.assertGreater(res.codigo, 0)

    def test_cancelamento_requisicao(self):
        res_sem_mot = self.service.cancelar_requisicao("REQ-1001", "1.01", "")
        self.assertFalse(res_sem_mot.sucesso)

        res = self.service.cancelar_requisicao("REQ-1001", "1.01", "Projeto cancelado")
        self.assertTrue(res.sucesso)

        req = self.service.obter_requisicao("REQ-1001", "1.01")
        self.assertEqual(req.status, "Cancelada")

        res2 = self.service.cancelar_requisicao("REQ-1001", "1.01", "Outro motivo")
        self.assertFalse(res2.sucesso)

    def test_devolucao_item_requisicao(self):
        self.service.atender_item_requisicao("REQ-1001", 1, 50.0, "1.01")

        res_inv = self.service.devolver_item_requisicao("REQ-1001", 1, 60.0, "1.01")
        self.assertFalse(res_inv.sucesso)

        res_dev = self.service.devolver_item_requisicao("REQ-1001", 1, 20.0, "1.01", "Sobrou na obra")
        self.assertTrue(res_dev.sucesso)

        req = self.service.obter_requisicao("REQ-1001", "1.01")
        self.assertEqual(req.itens[0].qtd_atendida, 30.0)
        self.assertEqual(req.itens[0].saldo_pendente, 70.0)

        movs = self.service.listar_movimentacoes(empcod="1.01", tipo_filtro="ENTRADA")
        self.assertEqual(len(movs), 1)
        self.assertEqual(movs[0].tipo_movimento, "E")
        self.assertEqual(movs[0].quantidade, 20.0)
        self.assertEqual(movs[0].origem_movimento, "DEVOLUCAO")

    def test_entrada_compras(self):
        res_err = self.service.registrar_entrada_compras("1.01", "", 10.0)
        self.assertFalse(res_err.sucesso)

        res = self.service.registrar_entrada_compras(
            empcod="1.01",
            prodcod_estr="101",
            quantidade=500.0,
            valor_unitario=2.50,
            num_doc="NF-12345",
            fornecedor_obs="FORNECEDOR FIBRA BRASIL",
        )
        self.assertTrue(res.sucesso)
        self.assertEqual(res.documento, "NF-12345")

        movs = self.service.listar_movimentacoes(empcod="1.01", tipo_filtro="ENTRADA")
        self.assertEqual(len(movs), 1)
        self.assertEqual(movs[0].quantidade, 500.0)
        self.assertEqual(movs[0].valor_unitario, 2.50)
        self.assertEqual(movs[0].origem_movimento, "COMPRA")

    def test_saida_direta(self):
        res_err = self.service.registrar_saida_direta("1.01", "102", 0)
        self.assertFalse(res_err.sucesso)

        res = self.service.registrar_saida_direta(
            empcod="1.01",
            prodcod_estr="102",
            quantidade=3.0,
            destino_obs="CONSUMO INTERNO LABORATORIO",
        )
        self.assertTrue(res.sucesso)

        movs = self.service.listar_movimentacoes(empcod="1.01", tipo_filtro="SAIDA")
        self.assertEqual(len(movs), 1)
        self.assertEqual(movs[0].quantidade, 3.0)
        self.assertEqual(movs[0].origem_movimento, "SAIDA_DIRETA")

    def test_ficha_estoque_kardex_e_saldos(self):
        self.service.registrar_entrada_compras("1.01", "101", 100.0, 3.0, "NF-100")
        self.service.atender_item_requisicao("REQ-1001", 1, 30.0, "1.01")
        self.service.devolver_item_requisicao("REQ-1001", 1, 10.0, "1.01")
        self.service.registrar_saida_direta("1.01", "101", 5.0, "TESTE BANCADA")

        kardex = self.service.consultar_ficha_estoque("101", "1.01")
        self.assertEqual(len(kardex), 4)
        self.assertEqual(kardex[-1].saldo_acumulado, 75.0)

        saldos = self.service.consultar_saldos_produtos("1.01", "101")
        self.assertEqual(len(saldos), 1)
        self.assertEqual(saldos[0].saldo_atual, 75.0)
        self.assertEqual(saldos[0].saldo_disponivel, 75.0)

    def test_obter_saldo_produto(self):
        s_atual, reserv, disp = self.service.obter_saldo_produto("101", "1.01")
        self.assertEqual(s_atual, 0.0)
        self.assertEqual(disp, 0.0)

        self.service.registrar_entrada_compras("1.01", "101", 120.0, 5.0, "NF-TESTE")
        s_atual, reserv, disp = self.service.obter_saldo_produto("101", "1.01")
        self.assertEqual(s_atual, 120.0)
        self.assertEqual(disp, 120.0)

    def test_atender_requisicao_completa(self):
        res = self.service.atender_requisicao_completa("REQ-1001", "1.01", "BAIXA TOTAL DE TESTE")
        self.assertTrue(res.sucesso)
        self.assertIn("2 item(ns) atendido(s)", res.mensagem)

        req = self.service.obter_requisicao("REQ-1001", "1.01")
        self.assertEqual(req.status, "Atendida Total")
        for item in req.itens:
            self.assertEqual(item.saldo_pendente, 0.0)
            self.assertEqual(item.status_item, "Atendido")

        movs = self.service.listar_movimentacoes(empcod="1.01", tipo_filtro="SAIDA")
        self.assertEqual(len(movs), 2)

    def test_listar_requisicoes_filtro_pendentes(self):
        reqs = self.service.listar_requisicoes(empcod="1.01", status_filtro="PENDENTES")
        self.assertEqual(len(reqs), 1)
        self.assertEqual(reqs[0].req_num, "REQ-1001")

        # Cancelando a requisição não deve mais aparecer em PENDENTES
        self.service.cancelar_requisicao("REQ-1001", "1.01", "TESTE FILTRO")
        reqs_apos = self.service.listar_requisicoes(empcod="1.01", status_filtro="PENDENTES")
        self.assertEqual(len(reqs_apos), 0)

    def test_filtro_movimentacoes_e_kardex_com_datas_br(self):
        self.service.registrar_entrada_compras("1.01", "101", 50.0, 10.0, "NF-DATA-BR")
        hoje_br = datetime.now().strftime("%d/%m/%Y")

        # Filtrando com formato DD/MM/AAAA
        movs = self.service.listar_movimentacoes(empcod="1.01", data_ini=hoje_br, data_fim=hoje_br)
        self.assertEqual(len(movs), 1)

        # Filtrando Kardex com formato DD/MM/AAAA
        kardex = self.service.consultar_ficha_estoque("101", "1.01", data_ini=hoje_br, data_fim=hoje_br)
        self.assertEqual(len(kardex), 1)

        # Filtrando com data futura não deve trazer nada
        futura_br = "31/12/2099"
        movs_vazio = self.service.listar_movimentacoes(empcod="1.01", data_ini=futura_br, data_fim=futura_br)
        self.assertEqual(len(movs_vazio), 0)

    def test_cancelar_item_requisicao_baixa_requisicao(self):
        """Garante que cancelar item pendente zera saldo, marca como Cancelado e baixa a requisição se não houver pendências."""
        # 1. Atende item 1
        res_atend = self.service.atender_item_requisicao("REQ-1001", 1, 100.0, empcod="1.01")
        self.assertTrue(res_atend.sucesso)

        req_meio = self.service.obter_requisicao("REQ-1001", empcod="1.01")
        self.assertEqual(req_meio.status, "Atendida Parcial")
        self.assertEqual(req_meio.total_pendente, 10.0)

        # 2. Cancela item 2 (ex: lote vencido)
        res_canc = self.service.cancelar_item_requisicao("REQ-1001", 2, "LOTE VENCIDO: 998877", empcod="1.01")
        self.assertTrue(res_canc.sucesso)
        self.assertIn("baixada", res_canc.mensagem.lower())

        # 3. Verifica que item 2 está cancelado e sem saldo pendente
        itens = self.service.obter_itens_requisicao("REQ-1001", empcod="1.01")
        it2 = next(it for it in itens if it.item_seq == 2)
        self.assertEqual(it2.saldo_pendente, 0.0)
        self.assertEqual(it2.status_item, "Cancelado")
        self.assertIn("LOTE VENCIDO", it2.observacao)

        # 4. Verifica que cabeçalho foi baixado para 'Atendida Total' (zero pendências)
        req_fim = self.service.obter_requisicao("REQ-1001", empcod="1.01")
        self.assertEqual(req_fim.status, "Atendida Total")
        self.assertEqual(req_fim.total_pendente, 0.0)

        # 5. Verifica que não aparece mais no filtro de PENDENTES (foi baixada)
        pendentes = self.service.listar_requisicoes(empcod="1.01", status_filtro="PENDENTES")
        self.assertNotIn("REQ-1001", [r.req_num for r in pendentes])

    def test_cancelar_todos_itens_marca_requisicao_cancelada(self):
        """Cancela todos os itens de uma requisição sem atendimentos e valida que status fica 'Cancelada'."""
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO USER_geoapolo_requisicoes (codigo_empresa, numero_requisicao, data_requisicao, solicitante, centro_custo, status, observacao, tipo_requisicao)
            VALUES ('1', 'REQ-9999', '2026-10-04 10:00:00', 'TESTE', '01.01', 'Aberta', '', 'Produto')
        """)
        cur.execute("""
            INSERT INTO USER_geoapolo_requisicao_itens (codigo_empresa, numero_requisicao, item_seq, prodcod, unidade, quantidade_solicitada, quantidade_atendida, saldo_pendente, status_item, observacao)
            VALUES ('1', 'REQ-9999', 1, 101, 'UN', 5.0, 0.0, 5.0, 'Pendente', '')
        """)
        self.conn.commit()

        # Cancela único item
        res = self.service.cancelar_item_requisicao("REQ-9999", 1, "MATERIAL INDISPONÍVEL", empcod="1")
        self.assertTrue(res.sucesso)

        req = self.service.obter_requisicao("REQ-9999", empcod="1")
        self.assertEqual(req.status, "Cancelada")
        self.assertEqual(req.total_pendente, 0.0)

    def test_listar_movimentacoes_compatibilidade_empresa(self):
        """Garante que movimentações gravadas com empresa '1' sejam listadas ao filtrar com '1.01', '1' ou 'TODOS'."""
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO USER_geoapolo_movimentacoes_estoque (
                codigo_movimento, codigo_empresa, data_movimento, tipo_movimento,
                origem_movimento, prodcod, unidade, quantidade, valor_unitario, valor_total,
                documento_origem, numero_requisicao, item_requisicao_seq, observacao
            ) VALUES (888, '1', '2026-10-04 15:00:00', 'S', 'REQUISICAO', 101, 'UN', 7.0, 0.0, 0.0, 'REQ-TEST', 'REQ-TEST', 1, 'SAIDA REQ')
        """)
        self.conn.commit()

        # Filtro com 1.01 (deve localizar pois base é 1)
        m_filial = self.service.listar_movimentacoes(empcod="1.01")
        chvs_filial = [m.mov_chv for m in m_filial]
        self.assertIn(888, chvs_filial)

        # Filtro com 1 (empresa exata)
        m_base = self.service.listar_movimentacoes(empcod="1")
        chvs_base = [m.mov_chv for m in m_base]
        self.assertIn(888, chvs_base)

        # Filtro com TODOS
        m_todos = self.service.listar_movimentacoes(empcod="TODOS")
        chvs_todos = [m.mov_chv for m in m_todos]
        self.assertIn(888, chvs_todos)


class TestEstoqueViewsHeadless(unittest.TestCase):
    """Teste de renderização headless das telas gráficas de Estoque."""

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
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
        self.conn = criar_banco_teste()
        self.repo = EstoqueRepository(self.conn)
        self.service = EstoqueService(self.repo)

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
        try:
            self.root.destroy()
        except Exception:
            pass

    def test_requisicoes_view_headless(self):
        view = RequisicoesView(self.root, service=self.service)
        self.assertEqual(len(view.tree_req.get_children()), 1)
        view.tree_req.selection_set("REQ-1001")
        view._ao_selecionar_requisicao()
        self.assertEqual(len(view.tree_itens.get_children()), 2)

    def test_nova_requisicao_view_headless(self):
        view = NovaRequisicaoView(self.root, service=self.service)
        self.assertTrue(view.var_req_num.get())
        self.assertTrue(view.var_empcod.get())

        # Adicionar item
        view.var_prod_cod.set("101")
        view.var_prod_nome.set("CABO FIBRA")
        view.var_prod_unid.set("MT")
        view.var_qtd_solic.set("15.5")
        view.var_item_obs.set("PONTO A")
        view._adicionar_item_grade()

        self.assertEqual(len(view._itens_requisicao), 1)
        self.assertEqual(view.lbl_tot_itens.cget("text"), "1 item(ns)")
        self.assertEqual(view.lbl_tot_qtd.cget("text"), "15.50")

    def test_movimentacao_view_headless(self):
        self.service.registrar_entrada_compras("1.01", "101", 50.0, 10.0, "NF-999")
        view = MovimentacaoView(self.root, service=self.service)
        self.assertEqual(len(view.tree.get_children()), 1)

    def test_consultas_estoque_view_headless(self):
        self.service.registrar_entrada_compras("1.01", "101", 80.0, 10.0, "NF-888")
        view = ConsultasEstoqueView(self.root, service=self.service, aba_inicial=0, prodcod_inicial="101")
        self.assertEqual(len(view.tree_kardex.get_children()), 1)
        self.assertEqual(view.lbl_card_saldo.cget("text"), "80.00")

    def test_listar_fornecedores(self):
        # 1. Lista todos
        todos = self.service.listar_fornecedores()
        self.assertGreater(len(todos), 0)

        # 2. Busca por termo existente
        res = self.service.listar_fornecedores("FIBRA")
        self.assertGreater(len(res), 0)
        self.assertTrue(any("FIBRA" in f[1].upper() for f in res))

        # 3. Busca por termo inexistente
        res_vazio = self.service.listar_fornecedores("XYZ999_NAO_EXISTE")
        self.assertEqual(len(res_vazio), 0)

    def test_entrada_compras_com_centro_custo_e_fornecedor(self):
        res = self.service.registrar_entrada_compras(
            empcod="1.01",
            prodcod_estr="101",
            quantidade=25.0,
            valor_unitario=12.50,
            num_doc="NF-777",
            fornecedor_obs="ENTREGA URGENTE",
            centro_custo="01.01.001",
            fornecedor_cod="FORN002",
            fornecedor_nome="FIBRA BRASIL TELECOMUNICACOES E CABOS",
        )
        self.assertTrue(res.sucesso)
        movs = self.service.listar_movimentacoes("1.01", termo_prod="101")
        self.assertEqual(len(movs), 1)
        m = movs[0]
        self.assertEqual(m.centro_custo, "01.01.001")
        self.assertIn("FORNECEDOR: FORN002 - FIBRA BRASIL", m.observacao)
        self.assertIn("CENTRO DE CUSTO: 01.01.001", m.observacao)
        self.assertEqual(m.quantidade, 25.0)

    def test_saida_direta_com_centro_custo(self):
        # Primeiro dá entrada
        self.service.registrar_entrada_compras("1.01", "102", 50.0, 5.0, "NF-100")
        # Registra saída direta com centro de custo
        res = self.service.registrar_saida_direta(
            empcod="1.01",
            prodcod_estr="102",
            quantidade=10.0,
            destino_obs="MANUTENCAO DE ROTEADOR",
            centro_custo="01.01.002",
        )
        self.assertTrue(res.sucesso)
        movs = self.service.listar_movimentacoes("1.01", tipo_filtro="SAIDA", termo_prod="102")
        self.assertEqual(len(movs), 1)
        m = movs[0]
        self.assertEqual(m.centro_custo, "01.01.002")
        self.assertIn("CENTRO DE CUSTO: 01.01.002", m.observacao)
        self.assertEqual(m.quantidade, 10.0)

    def test_movimentacao_view_com_centro_custo_na_grade(self):
        self.service.registrar_entrada_compras(
            empcod="1.01",
            prodcod_estr="101",
            quantidade=40.0,
            valor_unitario=15.0,
            num_doc="NF-555",
            centro_custo="01.01.001",
        )
        view = MovimentacaoView(self.root, service=self.service)
        # Verifica se coluna ccusto existe na treeview
        cols = view.tree.cget("columns")
        self.assertIn("ccusto", cols)
        items = view.tree.get_children()
        self.assertEqual(len(items), 1)
        vals = view.tree.item(items[0], "values")
        # vals[7] é lote, vals[12] é ccusto
        self.assertEqual(vals[12], "01.01.001")

    def test_unidade_medida_e_lote_em_movimentacoes(self):
        item = ItemRequisicaoDTO(prodcod_estr="101", unidade="CX")
        self.assertEqual(item.unidade, "CX")
        self.assertEqual(item.unidade_medida, "CX")
        self.assertEqual(item.unidademedida, "CX")
        self.assertEqual(item.tamanho, "CX")

        mov = MovimentoEstoqueDTO(mov_chv=1, unidade="KG", numero_lote="LT-01")
        self.assertEqual(mov.unidade_medida, "KG")
        self.assertEqual(mov.tamanho, "KG")
        self.assertEqual(mov.numero_lote, "LT-01")

        saldo = SaldoProdutoDTO(prodcod_estr="101", unidade="M")
        self.assertEqual(saldo.unidade_medida, "M")
        self.assertEqual(saldo.tamanho, "M")

        res_e = self.service.registrar_entrada_compras(
            empcod="1.01",
            prodcod_estr="101",
            quantidade=50.0,
            valor_unitario=12.0,
            num_doc="NF-LOTE-1",
            numero_lote="LT-ABC-1",
        )
        self.assertTrue(res_e.sucesso)

        movs = self.service.listar_movimentacoes(empcod="1.01", tipo_filtro="ENTRADA")
        self.assertEqual(movs[0].numero_lote, "LT-ABC-1")

        res_s = self.service.registrar_saida_direta(
            empcod="1.01",
            prodcod_estr="101",
            quantidade=10.0,
            numero_lote="LT-ABC-1",
        )
        self.assertTrue(res_s.sucesso)
        movs_s = self.service.listar_movimentacoes(empcod="1.01", tipo_filtro="SAIDA")
        self.assertEqual(movs_s[0].numero_lote, "LT-ABC-1")

    def test_estoque_repository_sem_coluna_tamanho(self):
        conn_sem_tam = sqlite3.connect(":memory:")
        cur = conn_sem_tam.cursor()
        cur.executescript("""
            CREATE TABLE USER_geoapolo_produtos (
                prodcod INTEGER PRIMARY KEY,
                prodnome TEXT,
                unidade_medida TEXT
            );
            INSERT INTO USER_geoapolo_produtos (prodcod, prodnome, unidade_medida)
            VALUES (500, 'PARAFUSO SEXTAVADO', 'PC');
        """)
        conn_sem_tam.commit()
        repo = EstoqueRepository(conn_sem_tam)
        unid = repo.obter_unidade_produto(500)
        self.assertEqual(unid, "PC")

        saldos = repo.consultar_saldos_produtos(empcod="1.01")
        self.assertEqual(len(saldos), 1)
        self.assertEqual(saldos[0].prodnome, "PARAFUSO SEXTAVADO")
        self.assertEqual(saldos[0].unidade, "PC")
        conn_sem_tam.close()


    def test_ui_ux_movimentacao_formatacao_e_saldo_periodo(self):
        from estoque.movimentacao_view import formatar_moeda_br, formatar_numero_br
        self.assertEqual(formatar_moeda_br(1250.5), "R$ 1.250,50")
        self.assertEqual(formatar_numero_br(1500.0), "1.500,00")

        self.service.registrar_entrada_compras("1.01", "101", 30.0, 10.0, "NF-10")
        self.service.registrar_saida_direta("1.01", "101", 10.0, "Uso interno", "01.01.001")
        view = MovimentacaoView(self.root, service=self.service)
        self.assertTrue(hasattr(view, "card_tot_saldo"))
        self.assertIn("Saldo Período", view.card_tot_saldo.cget("text"))
        self.assertTrue(hasattr(view, "_abrir_busca_filtro_produto"))

    def test_ui_ux_consultas_kardex_busca_f4(self):
        view = ConsultasEstoqueView(self.root, service=self.service, aba_inicial=0, prodcod_inicial="101")
        self.assertTrue(hasattr(view, "_abrir_modal_busca_kardex"))
        self.assertTrue(hasattr(view, "_ao_pressionar_f4"))

    def test_combobox_centro_custo_filtro_e_resolucao_movimentacao(self):
        view = MovimentacaoView(self.root, service=self.service)
        # Testa a resolução direta através de habilitar_filtro_dinamico_combobox
        from core import habilitar_filtro_dinamico_combobox
        cbo = ttk.Combobox(self.root)
        centros = [
            "01.01 - ADMINISTRATIVO / GERAL",
            "01.02 - OPERACIONAL / LOGÍSTICA",
            "01.04 - TECNOLOGIA DA INFORMAÇÃO",
        ]
        habilitar_filtro_dinamico_combobox(cbo, centros)

        # 1. Digita código "01.01" e resolve
        cbo.set("01.01")
        cbo.resolver_selecao_atual()
        self.assertEqual(cbo.get(), "01.01 - ADMINISTRATIVO / GERAL")

        # 2. Digita código "01.04"
        cbo.set("01.04")
        cbo.resolver_selecao_atual()
        self.assertEqual(cbo.get(), "01.04 - TECNOLOGIA DA INFORMAÇÃO")

        # 3. Digita nome "LOGÍSTICA" ou "LOGISTICA"
        cbo.set("LOGISTICA")
        cbo.resolver_selecao_atual()
        self.assertEqual(cbo.get(), "01.02 - OPERACIONAL / LOGÍSTICA")

        cbo.destroy()
        view.destroy()

    def test_combobox_centro_custo_nova_requisicao(self):
        view = NovaRequisicaoView(self.root, service=self.service)
        self.assertTrue(hasattr(view, "cb_cctrl"))
        self.assertTrue(hasattr(view, "_lista_centros_custo"))
        self.assertGreater(len(view.cb_cctrl["values"]), 0)

        # Testa simulação de digitação na combo de centro de custo da requisição
        view.cb_cctrl.set("01.01")
        if hasattr(view.cb_cctrl, "resolver_selecao_atual"):
            view.cb_cctrl.resolver_selecao_atual()
        self.assertIn("01.01", view.cb_cctrl.get())

        view.destroy()

    def test_modal_entrada_salvar_via_botao_e_f10(self):
        from unittest.mock import patch
        view = MovimentacaoView(self.root, service=self.service)

        # 1. Teste de confirmação via botão de salvar
        with patch("tkinter.messagebox.showinfo") as mock_info, patch("tkinter.messagebox.showerror") as mock_err:
            view._abrir_modal_entrada()
            modal = [w for w in view.winfo_children() if isinstance(w, tk.Toplevel)][-1]

            def find_widgets(w):
                res = [w]
                for c in w.winfo_children():
                    res.extend(find_widgets(c))
                return res

            all_w = find_widgets(modal)
            entries = [w for w in all_w if isinstance(w, tk.ttk.Entry)]
            buttons = [w for w in all_w if isinstance(w, (tk.Button, tk.ttk.Button))]
            btn_conf = [b for b in buttons if "Confirmar Entrada" in getattr(b, "cget", lambda x: "")("text")][0]

            entries[2].insert(0, "101")  # prod
            entries[3].set("01.01 - ADMINISTRATIVO / GERAL")  # centro custo
            entries[4].insert(0, "1")  # forn
            entries[5].insert(0, "LOTE-001")  # lote
            entries[6].insert(0, "10")  # qtd
            entries[7].delete(0, tk.END)
            entries[7].insert(0, "25,00")  # val_unit
            entries[8].insert(0, "NF-BOTAO")  # doc
            entries[10].insert(0, "COMPRA VIA BOTAO")  # obs

            btn_conf.invoke()
            self.assertTrue(mock_info.called)
            self.assertFalse(mock_err.called)

        movs = self.service.listar_movimentacoes("1.01", tipo_filtro="ENTRADA")
        self.assertEqual(len(movs), 1)
        self.assertEqual(movs[0].quantidade, 10.0)
        self.assertEqual(movs[0].numero_lote, "LOTE-001")

        # 2. Teste de confirmação via atalho F10
        with patch("tkinter.messagebox.showinfo") as mock_info, patch("tkinter.messagebox.showerror") as mock_err:
            view._abrir_modal_entrada()
            modal = [w for w in view.winfo_children() if isinstance(w, tk.Toplevel)][-1]
            all_w = find_widgets(modal)
            entries = [w for w in all_w if isinstance(w, tk.ttk.Entry)]

            entries[2].insert(0, "101")  # prod
            entries[3].set("01.01 - ADMINISTRATIVO / GERAL")  # centro custo
            entries[5].insert(0, "LOTE-002")  # lote
            entries[6].insert(0, "5")  # qtd
            entries[7].delete(0, tk.END)
            entries[7].insert(0, "15,00")  # val_unit
            entries[8].insert(0, "NF-F10")  # doc

            self.root.deiconify()
            modal.deiconify()
            modal.focus_force()
            modal.update()
            modal.event_generate("<Key-F10>")
            modal.update()
            self.root.withdraw()
            self.assertTrue(mock_info.called)
            self.assertFalse(mock_err.called)

        movs = self.service.listar_movimentacoes("1.01", tipo_filtro="ENTRADA")
        self.assertEqual(len(movs), 2)
        view.destroy()

    def test_modal_entrada_validacao_data_invalida(self):
        from unittest.mock import patch
        view = MovimentacaoView(self.root, service=self.service)

        with patch("tkinter.messagebox.showinfo") as mock_info, patch("tkinter.messagebox.showerror") as mock_err:
            view._abrir_modal_entrada()
            modal = [w for w in view.winfo_children() if isinstance(w, tk.Toplevel)][-1]

            def find_widgets(w):
                res = [w]
                for c in w.winfo_children():
                    res.extend(find_widgets(c))
                return res

            all_w = find_widgets(modal)
            entries = [w for w in all_w if isinstance(w, tk.ttk.Entry)]
            buttons = [w for w in all_w if isinstance(w, (tk.Button, tk.ttk.Button))]
            btn_conf = [b for b in buttons if "Confirmar Entrada" in getattr(b, "cget", lambda x: "")("text")][0]

            entries[2].insert(0, "101")  # prod
            entries[3].set("01.01 - ADMINISTRATIVO / GERAL")
            entries[6].insert(0, "2")
            entries[9].delete(0, tk.END)
            entries[9].insert(0, "99/99/9999")  # Data inválida

            btn_conf.invoke()
            self.assertTrue(mock_err.called)
            self.assertFalse(mock_info.called)
            modal.destroy()

        movs = self.service.listar_movimentacoes("1.01", tipo_filtro="ENTRADA")
        self.assertEqual(len(movs), 0)
        view.destroy()

    def test_ui_devolucao_e_cancelamento_item_f8(self):
        """Testa o acionamento de F8 em item pendente, abrindo modal de cancelamento/baixa."""
        view = RequisicoesView(self.root, service=self.service)
        view.tree_req.selection_set("REQ-1001")
        view._ao_selecionar_requisicao()

        # Seleciona o item 2 (pendente)
        view.tree_itens.selection_set("REQ-1001_2")
        item = view._obter_item_selecionado()
        self.assertIsNotNone(item)
        self.assertEqual(item.item_seq, 2)
        self.assertEqual(item.saldo_pendente, 10.0)
        self.assertEqual(item.qtd_atendida, 0.0)

        # Dispara F8 (deve abrir o modal de cancelamento/baixa)
        view._abrir_devolucao_selecionada()
        top_modals = [w for w in view.winfo_children() if isinstance(w, tk.Toplevel)]
        self.assertTrue(len(top_modals) > 0)
        modal = top_modals[-1]
        self.assertIn("Cancelar", modal.title())
        modal.destroy()
        view.destroy()


if __name__ == "__main__":
    unittest.main()
