"""
Módulo de Gestão de Ativo Imobilizado e Depreciação Contábil
GeoApolo V5
"""

from .models import (
    AtivoImobilizadoDTO,
    CalculoDepreciacaoDTO,
    LookupItemDTO,
    ResultadoOperacaoAtivo,
)
from .repository import AtivoImobilizadoRepository
from .service import AtivoImobilizadoService
from .view import AtivoImobilizadoView
from .categoria_bens_view import CategoriaBensView, abrir_categorias_bens_sistema
from .localizacao_fisica_view import LocalizacaoFisicaView, abrir_localizacoes_fisicas_sistema
from .classificacao_bens_view import ClassificacaoBensView, abrir_classificacao_bens_sistema

__all__ = [
    "AtivoImobilizadoDTO",
    "CalculoDepreciacaoDTO",
    "LookupItemDTO",
    "ResultadoOperacaoAtivo",
    "AtivoImobilizadoRepository",
    "AtivoImobilizadoService",
    "AtivoImobilizadoView",
    "CategoriaBensView",
    "abrir_categorias_bens_sistema",
    "LocalizacaoFisicaView",
    "abrir_localizacoes_fisicas_sistema",
    "ClassificacaoBensView",
    "abrir_classificacao_bens_sistema",
]

