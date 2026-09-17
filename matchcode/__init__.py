"""
Módulo de Unificação de Cadastros e Duplicidades (MatchCode).
GeoApolo V5
"""

from matchcode.models import (
    MatchCodeUsuarioDTO,
    MatchCodeEntidadeDTO,
    ResultadoMatchCodeDTO,
)
from matchcode.repository import MatchCodeRepository
from matchcode.service import MatchCodeService
from matchcode.view import MatchCodeView

__all__ = [
    "MatchCodeUsuarioDTO",
    "MatchCodeEntidadeDTO",
    "ResultadoMatchCodeDTO",
    "MatchCodeRepository",
    "MatchCodeService",
    "MatchCodeView",
]
