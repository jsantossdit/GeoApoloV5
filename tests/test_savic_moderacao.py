"""Testes unitários automatizados para o módulo de Moderação de Grupos de Oração SAVIC x Apolo."""

import unittest
from unittest.mock import MagicMock, patch
from datetime import date, datetime
from decimal import Decimal
import tkinter as tk

from savic.moderacao_models import (
    EstadoDTO,
    DioceseDTO,
    CidadeDioceseDTO,
    FiltroModeracaoDTO,
    CoordenadorModeracaoDTO,
    GrupoOracaoModeracaoDTO,
    FichaFinanceiraDTO,
    EntidadeApoloComparativoDTO,
)
from savic.moderacao_repository import SavicModeracaoRepository, remover_acentos
from savic.moderacao_service import SavicModeracaoService
from savic.moderacao_view import SavicModeracaoGOView, abrir_moderacao_go_savic


class TestSavicModeracaoDTOs(unittest.TestCase):
    """Testa inicialização e integridade dos DTOs de moderação."""

    def test_estado_dto(self):
        dto = EstadoDTO(id=1, sigla="SP", nome="São Paulo")
        self.assertEqual(dto.id, 1)
        self.assertEqual(dto.sigla, "SP")
        self.assertEqual(dto.nome, "São Paulo")

    def test_diocese_dto(self):
        dto = DioceseDTO(id=10, estado_id=1, nome="Diocese de Teste", ativo=1)
        self.assertEqual(dto.id, 10)
        self.assertEqual(dto.nome, "Diocese de Teste")
        self.assertEqual(dto.ativo, 1)

    def test_cidade_diocese_dto(self):
        dto = CidadeDioceseDTO(id=100, estado_id=1, descricao="CAMPINAS", ibge=3509502, diocese_id=10)
        self.assertEqual(dto.descricao, "CAMPINAS")
        self.assertEqual(dto.ibge, 3509502)

    def test_filtro_moderacao_dto(self):
        dto = FiltroModeracaoDTO(uf="SP", diocese_nome="Diocese SP", cidade_nome="SÃO PAULO", situacao_grupo="HOMOLOGADO")
        self.assertEqual(dto.uf, "SP")
        self.assertEqual(dto.situacao_grupo, "HOMOLOGADO")
        self.assertEqual(dto.categoria_apolo, "02.001")

    def test_coordenador_moderacao_dto(self):
        dto = CoordenadorModeracaoDTO(
            id_savic="1234",
            codigo_apolo="0005555",
            coordenador="MARIA DA SILVA",
            cpf="12345678901",
            cidade="SAO PAULO",
            uf="SP"
        )
        self.assertEqual(dto.id_savic, "1234")
        self.assertEqual(dto.codigo_apolo, "0005555")
        self.assertEqual(dto.coordenador, "MARIA DA SILVA")

    def test_grupo_oracao_moderacao_dto(self):
        dto = GrupoOracaoModeracaoDTO(
            gocodigo="GO-999",
            nome_grupo="GRUPO DE ORACAO SHALOM",
            situacao_grupo="HOMOLOGADO",
            dias_reuniao="QUARTA-FEIRA",
            horario="19:30"
        )
        self.assertEqual(dto.gocodigo, "GO-999")
        self.assertEqual(dto.nome_grupo, "GRUPO DE ORACAO SHALOM")

    def test_ficha_financeira_dto(self):
        dto = FichaFinanceiraDTO(
            empresa="1.01",
            tipo_cobranca_cod="0000001",
            tipo_cobranca_nome="BOLETO",
            vr_total_doado=Decimal("1500.50")
        )
        self.assertEqual(dto.empresa, "1.01")
        self.assertEqual(dto.vr_total_doado, Decimal("1500.50"))

    def test_entidade_apolo_dto(self):
        dto = EntidadeApoloComparativoDTO(
            entcod="0001234",
            entnome="GRUPO DE ORACAO NOSSA SENHORA",
            cidade="SAO PAULO",
            uf="SP"
        )
        self.assertEqual(dto.entcod, "0001234")
        self.assertEqual(dto.entnome, "GRUPO DE ORACAO NOSSA SENHORA")


