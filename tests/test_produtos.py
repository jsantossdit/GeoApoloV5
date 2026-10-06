"""
Testes Unitários para o Módulo de Cadastro e Manutenção de Produtos.
GeoApolo V5
Equivalente a unt_cadprodutos do Delphi.
"""

import sqlite3
import unittest
import tkinter as tk
from unittest.mock import MagicMock, patch

from produtos.models import ProdutoDTO, GrupoProdutoDTO, ResultadoProdutoDTO
from produtos.repository import ProdutosRepository
from produtos.service import ProdutosService
from produtos.view import ProdutosView


class TestProdutosModels(unittest.TestCase):
    """Testes dos DTOs e modelos do módulo de produtos."""

    def test_grupo_produto_dto(self):
        g1 = GrupoProdutoDTO(grupocod=1, codigo_estruturado="01", nome_grupo="PRODUTOS")
        self.assertEqual(g1.display, "01 - PRODUTOS")

        g2 = GrupoProdutoDTO(grupocod=5, codigo_estruturado="", nome_grupo="ACESSÓRIOS")
        self.assertEqual(g2.display, "05 - ACESSÓRIOS")

    def test_produto_dto(self):
        p = ProdutoDTO(prodcod=10, prodnome="CABO DE ENERGIA", tamanho="M")
        self.assertEqual(p.display, "10 - CABO DE ENERGIA")
        self.assertEqual(p.tamanho, "M")
        self.assertEqual(p.unidade_medida, "M")

    def test_produto_dto_unidade_inmetro_lote(self):
        p = ProdutoDTO(
            prodcod=20,
            prodnome="RECIPIENTE TERMICO",
            unidade_medida="CX",
            codigo_inmetro="INMETRO-987",
            codigo_lote="LT-2026-001",
        )
        self.assertEqual(p.unidade_medida, "CX")
        self.assertEqual(p.tamanho, "CX")
        self.assertEqual(p.codigo_inmetro, "INMETRO-987")
        self.assertEqual(p.codigo_lote, "LT-2026-001")

    def test_resultado_produto_dto(self):
        res = ResultadoProdutoDTO(sucesso=True, mensagem="OK", codigo=1)
        self.assertTrue(res.sucesso)
        self.assertEqual(res.codigo, 1)


