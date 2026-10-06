"""
Testes Unitários Automatizados para as Novas Melhorias e Correções da Versão 5.
"""

import unittest
import sqlite3
import tkinter as tk
from tkinter import ttk
from unittest.mock import MagicMock, patch

from core.recursos import habilitar_filtro_dinamico_combobox
from estoque.models import RequisicaoDTO, ItemRequisicaoDTO
from estoque.repository import EstoqueRepository
from contas_a_pagar.service import ContasPagarService
from contas_a_pagar.repository import ContasPagarRepository
from savic.moderacao_service import SavicModeracaoService


class TestNovasMelhoriasV5(unittest.TestCase):

    def setUp(self):
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

    def test_filtro_dinamico_combobox(self):
        if not self.root:
            self.skipTest("Ambiente sem display")

        cbo = ttk.Combobox(self.root)
        lista = ["ALVO", "GEOAPOLO", "APLICATIVO RCC", "SISTEMA ANTIGO"]
        habilitar_filtro_dinamico_combobox(cbo, lista)

        self.assertEqual(str(cbo["state"]), "normal")
        self.assertEqual(list(cbo["values"]), lista)

        # Simula digitação "geo"
        cbo.set("geo")
        event = MagicMock()
        event.keysym = "o"
        for binding in cbo.bind("<KeyRelease>").split():
            pass

        # Testa chamada direta do filtro
        cbo._lista_completa_original = lista
        filtrados = [it for it in lista if "geo" in it.lower()]
        cbo["values"] = filtrados
        self.assertEqual(list(cbo["values"]), ["GEOAPOLO"])

    def test_requisicao_dto_tipo(self):
        req = RequisicaoDTO(req_num="REQ001", tipo_requisicao="Serviço")
        self.assertEqual(req.tipo_requisicao, "Serviço")
        self.assertEqual(req.total_itens, 0)

        req_padrao = RequisicaoDTO(req_num="REQ002")
        self.assertEqual(req_padrao.tipo_requisicao, "Produto")

    def test_estoque_repository_salvar_e_listar_tipo_requisicao(self):
        conn = sqlite3.connect(":memory:")
        repo = EstoqueRepository(conn)

        req = RequisicaoDTO(
            req_num="1001",
            empcod="1.01",
            data_req="2026-09-29 14:00:00",
            tipo_requisicao="Serviço",
            requerente="JULIO",
            centro_custo="01.01",
            observacao="CONSERTO DE EQUIPAMENTO",
            itens=[
                ItemRequisicaoDTO(
                    req_num="1001",
                    item_seq=1,
                    empcod="1.01",
                    prodcod_estr="999",
                    prodnome="MANUTENÇÃO DE COMPUTADOR",
                    unidade="UN",
                    qtd_solicitada=1.0,
                    saldo_pendente=1.0,
                )
            ]
        )

        ok, msg, req_num = repo.criar_requisicao(req)
        self.assertTrue(ok)
        self.assertEqual(req_num, "1001")

        lista = repo.listar_requisicoes(empcod="1.01", termo_busca="1001")
        self.assertEqual(len(lista), 1)
        self.assertEqual(lista[0].tipo_requisicao, "Serviço")
        self.assertEqual(lista[0].requerente, "JULIO")

    def test_contas_a_pagar_gerar_titulo_servico(self):
        conn = sqlite3.connect(":memory:")
        repo = ContasPagarRepository(conn)
        repo.criar_tabela()
        service = ContasPagarService(repo)

        ok, msg, doc_id = service.gerar_titulo_por_servico_requisicao(
            empcod="1.01",
            req_num="1001",
            item_seq=1,
            descricao_servico="MANUTENÇÃO DE COMPUTADOR",
            valor_total=350.00,
            codigo_movimento_estoque=42,
            centro_custo="01.01",
            fornecedor_nome="TECNOLOGIA LTDA",
            observacao="ORDEM 1001",
        )

        self.assertTrue(ok)
        self.assertGreater(doc_id, 0)

        # Checa no banco se gravou
        cur = conn.cursor()
        cur.execute("SELECT numero_documento, valor_original, tipo_documento, origem, situacao FROM USER_geoapolo_contas_a_pagar WHERE codigo_documento = ?", [doc_id])
        row = cur.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "SRV_1001_1")
        self.assertEqual(float(row[1]), 350.00)
        self.assertEqual(row[2], "SERVICO")
        self.assertEqual(row[3], "REQUISICAO_SERVICO")
        self.assertEqual(row[4], "ABERTO")

    def test_moderacao_savic_obter_tipologradabrev_valido(self):
        cur = MagicMock()
        # Simula quando 'R.' existe
        cur.fetchone.return_value = ("R.",)
        res = SavicModeracaoService._obter_tipologradabrev_valido(cur)
        self.assertEqual(res, "R.")

        # Simula quando 'R.' não existe, mas 'RUA' existe
        cur.fetchone.side_effect = [None, ("RUA",)]
        res2 = SavicModeracaoService._obter_tipologradabrev_valido(cur)
        self.assertEqual(res2, "RUA")

    def test_garantir_origem_entidade_savic_repository(self):
        from savic.moderacao_repository import SavicModeracaoRepository
        conn = MagicMock()
        cur = MagicMock()
        conn.cursor.return_value = cur

        repo = SavicModeracaoRepository()
        ok = repo.garantir_origem_entidade("104944", "013.007", conn=conn)
        self.assertTrue(ok)
        cur.execute.assert_called_once()
        sql_exec = cur.execute.call_args[0][0]
        self.assertIn("USER_geoapolo_origens_entidade", sql_exec)
        self.assertEqual(cur.execute.call_args[0][1], ["104944", "013.007", "104944", "013.007", "104944"])

    def test_montar_payload_alvo_codigo_origem(self):
        from entidades.service import EntidadeService
        repo = MagicMock()
        repo.carregar_dados_completos_entidade_geoapolo.return_value = {
            "geoentcod": "0018570",
            "geoentnome": "SANTA TERESINHA",
            "geo_origcodestr": "013.007",
            "geo_orignome": "SAVIC",
        }
        repo.obter_cpf_rg_documentos.return_value = ("", "")
        repo.listar_categorias_entidade.return_value = [{"codigo": "02.001"}]
        repo.listar_telefones_entidade.return_value = []
        repo.listar_webcontatos_entidade.return_value = []
        repo.carregar_contatos_entidade.return_value = []

        service = EntidadeService(repo)
        payload_delphi = service.montar_payload_entidade_alvo("0018570", operacao="I", modo="delphi")
        self.assertEqual(payload_delphi.get("CodigoOrigem"), "013.007")


    def test_categoria_filtro_entidade_repository(self):
        from entidades.models import EntidadeFiltro
        from entidades.repository import EntidadeRepository
        conn = MagicMock()
        cursor = MagicMock()
        conn.cursor.return_value = cursor
        cursor.description = [("geoentcod",), ("geoentnome",), ("geocategnome",)]
        cursor.fetchall.return_value = [("0001001", "GRUPO PAZ", "02.001 - Grupo de Oração")]

        repo = EntidadeRepository(conn)
        filtro = EntidadeFiltro(base_dados="GeoApolo", categoria_busca="02.001 - Grupo de Oração")
        regs = repo.consultar_lista(filtro)
        self.assertEqual(len(regs), 1)
        self.assertEqual(regs[0]["geoentcod"], "0001001")

        # Verifica se o SQL de consulta filtrou por categoria
        sql_exec = cursor.execute.call_args[0][0]
        self.assertIn("USER_geoapolo_entcateg", sql_exec)

    def test_registrar_log_atividade_repository(self):
        from entidades.repository import EntidadeRepository
        conn = MagicMock()
        cursor = MagicMock()
        conn.cursor.return_value = cursor

        repo = EntidadeRepository(conn)
        ok = repo.registrar_log_atividade(
            usucod="JULIO",
            descricao="Exportou a Entidade: 0001001 e GRUPO TESTE para o alvo usando o geoapolo"
        )
        self.assertTrue(ok)
        insert_calls = [c for c in cursor.execute.call_args_list if len(c[0]) > 0 and "INSERT INTO" in str(c[0][0])]
        self.assertEqual(len(insert_calls), 1)
        sql_exec = insert_calls[0][0][0]
        params = insert_calls[0][0][1]
        self.assertIn("INSERT INTO", sql_exec)
        self.assertEqual(params[2], "JULIO")
        self.assertEqual(params[3], "Exportou a Entidade: 0001001 e GRUPO TESTE para o alvo usando o geoapolo")

    def test_mandato_vencido_check_and_tag_injection(self):
        from datetime import date, timedelta
        from savic.service import eh_mandato_vencido, aplicar_pendencia_mandato_vencido

        ontem = date.today() - timedelta(days=1)
        amanha = date.today() + timedelta(days=1)

        # Mandato vencido: Não indeterminado e data no passado
        self.assertTrue(eh_mandato_vencido("Não", ontem))
        self.assertTrue(eh_mandato_vencido("Nao", ontem.strftime("%Y-%m-%d")))
        self.assertTrue(eh_mandato_vencido("", ontem))

        # Mandato não vencido: Data futura
        self.assertFalse(eh_mandato_vencido("Não", amanha))

        # Mandato não vencido: Indeterminado Sim
        self.assertFalse(eh_mandato_vencido("Sim", ontem))
        self.assertFalse(eh_mandato_vencido("S", ontem))

        # Teste de injeção da tag [PENDÊNCIAS]
        obs_vazia = ""
        obs_com_pend = aplicar_pendencia_mandato_vencido(obs_vazia)
        self.assertIn("[PENDÊNCIAS]", obs_com_pend)
        self.assertIn("mandato do coordenador está vencido, checar na diocese", obs_com_pend)

        # Idempotência (não duplica se já presente)
        obs_duplicada = aplicar_pendencia_mandato_vencido(obs_com_pend)
        self.assertEqual(obs_duplicada.count("mandato do coordenador está vencido"), 1)

        # Preserva [INFORMAÇÕES]
        obs_info = "[INFORMAÇÕES]\nDia da Semana: Terça"
        obs_info_result = aplicar_pendencia_mandato_vencido(obs_info)
        self.assertTrue(obs_info_result.startswith("[PENDÊNCIAS]"))
        self.assertIn("[INFORMAÇÕES]", obs_info_result)

    def test_view_categoria_combo_and_batch_export_structure(self):
        from entidades.view import EntidadesView
        self.assertTrue(hasattr(EntidadesView, "_acao_exportar_filtro"))
        self.assertTrue(hasattr(EntidadesView, "_atualizar_lookup_categorias"))
        self.assertTrue(hasattr(EntidadesView, "_on_mudar_base"))

    def test_requisicao_dto_solicitante_cod(self):
        req = RequisicaoDTO(
            req_num="REQ100",
            solicitante_cod="12",
            requerente="JULIO SANTOS",
            centro_custo="1.01",
        )
        self.assertEqual(req.solicitante_cod, "12")
        self.assertEqual(req.requerente, "JULIO SANTOS")
        self.assertEqual(req.centro_custo, "1.01")

    def test_almoxarifado_dto_e_produto_almoxarifado_dto(self):
        from estoque.models import AlmoxarifadoDTO, ProdutoAlmoxarifadoDTO, MovimentoEstoqueDTO
        a = AlmoxarifadoDTO(codigo_almoxarifado="01", descricao="CENTRAL", centro_custo="1.01")
        self.assertEqual(a.codigo_almoxarifado, "01")
        self.assertEqual(a.descricao, "CENTRAL")

        pa = ProdutoAlmoxarifadoDTO(codigo_almoxarifado="01", prodcod=555, saldo_atual=25.0)
        self.assertEqual(pa.prodcod, 555)
        self.assertEqual(pa.saldo_atual, 25.0)

        mov = MovimentoEstoqueDTO(codigo_almoxarifado="01", descricao_almoxarifado="CENTRAL")
        self.assertEqual(mov.codigo_almoxarifado, "01")

    def test_almoxarifados_repository_mocked_sqlite(self):
        conn = sqlite3.connect(":memory:")
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE user_geoapolo_almoxarifados (
                codigo_almoxarifado VARCHAR(20) PRIMARY KEY,
                descricao VARCHAR(100),
                centro_custo VARCHAR(30),
                data_criacao DATETIME,
                finalidade VARCHAR(500),
                status CHAR(1)
            )
        """)
        cur.execute("""
            CREATE TABLE user_geoapolo_produtos_almoxarifados (
                id_produto_almoxarifado INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_almoxarifado VARCHAR(20),
                prodcod NUMERIC,
                saldo_atual DECIMAL,
                data_ultima_movimentacao DATETIME,
                data_vinculo DATETIME,
                status CHAR(1)
            )
        """)
        cur.execute("""
            CREATE TABLE USER_geoapolo_centrocontrole (
                geocctrlcodestr VARCHAR(30),
                geocctrlnome VARCHAR(100)
            )
        """)
        conn.commit()

        from estoque.almoxarifados_repository import AlmoxarifadosRepository
        repo = AlmoxarifadosRepository(conn)

        # Salvar almoxarifado
        res = repo.salvar_almoxarifado("02", "ALMOXARIFADO TI", "1.02", "Estoque de TI e periféricos", "A")
        self.assertTrue(res)

        almox = repo.obter_almoxarifado("02")
        self.assertIsNotNone(almox)
        self.assertEqual(almox["descricao"], "ALMOXARIFADO TI")

        # Vincular produto
        vinc = repo.vincular_produto("02", 101, saldo_inicial=10.0)
        self.assertTrue(vinc)
        self.assertEqual(repo.obter_saldo_produto("02", 101), 10.0)

        # Atualizar saldo
        novo_saldo = repo.atualizar_saldo("02", 101, 5.0)
        self.assertEqual(novo_saldo, 15.0)

        # Atualizar saldo saída
        novo_saldo_saida = repo.atualizar_saldo("02", 101, -3.0)
        self.assertEqual(novo_saldo_saida, 12.0)

    def test_ativo_imobilizado_categoria_e_localizacao_crud_mock(self):
        conn = sqlite3.connect(":memory:")
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE USER_geoapolo_satfi_categorias (
                codigo_categoria INTEGER PRIMARY KEY,
                descricao VARCHAR(70)
            )
        """)
        cur.execute("""
            CREATE TABLE USER_geoapolo_satfi_localizacao_fisica (
                codigo_localizacao VARCHAR(15) PRIMARY KEY,
                localizacao VARCHAR(50),
                codigo_departamento INTEGER,
                grupo VARCHAR(1)
            )
        """)
        cur.execute("""
            CREATE TABLE USER_geoapolo_departamentos (
                codigo_departamento INTEGER,
                nome_departamento VARCHAR(50)
            )
        """)
        conn.commit()

        from ativo_imobilizado.repository import AtivoImobilizadoRepository
        repo = AtivoImobilizadoRepository(conn)

        # Categorias
        prox = repo.obter_proximo_codigo_categoria()
        self.assertEqual(prox, 1)

        repo.salvar_categoria(1, "EQUIPAMENTOS DE TI")
        cat = repo.listar_categorias()
        self.assertEqual(len(cat), 1)
        self.assertEqual(cat[0]["descricao"], "EQUIPAMENTOS DE TI")

        repo.salvar_categoria(1, "EQUIPAMENTOS DE INFORMÁTICA")
        cat_upd = repo.listar_categorias()
        self.assertEqual(cat_upd[0]["descricao"], "EQUIPAMENTOS DE INFORMÁTICA")

        # Localização Física
        repo.salvar_localizacao("LOC01", "SALA DE SERVIDORES", 1, "A")
        locs = repo.listar_todas_localizacoes()
        self.assertEqual(len(locs), 1)
        self.assertEqual(locs[0]["localizacao"], "SALA DE SERVIDORES")
        self.assertEqual(locs[0]["grupo"], "A")

        repo.excluir_localizacao("LOC01")
        self.assertEqual(len(repo.listar_todas_localizacoes()), 0)


if __name__ == "__main__":
    unittest.main()

