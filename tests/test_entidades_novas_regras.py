"""
Testes Unitários e de Integração para as Novas Regras de Negócio:
1. Filtro exato por categoria (sem níveis abaixo)
2. Mapeamento da região por UF para todas as 27 UFs
3. Alerta de contribuição R$ 0,00 e envio de DataFundacao (aniversário)
4. Categoria 08.009 para Grupos de Oração e Coordenadores
5. Código do tipo de cobrança não-nulo com fallback '0000027'
"""

import unittest
from unittest.mock import MagicMock, patch
from datetime import date, datetime

from entidades.models import EntidadeFiltro
from entidades.repository import EntidadeRepository
from entidades.service import EntidadeService


class TestRegra1FiltroExatoCategoria(unittest.TestCase):
    """Testa que a busca por categoria realiza correspondência exata sem trazer níveis abaixo."""

    def setUp(self):
        self.repo = EntidadeRepository.__new__(EntidadeRepository)

    def test_consultar_lista_alvo_categoria_exata(self):
        with patch.object(self.repo, "_get_cursor") as mock_cursor:
            cursor = MagicMock()
            cursor.description = [("entcod",), ("entnome",)]
            cursor.fetchall.return_value = []
            mock_cursor.return_value = cursor

            filtro = EntidadeFiltro(base_dados="Alvo", categoria_busca="02.001")
            self.repo.consultar_lista(filtro)
            sql_executado = cursor.execute.call_args[0][0]
            params = cursor.execute.call_args[0][1]

            self.assertIn("EXISTS (SELECT 1 FROM ENT_CATEG ec WITH (NOLOCK)         WHERE ec.entcod = e.entcod AND ec.categcodestr = ?)", sql_executado)
            self.assertNotIn("ec.categcodestr LIKE", sql_executado)
            self.assertIn("02.001", params)

    def test_consultar_lista_alvo_categoria_com_descricao_extrai_codigo(self):
        with patch.object(self.repo, "_get_cursor") as mock_cursor:
            cursor = MagicMock()
            cursor.description = [("entcod",), ("entnome",)]
            cursor.fetchall.return_value = []
            mock_cursor.return_value = cursor

            filtro = EntidadeFiltro(base_dados="Alvo", categoria_busca="02.001 - Grupo de Oração")
            self.repo.consultar_lista(filtro)
            params = cursor.execute.call_args[0][1]
            self.assertIn("02.001", params)

    def test_consultar_lista_geoapolo_categoria_exata(self):
        with patch.object(self.repo, "_get_cursor") as mock_cursor:
            cursor = MagicMock()
            cursor.description = [("geoentcod",), ("geoentnome",)]
            cursor.fetchall.return_value = []
            mock_cursor.return_value = cursor

            filtro = EntidadeFiltro(base_dados="GeoApolo", categoria_busca="02.001.0006")
            self.repo.consultar_lista(filtro)
            sql_executado = cursor.execute.call_args[0][0]
            params = cursor.execute.call_args[0][1]

            self.assertIn("EXISTS (SELECT 1 FROM USER_geoapolo_entcateg uec WITH (NOLOCK)         WHERE uec.geoentcod = e.geoentcod AND uec.geocategcodestr = ?)", sql_executado)
            self.assertNotIn("uec.geocategcodestr LIKE", sql_executado)
            self.assertIn("02.001.0006", params)


