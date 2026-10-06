"""
Testes Unitários para o Módulo de Centros de Controle / Custos (GeoApolo V5).
Cobertura: CentroControleDTO, CentroControleRepository, CentroControleService e CentrosControleView (headless).
"""

import sqlite3
import tkinter as tk
import unittest
from datetime import datetime

from centro_controle.models import CentroControleDTO, ResultadoCentroControleDTO
from centro_controle.repository import CentroControleRepository
from centro_controle.service import CentroControleService
from centro_controle.view import CentrosControleView


def criar_banco_teste():
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE USER_geoapolo_centrocontrole (
            geocctrlcodestr VARCHAR(30) PRIMARY KEY,
            geocctrlcodreduzido VARCHAR(7) NOT NULL,
            geocctrlnome VARCHAR(60),
            geocctrlcodestrniv VARCHAR(30),
            geocctrlgrupo CHAR(1) DEFAULT 'A',
            geocctrlcusto VARCHAR(10),
            geodatavalidadeinicial TEXT,
            geodatavalidadefinal TEXT,
            empcod VARCHAR(20) DEFAULT '1.01'
        )
    """)
    cur.execute("""
        INSERT INTO USER_geoapolo_centrocontrole
        (geocctrlcodestr, geocctrlcodreduzido, geocctrlnome, geocctrlcodestrniv, geocctrlgrupo, geocctrlcusto, empcod)
        VALUES ('01', '1', 'ADMINISTRATIVO', '', 'T', 'CC01', '1.01')
    """)
    cur.execute("""
        INSERT INTO USER_geoapolo_centrocontrole
        (geocctrlcodestr, geocctrlcodreduzido, geocctrlnome, geocctrlcodestrniv, geocctrlgrupo, geocctrlcusto, empcod)
        VALUES ('01.01', '2', 'DIRETORIA GERAL', '01', 'A', 'CC02', '1.01')
    """)
    conn.commit()
    return conn


class TestCentroControleModels(unittest.TestCase):

    def test_dto_properties(self):
        dto = CentroControleDTO(
            geocctrlcodestr="01.01.001",
            geocctrlcodreduzido="10",
            geocctrlnome="TECNOLOGIA DA INFORMACAO",
            geocctrlcodestrniv="01.01",
            geocctrlgrupo="A",
            geocctrlcusto="CC10",
            empcod="1.01",
        )
        self.assertEqual(dto.display, "01.01.001 - TECNOLOGIA DA INFORMACAO")
        self.assertFalse(dto.is_sintetico)
        self.assertEqual(dto.display_tipo, "Analítico")

        dto_sint = CentroControleDTO(
            geocctrlcodestr="01",
            geocctrlnome="ADMINISTRACAO",
            geocctrlgrupo="T",
        )
        self.assertTrue(dto_sint.is_sintetico)
        self.assertEqual(dto_sint.display_tipo, "Sintético (Grupo)")

    def test_resultado_dto(self):
        res = ResultadoCentroControleDTO(sucesso=True, mensagem="Salvo com sucesso", codigo="01.01")
        self.assertTrue(res.sucesso)
        self.assertEqual(res.codigo, "01.01")


class TestCentroControleRepository(unittest.TestCase):

    def setUp(self):
        self.conn = criar_banco_teste()
        self.repo = CentroControleRepository(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_listar_centros(self):
        itens = self.repo.listar_centros(empcod="1.01")
        self.assertEqual(len(itens), 2)
        self.assertEqual(itens[0].geocctrlcodestr, "01")
        self.assertEqual(itens[1].geocctrlcodestr, "01.01")

    def test_obter_centro(self):
        c = self.repo.obter_centro("01.01")
        self.assertIsNotNone(c)
        self.assertEqual(c.geocctrlnome, "DIRETORIA GERAL")

        c_inexistente = self.repo.obter_centro("99.99")
        self.assertIsNone(c_inexistente)

    def test_listar_niveis_superiores(self):
        niveis = self.repo.listar_niveis_superiores()
        self.assertEqual(len(niveis), 1)
        self.assertEqual(niveis[0].geocctrlcodestr, "01")

    def test_obter_proximo_codigo_reduzido(self):
        prox = self.repo.obter_proximo_codigo_reduzido()
        self.assertEqual(prox, "03")

    def test_salvar_novo_e_atualizar(self):
        novo = CentroControleDTO(
            geocctrlcodestr="01.02",
            geocctrlcodreduzido="3",
            geocctrlnome="RECURSOS HUMANOS",
            geocctrlcodestrniv="01",
            geocctrlgrupo="A",
            geocctrlcusto="CC03",
            empcod="1.01",
        )
        self.repo.salvar_centro(novo)

        buscado = self.repo.obter_centro("01.02")
        self.assertIsNotNone(buscado)
        self.assertEqual(buscado.geocctrlnome, "RECURSOS HUMANOS")

        buscado.geocctrlnome = "DP / RECURSOS HUMANOS"
        self.repo.salvar_centro(buscado)

        atualizado = self.repo.obter_centro("01.02")
        self.assertEqual(atualizado.geocctrlnome, "DP / RECURSOS HUMANOS")

    def test_excluir(self):
        self.repo.excluir_centro("01.01")
        self.assertIsNone(self.repo.obter_centro("01.01"))


class TestCentroControleService(unittest.TestCase):

    def setUp(self):
        self.conn = criar_banco_teste()
        self.repo = CentroControleRepository(self.conn)
        self.service = CentroControleService(self.repo)

    def tearDown(self):
        self.conn.close()

    def test_validacoes_campos_obrigatorios(self):
        # Sem código estruturado
        res1 = self.service.salvar_centro(CentroControleDTO(geocctrlcodestr="", geocctrlnome="TESTE"))
        self.assertFalse(res1.sucesso)
        self.assertIn("Código Estruturado", res1.mensagem)

        # Sem nome
        res2 = self.service.salvar_centro(CentroControleDTO(geocctrlcodestr="02", geocctrlnome=""))
        self.assertFalse(res2.sucesso)
        self.assertIn("Descrição / Nome", res2.mensagem)

    def test_validacao_nivel_superior_recursivo(self):
        dto = CentroControleDTO(
            geocctrlcodestr="01.01",
            geocctrlnome="DIRETORIA",
            geocctrlcodestrniv="01.01",
        )
        res = self.service.salvar_centro(dto)
        self.assertFalse(res.sucesso)
        self.assertIn("não pode ser nível superior de si mesmo", res.mensagem)

    def test_bloqueio_exclusao_com_filhos(self):
        # Tentar excluir '01' que tem '01.01' como dependente
        res = self.service.excluir_centro("01")
        self.assertFalse(res.sucesso)
        self.assertIn("subn", res.mensagem.lower())

    def test_busca_por_termo(self):
        itens = self.service.listar_centros(termo="DIRETORIA", empcod="1.01")
        self.assertEqual(len(itens), 1)
        self.assertEqual(itens[0].geocctrlcodestr, "01.01")


class TestCentroControleViewHeadless(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.conn = criar_banco_teste()
        self.repo = CentroControleRepository(self.conn)
        self.service = CentroControleService(self.repo)

    def tearDown(self):
        self.root.destroy()
        self.conn.close()

    def test_renderizacao_view(self):
        view = CentrosControleView(self.root, service=self.service)
        self.assertTrue(hasattr(view, "tree"))
        self.assertTrue(hasattr(view, "ent_codestr"))
        self.assertTrue(hasattr(view, "ent_nome"))

        # Carregou registros
        items = view.tree.get_children()
        self.assertEqual(len(items), 2)

        # Selecionar primeiro item e carregar formulário
        view.tree.selection_set(items[0])
        view._ao_selecionar_centro()
        self.assertEqual(view.var_codestr.get(), "01")
        self.assertEqual(view.var_nome.get(), "ADMINISTRATIVO")

    def test_abrir_janela_centros_controle_dimensoes_e_botoes(self):
        from centro_controle.view import abrir_janela_centros_controle
        win = abrir_janela_centros_controle(self.root, connection=self.conn)
        self.assertIsInstance(win, tk.Toplevel)
        min_w, min_h = win.minsize()
        self.assertGreaterEqual(min_w, 1000)
        views = [w for w in win.winfo_children() if isinstance(w, CentrosControleView)]
        self.assertEqual(len(views), 1)
        win.destroy()


if __name__ == "__main__":

    unittest.main()
