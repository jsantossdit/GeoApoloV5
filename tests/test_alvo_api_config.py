"""
Testes Unitários para o Módulo de Configuração da API Alvo (Riosoft)
e Integração com o Esquema PHP (IntegracaoPHP.php).
GeoApolo V5
"""

import os
import unittest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch
import tkinter as tk

from configuracoes.alvo_api_config import (
    AlvoAPIConfig,
    parse_data_br,
    validar_status_token,
    carregar_configuracao_alvo,
    salvar_configuracao_alvo,
    testar_comunicacao_alvo,
)
from configuracoes.alvo_api_view import FrmConfiguracaoAPIAlvo, abrir_configuracao_api_alvo
from entidades.service import EntidadeService
from entidades.repository import EntidadeRepository
from entidades.api_client import AlvoAPIClient


class TestAlvoAPIConfigDataclass(unittest.TestCase):
    """Testes de instanciação e serialização do AlvoAPIConfig."""

    def test_valores_padrao(self):
        cfg = AlvoAPIConfig()
        self.assertEqual(cfg.token, "")
        self.assertEqual(cfg.data_inicial, "")
        self.assertEqual(cfg.data_final, "")
        self.assertEqual(cfg.base_url, "https://alvo.rccbrasil.org.br/api")
        self.assertEqual(cfg.timeout, 45)
        self.assertTrue(cfg.ativo)
        self.assertEqual(cfg.ambiente, "Produção")

    def test_to_dict_e_from_dict(self):
        cfg = AlvoAPIConfig(
            token="TOKEN_XYZ_12345",
            data_inicial="01/01/2026",
            data_final="31/12/2026",
            base_url="https://api.homologacao.alvo.com.br",
            timeout=60,
            ativo=True,
            ambiente="Homologação",
            usuario_padrao="operador_ti",
        )
        d = cfg.to_dict()
        self.assertEqual(d["token"], "TOKEN_XYZ_12345")
        self.assertEqual(d["data_inicial"], "01/01/2026")
        self.assertEqual(d["data_final"], "31/12/2026")
        self.assertEqual(d["timeout"], 60)

        cfg_reconst = AlvoAPIConfig.from_dict(d)
        self.assertEqual(cfg_reconst.token, cfg.token)
        self.assertEqual(cfg_reconst.data_inicial, cfg.data_inicial)
        self.assertEqual(cfg_reconst.data_final, cfg.data_final)
        self.assertEqual(cfg_reconst.base_url, cfg.base_url)
        self.assertEqual(cfg_reconst.timeout, cfg.timeout)
        self.assertEqual(cfg_reconst.ambiente, cfg.ambiente)
        self.assertEqual(cfg_reconst.usuario_padrao, cfg.usuario_padrao)

    def test_from_dict_vazio_ou_invalido(self):
        cfg1 = AlvoAPIConfig.from_dict({})
        self.assertEqual(cfg1.token, "")
        cfg2 = AlvoAPIConfig.from_dict(None)
        self.assertEqual(cfg2.token, "")


class TestParseDataBR(unittest.TestCase):
    """Testes para o conversor de datas brasileiras DD/MM/AAAA."""

    def test_parse_data_valida_br(self):
        dt = parse_data_br("22/09/2026")
        self.assertEqual(dt, date(2026, 9, 22))

        dt_ano_bissexto = parse_data_br("29/02/2024")
        self.assertEqual(dt_ano_bissexto, date(2024, 2, 29))

    def test_parse_data_valida_iso(self):
        dt = parse_data_br("2026-09-22")
        self.assertEqual(dt, date(2026, 9, 22))

    def test_parse_data_invalida(self):
        self.assertIsNone(parse_data_br("31/02/2026"))  # Data impossível
        self.assertIsNone(parse_data_br("invalida"))
        self.assertIsNone(parse_data_br(""))
        self.assertIsNone(parse_data_br(None))