class TestProdutosRepositorySQLite(unittest.TestCase):
    """Testes de persistência do repositório de produtos em SQLite em memória."""

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self._criar_schema()
        self._popular_dados()
        self.repo = ProdutosRepository(self.conn)

    def tearDown(self):
        self.conn.close()

    def _criar_schema(self):
        cur = self.conn.cursor()
        cur.executescript("""
            CREATE TABLE USER_geoapolo_produto_grupo (
                grupocod INTEGER PRIMARY KEY,
                codigo_estruturado TEXT,
                nome_grupo TEXT
            );

            CREATE TABLE USER_geoapolo_produtos (
                prodcod INTEGER PRIMARY KEY,
                prodnome TEXT,
                descricao_alternativa TEXT,
                grupocod INTEGER,
                tamanho TEXT,
                observacoes TEXT
            );

            CREATE TABLE USER_geoapolo_produto_marcas (
                codigo_marca INTEGER PRIMARY KEY,
                descricao_marca TEXT
            );

            CREATE TABLE USER_geoapolo_marca_produtos (
                codigo_marca INTEGER,
                prodcod INTEGER
            );

            CREATE TABLE USER_geoapolo_produto_cores (
                codigo_cor INTEGER PRIMARY KEY,
                descricao_cor TEXT
            );

            CREATE TABLE USER_geoapolo_produto_cor (
                codigo_cor INTEGER,
                prodcod INTEGER
            );
        """)
        self.conn.commit()

    def _popular_dados(self):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO USER_geoapolo_produto_grupo VALUES (1, '01', 'PRODUTOS')")
        cur.execute("INSERT INTO USER_geoapolo_produto_grupo VALUES (4, '01.01', 'INFORMÁTICA')")
        cur.execute("INSERT INTO USER_geoapolo_produtos VALUES (1, 'TECLADO USB', 'TECLADO ABNT2', 4, '', 'Obs 1')")
        cur.execute("INSERT INTO USER_geoapolo_produtos VALUES (2, 'MOUSE OPTICO', '', 4, '', '')")
        self.conn.commit()

    def test_contar_produtos(self):
        self.assertEqual(self.repo.contar_produtos(), 2)

    def test_obter_proximo_codigo(self):
        self.assertEqual(self.repo.obter_proximo_codigo(), 3)

    def test_listar_grupos(self):
        grupos = self.repo.listar_grupos()
        self.assertEqual(len(grupos), 2)
        self.assertEqual(grupos[0].nome_grupo, "PRODUTOS")

    def test_listar_produtos_sem_filtro(self):
        prods = self.repo.listar_produtos()
        self.assertEqual(len(prods), 2)
        self.assertEqual(prods[0].prodnome, "TECLADO USB")
        self.assertEqual(prods[0].nome_grupo, "INFORMÁTICA")

    def test_listar_produtos_com_filtro_texto(self):
        prods = self.repo.listar_produtos(filtro="MOUSE")
        self.assertEqual(len(prods), 1)
        self.assertEqual(prods[0].prodcod, 2)

    def test_listar_produtos_com_filtro_grupo(self):
        prods = self.repo.listar_produtos(grupocod=4)
        self.assertEqual(len(prods), 2)

        prods_vazio = self.repo.listar_produtos(grupocod=99)
        self.assertEqual(len(prods_vazio), 0)

    def test_obter_produto(self):
        p = self.repo.obter_produto(1)
        self.assertIsNotNone(p)
        self.assertEqual(p.prodnome, "TECLADO USB")
        self.assertEqual(p.descricao_alternativa, "TECLADO ABNT2")

        p_inexistente = self.repo.obter_produto(999)
        self.assertIsNone(p_inexistente)

    def test_salvar_produto_insercao(self):
        novo = ProdutoDTO(
            prodcod=3,
            prodnome="MONITOR 24 POL",
            descricao_alternativa="FULL HD",
            grupocod=4,
            tamanho="",
            observacoes="Sem detalhes",
        )
        self.assertTrue(self.repo.salvar_produto(novo))
        self.assertEqual(self.repo.contar_produtos(), 3)
        salvo = self.repo.obter_produto(3)
        self.assertEqual(salvo.prodnome, "MONITOR 24 POL")

    def test_salvar_produto_atualizacao(self):
        p = ProdutoDTO(
            prodcod=1,
            prodnome="TECLADO MECANICO RGB",
            descricao_alternativa="SWITCH BLUE",
            grupocod=4,
            tamanho="",
            observacoes="Atualizado",
        )
        self.assertTrue(self.repo.salvar_produto(p))
        atualizado = self.repo.obter_produto(1)
        self.assertEqual(atualizado.prodnome, "TECLADO MECANICO RGB")
        self.assertEqual(atualizado.descricao_alternativa, "SWITCH BLUE")

    def test_salvar_e_obter_produto_com_unidade_inmetro_lote(self):
        p = ProdutoDTO(
            prodcod=50,
            prodnome="EXTINTOR DE INCENDIO ABC",
            grupocod=4,
            unidade_medida="UN",
            codigo_inmetro="INMETRO-004523/2024",
            codigo_lote="LT-EXT-2026-9",
            observacoes="Validade 5 anos",
        )
        self.assertTrue(self.repo.salvar_produto(p))
        recuperado = self.repo.obter_produto(50)
        self.assertIsNotNone(recuperado)
        self.assertEqual(recuperado.prodnome, "EXTINTOR DE INCENDIO ABC")
        self.assertEqual(recuperado.unidade_medida, "UN")
        self.assertEqual(recuperado.tamanho, "UN")
        self.assertEqual(recuperado.codigo_inmetro, "INMETRO-004523/2024")
        self.assertEqual(recuperado.codigo_lote, "LT-EXT-2026-9")

        # Testa listagem
        prods = self.repo.listar_produtos(filtro="EXTINTOR")
        self.assertEqual(len(prods), 1)
        self.assertEqual(prods[0].codigo_inmetro, "INMETRO-004523/2024")
        self.assertEqual(prods[0].codigo_lote, "LT-EXT-2026-9")
        self.assertEqual(prods[0].unidade_medida, "UN")

    def test_salvar_produto_com_marca_e_cores(self):
        # Cadastra marca e cor
        self.conn.cursor().execute("INSERT INTO USER_geoapolo_produto_marcas VALUES (1, 'LOGITECH')")
        self.conn.cursor().execute("INSERT INTO USER_geoapolo_produto_cores VALUES (1, 'PRETO')")
        self.conn.cursor().execute("INSERT INTO USER_geoapolo_produto_cores VALUES (2, 'CINZA')")
        self.conn.commit()

        p = ProdutoDTO(
            prodcod=3,
            prodnome="HEADSET GAMER",
            grupocod=4,
            codigo_marca=1,
            nome_marca="LOGITECH",
            cores_codigos=[1, 2],
            cores_nomes=["PRETO", "CINZA"]
        )
        self.assertTrue(self.repo.salvar_produto(p))

        salvo = self.repo.obter_produto(3)
        self.assertIsNotNone(salvo)
        self.assertEqual(salvo.codigo_marca, 1)
        self.assertEqual(salvo.nome_marca, "LOGITECH")
        self.assertEqual(set(salvo.cores_codigos), {1, 2})
        self.assertEqual(set(salvo.cores_nomes), {"CINZA", "PRETO"})

    def test_obter_ou_criar_marca_repository(self):
        cod1, desc1 = self.repo.obter_ou_criar_marca("RAZER")
        self.assertEqual(cod1, 1)
        self.assertEqual(desc1, "RAZER")

        # Repetida deve reutilizar o mesmo código
        cod2, desc2 = self.repo.obter_ou_criar_marca("razer")
        self.assertEqual(cod2, 1)
        self.assertEqual(desc2, "RAZER")
    def test_excluir_produto(self):
        self.assertTrue(self.repo.excluir_produto(2))
        self.assertEqual(self.repo.contar_produtos(), 1)
        self.assertIsNone(self.repo.obter_produto(2))

    def test_obter_grupo(self):
        g = self.repo.obter_grupo(1)
        self.assertIsNotNone(g)
        self.assertEqual(g.nome_grupo, "PRODUTOS")
        self.assertIsNone(self.repo.obter_grupo(999))

    def test_salvar_grupo_insercao_e_atualizacao(self):
        novo = GrupoProdutoDTO(grupocod=10, codigo_estruturado="02", nome_grupo="LIVRARIA")
        self.assertTrue(self.repo.salvar_grupo(novo))
        salvo = self.repo.obter_grupo(10)
        self.assertIsNotNone(salvo)
        self.assertEqual(salvo.nome_grupo, "LIVRARIA")

        salvo.nome_grupo = "LIVROS E REVISTAS"
        self.assertTrue(self.repo.salvar_grupo(salvo))
        atualizado = self.repo.obter_grupo(10)
        self.assertEqual(atualizado.nome_grupo, "LIVROS E REVISTAS")

    def test_excluir_grupo(self):
        novo = GrupoProdutoDTO(grupocod=20, codigo_estruturado="03", nome_grupo="BRINDES")
        self.repo.salvar_grupo(novo)
        self.assertTrue(self.repo.excluir_grupo(20))
        self.assertIsNone(self.repo.obter_grupo(20))

    def test_produtos_repository_sem_coluna_tamanho(self):
        conn_sem_tam = sqlite3.connect(":memory:")
        cur = conn_sem_tam.cursor()
        cur.executescript("""
            CREATE TABLE USER_geoapolo_produto_grupo (
                grupocod INTEGER PRIMARY KEY,
                codigo_estruturado TEXT,
                nome_grupo TEXT
            );
            CREATE TABLE USER_geoapolo_produtos (
                prodcod INTEGER PRIMARY KEY,
                prodnome TEXT,
                descricao_alternativa TEXT,
                grupocod INTEGER,
                unidade_medida TEXT,
                observacoes TEXT
            );
            INSERT INTO USER_geoapolo_produtos (prodcod, prodnome, unidade_medida)
            VALUES (1, 'PRODUTO TESTE SEM TAMANHO', 'KG');
        """)

        conn_sem_tam.commit()
        repo = ProdutosRepository(conn_sem_tam)
        self.assertFalse(repo._tem_coluna_tamanho)
        self.assertNotIn("tamanho", repo._coluna_unidade_sql)

        # Listar
        prods = repo.listar_produtos()
        self.assertEqual(len(prods), 1)
        self.assertEqual(prods[0].unidade_medida, "KG")

        # Obter
        p = repo.obter_produto(1)
        self.assertIsNotNone(p)
        self.assertEqual(p.unidade_medida, "KG")

        # Salvar (update)
        p.prodnome = "PRODUTO TESTE ALTERADO"
        p.unidade_medida = "MT"
        self.assertTrue(repo.salvar_produto(p))
        p_up = repo.obter_produto(1)
        self.assertEqual(p_up.prodnome, "PRODUTO TESTE ALTERADO")
        self.assertEqual(p_up.unidade_medida, "MT")

        # Salvar (insert)
        p_novo = ProdutoDTO(prodcod=2, prodnome="NOVO PRODUTO", unidade_medida="UN")
        self.assertTrue(repo.salvar_produto(p_novo))
        p2 = repo.obter_produto(2)
        self.assertEqual(p2.prodnome, "NOVO PRODUTO")
        self.assertEqual(p2.unidade_medida, "UN")
        conn_sem_tam.close()



