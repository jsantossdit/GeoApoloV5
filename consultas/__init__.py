"""
Módulo do Motor de Consultas Dinâmicas e Gestão de Permissões SQL.
GeoApolo V5
"""

from consultas.models import (
    ConsultaConfigDTO,
    PermissaoConsultaDTO,
    FiltroConsultaDTO,
    ResultadoConsultaDTO,
)
from consultas.repository import ConsultasRepository
from consultas.service import ConsultasService
from consultas.view import ConsultasView

__all__ = [
    "ConsultaConfigDTO",
    "PermissaoConsultaDTO",
    "FiltroConsultaDTO",
    "ResultadoConsultaDTO",
    "ConsultasRepository",
    "ConsultasService",
    "ConsultasView",
]
