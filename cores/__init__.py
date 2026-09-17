"""
Módulo de Cadastro de Cores de Produtos e Estoque Auxiliar.
GeoApolo V5
Clean Architecture: Models, Repository, Service e View desacopladas.
"""

from .models import CorDTO, ResultadoCorDTO
from .repository import CoresRepository
from .service import CoresService
from .view import CoresView, abrir_janela_cores

__all__ = [
    "CorDTO",
    "ResultadoCorDTO",
    "CoresRepository",
    "CoresService",
    "CoresView",
    "abrir_janela_cores",
]
