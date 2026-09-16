"""
Testes Unitários para o Módulo de Localidades e Correção de Cidades/Distritos.
GeoApolo V5
"""

import unittest
from unittest.mock import MagicMock
from core.viacep import ViaCEPClient
from localidades.models import (
    CidadeDistritoDTO,
    EntidadeLocalidadeDTO,
    ResultadoCorrecaoLocalidadeDTO,
)
from localidades.repository import LocalidadesRepository
from localidades.service import LocalidadesService


class TestLocalidadesModule(unittest.TestCase):

    def setUp(self):
        self.mock_repo = MagicMock(spec=LocalidadesRepository)
        self.mock_viacep = MagicMock(spec=ViaCEPClient)
        self.service = LocalidadesService(self.mock_repo, self.mock_viacep)

    def test_buscar_cidades(self):
        self.mock_repo.listar_cidades.return_value = [
            CidadeDistritoDTO(cid_cod="3550308", nome="SAO PAULO", uf="SP", ibge="3550308", total_entidades=150)
        ]
        res = self.service.buscar_cidades("SAO", "SP")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].cid_cod, "3550308")
        self.assertEqual(res[0].nome, "SAO PAULO")
        self.mock_repo.listar_cidades.assert_called_once_with("SAO", "SP")

    def test_obter_entidades_localidade(self):
        self.mock_repo.listar_entidades_por_cidade.return_value = [
            EntidadeLocalidadeDTO("E1", "Entidade 1", "123", "01001-000", "Praca da Se", "Centro")
        ]
        res = self.service.obter_entidades_localidade("3550308")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].ent_cod, "E1")
        self.mock_repo.listar_entidades_por_cidade.assert_called_once_with("3550308")

    def test_consultar_cep_online(self):
        self.mock_viacep.consultar_cep.return_value = {
            "cep": "01001-000",
            "logradouro": "Praça da Sé",
            "localidade": "São Paulo",
            "uf": "SP",
            "ibge": "3550308",
        }
        info = self.service.consultar_cep("01001000")
        self.assertIsNotNone(info)
        self.assertEqual(info["localidade"], "São Paulo")
        self.mock_viacep.consultar_cep.assert_called_once_with("01001000")

    def test_corrigir_distrito_mesma_cidade(self):
        res = self.service.corrigir_distrito_para_cidade("35001", "35001")
        self.assertFalse(res.sucesso)
        self.assertIn("não podem ser as mesmas", res.mensagem)
        self.mock_repo.migrar_entidades.assert_not_called()

    def test_corrigir_distrito_com_sucesso(self):
        self.mock_repo.migrar_entidades.return_value = 14
        res = self.service.corrigir_distrito_para_cidade("DIST01", "CID01")
        self.assertTrue(res.sucesso)
        self.assertEqual(res.entidades_migradas, 14)
        self.mock_repo.migrar_entidades.assert_called_once_with("DIST01", "CID01")


if __name__ == "__main__":
    unittest.main()
