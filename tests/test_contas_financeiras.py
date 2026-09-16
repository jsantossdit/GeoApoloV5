"""
Testes Unitários para o Módulo de Permissões em Contas Financeiras.
GeoApolo V5
"""

import unittest
from unittest.mock import MagicMock
from permissoes.models import ContaFinanceiraDTO, ResultadoContasFinDTO
from permissoes.repository import PermissoesRepository
from permissoes.service import PermissoesService


class TestContasFinanceiras(unittest.TestCase):

    def setUp(self):
        self.mock_repo = MagicMock(spec=PermissoesRepository)
        self.service = PermissoesService(self.mock_repo)

    def test_dto_texto_formatado(self):
        conta = ContaFinanceiraDTO(codigo="001", nome="BANCO DO BRASIL", conta_corrente="12345-6")
        self.assertEqual(conta.texto_formatado, "001 -> BANCO DO BRASIL")

    def test_obter_contas_disponiveis(self):
        self.mock_repo.listar_contas_disponiveis.return_value = [
            ContaFinanceiraDTO("001", "BANCO DO BRASIL"),
            ContaFinanceiraDTO("104", "CAIXA ECONOMICA"),
        ]
        res = self.service.obter_contas_disponiveis()
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0].codigo, "001")
        self.assertEqual(res[1].codigo, "104")

    def test_obter_contas_usuario_vazio(self):
        res = self.service.obter_contas_usuario("")
        self.assertEqual(res, [])
        self.mock_repo.listar_contas_usuario.assert_not_called()

    def test_obter_contas_usuario_com_sucesso(self):
        self.mock_repo.listar_contas_usuario.return_value = [
            ContaFinanceiraDTO("237", "BRADESCO")
        ]
        res = self.service.obter_contas_usuario("OPERADOR1")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].codigo, "237")
        self.mock_repo.listar_contas_usuario.assert_called_once_with("OPERADOR1")

    def test_salvar_contas_usuario_sem_usucod(self):
        res = self.service.salvar_contas_usuario("", ["001", "104"])
        self.assertFalse(res.sucesso)
        self.assertIn("Selecione um usuário", res.mensagem)
        self.mock_repo.salvar_contas_usuario.assert_not_called()

    def test_salvar_contas_usuario_com_sucesso(self):
        self.mock_repo.salvar_contas_usuario.return_value = 2
        res = self.service.salvar_contas_usuario("JULIO", ["001", "237"])
        self.assertTrue(res.sucesso)
        self.assertEqual(res.total_afetado, 2)
        self.assertIn("JULIO", res.mensagem)
        self.mock_repo.salvar_contas_usuario.assert_called_once_with("JULIO", ["001", "237"])

    def test_salvar_contas_usuario_com_excecao(self):
        self.mock_repo.salvar_contas_usuario.side_effect = RuntimeError("Erro de banco")
        res = self.service.salvar_contas_usuario("JULIO", ["001"])
        self.assertFalse(res.sucesso)
        self.assertEqual(res.total_afetado, 0)
        self.assertIn("Erro de banco", res.mensagem)

    def test_revogar_contas_usuario(self):
        self.mock_repo.revogar_contas_usuario.return_value = 3
        res = self.service.revogar_contas_usuario("OPERADOR")
        self.assertTrue(res.sucesso)
        self.assertEqual(res.total_afetado, 3)
        self.mock_repo.revogar_contas_usuario.assert_called_once_with("OPERADOR")


if __name__ == "__main__":
    unittest.main()
