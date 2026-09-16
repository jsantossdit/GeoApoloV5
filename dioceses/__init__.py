"""
Módulo de Gestão e Relacionamento de Entidades RCC com Dioceses da CNBB.
GeoApolo V5
"""

from .models import (
    EntidadeDioceseDTO,
    DioceseCNBBDTO,
    FiltroVinculoDioceseDTO,
    ResultadoOperacaoDiocese,
)
from .repository import DiocesesRepository
from .service import DiocesesService
from .view import RelacionaDioceseEntidadeView

__all__ = [
    "EntidadeDioceseDTO",
    "DioceseCNBBDTO",
    "FiltroVinculoDioceseDTO",
    "ResultadoOperacaoDiocese",
    "DiocesesRepository",
    "DiocesesService",
    "RelacionaDioceseEntidadeView",
]