class TestRegra2MapeamentoRegiaoPorUF(unittest.TestCase):
    """Testa a validação das 27 UFs para as 5 regiões correspondentes."""

    def setUp(self):
        self.repo = EntidadeRepository.__new__(EntidadeRepository)
        self.mock_cursor = MagicMock()
        self.mock_cursor.fetchone.return_value = None  # Testa fallback verificado

    def test_todas_as_27_ufs_mapeadas_corretamente(self):
        with patch.object(self.repo, "_get_cursor", return_value=self.mock_cursor):
            # 1. Sul: RS, SC, PR -> '1'
            for uf in ["RS", "SC", "PR", "rs", "sc", "pr"]:
                cod = self.repo.obter_codigo_regiao_por_uf(uf)
                self.assertEqual(cod, "1", f"Falha para UF Sul: {uf}")

            # 2. Sudeste: SP, MG, RJ, ES -> '5'
            for uf in ["SP", "MG", "RJ", "ES", "sp", "mg", "rj", "es"]:
                cod = self.repo.obter_codigo_regiao_por_uf(uf)
                self.assertEqual(cod, "5", f"Falha para UF Sudeste: {uf}")

            # 3. Centro-Oeste: MS, MT, GO, TO, DF -> '3'
            for uf in ["MS", "MT", "GO", "TO", "DF", "ms", "mt", "go", "to", "df"]:
                cod = self.repo.obter_codigo_regiao_por_uf(uf)
                self.assertEqual(cod, "3", f"Falha para UF Centro-Oeste: {uf}")

            # 4. Norte: AM, RO, PA, AC, AP, RR -> '4'
            for uf in ["AM", "RO", "PA", "AC", "AP", "RR", "am", "ro", "pa", "ac", "ap", "rr"]:
                cod = self.repo.obter_codigo_regiao_por_uf(uf)
                self.assertEqual(cod, "4", f"Falha para UF Norte: {uf}")

            # 5. Nordeste: AL, BA, CE, MA, PB, PE, PI, RN, SE -> '2'
            for uf in ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE",
                       "al", "ba", "ce", "ma", "pb", "pe", "pi", "rn", "se"]:
                cod = self.repo.obter_codigo_regiao_por_uf(uf)
                self.assertEqual(cod, "2", f"Falha para UF Nordeste: {uf}")

    def test_uf_invalida_retorna_none(self):
        with patch.object(self.repo, "_get_cursor", return_value=self.mock_cursor):
            self.assertIsNone(self.repo.obter_codigo_regiao_por_uf(""))
            self.assertIsNone(self.repo.obter_codigo_regiao_por_uf("XX"))
            self.assertIsNone(self.repo.obter_codigo_regiao_por_uf(None))

    def test_payload_alvo_atribui_codigo_regiao_pela_uf(self):
        mock_repo = MagicMock(spec=EntidadeRepository)
        mock_repo.carregar_dados_completos_entidade_geoapolo.return_value = {
            "geoentcod": "123",
            "geoentnome": "Entidade SP",
            "ufsigla": "SP",
            "categcodestr": "01.001",
        }
        mock_repo.obter_cpf_rg_documentos.return_value = ("", "")
        mock_repo.listar_categorias_entidade.return_value = []
        mock_repo.listar_telefones_entidade.return_value = []
        mock_repo.listar_webcontatos_entidade.return_value = []
        mock_repo.carregar_contatos_entidade.return_value = []
        mock_repo.obter_codigo_regiao_por_uf.side_effect = lambda uf: "5" if uf == "SP" else "1"

        service = EntidadeService(mock_repo)
        payload = service.montar_payload_entidade_alvo("123", modo="php")
        self.assertEqual(payload.get("CodigoRegiao"), "5")


