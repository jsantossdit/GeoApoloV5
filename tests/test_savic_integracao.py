"""Testes unitários automatizados para o módulo de Integração SAVIC x GeoAlvo/Alvo e Configurações."""

import unittest
from unittest.mock import MagicMock, patch
from datetime import date
import tkinter as tk

from savic.models import (
    SavicResumoStatusDTO,
    SavicFiltroDTO,
    SavicGrupoOracaoDTO,
    SavicCoordenadorDTO,
    ResultadoImportacaoSavicDTO,
)
from savic.service import SavicService
from savic.repository import SavicRepository
from config_banco import DatabaseConfigForm


class TestSavicDTOs(unittest.TestCase):
    """Validação dos Data Transfer Objects do SAVIC."""

    def test_resumo_status_dto(self):
        resumo = SavicResumoStatusDTO(
            total_go=100,
            total_homologados=70,
            total_nao_homologados=20,
            total_em_andamento=10,
        )
        self.assertEqual(resumo.total_go, 100)
        self.assertEqual(resumo.total_homologados, 70)
        self.assertEqual(resumo.total_nao_homologados, 20)
        self.assertEqual(resumo.total_em_andamento, 10)

    def test_filtro_dto(self):
        filtro = SavicFiltroDTO(
            data_inicial=date(2026, 1, 1),
            data_final=date(2026, 1, 31),
            apenas_vigentes_ou_indeterminados=True,
        )
        self.assertEqual(filtro.data_inicial, date(2026, 1, 1))
        self.assertEqual(filtro.data_final, date(2026, 1, 31))
        self.assertTrue(filtro.apenas_vigentes_ou_indeterminados)

    def test_resultado_importacao_dto(self):
        res = ResultadoImportacaoSavicDTO(
            sucesso=True,
            total_registros_apurados=10,
            total_coordenadores_inseridos=3,
            total_coordenadores_atualizados=7,
            total_grupos_inseridos=2,
            total_grupos_atualizados=8,
        )
        self.assertTrue(res.sucesso)
        self.assertEqual(res.total_registros_apurados, 10)
        self.assertEqual(res.total_coordenadores_inseridos, 3)
        self.assertEqual(res.total_coordenadores_atualizados, 7)
        self.assertEqual(res.total_grupos_inseridos, 2)
        self.assertEqual(res.total_grupos_atualizados, 8)


