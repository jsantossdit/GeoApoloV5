"""
Testes Unitários para o Módulo de Licenciamento, Segurança & Versões.
GeoApolo V5
Clean Architecture: DTOs, Repositório SQLite em memória e Regras de Negócio do Service.
"""

from datetime import date, timedelta
import sqlite3
import unittest
from unittest.mock import MagicMock

from licenciamento.models import (
    LicencaDTO,
    ResultadoValidacaoLicencaDTO,
    VersaoSistemaDTO,
    ResultadoOperacaoVersaoDTO,
)
from licenciamento.repository import LicenciamentoRepository
from licenciamento.service import LicenciamentoService, CHAVE_MESTRA_EMERGENCIA


class TestLicenciamentoModels(unittest.TestCase):
    """Testes dos DTOs de Licenciamento e Versões."""

    def test_licenca_dto_properties(self):
        hoje = date(2026, 9, 17)
        dt_fim = date(2026, 9, 30)

        lic = LicencaDTO(
            id_palavra="PALAVRA_TESTE",
            data_inicial=date(2026, 9, 1),
            data_final=dt_fim,
            flag_bloqueia="N",
            tempo_bloqueio_dias=15,
            flag_ativar="S",
            mes_referencia=9,
            ano_referencia=2026,
        )

        self.assertFalse(lic.is_bloqueada)
        self.assertTrue(lic.is_ativa)
        self.assertEqual(lic.calcular_dias_restantes(hoje), 13)

        # Licença bloqueada
        lic_bloq = LicencaDTO(flag_bloqueia="S", flag_ativar="N")
        self.assertTrue(lic_bloq.is_bloqueada)
        self.assertFalse(lic_bloq.is_ativa)

    def test_versao_dto_properties(self):
        v1 = VersaoSistemaDTO("5.1.0", "17/09/2026", "Novidades da release", "S")
        self.assertTrue(v1.is_liberada)
        self.assertIn("Liberada", v1.display)

        v2 = VersaoSistemaDTO("5.2.0-beta", "01/10/2026", "Draft", "N")
        self.assertFalse(v2.is_liberada)
        self.assertIn("Em Edição", v2.display)


