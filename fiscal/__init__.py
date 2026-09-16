"""
Módulo Fiscal e de Auditoria de Cupons (NFC-e / PDV)
GeoApolo V5
"""

from .models import (
    AuditoriaCupomDTO,
    ResumoAuditoriaCupomDTO,
    ResultadoSincronizacaoCupomDTO,
)
from .repository import FiscalRepository
from .service import FiscalService
from .view import AuditoriaCuponsView

AuditoriaCuponsRepository = FiscalRepository
AuditoriaCuponsService = FiscalService

__all__ = [
    "AuditoriaCupomDTO",
    "ResumoAuditoriaCupomDTO",
    "ResultadoSincronizacaoCupomDTO",
    "FiscalRepository",
    "FiscalService",
    "AuditoriaCuponsRepository",
    "AuditoriaCuponsService",
    "AuditoriaCuponsView",
]
