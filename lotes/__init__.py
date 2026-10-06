"""
Módulo de Cadastro e Controle de Lotes de Produtos do GeoApolo V5.
Clean Architecture: models, repository, service e view.
"""

from .models import ProdutoLoteDTO, ResultadoLoteDTO
from .repository import LotesRepository
from .service import LotesService
from .view import LotesView, abrir_janela_lotes
from .alerta_vencimento_view import exibir_alerta_vencimento_lote

__all__ = [
    "ProdutoLoteDTO",
    "ResultadoLoteDTO",
    "LotesRepository",
    "LotesService",
    "LotesView",
    "abrir_janela_lotes",
    "exibir_alerta_vencimento_lote",
]
