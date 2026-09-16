"""
Pacote de Parâmetros e Configurações Gerais do Sistema GeoAlvo.
"""

from configuracoes.models import (
    ConfiguracaoSistemaDTO,
    ServidorEmailDTO,
    ContaEmailDTO,
    ResultadoOperacao,
)
from configuracoes.repository import ConfiguracoesRepository
from configuracoes.service import ConfiguracoesService
from configuracoes.view import ConfiguracoesView

__all__ = [
    "ConfiguracaoSistemaDTO",
    "ServidorEmailDTO",
    "ContaEmailDTO",
    "ResultadoOperacao",
    "ConfiguracoesRepository",
    "ConfiguracoesService",
    "ConfiguracoesView",
]