class TestValidarStatusToken(unittest.TestCase):
    """Testes da lógica de avaliação de vigência e validade do token."""

    def test_sem_token(self):
        cfg = AlvoAPIConfig(token="")
        status, msg, valido = validar_status_token(cfg)
        self.assertEqual(status, "SEM_TOKEN")
        self.assertFalse(valido)

    def test_desativado(self):
        cfg = AlvoAPIConfig(token="TOKEN_EXISTE", ativo=False)
        status, msg, valido = validar_status_token(cfg)
        self.assertEqual(status, "DESATIVADO")
        self.assertFalse(valido)

    def test_ativo_sem_datas(self):
        cfg = AlvoAPIConfig(token="TOKEN_PERMANENTE_SEM_DATAS")
        status, msg, valido = validar_status_token(cfg)
        self.assertEqual(status, "ATIVO_SEM_DATAS")
        self.assertTrue(valido)

    def test_token_ativo_e_vigente(self):
        hoje = date.today()
        dt_ini = (hoje - timedelta(days=30)).strftime("%d/%m/%Y")
        dt_fim = (hoje + timedelta(days=60)).strftime("%d/%m/%Y")

        cfg = AlvoAPIConfig(token="TOKEN_VIGENTE", data_inicial=dt_ini, data_final=dt_fim)
        status, msg, valido = validar_status_token(cfg)
        self.assertEqual(status, "ATIVO")
        self.assertTrue(valido)
        self.assertIn("restam", msg)

    def test_token_expirando_em_breve(self):
        hoje = date.today()
        dt_ini = (hoje - timedelta(days=30)).strftime("%d/%m/%Y")
        dt_fim = (hoje + timedelta(days=7)).strftime("%d/%m/%Y")

        cfg = AlvoAPIConfig(token="TOKEN_QUASE_EXPIRANDO", data_inicial=dt_ini, data_final=dt_fim)
        status, msg, valido = validar_status_token(cfg)
        self.assertEqual(status, "EXPIRANDO")
        self.assertTrue(valido)
        self.assertIn("restam 7 dia(s)", msg)

    def test_token_expirado(self):
        hoje = date.today()
        dt_ini = (hoje - timedelta(days=60)).strftime("%d/%m/%Y")
        dt_fim = (hoje - timedelta(days=5)).strftime("%d/%m/%Y")

        cfg = AlvoAPIConfig(token="TOKEN_JA_EXPIRADO", data_inicial=dt_ini, data_final=dt_fim)
        status, msg, valido = validar_status_token(cfg)
        self.assertEqual(status, "EXPIRADO")
        self.assertFalse(valido)
        self.assertIn("expirado", msg.lower())

    def test_token_futuro(self):
        hoje = date.today()
        dt_ini = (hoje + timedelta(days=10)).strftime("%d/%m/%Y")
        dt_fim = (hoje + timedelta(days=70)).strftime("%d/%m/%Y")

        cfg = AlvoAPIConfig(token="TOKEN_FUTURO", data_inicial=dt_ini, data_final=dt_fim)
        status, msg, valido = validar_status_token(cfg)
        self.assertEqual(status, "FUTURO")
        self.assertFalse(valido)
        self.assertIn("ainda não vigente", msg.lower())


class TestPersistenciaConfigAlvo(unittest.TestCase):
    """Testes de persistência em arquivo de configuração."""

    @patch("config_banco.ConfigManager")
    @patch("configuracoes.alvo_api_config._obter_caminhos_arquivo_config")
    def test_salvar_e_carregar_roundtrip(self, mock_caminhos, mock_cm):
        import tempfile
        from pathlib import Path

        mock_cm.return_value.load_settings.return_value = {}
        temp_dir = tempfile.TemporaryDirectory()
        temp_file = Path(temp_dir.name) / "teste_alvo_api_config.json"
        mock_caminhos.return_value = [temp_file]

        cfg_original = AlvoAPIConfig(
            token="MEU_TOKEN_SECRETO_TESTE",
            data_inicial="15/03/2026",
            data_final="15/03/2027",
            base_url="https://alvo.rccbrasil.org.br/api",
            timeout=30,
            ativo=True,
            ambiente="Produção",
        )

        sucesso = salvar_configuracao_alvo(cfg_original)
        self.assertTrue(sucesso)
        self.assertTrue(temp_file.exists())

        cfg_carregado = carregar_configuracao_alvo()
        self.assertEqual(cfg_carregado.token, "MEU_TOKEN_SECRETO_TESTE")
        self.assertEqual(cfg_carregado.data_inicial, "15/03/2026")
        self.assertEqual(cfg_carregado.data_final, "15/03/2027")

        temp_dir.cleanup()


