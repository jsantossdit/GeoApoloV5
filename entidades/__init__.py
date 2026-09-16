"""
Módulo de Gestão de Entidades do GeoAlvo.
Desacoplamento e migração de Delphi (unt_entidades.pas) para Python.
"""

from entidades.models import (
    EntidadeFiltro,
    ItemComparacao,
    DecisaoLinha,
    ResultadoOperacao,
    EntidadeEdicao,
    CredencialAlvo,
)
from entidades.repository import EntidadeRepository
from entidades.service import EntidadeService
from entidades.api_client import AlvoAPIClient
from entidades.view import EntidadesView

__all__ = [
    "EntidadeFiltro",
    "ItemComparacao",
    "DecisaoLinha",
    "ResultadoOperacao",
    "EntidadeEdicao",
    "CredencialAlvo",
    "EntidadeRepository",
    "EntidadeService",
    "AlvoAPIClient",
    "EntidadesView",
]
