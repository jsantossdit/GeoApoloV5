"""
Testes Unitários para o Módulo de Desativação e Desligamento de Usuários.
GeoApolo V5
"""

import unittest
from unittest.mock import MagicMock
from permissoes.models import UsuarioDesligamentoDTO, ResultadoDesligamentoDTO
from permissoes.repository import PermissoesRepository
from permissoes.service import PermissoesService


class TestDesligamentoUsuario(unittest.TestCase):

    def setUp(self):
        self.mock_repo = MagicMock(spec=PermissoesRepository)
        self.service = PermissoesService(self.mock_repo)

    def test_listar_usuarios_desligamento(self):
        self.mock_repo.listar_usuarios_por_status.return_value = [
            UsuarioDesligamentoDTO("ADMIN", "Administrador", "TI", "Ativo"),
            UsuarioDesligamentoDTO("USER1", "Operador 1", "Financeiro", "Ativo"),
        ]
        res = self.service.listar_usuarios_desligamento("Ativo")
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0].codigo, "ADMIN")
        self.assertEqual(res[1].codigo, "USER1")
        self.mock_repo.listar_usuarios_por_status.assert_called_once_with("Ativo")

    def test_pesquisar_usuarios(self):
        self.mock_repo.pesquisar_usuarios.return_value = [
            UsuarioDesligamentoDTO("JULIO", "Julio Cesar", "TI", "Ativo")
        ]
        res = self.service.pesquisar_usuarios_desligamento("usunome", "Julio", "Ativo")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].codigo, "JULIO")
        self.mock_repo.pesquisar_usuarios.assert_called_once_with("usunome", "Julio", "Ativo")

    def test_obter_detalhes_usuario_vazio(self):
        res = self.service.obter_detalhes_usuario("")
        self.assertIsNone(res)
        self.mock_repo.obter_usuario.assert_not_called()

    def test_obter_detalhes_usuario_encontrado(self):
        self.mock_repo.obter_usuario.return_value = UsuarioDesligamentoDTO(
            "OPERADOR", "Nome Operador", "Contábil", "Ativo"
        )
        res = self.service.obter_detalhes_usuario("OPERADOR")
        self.assertIsNotNone(res)
        self.assertEqual(res.codigo, "OPERADOR")
        self.mock_repo.obter_usuario.assert_called_once_with("OPERADOR")

    def test_desligar_usuario_sem_codigo(self):
        res = self.service.desligar_usuario("")
        self.assertFalse(res.sucesso)
        self.assertIn("Selecione um usuário", res.mensagem)
        self.mock_repo.executar_desligamento.assert_not_called()

    def test_desligar_usuario_com_sucesso(self):
        ret_dto = ResultadoDesligamentoDTO(
            sucesso=True,
            mensagem="Desligamento realizado.",
            vinculos_entidades=5,
            vinculos_categorias=2,
            permissoes_relatorios=10,
            permissoes_contas_fin=3,
        )
        self.mock_repo.executar_desligamento.return_value = ret_dto
        res = self.service.desligar_usuario("FUNC01")
        self.assertTrue(res.sucesso)
        self.assertEqual(res.vinculos_entidades, 5)
        self.assertEqual(res.permissoes_contas_fin, 3)
        self.mock_repo.executar_desligamento.assert_called_once_with("FUNC01")

    def test_reativar_usuario(self):
        self.mock_repo.reativar_usuario.return_value = True
        self.assertTrue(self.service.reativar_usuario("FUNC01"))
        self.mock_repo.reativar_usuario.assert_called_once_with("FUNC01")

        self.assertFalse(self.service.reativar_usuario(""))


if __name__ == "__main__":
    unittest.main()
