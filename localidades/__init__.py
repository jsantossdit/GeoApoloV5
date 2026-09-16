"""
Módulo de Gestão de Localidades, Cidades e Distritos
GeoApolo V5
"""

from .models import (
    CidadeDistritoDTO,
    EntidadeLocalidadeDTO,
    ResultadoCorrecaoLocalidadeDTO,
)
from .repository import LocalidadesRepository
from .service import LocalidadesService
from .view import CorrecaoCidadesDistritosView

__all__ = [
    "CidadeDistritoDTO",
    "EntidadeLocalidadeDTO",
    "ResultadoCorrecaoLocalidadeDTO",
    "LocalidadesRepository",
    "LocalidadesService",
    "CorrecaoCidadesDistritosView",
]