class TestGeoapoloConfigCod(unittest.TestCase):
    """Testes da função clássica geoapolo_configcod com SQLite em memória."""

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        cur = self.conn.cursor()
        cur.executescript("""
            CREATE TABLE USER_geoapolo_configcod (
                empcod TEXT,
                geotabela TEXT,
                tabela_ativa TEXT,
                proximo_codigo INTEGER,
                ultimo_numero_utilizado INTEGER
            );
            CREATE TABLE USER_geoapolo_produtos (
                prodcod INTEGER PRIMARY KEY,
                prodnome TEXT
            );
        """)
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def test_configcod_insere_se_inexistente(self):
        from core.recursos import geoapolo_configcod
        cod = geoapolo_configcod(empresa="1.01", tabela="USER_geoapolo_produtos", connection=self.conn)
        self.assertEqual(cod, "1")

        cur = self.conn.cursor()
        cur.execute("SELECT proximo_codigo, ultimo_numero_utilizado FROM USER_geoapolo_configcod WHERE empcod = '1.01' AND geotabela = 'USER_geoapolo_produtos'")
        row = cur.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 2)
        self.assertEqual(row[1], 1)

    def test_configcod_incrementa_existente(self):
        from core.recursos import geoapolo_configcod
        cur = self.conn.cursor()
        cur.execute("INSERT INTO USER_geoapolo_configcod VALUES ('1.01', 'USER_geoapolo_produtos', 'S', 20, 19)")
        self.conn.commit()

        cod = geoapolo_configcod(empresa="1.01", tabela="USER_geoapolo_produtos", connection=self.conn)
        self.assertEqual(cod, "20")

        cur.execute("SELECT proximo_codigo, ultimo_numero_utilizado FROM USER_geoapolo_configcod WHERE empcod = '1.01' AND geotabela = 'USER_geoapolo_produtos'")
        row = cur.fetchone()
        self.assertEqual(row[0], 21)
        self.assertEqual(row[1], 20)