class TestSavicModeracaoRepository(unittest.TestCase):
    """Testa métodos de acesso a dados com mocks de conexão SQL Server."""

    def test_remover_acentos(self):
        self.assertEqual(remover_acentos("São Paulo"), "SAO PAULO")
        self.assertEqual(remover_acentos("Criciúma"), "CRICIUMA")
        self.assertEqual(remover_acentos(""), "")

    @patch("savic.moderacao_repository.obter_conexao_banco")
    def test_listar_estados(self, mock_obter_conn):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_obter_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur
        mock_cur.fetchall.return_value = [
            (1, "SP", "São Paulo"),
            (2, "RJ", "Rio de Janeiro"),
        ]

        repo = SavicModeracaoRepository()
        estados = repo.listar_estados()
        self.assertEqual(len(estados), 2)
        self.assertEqual(estados[0].sigla, "SP")
        self.assertEqual(estados[1].sigla, "RJ")

    @patch("savic.moderacao_repository.obter_conexao_banco")
    def test_listar_dioceses_por_estado(self, mock_obter_conn):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_obter_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur
        mock_cur.fetchall.return_value = [
            (10, 1, "Arquidiocese de Sao Paulo", 1),
            (11, 1, "Diocese de Santo Amaro", 1),
        ]

        repo = SavicModeracaoRepository()
        dioceses = repo.listar_dioceses_por_estado("SP")
        self.assertEqual(len(dioceses), 2)
        self.assertEqual(dioceses[0].nome, "Arquidiocese de Sao Paulo")

    @patch("savic.moderacao_repository.obter_conexao_banco")
    def test_buscar_geocidcod_encontrado(self, mock_obter_conn):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_obter_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = ("00088412",)

        repo = SavicModeracaoRepository()
        cod = repo.buscar_geocidcod("SAO PAULO", "SP")
        self.assertEqual(cod, "00088412")

    @patch("savic.moderacao_repository.obter_conexao_banco")
    def test_buscar_ficha_financeira(self, mock_obter_conn):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_obter_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur
        mock_cur.fetchall.return_value = [
            ("1.01", "0000001", "BOLETO", datetime(2020, 1, 1), datetime(2021, 1, 1), 350.0),
        ]

        repo = SavicModeracaoRepository()
        fichas = repo.buscar_ficha_financeira("0008633")
        self.assertEqual(len(fichas), 1)
        self.assertEqual(fichas[0].empresa, "1.01")
        self.assertEqual(fichas[0].tipo_cobranca_nome, "BOLETO")
        self.assertEqual(fichas[0].vr_total_doado, Decimal("350.0"))

    @patch("savic.moderacao_repository.obter_conexao_banco")
    def test_buscar_geoentcod_por_cpf(self, mock_obter_conn):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_obter_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = ("00012345",)

        repo = SavicModeracaoRepository()
        cod = repo.buscar_geoentcod_por_cpf("318830871")
        self.assertEqual(cod, "00012345")
        mock_cur.execute.assert_called_once()
        self.assertIn("USER_geoapolo_entidade_documentos", mock_cur.execute.call_args[0][0])