class TestSavicServiceLogic(unittest.TestCase):
    """Testes da camada de serviço e regras de negócio da importação do SAVIC."""

    def setUp(self):
        self.mock_repo = MagicMock(spec=SavicRepository)
        self.service = SavicService(repository=self.mock_repo)

    def test_normalizar_tipo_logradouro(self):
        self.assertEqual(self.service.normalizar_tipo_logradouro("Rua das Flores"), "R.")
        self.assertEqual(self.service.normalizar_tipo_logradouro("R. das Flores"), "R.")
        self.assertEqual(self.service.normalizar_tipo_logradouro("Avenida Brasil"), "Av.")
        self.assertEqual(self.service.normalizar_tipo_logradouro("AV. Central"), "Av.")
        self.assertEqual(self.service.normalizar_tipo_logradouro("Alameda dos Anjos"), "Al.")
        self.assertEqual(self.service.normalizar_tipo_logradouro("Praça da Sé"), "Pç.")
        self.assertEqual(self.service.normalizar_tipo_logradouro("Praca da Se"), "Pç.")
        self.assertEqual(self.service.normalizar_tipo_logradouro("Rodovia SP-101"), "Rod.")
        self.assertEqual(self.service.normalizar_tipo_logradouro("Desconhecido"), "R.")

    def test_normalizar_tratamento(self):
        self.assertEqual(self.service.normalizar_tratamento("F"), "0002")
        self.assertEqual(self.service.normalizar_tratamento("Feminino"), "0002")
        self.assertEqual(self.service.normalizar_tratamento("M"), "0001")
        self.assertEqual(self.service.normalizar_tratamento("Masculino"), "0001")

    def test_resolver_cidade_excecoes_conhecidas(self):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        # Exceção Alvorada D Oeste -> Alvorada do Oeste
        mock_cursor.fetchone.side_effect = [
            ("00001234",),  # encontrado em USER_geoapolo_cidades
        ]
        cod = self.service.resolver_cidade_codigo("Alvorada D Oeste", "RO", mock_conn)
        self.assertEqual(cod, "00001234")

        # Exceção DF Estrutural -> Brasília
        mock_cursor.fetchone.side_effect = [
            None,           # não achou na primeira
            ("00005678",),  # achou na tabela cidade
        ]
        cod_df = self.service.resolver_cidade_codigo("Estrutural", "DF", mock_conn)
        self.assertEqual(cod_df, "00005678")

    def test_apurar_registros_por_data(self):
        self.mock_repo.contar_registros_apurados.return_value = 42
        filtro = SavicFiltroDTO(data_inicial=date(2026, 1, 1), data_final=date(2026, 1, 31))
        qtd = self.service.contar_apurados(filtro)
        self.assertEqual(qtd, 42)
        self.mock_repo.contar_registros_apurados.assert_called_once_with(filtro)

    @patch("savic.service.geoapolo_configcod")
    def test_importar_coordenador_novo_insert(self, mock_configcod):
        mock_configcod.return_value = "00000099"
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        self.service._get_geo_conn = MagicMock(return_value=mock_conn)

        # Simula coordenador não existente por CPF
        self.mock_repo.buscar_geoentcod_por_cpf.return_value = None
        # cursor.fetchone para busca de entcod no Alvo, etc.
        mock_cursor.fetchone.return_value = None

        coord = SavicCoordenadorDTO(
            cadastroid_coord="SAVIC-01",
            coordenador="Maria da Silva",
            cpf_coordenador="123.456.789-00",
            endereco_coordenador="Rua das Palmeiras",
            cidade="Campinas",
            estado="SP",
            genero_coord="F",
            mandato_indeterminado="S",
        )
        grupo = SavicGrupoOracaoDTO(
            goid="GO-100",
            grupo_de_oracao="G.O. Jesus Misericordioso",
            cidade="Campinas",
            estado="SP",
            coordenador=coord,
        )
        self.mock_repo.buscar_grupos_para_importacao.return_value = [grupo]

        filtro = SavicFiltroDTO(date(2026, 1, 1), date(2026, 1, 31))
        resultado = self.service.importar_grupos_e_coordenadores(filtro, empresa_codigo="01")

        self.assertTrue(resultado.sucesso)
        self.assertEqual(resultado.total_coordenadores_inseridos, 1)
        self.assertEqual(resultado.total_grupos_inseridos, 1)

    def test_importar_coordenador_existente_update(self):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        self.service._get_geo_conn = MagicMock(return_value=mock_conn)
        self.service.resolver_cidade_codigo = MagicMock(return_value="00000001")

        self.mock_repo.buscar_geoentcod_por_cpf.return_value = "0000055"
        mock_cursor.fetchone.side_effect = [
            ("COORD-EXISTENTE",),  # busca em USER_geoapolo_coordenadores_grupodeoracao
            ("GO-EXISTENTE",),     # busca em USER_geoapolo_gruposdeoracao
            ("GO-200", "0", ""),   # busca geoentcod em USER_geoapolo_entidade
            ("0001",),             # busca geotipotratcod em USER_geoapolo_entidade
        ]

        coord = SavicCoordenadorDTO(
            cadastroid_coord="SAVIC-02",
            coordenador="Joao Santos",
            cpf_coordenador="987.654.321-99",
            endereco_coordenador="Av. Central",
            cidade="Sao Paulo",
            estado="SP",
            genero_coord="M",
            mandato_indeterminado="S",
        )
        grupo = SavicGrupoOracaoDTO(
            goid="GO-200",
            grupo_de_oracao="G.O. Sao Miguel Arcanjo",
            cidade="Sao Paulo",
            estado="SP",
            coordenador=coord,
        )
        self.mock_repo.buscar_grupos_para_importacao.return_value = [grupo]

        filtro = SavicFiltroDTO(date(2026, 1, 1), date(2026, 1, 31))
        resultado = self.service.importar_grupos_e_coordenadores(filtro, empresa_codigo="01")

        self.assertTrue(resultado.sucesso)
        self.assertEqual(resultado.total_coordenadores_atualizados, 1)
        self.assertEqual(resultado.total_grupos_atualizados, 1)


class TestDualDatabaseConfig(unittest.TestCase):
    """Testes para o configurador dual de banco de dados (SQL Server + Savic MySQL)."""

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        try:
            self.root.destroy()
        except Exception:
            pass

    @patch("pyodbc.connect")
    @patch("tkinter.messagebox.showinfo")
    def test_testar_conexao_geoalvo(self, mock_msg, mock_connect):
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        form = DatabaseConfigForm(parent=self.root, initial_tab="MSSQL")
        form.geo_endereco_var.set("10.120.104.29")
        form.geo_banco_var.set("RCC")
        form.geo_usuario_var.set("sa")
        form.geo_senha_var.set("secret")

        form.testar_conexao_geoalvo()
        mock_connect.assert_called_once()
        self.assertIn("sucesso", form.lbl_status_geo.cget("text").lower())

    @patch("pymysql.connect")
    @patch("tkinter.messagebox.showinfo")
    def test_testar_conexao_savic(self, mock_msg, mock_connect):
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        form = DatabaseConfigForm(parent=self.root, initial_tab="SAVIC")
        form.savic_host_var.set("191.252.53.94")
        form.savic_porta_var.set("3306")
        form.savic_banco_var.set("rccbrasilsavic")
        form.savic_usuario_var.set("rccbrasilsavic")
        form.savic_senha_var.set("b2J4earCJuNcM7")

        form.testar_conexao_savic()
        mock_connect.assert_called_once()
        self.assertIn("sucesso", form.lbl_status_savic.cget("text").lower())

    def test_selecao_inicial_aba(self):
        form_geo = DatabaseConfigForm(parent=self.root, initial_tab="MSSQL")
        self.assertEqual(form_geo.notebook.select(), str(form_geo.tab_geoalvo))

        form_savic = DatabaseConfigForm(parent=self.root, initial_tab="SAVIC")
        self.assertEqual(form_savic.notebook.select(), str(form_savic.tab_savic))


if __name__ == "__main__":
    unittest.main()