class TestRegra3AlertaValorZeroEDataAniversario(unittest.TestCase):
    """Testa o envio de data de aniversário/fundação e campos de contribuição."""

    def test_data_aniversario_geoentdataanivfund_enviada_formato_iso(self):
        mock_repo = MagicMock(spec=EntidadeRepository)
        mock_repo.carregar_dados_completos_entidade_geoapolo.return_value = {
            "geoentcod": "123",
            "geoentnome": "Entidade Aniv",
            "geoentdataanivfund": date(1985, 7, 20),
            "categcodestr": "01.001",
        }
        mock_repo.obter_cpf_rg_documentos.return_value = ("", "")
        mock_repo.listar_categorias_entidade.return_value = []
        mock_repo.listar_telefones_entidade.return_value = []
        mock_repo.listar_webcontatos_entidade.return_value = []
        mock_repo.carregar_contatos_entidade.return_value = []
        mock_repo.obter_codigo_regiao_por_uf.return_value = None

        service = EntidadeService(mock_repo)
        payload = service.montar_payload_entidade_alvo("123", modo="php")
        self.assertEqual(payload.get("DataFundacao"), "1985-07-20T00:00:00.000Z")

    def test_data_aniversario_entdataanivfund_fallback(self):
        mock_repo = MagicMock(spec=EntidadeRepository)
        mock_repo.carregar_dados_completos_entidade_geoapolo.return_value = {
            "geoentcod": "123",
            "geoentnome": "Entidade Aniv",
            "entdataanivfund": "1990-12-25",
            "categcodestr": "01.001",
        }
        mock_repo.obter_cpf_rg_documentos.return_value = ("", "")
        mock_repo.listar_categorias_entidade.return_value = []
        mock_repo.listar_telefones_entidade.return_value = []
        mock_repo.listar_webcontatos_entidade.return_value = []
        mock_repo.carregar_contatos_entidade.return_value = []
        mock_repo.obter_codigo_regiao_por_uf.return_value = None

        service = EntidadeService(mock_repo)
        payload = service.montar_payload_entidade_alvo("123", modo="php")
        self.assertEqual(payload.get("DataFundacao"), "1990-12-25T00:00:00.000Z")

    def test_data_aniversario_vazia_fica_none(self):
        mock_repo = MagicMock(spec=EntidadeRepository)
        mock_repo.carregar_dados_completos_entidade_geoapolo.return_value = {
            "geoentcod": "123",
            "geoentnome": "Entidade Sem Data",
            "categcodestr": "01.001",
        }
        mock_repo.obter_cpf_rg_documentos.return_value = ("", "")
        mock_repo.listar_categorias_entidade.return_value = []
        mock_repo.listar_telefones_entidade.return_value = []
        mock_repo.listar_webcontatos_entidade.return_value = []
        mock_repo.carregar_contatos_entidade.return_value = []
        mock_repo.obter_codigo_regiao_por_uf.return_value = None

        service = EntidadeService(mock_repo)
        payload = service.montar_payload_entidade_alvo("123", modo="php")
        self.assertIsNone(payload.get("DataFundacao"))


class TestRegra4Categoria08009ParaGOParaLoja(unittest.TestCase):
    """Testa a inclusão obrigatória da categoria '08.009' para Grupos de Oração e Coordenadores."""

    def setUp(self):
        self.mock_repo = MagicMock(spec=EntidadeRepository)
        self.mock_repo.obter_cpf_rg_documentos.return_value = ("", "")
        self.mock_repo.listar_telefones_entidade.return_value = []
        self.mock_repo.listar_webcontatos_entidade.return_value = []
        self.mock_repo.carregar_contatos_entidade.return_value = []
        self.mock_repo.obter_codigo_regiao_por_uf.return_value = None
        self.service = EntidadeService(self.mock_repo)

    def test_grupo_de_oracao_adiciona_08009(self):
        self.mock_repo.carregar_dados_completos_entidade_geoapolo.return_value = {
            "geoentcod": "123",
            "geoentnome": "Grupo de Oração São José",
            "categcodestr": "02.001",
        }
        self.mock_repo.listar_categorias_entidade.return_value = [{"Codigo": "02.001"}]

        payload = self.service.montar_payload_entidade_alvo("123", modo="php")
        codigos_cats = [c["Codigo"] for c in payload.get("Categorias", [])]
        self.assertIn("02.001", codigos_cats)
        self.assertIn("08.009", codigos_cats)

    def test_coordenador_adiciona_08009(self):
        self.mock_repo.carregar_dados_completos_entidade_geoapolo.return_value = {
            "geoentcod": "456",
            "geoentnome": "Coordenador João",
            "categcodestr": "02.001.0006",
        }
        self.mock_repo.listar_categorias_entidade.return_value = [{"Codigo": "02.001.0006"}]

        payload = self.service.montar_payload_entidade_alvo("456", modo="php")
        codigos_cats = [c["Codigo"] for c in payload.get("Categorias", [])]
        self.assertIn("02.001.0006", codigos_cats)
        self.assertIn("08.009", codigos_cats)

    def test_entidade_comum_nao_adiciona_08009(self):
        self.mock_repo.carregar_dados_completos_entidade_geoapolo.return_value = {
            "geoentcod": "789",
            "geoentnome": "Fornecedor ABC",
            "categcodestr": "01.001",
        }
        self.mock_repo.listar_categorias_entidade.return_value = [{"Codigo": "01.001"}]

        payload = self.service.montar_payload_entidade_alvo("789", modo="php")
        codigos_cats = [c["Codigo"] for c in payload.get("Categorias", [])]
        self.assertNotIn("08.009", codigos_cats)

    def test_grupo_que_ja_possui_08009_nao_duplica(self):
        self.mock_repo.carregar_dados_completos_entidade_geoapolo.return_value = {
            "geoentcod": "123",
            "geoentnome": "Grupo de Oração",
            "categcodestr": "02.001,08.009",
        }
        self.mock_repo.listar_categorias_entidade.return_value = [
            {"Codigo": "02.001"},
            {"Codigo": "08.009"}
        ]

        payload = self.service.montar_payload_entidade_alvo("123", modo="php")
        codigos_cats = [c["Codigo"] for c in payload.get("Categorias", [])]
        self.assertEqual(codigos_cats.count("08.009"), 1)