class TestLicenciamentoRepository(unittest.TestCase):
    """Testes de persistência com banco de dados SQLite em memória."""

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()

        # Dicionário de Licenças
        self.cursor.execute("""
            CREATE TABLE user_geoapolo_dicionario (
                id_palavra VARCHAR(50) PRIMARY KEY,
                data_inicial DATE,
                data_final DATE,
                flag_bloqueia VARCHAR(1),
                tempo_bloqueio_dias INTEGER,
                flag_ativar VARCHAR(1)
            )
        """)

        # Manutenção de Versões
        self.cursor.execute("""
            CREATE TABLE USER_geoapolo_novversao (
                idversao VARCHAR(20) PRIMARY KEY,
                data_lancamento VARCHAR(20),
                textonovaversao TEXT,
                statusversao VARCHAR(1)
            )
        """)

        # Histórico de Leitura de Novidades
        self.cursor.execute("""
            CREATE TABLE USER_geoapolo_userversao (
                idversao VARCHAR(20),
                usucod VARCHAR(20),
                PRIMARY KEY (idversao, usucod)
            )
        """)
        self.conn.commit()
        self.repo = LicenciamentoRepository(connection=self.conn)

    def tearDown(self):
        self.conn.close()

    def test_salvar_e_buscar_licenca_mes(self):
        lic = LicencaDTO(
            id_palavra="LIC_SET_2026",
            data_inicial=date(2026, 9, 1),
            data_final=date(2026, 9, 30),
            flag_bloqueia="N",
            tempo_bloqueio_dias=10,
            flag_ativar="S",
        )
        self.repo.salvar_licenca(lic)

        buscada = self.repo.buscar_licenca_mes(9, 2026)
        self.assertIsNotNone(buscada)
        self.assertEqual(buscada.id_palavra, "LIC_SET_2026")
        self.assertEqual(buscada.tempo_bloqueio_dias, 10)
        self.assertEqual(buscada.data_final, date(2026, 9, 30))

    def test_bloquear_e_ativar_licenca(self):
        lic = LicencaDTO(
            id_palavra="LIC_OUT_2026",
            data_inicial=date(2026, 10, 1),
            data_final=date(2026, 10, 31),
            flag_bloqueia="N",
            flag_ativar="S",
        )
        self.repo.salvar_licenca(lic)

        self.repo.bloquear_licenca("LIC_OUT_2026")
        lic_b = self.repo.buscar_licenca_mes(10, 2026)
        self.assertTrue(lic_b.is_bloqueada)

        self.repo.ativar_licenca("LIC_OUT_2026")
        lic_a = self.repo.buscar_licenca_mes(10, 2026)
        self.assertFalse(lic_a.is_bloqueada)
        self.assertTrue(lic_a.is_ativa)

    def test_gestao_versoes(self):
        v1 = VersaoSistemaDTO("5.0.0", "01/08/2026", "Lançamento v5", "S")
        v2 = VersaoSistemaDTO("5.1.0", "15/09/2026", "Ajustes de segurança", "N")

        self.repo.salvar_versao(v1)
        self.repo.salvar_versao(v2)

        lista = self.repo.listar_versoes()
        self.assertEqual(len(lista), 2)

        v_buscada = self.repo.obter_versao("5.0.0")
        self.assertIsNotNone(v_buscada)
        self.assertEqual(v_buscada.textonovaversao, "Lançamento v5")

        # Atualização
        v1_up = VersaoSistemaDTO("5.0.0", "02/08/2026", "Lançamento v5 atualizado", "S")
        self.repo.salvar_versao(v1_up)
        v_atualizada = self.repo.obter_versao("5.0.0")
        self.assertEqual(v_atualizada.textonovaversao, "Lançamento v5 atualizado")

        # Exclusão
        self.repo.excluir_versao("5.1.0")
        self.assertIsNone(self.repo.obter_versao("5.1.0"))

    def test_controle_leitura_usuario(self):
        self.assertFalse(self.repo.usuario_ja_viu_versao("5.0.0", "ADMIN"))
        self.repo.marcar_versao_vista("5.0.0", "ADMIN")
        self.assertTrue(self.repo.usuario_ja_viu_versao("5.0.0", "ADMIN"))
        self.assertFalse(self.repo.usuario_ja_viu_versao("5.0.0", "USER2"))


