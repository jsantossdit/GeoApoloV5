"""
Módulo CRM do GeoApolo V5.
Gestão de Ocorrências, Tipos de Campanha e Tipos de Tratamento.
Clean Architecture: Models, Repository, Service e View desacopladas.
"""

from .models import (
    TipoCampanhaDTO,
    TipoTratamentoDTO,
    OcorrenciaDTO,
    MotivoOcorrenciaDTO,
    OrigemDTO,
    SolicitanteDTO,
    ResultadoCRM,
)
from .repository import CRMRepository
from .service import CRMService
from .view import CRMView

__all__ = [
    "TipoCampanhaDTO",
    "TipoTratamentoDTO",
    "OcorrenciaDTO",
    "MotivoOcorrenciaDTO",
    "OrigemDTO",
    "SolicitanteDTO",
    "ResultadoCRM",
    "CRMRepository",
    "CRMService",
    "CRMView",
]
