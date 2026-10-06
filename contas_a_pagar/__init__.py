"""
Módulo de Contas a Pagar / Documentos Financeiros do GeoAlvo.
Permite gestão de títulos, integração com compras de estoque e baixa de documentos.
"""

from .models import DocumentoPagarDTO, FiltroContasPagarDTO, BaixaDocumentoDTO
from .repository import ContasPagarRepository
from .service import ContasPagarService
from .view import DocumentosPagarView, abrir_documentos_pagar

__all__ = [
    "DocumentoPagarDTO",
    "FiltroContasPagarDTO",
    "BaixaDocumentoDTO",
    "ContasPagarRepository",
    "ContasPagarService",
    "DocumentosPagarView",
    "abrir_documentos_pagar",
]