class TestPayloadPHPIntegration(unittest.TestCase):
    """Testes para garantir conformidade do payload gerado com IntegracaoPHP.php."""

    def setUp(self):
        self.mock_repo = MagicMock(spec=EntidadeRepository)
        self.service = EntidadeService(self.mock_repo)

        # Mock de dados simulando cadastro no banco GeoApolo
        self.mock_repo.carregar_dados_completos_entidade_geoapolo.return_value = {
            "geoentcod": "12345",
            "entcod": "",
            "geoentnome": "Carlos da Silva",
            "entnome": "Carlos da Silva",
            "entcpfcgc": "12345678909",
            "entrgie": "MG-998877",
            "entdataanivfund": "1985-05-15",
            "entgenero": "MASCULINO",
            "geoentender": "Av. Brasil",
            "geoenderno": "1000",
            "geoentendercomp": "Bloco B",
            "geoentbair": "Jardim América",
            "geoentcep": "37130000",
            "cidcod": "3101607",
            "enttipofj": "F",
            "USERValor_Contribuicao": "75.50",
            "bancocod": "001",
            "agenciacod": "1234-5",
            "contacorrente": "98765-4",
            "tipocobcod": "01",
            "entobservacoes": "",
        }
        self.mock_repo.obter_cpf_rg_documentos.return_value = ("12345678909", "MG-998877")
        self.mock_repo.listar_categorias_entidade.return_value = [
            {"categcodestr": "CAT01"},
            {"categcodestr": "CAT02"},
        ]
        self.mock_repo.listar_telefones_entidade.return_value = [
            {
                "geotipotelefone": "CEL",
                "geotelefoneddd": "35",
                "geotelefonenumero": "999887766",
            }
        ]
        self.mock_repo.listar_webcontatos_entidade.return_value = [
            {"email": "carlos@exemplo.com.br"}
        ]

    def test_montar_payload_modo_php_estrutura_e_campos(self):
        """Verifica se todas as 21 propriedades do IntegracaoPHP.php estão presentes e limpas."""
        payload = self.service.montar_payload_entidade_alvo("12345", operacao="I", modo="php")

        # Verifica campos essenciais da DTO PHP
        self.assertEqual(payload["Operacao"], "I")
        self.assertNotIn("Codigo", payload)  # Inserção não envia Código (null filtrado)
        self.assertEqual(payload["TipoFisicaJuridica"], "Física")
        self.assertEqual(payload["CPFCNPJ"], "12345678909")
        self.assertEqual(payload["Nome"], "Carlos da Silva")
        self.assertIn("1985-05-15", payload["DataFundacao"])
        self.assertEqual(payload["Genero"], "M")
        self.assertEqual(payload["Endereco"], "Av. Brasil")
        self.assertEqual(payload["NumeroEndereco"], "1000")
        self.assertEqual(payload["ComplementoEndereco"], "Bloco B")
        self.assertEqual(payload["Bairro"], "Jardim América")
        self.assertEqual(payload["Cep"], "37130000")
        self.assertEqual(payload["CodigoCidade"], "3101607")
        self.assertEqual(payload["ValorContribuicao"], 75.50)
        self.assertEqual(payload["NumeroBanco"], "001")
        self.assertEqual(payload["NumeroAgBancaria"], "1234-5")
        self.assertEqual(payload["NumeroContaCorrente"], "98765-4")
        self.assertEqual(payload["ComunicacaoEmail"], "Sim")
        self.assertEqual(payload["CodigoTipoCobranca"], "01")
        self.assertEqual(len(payload["Categorias"]), 2)
        self.assertEqual(len(payload["Telefones"]), 1)
        self.assertEqual(len(payload["Emails"]), 1)

        # Garante ausência de sub-arrays dummy problemáticos do Delphi
        self.assertNotIn("Enderecos", payload)
        self.assertNotIn("Contatos", payload)
        self.assertNotIn("Vendedores", payload)
        self.assertNotIn("Documentos", payload)

        # Garante ausência de strings literais "null"
        for k, v in payload.items():
            self.assertNotEqual(v, "null", f"Campo {k} não deve ser a string literal 'null'")
            self.assertIsNotNone(v, f"Campo {k} não deve ter valor None")

    def test_montar_payload_tipo_pessoa_juridica(self):
        """Verifica se pessoa jurídica é identificada por CNPJ longo ou flag J."""
        self.mock_repo.carregar_dados_completos_entidade_geoapolo.return_value.update({
            "entcpfcgc": "12345678000199",
            "enttipofj": "J",
        })
        self.mock_repo.obter_cpf_rg_documentos.return_value = ("12345678000199", "ISENTO")

        payload = self.service.montar_payload_entidade_alvo("12345", operacao="I", modo="php")
        self.assertEqual(payload["TipoFisicaJuridica"], "Jurídica")

    def test_montar_payload_modo_delphi_retrocompatibilidade(self):
        """Verifica se o modo='delphi' mantém o formato original legado."""
        payload = self.service.montar_payload_entidade_alvo("12345", operacao="I", modo="delphi")
        self.assertIn("Enderecos", payload)
        self.assertIn("Contatos", payload)
        self.assertIn("CodigoAtivEconomica", payload)

    def test_montar_payload_normalizacao_genero_alvo(self):
        """Garante que o campo Genero nunca exceda 1 caractere ('M', 'F', 'N') para a API Alvo."""
        # Teste com FEMININO
        self.mock_repo.carregar_dados_completos_entidade_geoapolo.return_value["entgenero"] = "FEMININO"
        p_fem = self.service.montar_payload_entidade_alvo("12345", modo="php")
        self.assertEqual(p_fem["Genero"], "F")

        # Teste com MASCULINO
        self.mock_repo.carregar_dados_completos_entidade_geoapolo.return_value["entgenero"] = "MASCULINO"
        p_masc = self.service.montar_payload_entidade_alvo("12345", modo="php")
        self.assertEqual(p_masc["Genero"], "M")

        # Teste com NENHUM
        self.mock_repo.carregar_dados_completos_entidade_geoapolo.return_value["entgenero"] = "NENHUM"
        p_nenhum = self.service.montar_payload_entidade_alvo("12345", modo="php")
        self.assertEqual(p_nenhum["Genero"], "N")

        # Teste com M e F diretos
        self.mock_repo.carregar_dados_completos_entidade_geoapolo.return_value["entgenero"] = "M"
        self.assertEqual(self.service.montar_payload_entidade_alvo("12345", modo="php")["Genero"], "M")

        self.mock_repo.carregar_dados_completos_entidade_geoapolo.return_value["entgenero"] = "F"
        self.assertEqual(self.service.montar_payload_entidade_alvo("12345", modo="php")["Genero"], "F")

        # Teste em modo delphi com texto longo
        self.mock_repo.carregar_dados_completos_entidade_geoapolo.return_value["entgenero"] = "MASCULINO"
        p_delphi = self.service.montar_payload_entidade_alvo("12345", modo="delphi")
        self.assertEqual(p_delphi["Genero"], "M")
        self.assertLessEqual(len(p_delphi["Genero"]), 1)

    def test_montar_payload_normalizacao_tipo_telefone_alvo(self):
        """Garante que quando não houver entfonetipo ou for inválido (como 'CEL'), o padrão seja 'Pessoal'."""
        from entidades.service import _normalizar_tipo_telefone_alvo

        # Testes diretos da função auxiliar
        self.assertEqual(_normalizar_tipo_telefone_alvo(None), "Pessoal")
        self.assertEqual(_normalizar_tipo_telefone_alvo(""), "Pessoal")
        self.assertEqual(_normalizar_tipo_telefone_alvo("CEL"), "Pessoal")
        self.assertEqual(_normalizar_tipo_telefone_alvo("cel"), "Pessoal")
        self.assertEqual(_normalizar_tipo_telefone_alvo("PESSOAL"), "Pessoal")
        self.assertEqual(_normalizar_tipo_telefone_alvo("Comercial"), "Comercial")
        self.assertEqual(_normalizar_tipo_telefone_alvo("Residencial"), "Residencial")
        self.assertEqual(_normalizar_tipo_telefone_alvo("Celular"), "Celular")

        # Teste no payload quando o telefone não possui tipo definido
        self.mock_repo.listar_telefones_entidade.return_value = [
            {"numero": "988776655", "geotelefoneddd": "21", "tipotelefone": ""}
        ]
        p_sem_tipo = self.service.montar_payload_entidade_alvo("12345", modo="php")
        self.assertEqual(p_sem_tipo["Telefones"][0]["Tipo"], "Pessoal")
        self.assertEqual(p_sem_tipo["Telefones"][0]["entfonetipo"], "Pessoal")

        # Teste no payload com sigla legada 'CEL'
        self.mock_repo.listar_telefones_entidade.return_value = [
            {"numero": "988776655", "geotelefoneddd": "21", "geotipotelefone": "CEL"}
        ]
        p_cel = self.service.montar_payload_entidade_alvo("12345", modo="php")
        self.assertEqual(p_cel["Telefones"][0]["Tipo"], "Pessoal")
        self.assertEqual(p_cel["Telefones"][0]["entfonetipo"], "Pessoal")

        # Teste no payload com tipo Comercial
        self.mock_repo.listar_telefones_entidade.return_value = [
            {"numero": "33334444", "geotelefoneddd": "35", "tipotelefone": "Comercial"}
        ]
        p_com = self.service.montar_payload_entidade_alvo("12345", modo="php")
        self.assertEqual(p_com["Telefones"][0]["Tipo"], "Comercial")
        self.assertEqual(p_com["Telefones"][0]["entfonetipo"], "Comercial")


