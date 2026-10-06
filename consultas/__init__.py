"""
Módulo do Motor de Consultas Dinâmicas, Cadastro e Consultas Imediatas (Delphi).
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
from consultas.imediatas_view import ConsultasImediatasView, abrir_consultas_imediatas

__all__ = [
    "ConsultaConfigDTO",
    "PermissaoConsultaDTO",
    "FiltroConsultaDTO",
    "ResultadoConsultaDTO",
    "ConsultasRepository",
    "ConsultasService",
    "ConsultasView",
    "ConsultasImediatasView",
    "abrir_consultas_imediatas",
]
