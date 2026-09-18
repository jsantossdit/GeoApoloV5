"""
Módulo de Gestão de Entidades do GeoAlvo.
Desacoplamento e migração de Delphi (unt_entidades.pas) para Python.
"""

import sys
from pathlib import Path

# Garante que o diretório raiz esteja no sys.path
_raiz_projeto = str(Path(__file__).resolve().parent.parent)
if _raiz_projeto not in sys.path:
    sys.path.insert(0, _raiz_projeto)

try:
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
except (ImportError, ModuleNotFoundError):
    from .models import (
        EntidadeFiltro,
        ItemComparacao,
        DecisaoLinha,
        ResultadoOperacao,
        EntidadeEdicao,
        CredencialAlvo,
    )
    from .repository import EntidadeRepository
    from .service import EntidadeService
    from .api_client import AlvoAPIClient
    from .view import EntidadesView

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
