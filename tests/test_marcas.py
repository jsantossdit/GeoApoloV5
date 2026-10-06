"""
Testes Unitários para o Módulo de Marcas de Produtos.
GeoApolo V5
Equivalente a unt_cadmarcas do Delphi.
"""

import sqlite3
import unittest
import tkinter as tk

from marcas.models import MarcaDTO, ResultadoMarcaDTO
from marcas.repository import MarcasRepository
from marcas.service import MarcasService
from marcas.view import MarcasView


class TestMarcasModels(unittest.TestCase):
    """Testes dos DTOs e modelos do módulo de marcas."""

    def test_marca_dto_defaults(self):
        m = MarcaDTO()
        self.assertEqual(m.codigo_marca, 0)
        self.assertEqual(m.descricao_marca, "")

    def test_marca_dto_display_formatting(self):
        m = MarcaDTO(codigo_marca=7, descricao_marca="SONY")
        self.assertEqual(m.display, "007 - SONY")

    def test_resultado_marca_dto(self):
        res = ResultadoMarcaDTO(sucesso=True, mensagem="OK", codigo=10)
        self.assertTrue(res.sucesso)
        self.assertEqual(res.codigo, 10)


class TestMarcasRepository(unittest.TestCase):
    """Testes do repositório de marcas utilizando SQLite em memória."""

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE USER_geoapolo_produto_marcas (
                codigo_marca INTEGER PRIMARY KEY,
                descricao_marca TEXT
            );
        """)
        self.conn.commit()
        self.repo = MarcasRepository(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_obter_proximo_codigo_tabela_vazia(self):
        self.assertEqual(self.repo.obter_proximo_codigo(), 1)

    def test_obter_proximo_codigo_com_registros(self):
        self.repo.salvar_marca(MarcaDTO(codigo_marca=5, descricao_marca="DELL"))
        self.assertEqual(self.repo.obter_proximo_codigo(), 6)

    def test_salvar_e_listar_marcas(self):
        self.repo.salvar_marca(MarcaDTO(codigo_marca=1, descricao_marca="HP"))
        self.repo.salvar_marca(MarcaDTO(codigo_marca=2, descricao_marca="EPSON"))
        marcas = self.repo.listar_marcas()
        self.assertEqual(len(marcas), 2)
        self.assertEqual(marcas[0].descricao_marca, "HP")
        self.assertEqual(marcas[1].descricao_marca, "EPSON")

    def test_salvar_atualizacao_marca(self):
        self.repo.salvar_marca(MarcaDTO(codigo_marca=1, descricao_marca="HP"))
        self.repo.salvar_marca(MarcaDTO(codigo_marca=1, descricao_marca="HEWLETT PACKARD"))
        m = self.repo.obter_marca(1)
        self.assertIsNotNone(m)
        self.assertEqual(m.descricao_marca, "HEWLETT PACKARD")

    def test_obter_marca_inexistente(self):
        self.assertIsNone(self.repo.obter_marca(99))

    def test_obter_por_descricao(self):
        self.repo.salvar_marca(MarcaDTO(codigo_marca=1, descricao_marca="SAMSUNG"))
        m = self.repo.obter_por_descricao("samsung")
        self.assertIsNotNone(m)
        self.assertEqual(m.codigo_marca, 1)

    def test_existe_descricao(self):
        self.repo.salvar_marca(MarcaDTO(codigo_marca=1, descricao_marca="LG"))
        self.assertTrue(self.repo.existe_descricao("LG"))
        self.assertTrue(self.repo.existe_descricao("lg"))
        self.assertFalse(self.repo.existe_descricao("LG", codigo_ignorar=1))
        self.assertFalse(self.repo.existe_descricao("APPLE"))

    def test_excluir_marca(self):
        self.repo.salvar_marca(MarcaDTO(codigo_marca=1, descricao_marca="ASUS"))
        self.assertTrue(self.repo.excluir_marca(1))
        self.assertIsNone(self.repo.obter_marca(1))


class TestMarcasService(unittest.TestCase):
    """Testes de regras de negócio do serviço de marcas."""

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE USER_geoapolo_produto_marcas (
                codigo_marca INTEGER PRIMARY KEY,
                descricao_marca TEXT
            );
        """)
        self.conn.commit()
        self.repo = MarcasRepository(self.conn)
        self.service = MarcasService(self.repo)

    def tearDown(self):
        self.conn.close()

    def test_salvar_marca_descricao_vazia(self):
        res = self.service.salvar_marca(MarcaDTO(codigo_marca=1, descricao_marca=""))
        self.assertFalse(res.sucesso)
        self.assertIn("obrigatória", res.mensagem)

    def test_salvar_marca_nova_gera_codigo(self):
        res = self.service.salvar_marca(MarcaDTO(codigo_marca=0, descricao_marca="logitech"))
        self.assertTrue(res.sucesso)
        self.assertEqual(res.codigo, 1)
        m = self.service.obter_marca(1)
        self.assertEqual(m.descricao_marca, "LOGITECH")

    def test_salvar_marca_descricao_duplicada(self):
        self.service.salvar_marca(MarcaDTO(codigo_marca=1, descricao_marca="INTEL"))
        res = self.service.salvar_marca(MarcaDTO(codigo_marca=0, descricao_marca="intel"))
        self.assertFalse(res.sucesso)
        self.assertIn("já está cadastrada", res.mensagem)

    def test_obter_ou_criar_marca_existente(self):
        self.service.salvar_marca(MarcaDTO(codigo_marca=1, descricao_marca="AMD"))
        cod, desc, criada = self.service.obter_ou_criar_marca("amd")
        self.assertEqual(cod, 1)
        self.assertEqual(desc, "AMD")
        self.assertFalse(criada)

    def test_obter_ou_criar_marca_inexistente(self):
        cod, desc, criada = self.service.obter_ou_criar_marca("NVIDIA")
        self.assertEqual(cod, 1)
        self.assertEqual(desc, "NVIDIA")
        self.assertTrue(criada)
        m = self.service.obter_marca(1)
        self.assertEqual(m.descricao_marca, "NVIDIA")

    def test_excluir_marca_sucesso(self):
        self.service.salvar_marca(MarcaDTO(codigo_marca=1, descricao_marca="ACER"))
        res = self.service.excluir_marca(1)
        self.assertTrue(res.sucesso)
        self.assertIsNone(self.service.obter_marca(1))

    def test_excluir_marca_codigo_invalido(self):
        res = self.service.excluir_marca(0)
        self.assertFalse(res.sucesso)


class TestMarcasViewHeadless(unittest.TestCase):
    """Teste de renderização headless da MarcasView."""

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        try:
            self.root.destroy()
        except Exception:
            pass

    def test_view_marcas_headless(self):
        conn = sqlite3.connect(":memory:")
        cur = conn.cursor()
        cur.execute("CREATE TABLE USER_geoapolo_produto_marcas (codigo_marca INTEGER PRIMARY KEY, descricao_marca TEXT);")
        conn.commit()
        repo = MarcasRepository(conn)
        service = MarcasService(repo)
        service.salvar_marca(MarcaDTO(codigo_marca=1, descricao_marca="TOSHIBA"))

        view = MarcasView(self.root, service=service)
        self.assertEqual(len(view.tree.get_children()), 1)
        vals = view.tree.item(view.tree.get_children()[0])["values"]
        self.assertEqual(int(vals[0]), 1)
        self.assertEqual(str(vals[1]), "TOSHIBA")
        conn.close()


if __name__ == "__main__":
    unittest.main()