class TestExportarEntidadeComToken(unittest.TestCase):
    """Testes da orquestração de exportação utilizando o token configurado."""

    def setUp(self):
        self.mock_repo = MagicMock(spec=EntidadeRepository)
        self.service = EntidadeService(self.mock_repo)
        self.mock_repo.carregar_dados_completos_entidade_geoapolo.return_value = {
            "geoentcod": "500",
            "entnome": "Maria Souza",
            "entobservacoes": "",
        }
        self.mock_repo.obter_cpf_rg_documentos.return_value = ("98765432100", "")
        self.mock_repo.listar_categorias_entidade.return_value = []
        self.mock_repo.listar_telefones_entidade.return_value = []
        self.mock_repo.listar_webcontatos_entidade.return_value = []

    @patch("configuracoes.alvo_api_config.carregar_configuracao_alvo")
    def test_exportar_com_token_valido_dispensa_login_operador(self, mock_load_cfg):
        # Configura token válido
        mock_load_cfg.return_value = AlvoAPIConfig(
            token="TOKEN_PERMANENTE_VALIDO_123",
            base_url="https://alvo.rccbrasil.org.br/api",
            ativo=True,
        )

        mock_api = MagicMock(spec=AlvoAPIClient)
        mock_api.token = None
        mock_api.inserir_alterar_entidade.return_value = (True, '{"entcod": "9999"}', {"entcod": "9999"})
        mock_api.extrair_entcod_resposta.return_value = "9999"

        res = self.service.exportar_entidade_para_alvo(
            geoentcod="500",
            api_client=mock_api,
        )

        self.assertTrue(res.sucesso)
        self.assertEqual(res.codigo, "9999")
        # Garante que o token configurado foi repassado ao cliente HTTP
        self.assertEqual(mock_api.token, "TOKEN_PERMANENTE_VALIDO_123")
        self.mock_repo.vincular_entcod.assert_called_once_with("500", "9999")

    @patch("configuracoes.alvo_api_config.carregar_configuracao_alvo")
    def test_exportar_bloqueado_com_observacoes(self, mock_load_cfg):
        self.mock_repo.carregar_dados_completos_entidade_geoapolo.return_value["entobservacoes"] = "[PENDÊNCIAS] moderação"
        res = self.service.exportar_entidade_para_alvo(geoentcod="500")
        self.assertFalse(res.sucesso)
        self.assertIn("pendências", res.mensagem.lower())


