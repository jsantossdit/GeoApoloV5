"""
Módulo de Dicionário de Nomes Amigáveis de Telas e Controles.
GeoApolo V5
"""

from .models import ObjetoSistemaDTO, ResultadoNomesAmigaveisDTO
from .repository import NomesAmigaveisRepository
from .service import NomesAmigaveisService
from .view import NomesAmigaveisView, abrir_janela_nomes_amigaveis

__all__ = [
    "ObjetoSistemaDTO",
    "ResultadoNomesAmigaveisDTO",
    "NomesAmigaveisRepository",
    "NomesAmigaveisService",
    "NomesAmigaveisView",
    "abrir_janela_nomes_amigaveis",
]
