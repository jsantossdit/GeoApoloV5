"""
Módulo de Cadastro e Manutenção de Marcas de Produtos.
GeoApolo V5
Equivalente a unt_cadmarcas.pas do Delphi.
"""

from .models import MarcaDTO, ResultadoMarcaDTO
from .repository import MarcasRepository
from .service import MarcasService
from .view import MarcasView, abrir_janela_marcas

__all__ = [
    "MarcaDTO",
    "ResultadoMarcaDTO",
    "MarcasRepository",
    "MarcasService",
    "MarcasView",
    "abrir_janela_marcas",
]
