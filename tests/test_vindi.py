"""
Testes Unitários para o Módulo de Conciliação Vindi e Crédito Recorrente.
GeoApolo V5
"""

import unittest
from unittest.mock import MagicMock
from datetime import date
from vindi.models import (
    TransacaoVindiDTO,
    ResumoConciliacaoVindiDTO,
)
from vindi.repository import VindiRepository
from vindi.service import VindiService


class TestVindiModule(unittest.TestCase):

    def setUp(self):
        self.mock_repo = MagicMock(spec=VindiRepository)
        self.service = VindiService(self.mock_repo)

    def test_checar_integridade_sem_cpf(self):
        t = TransacaoVindiDTO(
            pedido_id="PED01",
            cpf_cnpj="",
            nome_cliente="Cliente Sem CPF",
            data_transacao=date(2025, 9, 1),
            valor_bruto=100.0,
            valor_tarifa=2.5,
            valor_liquido=97.5,
        )
        erros = self.service.checar_integridade(t)
        self.assertTrue(t.tem_erros)
        self.assertTrue(any("não informado" in e for e in erros))

    def test_checar_integridade_cpf_nao_localizado(self):
        t = TransacaoVindiDTO(
            pedido_id="PED02",
            cpf_cnpj="12345678901",
            nome_cliente="Cliente Nao Cadastrado",
            data_transacao=date(2025, 9, 1),
            valor_bruto=100.0,
            valor_tarifa=2.5,
            valor_liquido=97.5,
        )
        self.mock_repo.buscar_entidade_por_cpf.return_value = None
        erros = self.service.checar_integridade(t)
        self.assertTrue(t.tem_erros)
        self.assertTrue(any("não localizado" in e for e in erros))

    def test_checar_integridade_valida(self):
        t = TransacaoVindiDTO(
            pedido_id="PED03",
            cpf_cnpj="12345678901",
            nome_cliente="Doador Fiel",
            data_transacao=date(2025, 9, 1),
            valor_bruto=150.0,
            valor_tarifa=3.5,
            valor_liquido=146.5,
            status_vindi="Paga",
        )
        self.mock_repo.buscar_entidade_por_cpf.return_value = ("ENT010", "Doador Fiel")
        self.mock_repo.buscar_categorias_entidade.return_value = ["02.001"]

        erros = self.service.checar_integridade(t)
        self.assertFalse(t.tem_erros)
        self.assertEqual(len(erros), 0)
        self.assertEqual(t.ent_cod, "ENT010")
        self.assertEqual(t.categoria_cod, "02.001")

    def test_conciliar_periodo(self):
        t1 = TransacaoVindiDTO("P1", "123", "Cli 1", date(2025, 9, 1), 100.0, 2.0, 98.0, "Paga", False)
        t2 = TransacaoVindiDTO("P2", "456", "Cli 2", date(2025, 9, 2), 200.0, 4.0, 196.0, "Paga", True)

        self.mock_repo.listar_transacoes.return_value = [t1, t2]
        self.mock_repo.buscar_entidade_por_cpf.return_value = ("ENT001", "Cli")
        self.mock_repo.buscar_categorias_entidade.return_value = ["02.001"]

        trans, resumo = self.service.conciliar_periodo(date(2025, 9, 1), date(2025, 9, 30))
        self.assertEqual(len(trans), 2)
        self.assertEqual(resumo.total_transacoes, 2)
        self.assertEqual(resumo.total_bruto, 300.0)
        self.assertEqual(resumo.total_tarifas, 6.0)
        self.assertEqual(resumo.total_liquido, 294.0)
        self.assertEqual(resumo.total_integradas, 1)

    def test_integrar_transacao(self):
        self.mock_repo.marcar_transacao_integrada.return_value = True
        self.assertTrue(self.service.integrar_transacao("PED100"))
        self.mock_repo.marcar_transacao_integrada.assert_called_once_with("PED100")


if __name__ == "__main__":
    unittest.main()
