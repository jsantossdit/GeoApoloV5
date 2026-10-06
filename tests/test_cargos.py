"""
Testes Unitários para o Módulo de Cadastro de Cargos (GeoApolo V5).
Cobertura: CargoDTO, CargoRepository, CargoService e FrmCadCargo (headless).
"""

import sqlite3
import tkinter as tk
import unittest
from unittest.mock import patch

from cargos.models import CargoDTO, ResultadoCargoDTO
from cargos.repository import CargoRepository
from cargos.service import CargoService
from cargos.cadcargo_view import FrmCadCargo, abrir_cargos


def criar_banco_teste():
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE USER_geoapolo_cargos (
            geocargocodestr INTEGER PRIMARY KEY,
            geocargonome TEXT NOT NULL,
            geofaixasalarial TEXT
        )
    """)
    cur.execute("INSERT INTO USER_geoapolo_cargos (geocargocodestr, geocargonome, geofaixasalarial) VALUES (1, 'ANALISTA DE SISTEMAS', 'FAIXA A')")
    cur.execute("INSERT INTO USER_geoapolo_cargos (geocargocodestr, geocargonome, geofaixasalarial) VALUES (2, 'GERENTE DE PROJETOS', 'FAIXA B')")
    conn.commit()
    return conn


class TestCargos(unittest.TestCase):

    def setUp(self):
        self.conn = criar_banco_teste()
        self.repo = CargoRepository(self.conn)
        self.service = CargoService(self.repo)

    def tearDown(self):
        self.conn.close()

    def test_01_cargo_dto(self):
        dto = CargoDTO(geocargocodestr=10, geocargonome="diretor financeiro", geofaixasalarial="faixa 1")
        self.assertEqual(dto.codigo, 10)
        self.assertEqual(dto.nome, "DIRETOR FINANCEIRO")
        self.assertEqual(dto.faixa_salarial, "FAIXA 1")

    def test_02_listar_cargos(self):
        cargos = self.service.listar_cargos()
        self.assertEqual(len(cargos), 2)
        self.assertEqual(cargos[0].geocargocodestr, 1)
        self.assertEqual(cargos[0].geocargonome, "ANALISTA DE SISTEMAS")

    def test_03_filtrar_cargos(self):
        filtrados = self.service.listar_cargos("ANALISTA")
        self.assertEqual(len(filtrados), 1)
        self.assertEqual(filtrados[0].geocargonome, "ANALISTA DE SISTEMAS")

        filtrados_vazio = self.service.listar_cargos("MEDICO")
        self.assertEqual(len(filtrados_vazio), 0)

    def test_04_obter_cargo(self):
        c = self.service.obter_cargo(2)
        self.assertIsNotNone(c)
        self.assertEqual(c.geocargonome, "GERENTE DE PROJETOS")

        self.assertIsNone(self.service.obter_cargo(99))

    def test_05_proximo_codigo(self):
        prox = self.service.obter_proximo_codigo()
        self.assertEqual(prox, 3)

    def test_06_salvar_novo_cargo(self):
        novo = CargoDTO(geocargocodestr=3, geocargonome="coordenador pedagógico", geofaixasalarial="faixa c")
        res = self.service.salvar_cargo(novo)
        self.assertTrue(res.sucesso)
        self.assertEqual(res.codigo, 3)

        c = self.service.obter_cargo(3)
        self.assertIsNotNone(c)
        self.assertEqual(c.geocargonome, "COORDENADOR PEDAGÓGICO")
        self.assertEqual(c.geofaixasalarial, "FAIXA C")

    def test_07_atualizar_cargo(self):
        alterado = CargoDTO(geocargocodestr=1, geocargonome="ANALISTA SENIOR", geofaixasalarial="FAIXA A2")
        res = self.service.salvar_cargo(alterado)
        self.assertTrue(res.sucesso)

        c = self.service.obter_cargo(1)
        self.assertEqual(c.geocargonome, "ANALISTA SENIOR")
        self.assertEqual(c.geofaixasalarial, "FAIXA A2")

    def test_08_validacao_nome_obrigatorio(self):
        invalido = CargoDTO(geocargocodestr=5, geocargonome="   ")
        res = self.service.salvar_cargo(invalido)
        self.assertFalse(res.sucesso)
        self.assertIn("obrigatório", res.mensagem.lower())

    def test_09_excluir_cargo(self):
        res = self.service.excluir_cargo(2)
        self.assertTrue(res.sucesso)
        self.assertIsNone(self.service.obter_cargo(2))

    def test_10_bloqueio_exclusao_em_uso(self):
        cur = self.conn.cursor()
        cur.execute("CREATE TABLE USER_geoapolo_funcionarios (funcod INTEGER, geocargocodestr INTEGER)")
        cur.execute("INSERT INTO USER_geoapolo_funcionarios VALUES (1, 1)")
        self.conn.commit()

        res = self.service.excluir_cargo(1)
        self.assertFalse(res.sucesso)
        self.assertIn("vínculos", res.mensagem.lower())

    @patch("tkinter.messagebox.showinfo")
    def test_11_frm_cad_cargo_headless(self, mock_msg):
        root = tk.Tk()
        root.withdraw()
        try:
            view = FrmCadCargo(parent=root, connection=self.conn)
            self.assertEqual(len(view.tree.get_children()), 2)
            
            # Testa novo registro
            view.novo_registro()
            self.assertEqual(view.var_codigo.get(), "3")
            self.assertEqual(view.var_nome.get(), "")

            # Testa salvar via view
            view.var_nome.set("SUPERVISOR")
            view.salvar_registro()
            self.assertIn("3", view.tree.get_children())
            
            view.destroy()
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
