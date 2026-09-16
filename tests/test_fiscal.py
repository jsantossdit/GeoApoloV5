"""
Testes Unitários para o Módulo Fiscal e Auditoria de Cupons NFC-e.
GeoApolo V5
"""

import unittest
from unittest.mock import MagicMock
from datetime import date
from fiscal.models import (
    AuditoriaCupomDTO,
    ResumoAuditoriaCupomDTO,
    ResultadoSincronizacaoCupomDTO,
)
from fiscal.repository import FiscalRepository
from fiscal.service import FiscalService


class TestFiscalModule(unittest.TestCase):

    def setUp(self):
        self.mock_repo = MagicMock(spec=FiscalRepository)
        self.service = FiscalService(self.mock_repo)

    def test_dto_eh_pendente(self):
        cupom_ok = AuditoriaCupomDTO(
            empresa_cod="001",
            entidade_cod="500",
            entidade_nome="CONSUMIDOR FINAL",
            serie="1",
            numero="100",
            valor_total=50.0,
            status_sefaz="Transmitiu",
            integrado_alvo=True,
            integrado_financ=True,
            integrado_fiscal=True,
            baixou_estoque=True,
        )
        self.assertFalse(cupom_ok.eh_pendente)

        cupom_pendente = AuditoriaCupomDTO(
            empresa_cod="001",
            entidade_cod="500",
            entidade_nome="CONSUMIDOR FINAL",
            serie="1",
            numero="101",
            valor_total=75.0,
            status_sefaz="Transmitiu",
            integrado_alvo=False,
            integrado_financ=True,
            integrado_fiscal=False,
            baixou_estoque=True,
        )
        self.assertTrue(cupom_pendente.eh_pendente)

    def test_executar_auditoria_datas_invalidas(self):
        with self.assertRaises(ValueError):
            self.service.executar_auditoria(date(2026, 7, 30), date(2026, 7, 20))

    def test_executar_auditoria_com_sucesso(self):
        cupons_mock = [
            AuditoriaCupomDTO("001", "500", "CLIENTE A", "1", "101", 100.0, "Transmitiu", True, True, True, True),
            AuditoriaCupomDTO("001", "501", "CLIENTE B", "1", "102", 50.0, "Não Transmitiu", False, False, False, False),
        ]
        self.mock_repo.listar_cupons_pdv.return_value = cupons_mock

        cupons, resumo = self.service.executar_auditoria(date(2026, 7, 20), date(2026, 7, 25))
        self.assertEqual(len(cupons), 2)
        self.assertEqual(resumo.total_cupons, 2)
        self.assertEqual(resumo.total_transmitidos, 1)
        self.assertEqual(resumo.total_nao_transmitidos, 1)
        self.assertEqual(resumo.total_integrados, 1)
        self.assertEqual(resumo.total_pendentes, 1)

    def test_sincronizar_flags_com_apolo(self):
        cupom = AuditoriaCupomDTO("001", "500", "CLIENTE", "1", "101", 100.0, "Transmitiu", False, False, False, False)
        self.mock_repo.verificar_cupom_no_apolo.return_value = True
        self.mock_repo.atualizar_flags_pdv.return_value = True

        res = self.service.sincronizar_flags_com_apolo([cupom])
        self.assertTrue(res.sucesso)
        self.assertEqual(res.cupons_atualizados, 1)
        self.assertTrue(cupom.integrado_alvo)
        self.assertTrue(cupom.integrado_financ)
        self.mock_repo.verificar_cupom_no_apolo.assert_called_once_with("101", "1")
        self.mock_repo.atualizar_flags_pdv.assert_called_once_with("101", "Sim", "Sim", "Sim", "Sim")


if __name__ == "__main__":
    unittest.main()