class TestFrmConfiguracaoAPIAlvoUI(unittest.TestCase):
    """Testes de interface gráfica para a tela FrmConfiguracaoAPIAlvo."""

    def setUp(self):
        FrmConfiguracaoAPIAlvo._instancia_ativa = None
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        FrmConfiguracaoAPIAlvo._instancia_ativa = None
        self.root.destroy()

    @patch("configuracoes.alvo_api_view.carregar_configuracao_alvo")
    def test_instanciacao_formulario_e_carregamento(self, mock_load):
        mock_load.return_value = AlvoAPIConfig(
            token="TOKEN_UI_TESTE",
            data_inicial="01/01/2026",
            data_final="31/12/2026",
            base_url="https://alvo.rccbrasil.org.br/api",
        )

        form = FrmConfiguracaoAPIAlvo(self.root)
        self.assertEqual(form.txt_token.get("1.0", tk.END).strip(), "TOKEN_UI_TESTE")
        self.assertEqual(form.txt_dt_inicial.get(), "01/01/2026")
        self.assertEqual(form.txt_dt_final.get(), "31/12/2026")
        form.destroy()

    @patch("configuracoes.alvo_api_config.carregar_configuracao_alvo")
    def test_singleton_controle_instancia(self, mock_load):
        mock_load.return_value = AlvoAPIConfig()
        form1 = FrmConfiguracaoAPIAlvo(self.root)
        form2 = FrmConfiguracaoAPIAlvo(self.root)
        self.assertIs(form1, form2)
        form1.destroy()
        self.assertIsNone(FrmConfiguracaoAPIAlvo._instancia_ativa)


if __name__ == "__main__":
    unittest.main()