class TestProdutosService(unittest.TestCase):
    """Testes de regras de negócio do serviço de produtos."""

    def setUp(self):
        self.mock_repo = MagicMock(spec=ProdutosRepository)
        self.service = ProdutosService(self.mock_repo)

    def test_salvar_produto_validacao_nome_obrigatorio(self):
        p = ProdutoDTO(prodcod=1, prodnome="")
        res = self.service.salvar_produto(p)
        self.assertFalse(res.sucesso)
        self.assertIn("obrigatória", res.mensagem)

    def test_salvar_produto_sucesso_com_proximo_codigo(self):
        self.mock_repo.obter_proximo_codigo.return_value = 10
        p = ProdutoDTO(prodcod=0, prodnome="cabo hdmi")
        res = self.service.salvar_produto(p)
        self.assertTrue(res.sucesso)
        self.assertEqual(res.codigo, 10)
        self.assertEqual(p.prodnome, "CABO HDMI")
        self.mock_repo.salvar_produto.assert_called_once()

    def test_salvar_produto_normalizacao_unidade_inmetro_lote(self):
        self.mock_repo.obter_proximo_codigo.return_value = 1
        # 1. Caixa
        p1 = ProdutoDTO(
            prodcod=1,
            prodnome="PAPEL A4",
            unidade_medida="CX - CAIXA",
            codigo_inmetro="inmetro-br-123",
            codigo_lote="lote-01",
        )
        res1 = self.service.salvar_produto(p1)
        self.assertTrue(res1.sucesso)
        self.assertEqual(p1.unidade_medida, "CX")
        self.assertEqual(p1.tamanho, "CX")
        self.assertEqual(p1.codigo_inmetro, "INMETRO-BR-123")
        self.assertEqual(p1.codigo_lote, "LOTE-01")

        # 2. Pacote
        p2 = ProdutoDTO(
            prodcod=2,
            prodnome="COPOS DESCARTAVEIS",
            unidade_medida="PCT - PACOTE",
        )
        res2 = self.service.salvar_produto(p2)
        self.assertTrue(res2.sucesso)
        self.assertEqual(p2.unidade_medida, "PCT")
        self.assertEqual(p2.tamanho, "PCT")

    def test_excluir_produto_codigo_invalido(self):
        res = self.service.excluir_produto(0)
        self.assertFalse(res.sucesso)
        self.assertIn("inválido", res.mensagem)

    def test_excluir_produto_sucesso(self):
        self.mock_repo.obter_produto.return_value = ProdutoDTO(prodcod=5, prodnome="TESTE")
        res = self.service.excluir_produto(5)
        self.assertTrue(res.sucesso)
        self.mock_repo.excluir_produto.assert_called_once_with(5)

    def test_salvar_grupo_validacao_nome_obrigatorio(self):
        g = GrupoProdutoDTO(grupocod=1, nome_grupo="")
        res = self.service.salvar_grupo(g)
        self.assertFalse(res.sucesso)
        self.assertIn("obrigat", res.mensagem.lower())

    def test_salvar_grupo_sucesso(self):
        g = GrupoProdutoDTO(grupocod=5, nome_grupo="uniformes")
        res = self.service.salvar_grupo(g)
        self.assertTrue(res.sucesso)
        self.assertEqual(g.nome_grupo, "UNIFORMES")
        self.mock_repo.salvar_grupo.assert_called_once()

    def test_excluir_grupo_validacao(self):
        res = self.service.excluir_grupo(0)
        self.assertFalse(res.sucesso)


