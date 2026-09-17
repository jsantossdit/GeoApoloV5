"""
Módulo de Departamentos, Seções e Vínculo com Centros de Controle.
GeoApolo V5
"""

from .models import DepartamentoDTO, ResultadoDepartamentoDTO
from .repository import DepartamentosRepository
from .service import DepartamentosService
from .view import DepartamentosView, abrir_janela_departamentos

__all__ = [
    "DepartamentoDTO",
    "ResultadoDepartamentoDTO",
    "DepartamentosRepository",
    "DepartamentosService",
    "DepartamentosView",
    "abrir_janela_departamentos",
]