class TestLicenciamentoService(unittest.TestCase):
    """Testes das regras de negócio do LicenciamentoService."""

    def setUp(self):
        self.mock_repo = MagicMock(spec=LicenciamentoRepository)
        self.service = LicenciamentoService(self.mock_repo)

    def test_validar_licenca_inexistente(self):
        self.mock_repo.buscar_licenca_mes.return_value = None
        res = self.service.validar_licenca_atual(date(2026, 9, 17))
        self.assertFalse(res.sucesso)
        self.assertEqual(res.status, "ERRO_CONSULTA")

    def test_validar_licenca_bloqueada(self):
        self.mock_repo.buscar_licenca_mes.return_value = LicencaDTO(
            id_palavra="LIC1", flag_bloqueia="S", flag_ativar="S"
        )
        res = self.service.validar_licenca_atual(date(2026, 9, 17))
        self.assertFalse(res.sucesso)
        self.assertEqual(res.status, "BLOQUEADA")

    def test_validar_licenca_nao_ativada(self):
        self.mock_repo.buscar_licenca_mes.return_value = LicencaDTO(
            id_palavra="LIC1", flag_bloqueia="N", flag_ativar="N"
        )
        res = self.service.validar_licenca_atual(date(2026, 9, 17))
        self.assertFalse(res.sucesso)
        self.assertEqual(res.status, "NAO_ATIVADA")

    def test_validar_licenca_aviso_expiracao(self):
        self.mock_repo.buscar_licenca_mes.return_value = LicencaDTO(
            id_palavra="LIC1",
            data_inicial=date(2026, 9, 1),
            data_final=date(2026, 9, 20),  # 3 dias restantes
            flag_bloqueia="N",
            flag_ativar="S",
            tempo_bloqueio_dias=10,
        )
        res = self.service.validar_licenca_atual(date(2026, 9, 17))
        self.assertTrue(res.sucesso)
        self.assertEqual(res.status, "AVISO_EXPIRACAO")
        self.assertEqual(res.dias_restantes, 3)

    def test_validar_licenca_ok(self):
        self.mock_repo.buscar_licenca_mes.return_value = LicencaDTO(
            id_palavra="LIC1",
            data_inicial=date(2026, 9, 1),
            data_final=date(2026, 9, 30),  # 13 dias restantes (> 10)
            flag_bloqueia="N",
            flag_ativar="S",
            tempo_bloqueio_dias=10,
        )
        res = self.service.validar_licenca_atual(date(2026, 9, 17))
        self.assertTrue(res.sucesso)
        self.assertEqual(res.status, "OK")

    def test_ativacao_com_chave(self):
        chave_correta = self.service.gerar_chave_licenca("GEO_2026", 9, 2026)

        # Chave inválida
        res_inv = self.service.ativar_licenca_com_chave("GEO_2026", "CHAVE-ERRADA", 9, 2026)
        self.assertFalse(res_inv.sucesso)

        # Chave correta
        res_ok = self.service.ativar_licenca_com_chave("GEO_2026", chave_correta, 9, 2026)
        self.assertTrue(res_ok.sucesso)
        self.mock_repo.ativar_licenca.assert_called_with("GEO_2026")

        # Chave mestra emergência
        res_master = self.service.ativar_licenca_com_chave("GEO_2026", CHAVE_MESTRA_EMERGENCIA, 9, 2026)
        self.assertTrue(res_master.sucesso)

    def test_salvar_versao_validacoes(self):
        # Versão sem id
        res1 = self.service.salvar_versao(VersaoSistemaDTO("", "17/09/2026"))
        self.assertFalse(res1.sucesso)
        self.assertIn("obrigatório", res1.mensagem)

        # Versão sem data
        res2 = self.service.salvar_versao(VersaoSistemaDTO("5.0.1", ""))
        self.assertFalse(res2.sucesso)
        self.assertIn("obrigatória", res2.mensagem)

        # Versão válida
        res3 = self.service.salvar_versao(VersaoSistemaDTO("5.0.1", "17/09/2026", "Notes", "S"))
        self.assertTrue(res3.sucesso)
        self.mock_repo.salvar_versao.assert_called_once()

    def test_excluir_versao_liberada_bloqueia(self):
        self.mock_repo.obter_versao.return_value = VersaoSistemaDTO("5.0.0", "01/01/2026", "Notes", "S")
        res = self.service.excluir_versao("5.0.0")
        self.assertFalse(res.sucesso)
        self.assertIn("Não é permitido excluir", res.mensagem)

    def test_excluir_versao_nao_liberada_permite(self):
        self.mock_repo.obter_versao.return_value = VersaoSistemaDTO("5.1.0-draft", "01/01/2026", "Draft", "N")
        res = self.service.excluir_versao("5.1.0-draft")
        self.assertTrue(res.sucesso)
        self.mock_repo.excluir_versao.assert_called_once_with("5.1.0-draft")

    def test_novidades_pendentes_e_confirmacao(self):
        self.mock_repo.usuario_ja_viu_versao.return_value = False
        self.mock_repo.obter_versao.return_value = VersaoSistemaDTO("5.0.0", "01/01/2026", "Novidades!", "S")

        notas = self.service.obter_novidades_pendentes("5.0.0", "USER1")
        self.assertEqual(notas, "Novidades!")

        # Se já viu
        self.mock_repo.usuario_ja_viu_versao.return_value = True
        self.assertIsNone(self.service.obter_novidades_pendentes("5.0.0", "USER1"))

        # Confirmação
        self.service.confirmar_leitura_versao("5.0.0", "USER1")
        self.mock_repo.marcar_versao_vista.assert_called_with("5.0.0", "USER1")


if __name__ == "__main__":
    unittest.main()