class TestSavicModeracaoService(unittest.TestCase):
    """Testa regras de negócio da moderação."""

    def setUp(self):
        self.mock_repo = MagicMock(spec=SavicModeracaoRepository)
        self.service = SavicModeracaoService(repo=self.mock_repo)

    def test_filtros_opcionais_permitem_vazio(self):
        """Verifica que UF, Diocese e Cidade podem ficar em branco para consulta por situação."""
        self.mock_repo.listar_coordenadores.return_value = [
            CoordenadorModeracaoDTO(id_savic="1", coordenador="COORDENADOR GERAL", flagexportado="Não")
        ]
        # Filtro somente com Situação HOMOLOGADO
        filtro = FiltroModeracaoDTO(uf="", diocese_nome="", cidade_nome="", situacao_grupo="HOMOLOGADO")
        geocidcod, coords, msg = self.service.filtrar_coordenadores(filtro)

        self.assertIsNone(geocidcod)
        self.assertEqual(len(coords), 1)
        self.assertIn("1 coordenador(es) encontrado(s)", msg)
        self.mock_repo.listar_coordenadores.assert_called_with(
            geocidcod=None, uf=None, diocese_nome_ou_id=None, situacao_grupo="HOMOLOGADO"
        )

    def test_filtrar_coordenadores_sucesso(self):
        self.mock_repo.buscar_geocidcod.return_value = "00088412"
        self.mock_repo.listar_coordenadores.return_value = [
            CoordenadorModeracaoDTO(id_savic="1", coordenador="COORDENADOR TESTE")
        ]

        filtro = FiltroModeracaoDTO(uf="SP", diocese_nome="Diocese SP", cidade_nome="SAO PAULO", situacao_grupo="HOMOLOGADO")
        geocidcod, coords, msg = self.service.filtrar_coordenadores(filtro)

        self.assertEqual(geocidcod, "00088412")
        self.assertEqual(len(coords), 1)
        self.assertIn("1 coordenador(es) encontrado(s)", msg)

    def test_obter_grupos_do_coordenador(self):
        self.mock_repo.buscar_grupos_por_coordenador.return_value = [
            GrupoOracaoModeracaoDTO(gocodigo="100", nome_grupo="GRUPO TESTE")
        ]
        grupos = self.service.obter_grupos_do_coordenador("1")
        self.assertEqual(len(grupos), 1)
        self.assertEqual(grupos[0].nome_grupo, "GRUPO TESTE")

    def test_obter_ficha_financeira_vazia(self):
        fichas = self.service.obter_ficha_financeira("")
        self.assertEqual(fichas, [])

        fichas_zero = self.service.obter_ficha_financeira("0")
        self.assertEqual(fichas_zero, [])

    @patch("savic.moderacao_service.geoapolo_configcod")
    def test_exportar_entidades_selecionadas(self, mock_configcod):
        mock_configcod.side_effect = ["00001001", "00001002"]
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur
        self.mock_repo._get_conn.return_value = mock_conn

        # Simula coordenador não existente na base de documentos
        self.mock_repo.buscar_geoentcod_por_cpf.return_value = None
        self.mock_repo.buscar_geocidcod.return_value = "00088412"
        # Simula grupo não existente na base
        self.mock_repo.buscar_geoentcod_por_nome_e_cidade.return_value = None

        coordenadores = [
            CoordenadorModeracaoDTO(
                id_savic="99",
                coordenador="JOAO SILVA",
                cpf="11122233344",
                cidade="SAO PAULO",
                uf="SP"
            )
        ]
        grupos = [
            GrupoOracaoModeracaoDTO(
                gocodigo="500",
                nome_grupo="GRUPO DE ORACAO RENASCER",
                geocidcod="00088412"
            )
        ]

        resultado = self.service.exportar_entidades_selecionadas(coordenadores, grupos)

        self.assertTrue(resultado.sucesso)
        self.assertEqual(resultado.total_coordenadores_inseridos, 1)
        self.assertEqual(resultado.total_grupos_inseridos, 1)
        self.assertEqual(resultado.total_categorias_vinculadas, 4)

        # Verifica chamadas de categorias: 02.001.0006 e 08.009 para coordenador e 02.001 e 08.009 para grupo
        self.mock_repo.garantir_categoria_entidade.assert_any_call("00001001", "02.001.0006")
        self.mock_repo.garantir_categoria_entidade.assert_any_call("00001001", "08.009")
        self.mock_repo.garantir_categoria_entidade.assert_any_call("00001002", "02.001")
        self.mock_repo.garantir_categoria_entidade.assert_any_call("00001002", "08.009")

        # Verifica marcação de flagexportado
        self.mock_repo.marcar_coordenador_exportado.assert_called_with("99", "00001001")
        self.mock_repo.marcar_grupo_exportado.assert_called_with("500", "00001002")

        self.assertEqual(coordenadores[0].flagexportado, "Sim")
        self.assertEqual(grupos[0].flagexportado, "Sim")

    @patch("savic.moderacao_service.geoapolo_configcod")
    def test_exportar_entidades_selecionadas_oito_tabelas(self, mock_configcod):
        """Verifica a alimentação completa das 8 tabelas na exportação."""
        mock_configcod.side_effect = ["00002001", "00002002"]
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur
        self.mock_repo._get_conn.return_value = mock_conn

        self.mock_repo.buscar_geoentcod_por_cpf.return_value = None
        self.mock_repo.buscar_geocidcod.return_value = "00088412"
        self.mock_repo.buscar_geoentcod_por_nome_e_cidade.return_value = None

        coordenador = CoordenadorModeracaoDTO(
            id_savic="101",
            coordenador="JULIO DIAS DE LIMA",
            cpf="31883050871",
            rg="12345678",
            orgao_emissor="SSP/SP",
            celular="11999998888",
            telefone_fixo="1133334444",
            email="julio@dias.com",
            endereco="RUA DAS FLORES",
            numero="100",
            complemento="APTO 12",
            bairro="CENTRO",
            cep="01001000",
            cidade="SAO PAULO",
            uf="SP",
            data_inicio=date(2025, 1, 1),
            data_fim=date(2026, 12, 31)
        )
        grupo = GrupoOracaoModeracaoDTO(
            gocodigo="901",
            nome_grupo="GRUPO DE ORACAO SAGRADO CORACAO",
            local_reuniao="SALAO PAROQUIAL",
            tipo_local="PAROQUIA",
            geocidcod="00088412",
            cadastroid_coordenador="101"
        )

        resultado = self.service.exportar_entidades_selecionadas([coordenador], [grupo])

        self.assertTrue(resultado.sucesso)
        self.assertEqual(len(resultado.erros), 0)

        # Coleta todas as instruções SQL executadas
        sqls_executados = " ".join(call[0][0] for call in mock_cur.execute.call_args_list if call[0])

        # Verifica presença das 8 tabelas
        self.assertIn("USER_geoapolo_entidade", sqls_executados)
        self.assertIn("USER_geoapolo_entidade_documentos", sqls_executados)
        self.assertIn("USER_geoapolo_entidade_comunicacao", sqls_executados)
        self.assertIn("USER_geoapolo_entidade_webcontato", sqls_executados)
        self.assertIn("USER_geoapolo_entidade_endereco_adicionais", sqls_executados)
        self.assertIn("USER_geoapolo_entidade_ativecon", sqls_executados)
        self.assertIn("USER_geoapolo_entidade_contato", sqls_executados)

        # Categorias
        self.mock_repo.garantir_categoria_entidade.assert_any_call("00002001", "02.001.0006")
        self.mock_repo.garantir_categoria_entidade.assert_any_call("00002001", "08.009")
        self.mock_repo.garantir_categoria_entidade.assert_any_call("00002002", "02.001")
        self.mock_repo.garantir_categoria_entidade.assert_any_call("00002002", "08.009")

        # Origens SAVIC '013.007'
        self.mock_repo.garantir_origem_entidade.assert_any_call("00002001", "013.007", conn=mock_conn)
        self.mock_repo.garantir_origem_entidade.assert_any_call("00002002", "013.007", conn=mock_conn)

    @patch("savic.moderacao_service.geoapolo_configcod")
    def test_exportar_entidade_existente_por_cpf_atualiza_campos_padrao(self, mock_configcod):
        """Testa que quando entidade já existe por CPF na tabela de documentos, é feito UPDATE com campos padrão."""
        mock_configcod.side_effect = ["00009999"]
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur
        self.mock_repo._get_conn.return_value = mock_conn

        # Coordenador encontrado por CPF em USER_geoapolo_entidade_documentos
        self.mock_repo.buscar_geoentcod_por_cpf.return_value = "00055555"
        self.mock_repo.buscar_geocidcod.return_value = "00088412"

        def mock_fetchone():
            last_sql = mock_cur.execute.call_args[0][0] if mock_cur.execute.call_args else ""
            if "FROM USER_geoapolo_entidade" in last_sql:
                return ("00055555",)
            return None
        mock_cur.fetchone.side_effect = mock_fetchone

        coord = CoordenadorModeracaoDTO(
            id_savic="200",
            coordenador="JULIO DIAS DE LIMA",
            cpf="318830871",
            cidade="SAO PAULO",
            uf="SP"
        )
        grupo = GrupoOracaoModeracaoDTO(
            gocodigo="999",
            nome_grupo="GRUPO SAO JOSE",
            geocidcod="00088412",
            cadastroid_coordenador="200"
        )

        resultado = self.service.exportar_entidades_selecionadas([coord], [grupo])

        self.assertTrue(resultado.sucesso)
        self.assertEqual(resultado.total_coordenadores_atualizados, 1)
        self.assertEqual(resultado.total_coordenadores_inseridos, 0)

        # Verifica se o UPDATE em USER_geoapolo_entidade contém tratamento de campos padrão
        sqls_executados = [call[0][0] for call in mock_cur.execute.call_args_list if call[0]]
        update_coordenador_sql = [s for s in sqls_executados if "UPDATE USER_geoapolo_entidade" in s]
        self.assertTrue(len(update_coordenador_sql) > 0)
        self.assertIn("tipolograd = ISNULL(NULLIF(tipolograd, 0), 1)", update_coordenador_sql[0])
        self.assertIn("geotipofj = ISNULL(NULLIF(geotipofj, ''), 'Física')", update_coordenador_sql[0])
        self.assertIn("geoentloccobrancaomesmo = ISNULL(NULLIF(geoentloccobrancaomesmo, ''), 'Sim')", update_coordenador_sql[0])



class TestSavicModeracaoView(unittest.TestCase):
    """Testa instanciação da tela Tkinter de moderação."""

    def test_abrir_moderacao_go_savic(self):
        root = tk.Tk()
        root.withdraw()
        try:
            with patch("savic.moderacao_service.SavicModeracaoService.obter_estados", return_value=[]):
                view = abrir_moderacao_go_savic(parent=root)
                self.assertIsInstance(view, SavicModeracaoGOView)
                view.destroy()
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()

