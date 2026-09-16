"""
Testes unitários para o módulo core (validadores, viacep, email).
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

PASTA_RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PASTA_RAIZ not in sys.path:
    sys.path.insert(0, PASTA_RAIZ)

from core.validators import (
    validar_cpf,
    validar_cnpj,
    validar_email,
    validar_cep,
    limpar_formatacao,
    formatar_cpf,
    formatar_cnpj,
    formatar_cep,
)
from core.viacep import consultar_cep
from core.email_service import EmailService


class TestCoreValidators(unittest.TestCase):

    def test_limpar_formatacao(self):
        self.assertEqual(limpar_formatacao("123.456.789-00"), "12345678900")
        self.assertEqual(limpar_formatacao("(11) 98765-4321"), "11987654321")
        self.assertEqual(limpar_formatacao(None), "")

    def test_validar_cpf(self):
        # CPFs com dígitos idênticos são inválidos
        self.assertFalse(validar_cpf("111.111.111-11"))
        self.assertFalse(validar_cpf("000.000.000-00"))
        # CPF com tamanho incorreto
        self.assertFalse(validar_cpf("123.456"))
        self.assertFalse(validar_cpf(""))
        # CPF com dígitos verificadores matematicamente válidos:
        # Ex: 529.982.247-25
        self.assertTrue(validar_cpf("529.982.247-25"))
        # Dígito final errado
        self.assertFalse(validar_cpf("529.982.247-20"))

    def test_validar_cnpj(self):
        # CNPJs com todos iguais
        self.assertFalse(validar_cnpj("11.111.111/1111-11"))
        self.assertFalse(validar_cnpj("00000000000000"))
        # CNPJ matematicamente válido:
        # Ex: 11.222.333/0001-81
        self.assertTrue(validar_cnpj("11.222.333/0001-81"))
        # Dígito final errado
        self.assertFalse(validar_cnpj("11.222.333/0001-99"))

    def test_validar_email(self):
        self.assertTrue(validar_email("usuario@empresa.com.br"))
        self.assertTrue(validar_email("contato.sdit@gmail.com"))
        self.assertFalse(validar_email("email_sem_arroba.com"))
        self.assertFalse(validar_email("@semusuario.com"))
        self.assertFalse(validar_email("usuario@semdominio"))
        self.assertFalse(validar_email(""))

    def test_validar_cep(self):
        self.assertTrue(validar_cep("01310-100"))
        self.assertTrue(validar_cep("01310100"))
        self.assertFalse(validar_cep("12345"))
        self.assertFalse(validar_cep(""))

    def test_formatadores(self):
        self.assertEqual(formatar_cpf("52998224725"), "529.982.247-25")
        self.assertEqual(formatar_cnpj("11222333000181"), "11.222.333/0001-81")
        self.assertEqual(formatar_cep("01310100"), "01310-100")


class TestCoreViaCEP(unittest.TestCase):

    def test_consultar_cep_invalido(self):
        self.assertIsNone(consultar_cep("123"))

    @patch("urllib.request.urlopen")
    def test_consultar_cep_mock(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = b'{"cep": "01310-100", "logradouro": "Avenida Paulista", "bairro": "Bela Vista", "localidade": "Sao Paulo", "uf": "SP"}'
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        dados = consultar_cep("01310-100")
        self.assertIsNotNone(dados)
        self.assertEqual(dados["logradouro"], "Avenida Paulista")
        self.assertEqual(dados["cidade"], "Sao Paulo")


class TestCoreEmailService(unittest.TestCase):

    def test_email_sem_credenciais(self):
        service = EmailService(usuario="", senha="")
        resultado = service.enviar("destinatario@teste.com", "Assunto", "<p>Corpo</p>")
        self.assertFalse(resultado)


if __name__ == "__main__":
    unittest.main()
