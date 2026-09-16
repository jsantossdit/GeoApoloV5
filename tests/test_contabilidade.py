"""
Testes Unitários para o Módulo de Contabilidade e Conciliação Financeira.
GeoApolo V5
"""

import unittest
from unittest.mock import MagicMock
from datetime import date
from contabilidade.models import (
    LancamentoContabilDTO,
    ValidacaoExclusaoDTO,
    FiltroExclusaoModuloDTO,
    ResultadoExclusaoContabilDTO,
    DebxCredItemDTO,
    ResumoConciliacaoDTO,
)
from contabilidade.repository import ContabilidadeRepository
from contabilidade.service import ContabilidadeService


class TestContabilidadeService(unittest.TestCase):

    def setUp(self):
        self.mock_repo = MagicMock(spec=ContabilidadeRepository)
        self.service = ContabilidadeService(self.mock_repo)

    def test_debxcred_item_divergente(self):
        item_equilibrado = DebxCredItemDTO(
            chave="1",
            data=date(2025, 9, 15),
            conta_debito="1001",
            conta_credito="2001",
            valor_debito=150.00,
            valor_credito=150.00,
            historico="Lancamento ok",
        )
        self.assertFalse(item_equilibrado.eh_divergente)

        item_divergente = DebxCredItemDTO(
            chave="2",
            data=date(2025, 9, 15),
            conta_debito="1001",
            conta_credito="",
            valor_debito=150.00,
            valor_credito=0.00,
            historico="Apenas debito",
        )
        self.assertTrue(item_divergente.eh_divergente)

    def test_pesquisar_lancamentos(self):
        self.mock_repo.pesquisar_lancamentos.return_value = [
            LancamentoContabilDTO(
                chave="1001",
                numero_origem="DOC1",
                origem_chave="CHV1",
                modulo="Financeiro",
                submodulo="Realizado",
                data=date(2025, 9, 15),
                empresa_cod="001",
                valor=500.0,
                historico="Pagamento de fornecedor",
                conta_debito="2001",
                conta_credito="1001",
            )
        ]
        itens = self.service.pesquisar_lancamentos(campo="contablancchv", valor="1001")
        self.assertEqual(len(itens), 1)
        self.assertEqual(itens[0].chave, "1001")
        self.assertEqual(itens[0].valor, 500.0)

    def test_validar_exclusao_chave_vazia(self):
        val = self.service.validar_exclusao("")
        self.assertFalse(val.permitido)
        self.assertIn("Informe o número de chave", val.mensagem)

    def test_validar_exclusao_nao_encontrado(self):
        self.mock_repo.obter_lancamento.return_value = None
        val = self.service.validar_exclusao("99999")
        self.assertFalse(val.permitido)
        self.assertIn("não encontrado", val.mensagem)

    def test_validar_exclusao_bloqueada_por_origem(self):
        lanc = LancamentoContabilDTO(
            chave="123",
            numero_origem="MOV50",
            origem_chave="",
            modulo="Financeiro",
            submodulo="Realizado",
            data=date(2025, 9, 15),
            empresa_cod="001",
            valor=250.0,
            historico="Cheque",
            conta_debito="1001",
            conta_credito="2001",
        )
        self.mock_repo.obter_lancamento.return_value = lanc
        self.mock_repo.validar_integridade_origem.return_value = ValidacaoExclusaoDTO(
            permitido=False, mensagem="Bloqueado por movimento bancário.", origem_detectada="MOV50"
        )

        val = self.service.validar_exclusao("123")
        self.assertFalse(val.permitido)
        self.assertIn("Bloqueado por movimento bancário", val.mensagem)

    def test_excluir_lancamento_bloqueado(self):
        lanc = LancamentoContabilDTO(
            chave="123",
            numero_origem="MOV50",
            origem_chave="",
            modulo="Financeiro",
            submodulo="Realizado",
            data=date(2025, 9, 15),
            empresa_cod="001",
            valor=250.0,
            historico="Cheque",
            conta_debito="1001",
            conta_credito="2001",
        )
        self.mock_repo.obter_lancamento.return_value = lanc
        self.mock_repo.validar_integridade_origem.return_value = ValidacaoExclusaoDTO(
            permitido=False, mensagem="Bloqueado por movimento bancário."
        )

        res = self.service.excluir_lancamento("123", forcar=False)
        self.assertFalse(res.sucesso)
        self.mock_repo.excluir_lancamento.assert_not_called()

    def test_excluir_lancamento_permitido(self):
        lanc = LancamentoContabilDTO(
            chave="123",
            numero_origem="MANUAL",
            origem_chave="",
            modulo="Contabilidade",
            submodulo="",
            data=date(2025, 9, 15),
            empresa_cod="001",
            valor=100.0,
            historico="Ajuste manual",
            conta_debito="1001",
            conta_credito="2001",
        )
        self.mock_repo.obter_lancamento.return_value = lanc
        self.mock_repo.validar_integridade_origem.return_value = ValidacaoExclusaoDTO(
            permitido=True, mensagem="Exclusão permitida."
        )
        self.mock_repo.excluir_lancamento.return_value = ResultadoExclusaoContabilDTO(
            sucesso=True, mensagem="Lançamento excluído com sucesso.", registros_excluidos=1
        )

        res = self.service.excluir_lancamento("123")
        self.assertTrue(res.sucesso)
        self.assertEqual(res.registros_excluidos, 1)

    def test_pesquisar_por_modulo_data_invalida(self):
        filtro = FiltroExclusaoModuloDTO(
            data_inicial=date(2025, 9, 20),
            data_final=date(2025, 9, 10),
            modulo="Financeiro",
        )
        with self.assertRaises(ValueError):
            self.service.pesquisar_por_modulo(filtro)

    def test_conciliar_debxcred_com_sucesso(self):
        itens_mock = [
            DebxCredItemDTO(
                chave="1",
                data=date(2025, 9, 15),
                conta_debito="1001",
                conta_credito="2001",
                valor_debito=100.0,
                valor_credito=100.0,
                historico="Lanc 1",
            ),
            DebxCredItemDTO(
                chave="2",
                data=date(2025, 9, 15),
                conta_debito="1001",
                conta_credito="",
                valor_debito=50.0,
                valor_credito=0.0,
                historico="Lanc 2",
            ),
        ]
        self.mock_repo.conciliar_debxcred.return_value = itens_mock

        itens, resumo = self.service.conciliar_debxcred(date(2025, 9, 1), date(2025, 9, 30))
        self.assertEqual(len(itens), 2)
        self.assertEqual(resumo.total_debito, 150.0)
        self.assertEqual(resumo.total_credito, 100.0)
        self.assertEqual(resumo.saldo_divergencia, 50.0)
        self.assertEqual(resumo.total_divergentes, 1)

    def test_obter_nome_conta_contabil(self):
        self.mock_repo.obter_nome_conta_contabil.return_value = "BANCO BRADESCO S/A"
        nome = self.service.obter_nome_conta_contabil("1001")
        self.assertEqual(nome, "BANCO BRADESCO S/A")
        self.mock_repo.obter_nome_conta_contabil.assert_called_once_with("1001")


if __name__ == "__main__":
    unittest.main()