class TestProdutosViewHeadless(unittest.TestCase):
    """Testes de inicialização da interface gráfica em modo headless."""

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        self.root.destroy()

    def test_view_produtos_headless(self):
        mock_repo = MagicMock(spec=ProdutosRepository)
        mock_repo.contar_produtos.return_value = 5
        mock_repo.listar_grupos.return_value = [GrupoProdutoDTO(1, "01", "PRODUTOS")]
        mock_repo.listar_produtos.return_value = [
            ProdutoDTO(1, "PRODUTO A", grupocod=1, nome_grupo="PRODUTOS")
        ]
        mock_repo.obter_proximo_codigo.return_value = 2

        service = ProdutosService(mock_repo)
        view = ProdutosView(self.root, service=service)

        self.assertIsNotNone(view.tree_produtos)
        self.assertIsNotNone(view.ent_prodcod)
        self.assertIsNotNone(view.ent_prodnome)
        self.assertEqual(view.lbl_num_produtos.cget("text"), "5")

        # Testa conversão automática para maiúsculo via trace
        view.var_prodnome.set("mouse sem fio")
        self.assertEqual(view.var_prodnome.get(), "MOUSE SEM FIO")

        view.var_tamanho.set("gg")
        self.assertEqual(view.var_tamanho.get(), "GG")
        self.assertEqual(view.var_unidade.get(), "GG")

        # Verifica componentes da Unidade de Medida e INMETRO
        self.assertIsNotNone(view.cbo_unidade)
        self.assertIsNotNone(view.ent_codigo_inmetro)
        # Código de lote foi removido da tela de produtos conforme regra
        self.assertFalse(hasattr(view, "ent_codigo_lote"))
        self.assertFalse(hasattr(view, "var_codigo_lote"))

        # Verifica opções de Unidade no Combobox (Caixa e Pacote)
        self.assertIn("CX - CAIXA", view.cbo_unidade["values"])
        self.assertIn("PCT - PACOTE", view.cbo_unidade["values"])

        # Testa traces de maiúsculo nos novos campos
        view.var_codigo_inmetro.set("inm-12345/2026")
        self.assertEqual(view.var_codigo_inmetro.get(), "INM-12345/2026")

        # Testa limpeza dos campos
        view._limpar_campos()
        self.assertEqual(view.var_unidade.get(), "UN - UNIDADE")
        self.assertEqual(view.var_codigo_inmetro.get(), "")

        view.destroy()

    def test_view_grupos_produtos_headless(self):
        from produtos.grupos_view import GruposProdutosView
        mock_repo = MagicMock(spec=ProdutosRepository)
        mock_repo.listar_grupos.return_value = [GrupoProdutoDTO(1, "01", "PRODUTOS")]
        service = ProdutosService(mock_repo)

        view = GruposProdutosView(self.root, service=service)
        self.assertIsNotNone(view.tree_grupos)
        self.assertIsNotNone(view.ent_grupocod)
        self.assertIsNotNone(view.ent_nome_grupo)

        # Testa maiúsculo automático
        view.var_nome_grupo.set("eletrônicos")
        self.assertEqual(view.var_nome_grupo.get(), "ELETRÔNICOS")

    def test_view_produtos_combo_marca_digitar_codigo(self):
        mock_repo = MagicMock(spec=ProdutosRepository)
        mock_repo.listar_marcas.return_value = [
            (7, "ADOBE"),
            (164, "CANON U.S.A., INC."),
            (48, "LG"),
        ]
        mock_repo.listar_grupos.return_value = [GrupoProdutoDTO(1, "01", "INFORMÁTICA")]
        mock_repo.listar_produtos.return_value = []
        mock_repo.contar_produtos.return_value = 0
        service = ProdutosService(mock_repo)

        view = ProdutosView(self.root, service=service)

        # 1. Digita código "7" na combo de marcas
        view.var_marca.set("7")
        cod, desc = view._verificar_marca_digitada()
        self.assertEqual(cod, 7)
        self.assertEqual(desc, "ADOBE")
        self.assertIn("ADOBE", view.var_marca.get())

        # 2. Digita código "164" na combo de marcas
        view.var_marca.set("164")
        cod, desc = view._verificar_marca_digitada()
        self.assertEqual(cod, 164)
        self.assertEqual(desc, "CANON U.S.A., INC.")

        # 3. Digita código com zeros à esquerda "007"
        view.var_marca.set("007")
        cod, desc = view._verificar_marca_digitada()
        self.assertEqual(cod, 7)
        self.assertEqual(desc, "ADOBE")

        view.destroy()

    def test_view_produtos_combo_marca_digitar_nome_ou_prefixo(self):
        mock_repo = MagicMock(spec=ProdutosRepository)
        mock_repo.listar_marcas.return_value = [
            (7, "ADOBE"),
            (164, "CANON U.S.A., INC."),
            (48, "LG"),
            (366, "MICROSOFT CORPORATION"),
        ]
        mock_repo.listar_grupos.return_value = []
        mock_repo.listar_produtos.return_value = []
        mock_repo.contar_produtos.return_value = 0
        service = ProdutosService(mock_repo)

        view = ProdutosView(self.root, service=service)

        # 1. Digita prefixo "CANON"
        view.var_marca.set("CANON")
        cod, desc = view._verificar_marca_digitada()
        self.assertEqual(cod, 164)
        self.assertEqual(desc, "CANON U.S.A., INC.")

        # 2. Digita em minúsculas "adobe"
        view.var_marca.set("adobe")
        cod, desc = view._verificar_marca_digitada()
        self.assertEqual(cod, 7)
        self.assertEqual(desc, "ADOBE")

        # 3. Digita substring "MICROSOFT"
        view.var_marca.set("MICROSOFT")
        cod, desc = view._verificar_marca_digitada()
        self.assertEqual(cod, 366)
        self.assertEqual(desc, "MICROSOFT CORPORATION")

        view.destroy()

    def test_view_produtos_combo_marca_digitar_inexistente(self):
        from unittest.mock import patch
        mock_repo = MagicMock(spec=ProdutosRepository)
        mock_repo.listar_marcas.return_value = [(7, "ADOBE")]
        mock_repo.obter_ou_criar_marca.return_value = (99, "MARCA TESTE NOVA")
        mock_repo.listar_grupos.return_value = []
        mock_repo.listar_produtos.return_value = []
        mock_repo.contar_produtos.return_value = 0
        service = ProdutosService(mock_repo)

        view = ProdutosView(self.root, service=service)

        view.var_marca.set("MARCA TESTE NOVA")

        # Se o usuário aceitar criar nova marca
        with patch("tkinter.messagebox.askyesno", return_value=True):
            cod, desc = view._verificar_marca_digitada()
            self.assertEqual(cod, 99)
            self.assertEqual(desc, "MARCA TESTE NOVA")
            mock_repo.obter_ou_criar_marca.assert_called_with("MARCA TESTE NOVA")

        # Se o usuário recusar criar
        view.var_marca.set("OUTRA INEXISTENTE")
        with patch("tkinter.messagebox.askyesno", return_value=False):
            cod, desc = view._verificar_marca_digitada()
            self.assertIsNone(cod)
            self.assertEqual(desc, "")
            self.assertEqual(view.var_marca.get(), "(Nenhuma marca)")

        view.destroy()

    def test_view_produtos_combo_grupo_resolucao(self):
        mock_repo = MagicMock(spec=ProdutosRepository)
        mock_repo.listar_grupos.return_value = [
            GrupoProdutoDTO(1, "01", "INFORMÁTICA"),
            GrupoProdutoDTO(2, "02", "PAPELARIA"),
        ]
        mock_repo.listar_marcas.return_value = []
        mock_repo.listar_produtos.return_value = []
        mock_repo.contar_produtos.return_value = 0
        service = ProdutosService(mock_repo)

        view = ProdutosView(self.root, service=service)

        # Testa que a lista do combobox tem os grupos
        self.assertIn("01 - INFORMÁTICA", view.cbo_grupo["values"])
        self.assertIn("02 - PAPELARIA", view.cbo_grupo["values"])

        # Testa resolução ao salvar produto digitando apenas código "01" ou nome
        view.cbo_grupo.set("01")
        view.ent_prodcod.insert(0, "100")
        view.var_prodnome.set("TECLADO USB")

        mock_repo.salvar_produto.return_value = None
        with patch("tkinter.messagebox.askyesno", return_value=True), \
             patch("tkinter.messagebox.showinfo"):
            view._salvar_produto()

        # Verifica se o grupocod salvo foi 1
        chamada_dto = mock_repo.salvar_produto.call_args[0][0]
        self.assertEqual(chamada_dto.grupocod, 1)

        view.destroy()

    def test_view_produtos_salvar_unidade_inmetro(self):
        mock_repo = MagicMock(spec=ProdutosRepository)
        mock_repo.listar_grupos.return_value = []
        mock_repo.listar_marcas.return_value = []
        mock_repo.listar_produtos.return_value = []
        mock_repo.contar_produtos.return_value = 0
        service = ProdutosService(mock_repo)

        view = ProdutosView(self.root, service=service)
        view.ent_prodcod.insert(0, "200")
        view.var_prodnome.set("CAIXA DE RESMAS SULFITE A4")
        view.var_unidade.set("CX - CAIXA")
        view.var_codigo_inmetro.set("INMETRO-789-2026")

        with patch("tkinter.messagebox.askyesno", return_value=True), \
             patch("tkinter.messagebox.showinfo"):
            sucesso = view._salvar_produto()

        self.assertTrue(sucesso)
        self.assertTrue(mock_repo.salvar_produto.called)
        dto_salvo = mock_repo.salvar_produto.call_args[0][0]
        self.assertEqual(dto_salvo.unidade_medida, "CX")
        self.assertEqual(dto_salvo.tamanho, "CX")
        self.assertEqual(dto_salvo.codigo_inmetro, "INMETRO-789-2026")
        self.assertEqual(dto_salvo.codigo_lote, "")

        view.destroy()


if __name__ == "__main__":
    unittest.main()
