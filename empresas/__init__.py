"""
Módulo de Multi-Empresas e Contexto Corporativo.
GeoApolo V5
"""

import sys
from pathlib import Path

# Garante que o diretório raiz esteja no sys.path
_raiz_projeto = str(Path(__file__).resolve().parent.parent)
if _raiz_projeto not in sys.path:
    sys.path.insert(0, _raiz_projeto)

try:
    from empresas.models import EmpresaDTO, ResultadoEmpresaDTO
    from empresas.repository import EmpresasRepository
    from empresas.service import EmpresasService
    from empresas.view import EmpresasView
except (ImportError, ModuleNotFoundError):
    from .models import EmpresaDTO, ResultadoEmpresaDTO
    from .repository import EmpresasRepository
    from .service import EmpresasService
    from .view import EmpresasView

__all__ = [
    "EmpresaDTO",
    "ResultadoEmpresaDTO",
    "EmpresasRepository",
    "EmpresasService",
    "EmpresasView",
]
