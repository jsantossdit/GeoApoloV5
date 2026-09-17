"""
Pacote de Serviços Centrais (Core) do GeoAlvo.
Validações de documentos, serviços de integração de CEP e e-mail.
"""

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
from core.recursos import obter_caminho_recurso

__all__ = [
    "validar_cpf",
    "validar_cnpj",
    "validar_email",
    "validar_cep",
    "limpar_formatacao",
    "formatar_cpf",
    "formatar_cnpj",
    "formatar_cep",
    "consultar_cep",
    "EmailService",
    "obter_caminho_recurso",
]
