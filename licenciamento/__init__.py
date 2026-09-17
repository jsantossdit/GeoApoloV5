"""
Módulo de Licenciamento, Segurança & Manutenção de Versões do GeoApolo.
GeoApolo V5
"""

from .models import (
    LicencaDTO,
    ResultadoValidacaoLicencaDTO,
    VersaoSistemaDTO,
    ResultadoOperacaoVersaoDTO,
)
from .repository import LicenciamentoRepository
from .service import LicenciamentoService
from .view import (
    ValidacaoLicencaView,
    ManutencaoVersoesView,
    NovidadesVersaoDialog,
    abrir_validacao_licenca,
    abrir_manutencao_versoes,
    verificar_novidades_ao_iniciar,
)

__all__ = [
    "LicencaDTO",
    "ResultadoValidacaoLicencaDTO",
    "VersaoSistemaDTO",
    "ResultadoOperacaoVersaoDTO",
    "LicenciamentoRepository",
    "LicenciamentoService",
    "ValidacaoLicencaView",
    "ManutencaoVersoesView",
    "NovidadesVersaoDialog",
    "abrir_validacao_licenca",
    "abrir_manutencao_versoes",
    "verificar_novidades_ao_iniciar",
]