class TestRegra5CodigoTipoCobrancaNaoNulo(unittest.TestCase):
    """Testa que CodigoTipoCobranca nunca é enviado nulo/vazio, usando fallback '0000027'."""

    def setUp(self):
        self.mock_repo = MagicMock(spec=EntidadeRepository)
        self.mock_repo.obter_cpf_rg_documentos.return_value = ("", "")
        self.mock_repo.listar_telefones_entidade.return_value = []
        self.mock_repo.listar_webcontatos_entidade.return_value = []
        self.mock_repo.carregar_contatos_entidade.return_value = []
        self.mock_repo.listar_categorias_entidade.return_value = [{"Codigo": "01.001"}]
        self.mock_repo.obter_codigo_regiao_por_uf.return_value = None
        self.service = EntidadeService(self.mock_repo)

    def test_cobranca_vazia_usa_fallback_0000027(self):
        self.mock_repo.carregar_dados_completos_entidade_geoapolo.return_value = {
            "geoentcod": "123",
            "geoentnome": "Entidade Teste",
            "geotipocobcod": "",
            "tipocobcod": None,
        }
        payload = self.service.montar_payload_entidade_alvo("123", modo="php")
        self.assertEqual(payload.get("CodigoTipoCobranca"), "0000027")

    def test_cobranca_sem_campo_usa_fallback_0000027(self):
        self.mock_repo.carregar_dados_completos_entidade_geoapolo.return_value = {
            "geoentcod": "123",
            "geoentnome": "Entidade Teste",
        }
        payload = self.service.montar_payload_entidade_alvo("123", modo="php")
        self.assertEqual(payload.get("CodigoTipoCobranca"), "0000027")

    def test_cobranca_preenchida_mantem_valor(self):
        self.mock_repo.carregar_dados_completos_entidade_geoapolo.return_value = {
            "geoentcod": "123",
            "geoentnome": "Entidade Teste",
            "geotipocobcod": "0000015",
        }
        payload = self.service.montar_payload_entidade_alvo("123", modo="php")
        self.assertEqual(payload.get("CodigoTipoCobranca"), "0000015")

    def test_modo_delphi_tambem_respeita_todas_as_regras(self):
        self.mock_repo.carregar_dados_completos_entidade_geoapolo.return_value = {
            "geoentcod": "123",
            "geoentnome": "Entidade Teste",
            "ufsigla": "MG",
            "categcodestr": "02.001",
            "geotipocobcod": "",
            "geoentdataanivfund": date(1980, 1, 10),
        }
        self.mock_repo.listar_categorias_entidade.return_value = [{"Codigo": "02.001"}]
        self.mock_repo.obter_codigo_regiao_por_uf.side_effect = lambda uf: "5" if uf == "MG" else "1"

        payload = self.service.montar_payload_entidade_alvo("123", modo="delphi")
        self.assertEqual(payload.get("CodigoTipoCobranca"), "0000027")
        self.assertEqual(payload.get("CodigoRegiao"), "5")
        self.assertEqual(payload.get("DataFundacao"), "1980-01-10T00:00:00.000Z")
        codigos_cats = [c["Codigo"] for c in payload.get("Categorias", [])]
        self.assertIn("02.001", codigos_cats)
        self.assertIn("08.009", codigos_cats)


if __name__ == "__main__":
    unittest.main()
